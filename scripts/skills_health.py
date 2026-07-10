#!/bin/sh
""":"
if command -v python >/dev/null 2>&1; then
    exec python "$0" "$@"
fi
exec python3 "$0" "$@"
":"""
"""Aggregate a read-only health report for the skill catalog.

Combines two deterministic signals into one per-skill view:
- SKILL Contract status (pass/warn/fail) from validate_skill_contract.py
- Declared-trigger routing (self-route + collision) from run_trigger_evals.py

This is reporting, not a gate — CI enforces the contract separately. Use it to
answer "which skills are healthy, and is the catalog's trigger routing clean?"

Usage:
    skills_health.py            # human-readable report
    skills_health.py --json     # machine-readable report
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_health_runtime as runtime  # noqa: E402  (I/O-free import)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "validate_skill_contract.py"
TRIGGERS = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "run_trigger_evals.py"


def _run_json(args: list[str]) -> dict:
    proc = subprocess.run(args, capture_output=True, text=True)
    # Both tools print JSON to stdout and use exit codes to flag issues; we read
    # the payload regardless of exit code (a failing contract is still valid JSON).
    out = proc.stdout.strip()
    if not out:
        raise RuntimeError(f"no JSON from {' '.join(args)}\n{proc.stderr}")
    return json.loads(out)


def _dojo_skill_names(skills_root: Path) -> list[str]:
    """Dojo catalog skill names: every `skills/<name>/SKILL.md` directory.

    Matches how the contract validator scopes the catalog (globs
    `skills_root/*/SKILL.md`), so findings scope stays identical to the full
    report without running the eval subprocesses.
    """
    return sorted(p.parent.name for p in skills_root.glob("*/SKILL.md"))


def build_report(skills_root: Path) -> dict:
    contract = _run_json([sys.executable, str(CONTRACT), "--skills-root", str(skills_root), "--json"])
    triggers = _run_json([sys.executable, str(TRIGGERS), "--from-triggers", "--skills-root", str(skills_root)])

    # Group trigger assertions by skill
    trig_by_skill: dict[str, list[dict]] = {}
    for a in triggers.get("assertions", []):
        trig_by_skill.setdefault(a["skill"], []).append(a)

    skills = []
    for item in contract.get("skills", []):
        name = item["skill"]
        declared = trig_by_skill.get(name, [])
        trig_failed = [a for a in declared if not a["passed"]]
        skills.append(
            {
                "skill": name,
                "skill_type": item.get("skill_type"),
                "contract_status": item["status"],
                "warnings": item.get("warnings", []),
                "required_failures": item.get("required_failures", []),
                "line_count": item.get("line_count"),
                "triggers_declared": len(declared),
                "triggers_failed": [a["trigger"] for a in trig_failed],
            }
        )

    csum = contract.get("summary", {})
    declaring = sum(1 for s in skills if s["triggers_declared"] > 0)
    report = {
        "summary": {
            "total": csum.get("total", len(skills)),
            "contract_pass": csum.get("pass", 0),
            "contract_warn": csum.get("warn", 0),
            "contract_fail": csum.get("fail", 0),
            "skills_declaring_triggers": declaring,
            "trigger_assertions": triggers.get("summary", {}).get("assertions", 0),
            "trigger_passed": triggers.get("summary", {}).get("passed", 0),
            "trigger_failed": triggers.get("summary", {}).get("failed", 0),
        },
        "skills": skills,
    }
    return report


def format_report(report: dict) -> str:
    s = report["summary"]
    lines = [
        "Skill Health Report",
        f"  catalog: {s['total']} skills",
        f"  contract: pass={s['contract_pass']} warn={s['contract_warn']} fail={s['contract_fail']}",
        f"  triggers: {s['skills_declaring_triggers']}/{s['total']} skills declare triggers; "
        f"assertions={s['trigger_assertions']} passed={s['trigger_passed']} failed={s['trigger_failed']}",
    ]

    flagged = [
        sk for sk in report["skills"]
        if sk["contract_status"] != "pass" or sk["triggers_failed"]
    ]
    if flagged:
        lines.append("")
        lines.append("Needs attention:")
        for sk in sorted(flagged, key=lambda x: (x["contract_status"] != "fail", x["skill"])):
            bits = [f"contract={sk['contract_status']}"]
            if sk["warnings"]:
                bits.append("warn:" + ",".join(sk["warnings"]))
            if sk["required_failures"]:
                bits.append("fail:" + ",".join(sk["required_failures"]))
            if sk["triggers_failed"]:
                bits.append("trigger-issues:" + ",".join(sk["triggers_failed"]))
            lines.append(f"  {sk['contract_status']:<5} {sk['skill']:<32} {'  '.join(bits)}")
    else:
        lines.append("")
        lines.append("All skills pass the contract; no trigger routing issues.")

    # Runtime section is strictly additive: rendered only when the report was
    # enriched with runtime health (i.e. runtime flags were passed).
    if report["summary"].get("runtime_source"):
        lines.extend(runtime.render_runtime_section(report))

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-root", default="skills", help="Path to skills directory (default: skills)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--runtime", action="store_true",
        help="Enrich the report with AgentMonitor trigger health (default endpoint)",
    )
    parser.add_argument(
        "--agentmonitor-url", default=None,
        help="AgentMonitor skills/health endpoint (implies --runtime)",
    )
    parser.add_argument(
        "--health-json", default=None,
        help="Read health data from a saved JSON file instead of the endpoint (implies --runtime)",
    )
    parser.add_argument(
        "--findings", action="store_true",
        help="Print paste-ready BACKLOG findings for never-fired skills (requires runtime; writes nothing)",
    )
    args = parser.parse_args()

    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        skills_root = (REPO_ROOT / skills_root).resolve()
    if not skills_root.is_dir():
        print(f"Skills root not found: {skills_root}", file=sys.stderr)
        return 1

    # Any runtime flag activates the runtime path.
    runtime_active = (
        args.runtime or args.agentmonitor_url is not None
        or args.health_json is not None or args.findings
    )
    url = None if args.health_json else (args.agentmonitor_url or runtime.DEFAULT_URL)
    source = args.health_json or url

    # Findings mode is deliberately decoupled from the static report: it needs
    # only the dojo catalog (for scoping) and the health rows, so it never runs
    # the contract/trigger eval subprocesses. A failure there must not suppress
    # a valid findings run, and findings must not invoke skill-evals (per spec).
    if args.findings:
        try:
            rows = runtime.load_health_rows(url=url, path=args.health_json)
        except RuntimeError as exc:
            print(f"Failed to load runtime skill health: {exc}", file=sys.stderr)
            return 1
        report = {
            "summary": {},
            "skills": [{"skill": n} for n in _dojo_skill_names(skills_root)],
        }
        runtime.enrich_report(report, rows, source=source)
        print(runtime.render_findings(report))
        return 0

    try:
        report = build_report(skills_root)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"Failed to build health report: {exc}", file=sys.stderr)
        return 1

    # Load + enrich happen before any report is printed, so a requested-but-failed
    # runtime load yields no partial report.
    if runtime_active:
        try:
            rows = runtime.load_health_rows(url=url, path=args.health_json)
            runtime.enrich_report(report, rows, source=source)
        except RuntimeError as exc:
            print(f"Failed to load runtime skill health: {exc}", file=sys.stderr)
            return 1

    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
