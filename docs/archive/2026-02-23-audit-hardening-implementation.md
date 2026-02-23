---
date: 2026-02-23
topic: audit-hardening
stage: implementation-plan
status: draft
source: conversation
---

# Audit Hardening Implementation Plan

## Goal

Fix false positives and gaps in the audit-skill tooling, then remediate real findings across all 40 skills, raising the fleet-wide pass rate from 82.5% to 95%+.

## Scope

### In Scope

- Fix the broken semgrep `python-hardcoded-secret` rule structure (~80+ false positives)
- Exclude `__pycache__` consistently across all audit layers
- Fix overreach pattern to distinguish "mentions" from "modifies"
- Fix allowed-tools parsing for YAML scalar strings (comma-separated)
- Add `compatibility` field to skills that use network APIs
- Remove `.DS_Store` files from 3 gh-* skills
- Convert `gh-commit-push-pr` allowed-tools from scalar to YAML list
- Re-audit all 40 skills and confirm pass rate improvement

### Out of Scope

- Suppression/allowlist mechanism (future enhancement)
- Moving oversized SKILL.md content to references/ (cosmetic, low priority)
- Adding `allowed-tools` to all 38 skills missing it (INFORMATIONAL, not actionable)
- Resolving self-referential trifecta findings in secure-code/audit-skill (inherent to security tools)

## Assumptions And Constraints

- The semgrep `metavariable-regex` is ignored because it's a sibling of `pattern-either` instead of being nested in a `patterns` block — this is a confirmed semgrep YAML structure bug
- Overreach patterns should only flag imperative instructions to modify config files, not documentation references
- `__pycache__` directories are build artifacts that should never be scanned
- Skills that call external APIs (OpenAI, GitHub, Vercel) should declare network in `compatibility`

## Task Breakdown

### Task 1: Fix semgrep `python-hardcoded-secret` rule structure

**Objective**

Wrap `pattern-either` and `metavariable-regex` inside a `patterns` conjunction so semgrep applies the variable name filter correctly.

**Files**

- Modify: `skills/audit-skill/rules/skill-scripts.yaml`

**Dependencies**

None

**Implementation Steps**

1. Replace the current `python-hardcoded-secret` rule (lines 51-67) with a corrected structure that uses `patterns` as the top-level operator containing both `pattern-either` and `metavariable-regex`.
2. Verify the regex covers: `api_key`, `apikey`, `secret`, `token`, `password`, `passwd`, `credential`, `auth_token`, `private_key`, `access_key`.

**Verification**

- Run: `semgrep --config skills/audit-skill/rules/skill-scripts.yaml skills/skill-standardizer/scripts/skill_standardizer_lib.py --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([r for r in d.get('results',[]) if 'hardcoded-secret' in r['check_id']]))"`
- Expect: 0 (was 25 false positives before)
- Run: `echo 'api_key = "sk-live-1234"' > /tmp/test_secret.py && semgrep --config skills/audit-skill/rules/skill-scripts.yaml /tmp/test_secret.py --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('results',[])))"`
- Expect: 1 (true positive still caught)

**Done When**

- Rule only fires on variables matching the secret-name regex
- Zero false positives on skill-standardizer (currently 25 hits)
- True positive on `api_key = "sk-live-1234"` still detected

### Task 2: Exclude `__pycache__` from all audit layers

**Objective**

Ensure `__pycache__` directories are skipped in `network_inference()` and that semgrep/trifecta scans exclude them too.

**Files**

- Modify: `skills/audit-skill/scripts/structural_audit.py`
- Modify: `skills/audit-skill/scripts/audit_skill.py`

**Dependencies**

None

**Implementation Steps**

1. In `structural_audit.py` `network_inference()`, change `scripts_dir.rglob("*")` to skip `__pycache__` directories (filter out paths where any component is `__pycache__`).
2. In `audit_skill.py` `run_code_audit_regex()`, add similar `__pycache__` filtering when walking script files.
3. For semgrep/trifecta subprocess calls, add `--exclude='__pycache__'` or `--exclude-dir` flag if supported, or filter results post-hoc.

**Verification**

- Run: `python3 skills/audit-skill/scripts/audit_skill.py skills/deep-research/ --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([f for f in d['findings'] if '__pycache__' in f.get('file','')]))"`
- Expect: 0

**Done When**

- No findings reference `__pycache__` paths in any skill audit
- deep-research and gpt-imagen audits produce fewer findings

### Task 3: Fix overreach patterns for documentation references

**Objective**

Overreach scan should only flag instructions to *modify* AGENTS.md/CLAUDE.md, not references to *reading* them.

**Files**

- Modify: `skills/audit-skill/scripts/instruction_audit.py`

**Dependencies**

None

**Implementation Steps**

1. Change the `AGENTS.md` and `CLAUDE.md` overreach patterns from bare filename matches to patterns that require modification verbs nearby (e.g., "modify", "edit", "change", "update", "write to", "add to") or imperative code patterns (`Edit`, `Write`).
2. Alternative simpler approach: require the match to NOT be preceded by documentation verbs ("see", "read", "refer to", "check", "consult", "For the complete guide").

**Verification**

- Run: `python3 skills/audit-skill/scripts/audit_skill.py skills/vercel-composition-patterns/ --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([f for f in d['findings'] if f['category']=='overreach']))"`
- Expect: 0 (was 1 false positive)

**Done When**

- Vercel skills (composition-patterns, react-best-practices, react-native-skills) no longer flagged for overreach
- Actual overreach patterns ("modify CLAUDE.md", "edit .claude/settings") still detected

### Task 4: Fix allowed-tools parsing for YAML scalars

**Objective**

When `allowed-tools` is a YAML scalar string (comma-separated) instead of a YAML list, parse it correctly by splitting on commas.

**Files**

- Modify: `skills/audit-skill/scripts/structural_audit.py`

**Dependencies**

None

**Implementation Steps**

1. In `allowed_tools_blast_radius()`, after reading `tools = fm.get("allowed-tools")`, check if `tools` is a string. If so, split on `, ` (comma-space) to produce a list.
2. Ensure the split handles edge cases: trailing commas, no spaces after commas.

**Verification**

- Run: `python3 skills/audit-skill/scripts/audit_skill.py skills/gh-commit-push-pr/ --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['score']['has_critical'])"`
- Expect: `False` (was `True` due to CRITICAL on unparsed string)

**Done When**

- gh-commit-push-pr passes audit (no CRITICAL)
- Individual tools in the comma-separated list are evaluated correctly (all are MEDIUM git/gh commands)

### Task 5: Add `compatibility` field for network-using skills

**Objective**

Declare network requirements in SKILL.md frontmatter for skills that use external APIs.

**Files**

- Modify: `skills/gpt-imagen/SKILL.md`
- Modify: `skills/skill-installer/SKILL.md`
- Modify: `skills/deep-research/SKILL.md`
- Modify: `skills/vercel-deploy/SKILL.md`
- Modify: `skills/secure-code/SKILL.md`
- Modify: `skills/audit-skill/SKILL.md`

**Dependencies**

None

**Implementation Steps**

1. For each skill, add or update the `compatibility` field in YAML frontmatter to mention network/internet/API requirements.
   - gpt-imagen: `compatibility: "Requires python3, openai package, OPENAI_API_KEY. Requires network access for API calls."`
   - skill-installer: `compatibility: "Requires python3, requests package. Requires network access for GitHub API."`
   - deep-research: `compatibility: "Requires python3. Requires network access for web research."`
   - vercel-deploy: `compatibility: "Requires Vercel CLI (npm i -g vercel). Requires network access for deployment."`
   - secure-code: `compatibility: "Requires python3, PyYAML. Layer 3 requires semgrep CLI. Semgrep rule downloads require network on first run."`
   - audit-skill: `compatibility: "Requires python3, PyYAML. Layer 3 requires semgrep CLI. Semgrep rule downloads require network on first run."`

**Verification**

- Run: `python3 skills/audit-skill/scripts/audit_skill.py skills/gpt-imagen/ --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([f for f in d['findings'] if f['category']=='undeclared-network']))"`
- Expect: 0 (was 8 for gpt-imagen)

**Done When**

- All 6 skills have `compatibility` field mentioning network
- No more STRUCT-030 undeclared-network findings for these skills

### Task 6: Remove `.DS_Store` and add `.gitignore`

**Objective**

Clean up macOS filesystem artifacts from skill directories.

**Files**

- Delete: `skills/gh-fix-issue/.DS_Store`
- Delete: `skills/gh-review-pr/.DS_Store`
- Delete: `skills/gh-triage-issues/.DS_Store`
- Create: `skills/.gitignore` (if not exists)

**Dependencies**

None

**Implementation Steps**

1. Remove `.DS_Store` from the three skill directories.
2. Add `.DS_Store` to `skills/.gitignore` (or root `.gitignore` if it already covers skills/).
3. Run `git rm --cached` if the files are tracked.

**Verification**

- Run: `find skills/ -name .DS_Store`
- Expect: no output

**Done When**

- No `.DS_Store` files in any skill directory
- `.gitignore` prevents future occurrences

### Task 7: Re-audit all 40 skills and validate improvement

**Objective**

Run the full audit suite and confirm the pass rate has improved significantly.

**Files**

- None (verification only)

**Dependencies**

Tasks 1-6

**Implementation Steps**

1. Run audit on all 40 skills with `--json` output.
2. Compile scorecard.
3. Compare pass rate against baseline (82.5%, 7 failures).

**Verification**

- Run: `for skill in skills/*/; do name=$(basename $skill); result=$(python3 skills/audit-skill/scripts/audit_skill.py "$skill" --json 2>/dev/null); score=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['score']['passed'])"); echo "$name: $score"; done`
- Expect: 95%+ pass rate (at most 2 failures — likely audit-skill and secure-code due to self-referential patterns)

**Done When**

- Pass rate >= 95% (38+ of 40 skills pass)
- Zero false positive `python-hardcoded-secret` findings
- Zero `__pycache__` findings
- Zero spurious overreach findings on documentation references
- gh-commit-push-pr no longer has CRITICAL

## Risks And Mitigations

- Risk: Tightening the semgrep secret rule could miss actual hardcoded secrets.
  Mitigation: Test against known true positive (`api_key = "sk-live-1234"`) and verify detection. The regex already covers the important variable name patterns.

- Risk: Overreach pattern relaxation could miss actual config modification attempts.
  Mitigation: Test against known bad patterns ("modify CLAUDE.md", "edit .claude/settings") to ensure they're still caught.

- Risk: Adding `compatibility` to SKILL.md could break frontmatter validation.
  Mitigation: `compatibility` is an allowed frontmatter field per the spec. Run quick_validate after each change.

## Verification Matrix

| Requirement | Proof command | Expected signal |
| --- | --- | --- |
| Semgrep secret rule precision | `semgrep --config ... skill_standardizer_lib.py` | 0 hardcoded-secret hits |
| Semgrep secret rule recall | `semgrep --config ... /tmp/test_secret.py` | 1 hit on `api_key = "sk-..."` |
| No __pycache__ findings | audit deep-research, grep for __pycache__ | 0 matches |
| No overreach on docs refs | audit vercel-composition-patterns | 0 overreach findings |
| gh-commit-push-pr passes | audit gh-commit-push-pr | `has_critical: false` |
| Network skills declare compat | audit gpt-imagen | 0 undeclared-network |
| No .DS_Store files | `find skills/ -name .DS_Store` | no output |
| Fleet pass rate | audit all 40 skills | >= 38 pass |

## Handoff

1. Execute in this session, task by task.
2. Open a separate execution session.
3. Refine this plan before implementation.
