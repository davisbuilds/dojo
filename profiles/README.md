# Distribution profiles

These files are **reviewed data, not configuration**. Each one declares a named,
versioned subset of the canonical dojo catalog so that a maintainer can say which
skills a target should receive — and so that absence from a profile reads as
intentional exclusion rather than as an installation nobody has got round to yet.

Contract: [`docs/specs/2026-07-27-distribution-profiles-spec.md`](../docs/specs/2026-07-27-distribution-profiles-spec.md)
(SC-01, SC-02, SC-03, SC-11). Loader and validation rules:
[`scripts/profiles/definitions.py`](../scripts/profiles/definitions.py).

## What is here

| File | Kind | Role |
|---|---|---|
| `core.yaml` | baseline | The general delivery loop. Mandatory in every deployable composition; membership fixed by SC-03. |
| `design.yaml`, `engineering.yaml`, `knowledge.yaml`, `research.yaml`, `shipping.yaml`, `skill-authoring.yaml` | overlay | Additive capability sets. Each carries its SC-02 anchors plus at least two non-`core` members. |
| `full.yaml` | inspection | The whole catalog, via the `"*"` sentinel. Never a default, no budget exemption. |
| `harness-equivalences.yaml` | — | Per `(skill, harness)` declarations that the harness ships its own equivalent of a member. |

One file per profile, on purpose: a duplicate definition then becomes a real,
detectable condition instead of a silently last-wins YAML key.

## The two identities, and which file moves which

This is the distinction most likely to be got wrong when editing here.

- **Changing overlay membership changes _profile identity_.** Profile identity is
  *intent* — the normalized selection plus the reviewed definition bodies — and
  it is harness-independent. Two machines selecting the same profile identity for
  the same harness must receive the same skills (SC-11); a membership edit means
  they are no longer selecting the same thing.
- **Changing `harness-equivalences.yaml` changes only _realization identity_.**
  A suppression describes what physically landed on one harness, not what the
  maintainer asked for. Profile identity stays byte-identical across harnesses
  while the realizations legitimately differ — which is precisely why spec
  revision 9 split the two identities rather than forbidding the divergence.

Consequences worth stating: an anchor suppressed on a harness that bundles its own
equivalent still satisfies SC-02, because anchors constrain the definition rather
than the realization. An anchor absent from the definition remains a violation.

## Why the overlays are small

Listing budget is the entire reason this contract exists. At a 200k-window Claude
Code session the harness-bundled entries alone take 3,774 of an 8,000-character
budget, leaving roughly 4,226 characters against a measured mean of ~313 per dojo
entry — **about 13 skills**, i.e. `core` (8) plus roughly one overlay (measured
2026-08-02; the verifier recomputes it at verify time and no number here is
load-bearing). A nine-member overlay is not a richer profile, it is an
undeployable one. Overlays here run three to four members and each member is
chosen for capability coherence with the overlay's name.

Every member carries an inline comment saying why it is present, and each file's
`description` records what was deliberately left out. Both are there so a reviewer
can challenge a choice; a member you cannot argue for should not be added.

**Not every catalog skill belongs to an overlay, and that is the design.** The
canonical catalog is the complete authoring inventory and may be larger than any
deployable profile (spec Assumptions). Full coverage of the catalog is not a goal,
and reaching for it would defeat the budget the profiles exist to respect.

## Changing something here

1. Edit the file, keeping the per-member comment.
2. `.venv/bin/python scripts/profiles/definitions.py` — prints resolved membership
   and the equivalence identity, and fails closed on any invalid definition.
3. `.venv/bin/python -m pytest tests/test_profiles_definitions.py -q`.

Adding or removing a profile *name* is a contract revision, not an edit: the
loader validates the file set against SC-02's vocabulary in both directions, so a
new file is rejected rather than silently admitted.
