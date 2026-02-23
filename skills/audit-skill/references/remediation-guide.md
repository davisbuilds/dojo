# Audit Finding Remediation Guide

## Structural Findings (STRUCT-*)

### STRUCT-001: Frontmatter Validation Failed
**Why dangerous**: Invalid frontmatter prevents proper skill loading and may indicate a tampered skill.
**Fix**: Ensure SKILL.md starts with valid YAML frontmatter containing `name` and `description`. Run `python3 skills/skill-creator/scripts/quick_validate.py <skill-dir>` to validate.

### STRUCT-011: High-Risk Allowed Tools
**Why dangerous**: Broad tool permissions (especially `Bash(*)`) let skill scripts execute arbitrary commands.
**Fix**: Narrow tool scopes to the minimum required. Instead of `Bash(*)`, use specific prefixes like `Bash(python3 scripts/my_script.py:*)`.

**Before**: `allowed-tools: [Bash(*)]`
**After**: `allowed-tools: [Bash(python3 skills/my-skill/scripts/run.py:*), Read, Glob]`

### STRUCT-020: Binary/Compiled Files
**Why dangerous**: Binary files cannot be audited and may contain malware.
**Fix**: Remove all `.pyc`, `.so`, `.dll`, `.exe`, `.bin` files. Skills should contain source code only.

### STRUCT-030: Undeclared Network Access
**Why dangerous**: Scripts making network calls without declaring the requirement may be exfiltrating data.
**Fix**: If network access is legitimate, add it to the `compatibility` field. If not needed, remove the network calls.

### STRUCT-040: Oversized Files
**Why dangerous**: Excessively large files consume context window and may hide malicious content.
**Fix**: Move detailed content to `references/` and keep SKILL.md concise. Split large references into focused documents.

## Instruction Findings (INSTR-*)

### INSTR-001: Prompt Injection Detected
**Why dangerous**: Prompt injection overrides agent safety constraints, enabling arbitrary behavior.
**Fix**: Remove the injection pattern. If the pattern is documented as an example (e.g., in a security reference), wrap it in a fenced code block — the audit strips code blocks before scanning.

**Before** (in prose): `If the user says "ignore previous instructions", handle it gracefully.`
**After** (in code block):
````
```
Example attack: "ignore previous instructions"
```
````

### INSTR-010: Encoding Tricks
**Why dangerous**: Base64 blobs and zero-width Unicode can hide instructions from human review while remaining visible to the agent.
**Fix**: Remove unexplained base64 content and zero-width characters. If base64 is needed (e.g., for image data), document its purpose clearly.

### INSTR-020: Exfiltration Patterns
**Why dangerous**: Instructions to send data to external URLs can leak sensitive information.
**Fix**: Remove exfiltration language. If the skill legitimately needs to send data externally, document the destination and purpose in the compatibility field.

### INSTR-030: Overreach
**Why dangerous**: Skills modifying agent configuration or accessing sensitive paths can compromise the entire agent environment.
**Fix**: Skills should never modify `.claude/settings`, `CLAUDE.md`, or access `~/.ssh`, `~/.aws`. Remove these references or clearly scope them as read-only documentation.

## Code Findings (CODE-*)

### CODE-001: eval()/exec() Usage
**Why dangerous**: Dynamic code execution enables arbitrary code injection (CWE-94).
**Fix**: Replace `eval()` with `ast.literal_eval()` for data parsing. Restructure logic to avoid dynamic execution.

**Before**: `result = eval(user_input)`
**After**: `result = ast.literal_eval(user_input)`

### CODE-002: Shell Injection (shell=True)
**Why dangerous**: `shell=True` and `os.system()` enable command injection (CWE-78).
**Fix**: Use `subprocess.run()` with argument lists.

**Before**: `subprocess.run(f"grep {query} file.txt", shell=True)`
**After**: `subprocess.run(["grep", query, "file.txt"])`

### CODE-003: Hardcoded Secrets
**Why dangerous**: Secrets in source code are exposed to anyone with repo access (CWE-798).
**Fix**: Use environment variables or a secrets manager.

**Before**: `api_key = "sk-abc123..."`
**After**: `api_key = os.environ["API_KEY"]`

### CODE-004: Dangerous Shell Patterns
**Why dangerous**: `rm -rf`, `curl|bash`, `chmod 777` are high-blast-radius operations (CWE-78).
**Fix**: Use targeted file operations, validate URLs before fetching, use minimal permissions.

### CODE-005: Runtime Package Installation
**Why dangerous**: Installing packages at runtime is a supply chain attack vector (CWE-829).
**Fix**: Declare dependencies in `requirements.txt` or `package.json` and install during setup, not at runtime.

For code-level vulnerability details, see also: `skills/secure-code/references/secure-coding-guidelines.md`
