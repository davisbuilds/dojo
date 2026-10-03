# Local Review Replay Cases

Authored acceptance cases, not measured reviewer outcomes. In a blind evaluation,
provide the request and raw before/after repository fixtures without the expected
finding. Judge whether each comment establishes a real defect, not its wording.

| Case | Expected behavior |
| --- | --- |
| A changed producer renames a field; an unchanged consumer still reads the old key | Trace the consumer outside the diff; report the introduced mismatch at the changed producer. |
| One query adds a tenant condition; a sibling aggregation still mixes tenants | Determine whether the change introduces/exposes a promised isolation failure; report that path, not an assumed universal requirement. |
| An authoritative fetch now returns an empty list on transport failure; reconciliation deletes absent records | Report the reachable data-loss path and calibrate priority to its conditions. |
| CacheMiss is deliberately converted to None and the caller fetches from origin | No swallowed-error finding merely because there is no log. |
| A new update helper bypasses the validated constructor; negative quantities reach allocation | Trace the alternate write and violated consumer assumption; no type scorecard. |
| A plain DTO has public fields, with validated boundaries and no broken consumer | No anemic-model, branding, or encapsulation finding without a concrete defect. |
| A suspicious cast is preceded by a validator that rejects the candidate input | Reject the candidate after inspecting counterevidence. |
| A pre-existing bug is unchanged and not newly exposed | Exclude it from change findings; a broader audit can report it with explicit provenance. |
| A deliberate API break has an accepted migration and updated supported consumers | Do not flag the intended change; still examine whether the migration works. |
| Staged code differs from working-tree code | Review index blobs and matching context; do not cite unstaged behavior as a staged defect. |
| A long diff truncates before a second unrelated regression | Read the omitted paths; do not stop at the first finding or claim full coverage from the packet. |
| Review finds no defect, and no tests were run | State no qualifying findings and relevant evidence limits; no correctness certification or invented issue. |
| User requests native Codex review | Distinguish the native invocation from reading this skill; do not claim delegation occurred when it did not. |
