---
date: 2026-07-09
topic: skill-health-consumer
stage: spec
status: complete
source: conversation
---

# Skill Health Consumer Spec

## Problem

AgentMonitor now measures per-skill trigger health (phase 1, shipped: `GET
/api/v2/analytics/skills/health` returns invocations, last-invoked, never-fired,
version attribution, and a misfire rate over real sessions). But nothing in dojo
consumes it, so the data improves no skills. Today skill maintenance is
intuition-driven: there's no routine surfacing which skills are dead weight in
the catalog (and the context budget), which are load-bearing, or which are
candidates for a closer look — even though that signal now exists and is
non-zero on real data (6 never-fired skills, invocation counts spanning 1–125
across 73 skills).

This is the improvement plane of the feedback loop: turn measured trigger health
into concrete, reviewable skill-maintenance actions, closing the loop that phase
1 opened. Without it, the measurement plane is a dashboard nobody acts on — the
explicit failure mode called out when this effort began.

## Contract

When this ships, running the consumer against a reachable AgentMonitor produces
a **deterministic skill-health report** that ranks dojo's skills by actionable
signal and records findings where a maintainer will see them:

1. The consumer fetches the health endpoint, joins it to dojo's own skill
   catalog (`skills.json`), and emits a report that, per skill, states:
   invocation count, never-fired status, last-invoked, and — labeled
   experimental — the misfire rate with its eligible denominator.
2. The report **ranks by the trustworthy signals**: never-fired skills (dead
   weight) and invocation volume (over/under-used). Misfire is displayed but is
   **not** a ranking input in v1.
3. Skills flagged by the trustworthy signals (e.g. never-fired dojo skills) are
   recorded as **actionable findings** a maintainer can act on — surfaced in the
   report and appendable to `BACKLOG.md` — rather than silently printed and lost.
4. The consumer **degrades honestly**: when AgentMonitor is unreachable or
   returns an unexpected shape, it fails with a clear message and non-zero exit,
   never a partial or fabricated report.

Verified by:

- The consumer, run against a committed health fixture, produces a report whose
  top-ranked entries are never-fired dojo skills, with misfire shown but not
  driving rank — asserted in tests, no network.
- Run against a malformed health payload, it exits non-zero with a diagnostic and
  writes no report.
- A test proves a never-fired dojo skill in the fixture yields a BACKLOG-shaped
  finding, and that a skill present in the health data but not in dojo's own
  catalog (installed elsewhere, renamed, or a plugin) is excluded from
  dojo-scoped findings.
- Against a live local AgentMonitor, the consumer returns a report over real data
  (smoke check; not a CI gate).

## Success Criteria

- A maintainer can answer "which of my skills never fire, and which are heavily
  used?" from one command, without opening AgentMonitor's UI.
- Never-fired dojo skills surface as findings ready to drop into `BACKLOG.md`.
- Misfire appears in the report clearly marked experimental, and changing a
  skill's misfire rate does not change its rank.
- Skills present in AgentMonitor but absent from dojo's catalog (other sources,
  renamed, plugins) do not produce dojo-scoped findings or crash the join.
- The report is reproducible: same input health data → byte-identical report.
- Running with AgentMonitor down produces a clear failure, not an empty or
  misleading report.

## Evaluation

If this is a measurable bet: the loop's value shows when consumer-surfaced
findings drive real skill edits (a never-fired skill's description gets fixed, a
dead skill is retired). That outcome is observed over subsequent sessions, not
gated here.

Mechanical acceptance for this spec is the verification commands above
(fixture-backed report + failure-path tests). No kill/scale thresholds.

## Scope

**In scope**

- A dojo-side consumer of the phase-1 health endpoint (fetch + catalog join).
- A deterministic, reproducible skill-health report ranked by never-fired and
  invocation-volume signals.
- Misfire displayed as experimental, excluded from ranking.
- Findings output for trustworthy-signal skills, shaped to append to
  `BACKLOG.md`.
- Honest failure on unreachable/malformed AgentMonitor responses.

**Out of scope**

- Widening or fixing the misfire signal itself (an AgentMonitor concern; tracked
  in its BACKLOG). This spec only consumes and labels it.
- Broadening version-attribution coverage (AgentMonitor-side, background).
- LLM-judged outcome scoring of transcripts.
- Auto-editing skills or auto-filing BACKLOG entries without a maintainer in the
  loop (findings are proposed, not applied).
- Automatically invoking `skill-evals` as a side effect; the report may
  recommend it, but running it stays a maintainer action in v1.
- A persistent dashboard or historical trend store (the report is point-in-time;
  AgentMonitor owns history).

## Assumptions And Constraints

- AgentMonitor's `GET /api/v2/analytics/skills/health` is the data source, in the
  shipped envelope `{ data: SkillHealthRow[], coverage }` where each row carries
  `name, version, versionApproximate, invocations, lastInvokedAt, neverFired,
  misfireEligible, misfires, misfireRate`.
- dojo's own skill set (the skills under `skills/`, as reflected in the catalog)
  is the scope for findings; skills present in the health data but not maintained
  by dojo must not produce dojo-scoped findings.
- Consumer runs locally against `127.0.0.1:3141` by default; AgentMonitor may not
  be running, which is an expected, handled condition — not an error to hide.
- Deterministic and reproducible per dojo's skill-evals conventions: same health
  input yields the same report; no time-varying content baked into the body.
- The misfire signal is currently near-zero on real data and under validation
  (AgentMonitor BACKLOG); v1 must not build ranking or automated action on it.

## Open Questions

- **Findings sink**: append directly to `docs/project/BACKLOG.md`, emit a
  paste-ready block the maintainer commits, or both behind a flag? Leaning
  paste-ready-by-default to keep a human in the loop.
- **Volume ranking normalization**: is raw invocation count enough, or does
  "under-used" need a floor/threshold to be meaningful (a skill used twice vs. a
  skill never used vs. a skill used 125×)? A never-fired-vs-rarely-fired boundary
  may need defining.
- **Input source**: fetch the endpoint live only, or also accept a saved
  `--health-json` file (used by tests) as a first-class mode for offline/CI runs?
- **Catalog identity**: `skills.json` name matching is straightforward, but
  should the report note when AgentMonitor's version attribution disagrees with
  the currently-installed dojo version (a possible sync-drift signal)?

## Handoff

Route to `write-plan` to sequence the build against this contract. The plan
lands in dojo (`docs/plans/`), since all phase-2 code (the consumer script,
fixtures, tests, report format) lives here. The AgentMonitor endpoint is a fixed
upstream dependency, already shipped.
