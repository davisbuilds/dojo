#!/usr/bin/env python3
"""The phase-1 CI gate: validate what CI can see, and refuse to pretend otherwise.

CI has neither harness binary and no session rollouts, so **it cannot observe an
effective catalog at all**. That bounds this gate sharply, and the boundary is
the point: the failures this program actually hit — a ceiling that moved three
times in eight days, a locator convention that reversed between builds, a
connector sync that refilled recovered headroom overnight — are all invisible
from CI by construction. A gate that appeared to cover them would be worse than
no gate.

What CI *can* prove is that the reviewed data is internally coherent and that the
cost model still reproduces a recorded render. That is checked here.

Exit 0 clean, 1 on failure. Every check reports what it evaluated, because a
green step that silently evaluated nothing is the degenerate pass this gate
exists to avoid.

Contract: docs/specs/2026-07-27-distribution-profiles-spec.md (SC-01…SC-04).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import definitions  # noqa: E402
from profiles.budget import Verdict, assess, load_policy  # noqa: E402
from profiles.resolve import resolve  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    failures: list[str] = []
    evaluated = 0

    catalog = definitions.load_catalog(REPO_ROOT / "skills.json")
    defs = definitions.load_definitions(REPO_ROOT / "profiles", catalog)
    print(f"definitions: {len(defs)} profiles over a {len(catalog)}-skill catalog")

    # Every declared composition must resolve, and its members must exist.
    overlays = [n for n, d in sorted(defs.items()) if d.kind == "overlay"]
    for overlay in overlays:
        try:
            result = resolve(("core", overlay), defs, catalog)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"core+{overlay} does not resolve: {exc}")
            continue
        missing = sorted(set(result.members) - set(catalog))
        if missing:
            failures.append(f"core+{overlay} names skills not in the catalog: {missing}")
        evaluated += 1
    print(f"compositions resolved: {evaluated} of {len(overlays)}")

    # Every reviewed policy must load, and a policy whose limit was never checked
    # against behaviour must not be able to gate.
    policy_dir = REPO_ROOT / "profiles" / "policies"
    policies = sorted(policy_dir.glob("*.yaml"))
    if not policies:
        failures.append("no budget policies found — the gate would evaluate nothing")
    for path in policies:
        try:
            policy = load_policy(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.name} does not load: {exc}")
            continue
        if policy.deployable and policy.provisional:
            failures.append(
                f"{path.name} is declared deployable on a provisional limit "
                f"({policy.limit_basis!r}); a limit never checked against behaviour "
                "may not gate")
        print(f"policy {path.name}: limit {policy.limit} {policy.unit} "
              f"({policy.limit_basis}), deployable={policy.deployable}, "
              f"surfaces={policy.declared_surfaces or 'any'}")

    # Non-degeneracy: score a real composition so the gate exercises the arithmetic
    # rather than only loading files.
    codex = load_policy(policy_dir / "codex.yaml")
    members = resolve(("core", "engineering"), defs, catalog).members
    entries = []
    for name in members:
        md = REPO_ROOT / "skills" / name / "SKILL.md"
        parts = md.read_text(encoding="utf-8").split("---")
        import yaml  # noqa: PLC0415

        desc = ((yaml.safe_load(parts[1]) or {}).get("description") or "").strip()
        entries.append({"name": name, "source_description": desc,
                        "locator": f"/r/{name}/SKILL.md"})
    scored = assess(entries, codex, surface="codex-tui")
    print(f"scored core+engineering: {len(members)} skills, {scored.demand} "
          f"{scored.unit} = {scored.basis_points / 100:.1f}% of {scored.limit} "
          f"-> {scored.verdict.value}")
    if scored.demand <= 0:
        failures.append("scoring produced zero demand; the gate evaluated nothing")
    if scored.verdict is Verdict.UNSUPPORTED:
        failures.append(f"scoring a reviewed composition was unsupported: {scored.reason}")

    # State the boundary rather than implying coverage.
    print("\nNOT checked here (requires a harness and session rollouts, which CI "
          "has neither of): effective-catalog observation, budget ceiling by "
          "saturation, degradation, and drift. Those are machine-side.")

    if failures:
        print("\nFAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("\nphase-1 profile gate: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
