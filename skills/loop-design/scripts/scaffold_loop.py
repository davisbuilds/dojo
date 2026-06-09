#!/usr/bin/env python3
"""Scaffold a loop bundle from a blueprint.

This emits the concrete files a harness runs (LOOP.md, verify.sh, progress.md,
verifier.md, BINDINGS.md, blueprint.json). It does NOT run the loop.

The oracle gate is enforced here: a blueprint without a non-empty `done_when`
is refused, because a loop without a verifiable stop condition is not a loop.

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"

DEFAULTS = {
    "cadence": "until-done",
    "harness": "claude-code",
    "state_file": "progress.md",
    "constraints": ["Never edit, delete, or skip tests to make the oracle pass."],
    "checker": {
        "enabled": True,
        "model": "different",
        "instructions": (
            "Review the diff against the goal, constraints, and oracle output. "
            "Reject premature 'done', weakened tests, abstraction bloat, or dead code."
        ),
    },
    "sandbox": {
        "mode": "container",
        "creds": "staging-only / least-privilege",
        "budget": {"per_run_steps": 50, "daily_usd": 50},
    },
}

HARNESS_BINDINGS = {
    "claude-code": (
        "## Claude Code\n\n"
        "- `until-done`: run `/goal` with the contents of `LOOP.md` as the objective and "
        "\"stop when `./verify.sh` exits 0\" as the condition (a separate model grades the stop).\n"
        "- `interval:<dur>`: `/loop <dur> \"read LOOP.md and run exactly one iteration\"`.\n"
        "- `cron:'<expr>'`: a `/schedule` routine running the same one-iteration prompt.\n"
        "- Checker: place `verifier.md` at `.claude/agents/{name}-verifier.md` with `isolation: worktree`.\n"
        "- Isolation: run the maker with `--worktree` so parallel loops never collide.\n"
    ),
    "codex": (
        "## Codex\n\n"
        "- Scheduled: Automations tab -> project + prompt \"read LOOP.md, run one iteration\" + cadence, "
        "running on a worktree. Findings go to the Triage inbox.\n"
        "- `until-done`: `/goal` works across turns to a verifiable stop, with pause/resume.\n"
        "- Reusable method: wrap the iteration prompt as a skill (`$skill`). Skills define the method, "
        "automations define the schedule.\n"
        "- Checker: `.codex/agents/{name}-verifier.toml` (instructions from `verifier.md`, optional stronger model).\n"
    ),
    "github-actions": (
        "## GitHub Actions\n\n"
        "- `on: schedule: cron` workflow checks out the repo and runs the agent headless:\n"
        "  - Claude Code: `claude -p \"$(cat .loops/{name}/LOOP.md)\"`\n"
        "  - Codex: `codex exec \"$(cat .loops/{name}/LOOP.md)\"`\n"
        "- The job runs `verify.sh`; exit 0 -> open/label a PR, else commit progress and exit so the next run resumes.\n"
        "- Use repository/environment secrets scoped to staging. Hard-cap spend.\n"
    ),
    "ralph": (
        "## Ralph (bring your own runner)\n\n"
        "```bash\n"
        "# from inside .loops/{name}/\n"
        "while :; do\n"
        "  <agent> -p \"$(cat LOOP.md)\"   # fresh context each pass; memory is the repo\n"
        "  ./verify.sh && break           # the oracle is the only exit\n"
        "done\n"
        "```\n\n"
        "This skill does not ship the runner (that duplicates /loop and the ralph-wiggum plugin). "
        "Only loop with a real oracle, and add the checker before running unattended.\n"
    ),
}


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif v is not None:
            out[k] = v
    return out


def load_blueprint(args: argparse.Namespace) -> dict:
    bp: dict = {}
    if args.blueprint:
        bp = json.loads(Path(args.blueprint).read_text(encoding="utf-8"))
    # CLI overrides win over the file.
    overrides = {
        k: v
        for k, v in {
            "name": args.name,
            "goal": args.goal,
            "done_when": args.done_when,
            "cadence": args.cadence,
            "harness": args.harness,
        }.items()
        if v is not None
    }
    bp = deep_merge(DEFAULTS, deep_merge(bp, overrides))
    return bp


def require(bp: dict, key: str) -> str:
    val = bp.get(key)
    if val is None or str(val).strip() == "":
        raise SystemExit(
            f"[loop-design] Missing required field '{key}'. "
            "Provide it in the blueprint or via the matching flag."
        )
    return str(val).strip()


def enforce_oracle(bp: dict) -> None:
    dw = bp.get("done_when")
    if dw is None or str(dw).strip() == "":
        raise SystemExit(
            "[loop-design] GATE FAILED: no `done_when` oracle.\n"
            "A loop needs a verifiable stop condition: a command that exits 0 only when the goal is met.\n"
            "If you cannot write one, this task is not loop-shaped -- keep prompting interactively.\n"
            "Refusing to scaffold an unverifiable loop."
        )


def render(template_name: str, mapping: dict) -> str:
    text = (TEMPLATES / template_name).read_text(encoding="utf-8")
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def build_mapping(bp: dict) -> dict:
    constraints = bp.get("constraints") or DEFAULTS["constraints"]
    constraints_md = "\n".join(f"- {c}" for c in constraints)
    budget = (bp.get("sandbox") or {}).get("budget") or {}
    checker = bp.get("checker") or {}
    return {
        "NAME": require(bp, "name"),
        "GOAL": require(bp, "goal"),
        "DONE_WHEN": require(bp, "done_when"),
        "CONSTRAINTS": constraints_md,
        "STATE_FILE": str(bp.get("state_file", "progress.md")),
        "CADENCE": str(bp.get("cadence", "until-done")),
        "CHECKER_INSTRUCTIONS": str(checker.get("instructions", DEFAULTS["checker"]["instructions"])),
        "BUDGET_STEPS": str(budget.get("per_run_steps", 50)),
        "BUDGET_USD": str(budget.get("daily_usd", 50)),
        "SANDBOX_MODE": str((bp.get("sandbox") or {}).get("mode", "container")),
        "CREDS": str((bp.get("sandbox") or {}).get("creds", "staging-only / least-privilege")),
    }


def build_bindings(bp: dict) -> str:
    name = require(bp, "name")
    harness = str(bp.get("harness", "claude-code"))
    keys = list(HARNESS_BINDINGS) if harness in ("all", "any") else [harness]
    unknown = [k for k in keys if k not in HARNESS_BINDINGS]
    if unknown:
        raise SystemExit(f"[loop-design] Unknown harness(es): {', '.join(unknown)}")
    body = "\n".join(HARNESS_BINDINGS[k].format(name=name) for k in keys)
    return (
        f"# Bindings: {name}\n\n"
        f"Cadence: `{bp.get('cadence', 'until-done')}`. "
        "Full reference: `skills/loop-design/references/harness-bindings.md`.\n\n"
        f"{body}"
    )


def write_file(path: Path, content: str, executable: bool = False) -> None:
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a loop bundle from a blueprint.")
    ap.add_argument("--blueprint", help="Path to a blueprint JSON file.")
    ap.add_argument("--out-dir", help="Output directory (default: .loops/<name>).")
    ap.add_argument("--name", help="Loop name (slug).")
    ap.add_argument("--goal", help="One-sentence goal.")
    ap.add_argument("--done-when", dest="done_when", help="Oracle command (exit 0 == done).")
    ap.add_argument("--cadence", help="until-done | interval:<dur> | cron:'<expr>' | on-demand")
    ap.add_argument("--harness", help="claude-code | codex | github-actions | ralph | all")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing bundle dir.")
    args = ap.parse_args(argv)

    bp = load_blueprint(args)
    enforce_oracle(bp)
    mapping = build_mapping(bp)

    name = mapping["NAME"]
    out_dir = Path(args.out_dir) if args.out_dir else Path(".loops") / name
    if out_dir.exists() and any(out_dir.iterdir()) and not args.force:
        raise SystemExit(f"[loop-design] {out_dir} is not empty. Use --force to overwrite.")
    out_dir.mkdir(parents=True, exist_ok=True)

    write_file(out_dir / "LOOP.md", render("LOOP.md.tpl", mapping))
    write_file(out_dir / "verify.sh", render("verify.sh.tpl", mapping), executable=True)
    write_file(out_dir / mapping["STATE_FILE"], render("progress.md.tpl", mapping))
    write_file(out_dir / "verifier.md", render("verifier.md.tpl", mapping))
    write_file(out_dir / "BINDINGS.md", build_bindings(bp))
    write_file(out_dir / "blueprint.json", json.dumps(bp, indent=2) + "\n")

    print(f"[loop-design] Scaffolded loop '{name}' -> {out_dir}")
    for f in ("LOOP.md", "verify.sh", mapping["STATE_FILE"], "verifier.md", "BINDINGS.md", "blueprint.json"):
        print(f"  - {out_dir / f}")
    print(
        "\nNext: wire it via BINDINGS.md, then DRY-RUN ONE ITERATION ATTENDED.\n"
        "Confirm verify.sh exits 0 only when truly done and the checker rejects a weakened result\n"
        "before letting it run unattended."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
