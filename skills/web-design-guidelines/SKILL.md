---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## When To Use

- User asks to review, audit, or check UI code for best practices
- Checking accessibility, UX quality, or Web Interface Guidelines compliance
- User says "review my UI", "audit design", "check my site", or "check accessibility"
- Validating frontend code against the Vercel Web Interface Guidelines ruleset

## Boundaries

- Not for building or implementing UI; this skill only reviews existing code
- Not for backend, API, or non-UI code review
- Skip when the user needs visual design feedback on mockups rather than code-level audits
- Do not cache guidelines across sessions; always fetch fresh from the source URL

## Output

- A findings report in terse `file:line` format as specified by the fetched guidelines
- Each finding references the specific guideline rule that was violated
- A prompt for file selection if no files were specified by the user

## Verification

- Guidelines were freshly fetched from the source URL before the review
- All specified files were read and checked against the full ruleset
- Findings use the exact output format defined in the fetched guidelines document
- No false positives from rules that do not apply to the file's framework or context
