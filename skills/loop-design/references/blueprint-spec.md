# Optional Loop Blueprint

Use a blueprint when a portable execution brief serves a consumer. An existing
runtime prompt, task record, or scheduler configuration may already be sufficient.
The scaffolder writes instructions, not an enforcement layer or a runtime.

## Schema 2

Required fields are `schema_version: 2`, `name`, `kind`, `goal`, `evidence`, and
`stop_when`. Except for the integer version, these are nonempty strings. Unknown
fields are rejected to catch typos and obsolete control declarations.

| Field | Meaning |
| --- | --- |
| `name` | Lowercase letters/digits separated by single hyphens; at most 64 characters. Used for the default `.loops/<name>` directory. |
| `kind` | `task`, `monitor`, or `experiment`. Selects the interpretation reminder in the generated prompt. |
| `goal` | Intended outcome or useful observation. |
| `evidence` | How to assess the result, including coverage, uncertainty, and any acceptance or review needed. |
| `stop_when` | Relevant completion, run limits, cancellation, and escalation conditions. Text describing them does not enforce them. |
| `authority` | Optional scope of authorized actions. Defaults to read-only, with no external writes, publication, or dispatch. Supply the actual previously authorized scope for mutating work. |
| `runtime` | Optional runner, cadence, enforcement, state, and delivery wiring. Defaults explicitly to unconfigured. |
| `constraints` | Optional array of task-specific instructions. Defaults to empty; project guidance still applies. |
| `checkpoint` | Optional boolean, default false. Generates a compact `checkpoint.md` when existing runtime state is insufficient. |
| `check` | Optional object containing exactly `command` and `cwd`, both nonempty strings. `cwd` must be an existing absolute directory on this host. Generates `check.sh`; shell text is intentional executable code, not validated as safe by the scaffolder. |

Example: a monitor with a finite schedule, no completion command, and explicit
unavailable-data handling. Replace the illustrative runtime with actual wiring
before running it:

```json
{
  "schema_version": 2,
  "name": "deployment-monitor",
  "kind": "monitor",
  "goal": "Track the selected deployment until the end of the observation window.",
  "evidence": "Read the deployment's authoritative status by ID. Report transitions once. Treat denied, missing, or partial data as unavailable, never healthy.",
  "stop_when": "End each observation after its result or 60 seconds. Expire the schedule after 30 minutes or on cancellation; report final coverage.",
  "authority": "Read deployment state and report in the requesting session. No repairs or external messages.",
  "runtime": "Not wired yet: select an available scheduler with per-run timeout, expiry, no overlapping runs, and delivery to the requesting session.",
  "checkpoint": true
}
```

For a **task**, evidence might be a reproducer passing on the changed revision
plus inspection of the affected behavior; a limit must still yield an incomplete
report if acceptance is unmet. For an **experiment**, evidence might compare
latency and correctness against a recorded baseline on the same workload; stopping
after the trial budget preserves the best candidate without adopting it.
These descriptions need concrete task details, not a universal pass/fail oracle.

## Invocation and output

```bash
python3 <skill-dir>/scripts/scaffold_loop.py --blueprint <blueprint.json> --out-dir .loops/<name>
```

The brief can also be supplied through `--name`, `--kind`, `--goal`, `--evidence`,
`--stop-when`, `--authority`, and `--runtime`; `--checkpoint` opts in to the state
file. CLI fields override the JSON file. File input must declare schema 2; direct
CLI input uses schema 2. `--help` describes the arguments.

The default output is `LOOP.md` and the effective `blueprint.json`. Optional
files are `checkpoint.md` and `check.sh`. The output path must be new, even if an
existing directory is empty. There is no force-overwrite option: regenerating
must not erase recovery state or leave obsolete executables next to new guidance.

`check.sh` runs the supplied command **once** through POSIX `sh` in the declared
absolute directory, preserving stdout, stderr, and exit status. It has no timeout
or retry logic; the caller owns those. Missing working directories fail before
the command executes. Commands requiring another shell must invoke it explicitly.
Moving the bundle to another host requires revisiting its recorded paths.
Scaffolding never executes the command. Inspect its effects and authorization
before running it; a verification command can itself mutate data or incur cost.

A zero exit means only what the command's contract establishes. The evidence
criteria must distinguish task acceptance, a healthy monitoring sample, a valid
measurement, and unavailable evidence. An identical failure message on two runs
does not by itself establish a stall. More matching results do not by themselves
establish determinism.

## Migrating a v1 bundle

Version 2 changes the workflow and generated-file contract. Existing v1 bundles
continue to be files under their original runner; updating the skill does not
migrate, stop, or reschedule them. Pause an affected runner before switching its
inputs, preserve its current checkpoint and any in-flight operation references,
and inspect its actual configuration.

- Replace `done_when` with explicit `evidence` and `stop_when`; optionally move
  its command into `check.command` with an explicit `check.cwd`. Do not reinterpret
  a health check as whole-schedule completion.
- Replace `cadence` and `harness` with the actual `runtime` wiring. Replace
  `sandbox` declarations with real runtime controls and the `authority` scope;
  a configured-looking label is not proof those controls were ever active.
- Use `checkpoint: true` only if the runtime lacks sufficient state. Summarize
  the old `state_file` into current facts and evidence references; retain useful
  history without making the next run reread it all.
- Move applicable checker criteria into `evidence` and retain an independently
  wired reviewer when the task warrants one. There is no generated `verifier.md`.
- `protected_paths`, `guard.sh`, `verify.sh --selftest`, and generated `BINDINGS.md`
  are retired. A writable Git-status script was neither containment nor proof
  of cheating. If path-change detection is needed, use a trusted baseline and
  a check that reports detector errors; committed changes must also be covered.
  Permissions belong to the runtime, not to an agent-editable gate.

Generate into a new directory, transfer the necessary current state, update all
runner references, and check the changed behavior before resuming. Keep prior
run evidence where it has a consumer; ordinary recoverable source need not be
copied into backup directories. The scaffolder rejects v1 input rather than
silently dropping old fields or pretending their controls were migrated.
