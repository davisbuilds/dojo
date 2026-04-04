# Artifact Layout

Default repo-local output directory:

```text
.repo-hardening/
```

Default files:

- `inventory.json`
  Raw deterministic scan output. This is the evidence source.
- `audit.md`
  Findings-first human-readable summary of the current repo state.
- `hardening-plan.md`
  Ordered fix plan with immediate and next steps.

## Override Rule

Use `.repo-hardening/` unless the target repo already has an established security artifact location and the user wants to keep using it.

Examples:

- default: `.repo-hardening/`
- explicit override: `security/`

## Update Rule

Refresh the artifact packet:

- after a new audit
- after any hardening change
- before handoff when residual risk changed
