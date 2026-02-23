# Full Skill Audit Results — 2026-02-23

## Scorecard

| Skill | Grade | Score | Pass? | CRIT | HIGH | MED | LOW | Findings |
|-------|-------|-------|-------|------|------|-----|-----|----------|
| agent-native-architecture | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| algorithmic-art | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| **audit-skill** | **F** | **10.5** | **No** | **0** | **17** | **0** | **0** | 26 |
| autonomous-engineering | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| brainstorming | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| code-review-agents | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| compact-session | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| compound-docs | A | 95 | Yes | 0 | 1 | 1 | 0 | 2 |
| create-cli | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| **deep-research** | **B** | **75** | **No** | **1** | **5** | **0** | **0** | 7 |
| find-skills | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| first-principles | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| frontend-design | A | 92 | Yes | 0 | 2 | 0 | 0 | 3 |
| gemini-imagen | B | 84 | Yes | 0 | 4 | 0 | 0 | 5 |
| **gh-commit-push-pr** | **A** | **95** | **No** | **1** | **0** | **0** | **0** | 1 |
| gh-fix-issue | A | 98.8 | Yes | 0 | 0 | 1 | 0 | 2 |
| gh-review-pr | A | 98.8 | Yes | 0 | 0 | 1 | 0 | 2 |
| gh-triage-issues | A | 98.8 | Yes | 0 | 0 | 1 | 0 | 2 |
| **gpt-imagen** | **D** | **55** | **No** | **0** | **13** | **0** | **0** | 15 |
| json-canvas | A | 97.9 | Yes | 0 | 0 | 1 | 0 | 2 |
| local-review | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| markdown-converter | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| obsidian-bases | A | 97.9 | Yes | 0 | 0 | 1 | 0 | 2 |
| obsidian-markdown | A | 97.9 | Yes | 0 | 0 | 1 | 0 | 2 |
| playwright | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| screenshot | B | 80 | Yes | 0 | 5 | 0 | 0 | 6 |
| **secure-code** | **B** | **86** | **No** | **1** | **2** | **0** | **0** | 4 |
| skill-creator | B | 80 | Yes | 0 | 5 | 0 | 0 | 6 |
| **skill-installer** | **F** | **35** | **No** | **0** | **23** | **1** | **0** | 25 |
| **skill-standardizer** | **C** | **60** | **No** | **0** | **25** | **0** | **0** | 26 |
| template | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| theme-factory | A | 96 | Yes | 0 | 1 | 0 | 0 | 2 |
| vercel-composition-patterns | A | 94.2 | Yes | 0 | 1 | 0 | 0 | 2 |
| vercel-deploy | B | 87 | Yes | 0 | 4 | 0 | 0 | 5 |
| vercel-preview-logs | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| vercel-react-best-practices | A | 92.1 | Yes | 0 | 1 | 1 | 0 | 3 |
| vercel-react-native-skills | A | 94.2 | Yes | 0 | 1 | 0 | 0 | 2 |
| verify-before-complete | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| web-design-guidelines | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |
| writing-plans | A | 100 | Yes | 0 | 0 | 0 | 0 | 1 INFO |

## Summary

- **40 skills audited**
- **33 pass** (82.5%), **7 fail** (17.5%)
- **3 CRITICAL findings** (2x trifecta, 1x allowed-tools parse bug)
- **~100+ HIGH findings**, majority are false positive "hardcoded secret" detections

## Failing Skills

| Skill | Score | Root Cause |
|-------|-------|------------|
| audit-skill | F (10.5) | Self-referential: its security patterns appear in its own code |
| skill-installer | F (35) | Undeclared network + many FP "hardcoded secret" hits |
| gpt-imagen | D (55) | Undeclared network + FP secrets + __pycache__ scanning |
| skill-standardizer | C (60) | 25 FP "hardcoded secret" hits on constant definitions |
| deep-research | B (75) | Trifecta detection + FP secrets + __pycache__ |
| secure-code | B (86) | Trifecta detection (expected — it scans trifectas) |
| gh-commit-push-pr | A (95) | Allowed-tools parsing bug (comma-sep string parsed as one token) |

## Systemic Issues Identified

### Issue 1: `python-hardcoded-secret` semgrep rule is far too broad (HIGHEST IMPACT)
The rule `$KEY = "..."` matches ANY Python string assignment. It fires on:
- `AGENTS_HOME_ENV = "AGENTS_HOME"` (env var names)
- `TEST_MODE_ENV = "CODEX_SCREENSHOT_TEST_MODE"` (test config)
- `DEFAULT_MODEL = "gpt-image-1"` (model names)
- Constants, paths, format strings, etc.

**Impact**: ~80+ false positive findings across 10+ skills. This is the single biggest source of noise.

### Issue 2: `__pycache__` directories not excluded from scanning
`structural_audit.py` excludes `__pycache__` in `file_inventory()` but NOT in `network_inference()`. Other layers also scan `.pyc` files via semgrep.

**Impact**: Duplicate findings on compiled bytecode in deep-research, gpt-imagen, skill-installer.

### Issue 3: Undeclared network access in `compatibility` field
Several skills use network APIs (OpenAI, GitHub) but don't declare this in their SKILL.md `compatibility` field.

**Impact**: 5+ skills flagged (gpt-imagen, skill-installer, deep-research, vercel-deploy, secure-code, audit-skill).

### Issue 4: Allowed-tools comma-separated string parsing bug
`gh-commit-push-pr` uses a YAML scalar for `allowed-tools` (comma-separated string) instead of a YAML list. The audit parses it as a single tool string, which fails the length check and gets CRITICAL.

**Impact**: 1 skill (gh-commit-push-pr), but reveals a parser robustness gap.

### Issue 5: Self-referential false positives in security tools
`audit-skill` and `secure-code` contain security detection patterns (keywords like "curl", "wget", "eval") in their own code. The audit correctly flags these as findings but they're false positives in context.

**Impact**: audit-skill scores F, secure-code gets trifecta CRITICAL.

### Issue 6: `.DS_Store` files in skill directories
macOS Finder detritus in 3 skills (gh-fix-issue, gh-review-pr, gh-triage-issues).

**Impact**: Low (MEDIUM severity), but indicates missing `.gitignore`.

### Issue 7: Oversized SKILL.md files
4 skills exceed the 500-line threshold: compound-docs, json-canvas, obsidian-bases, obsidian-markdown.

**Impact**: Low. Content could move to `references/`.

### Issue 8: Vercel skills have "overreach" false positives
3 Vercel skills reference `AGENTS.md` in their text, triggering config-modification detection.

**Impact**: Low. The reference is documentation, not modification.
