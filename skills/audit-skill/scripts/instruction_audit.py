#!/usr/bin/env python3
"""Layer 2: Instruction audit for agent skills — prompt injection,
encoding tricks, exfiltration, and overreach detection."""

import re
import sys
from pathlib import Path

# --- Code block stripping ---


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks to avoid false positives on documented patterns."""
    return re.sub(r"```[\s\S]*?```", "", text)


# --- Pattern categories ---

PROMPT_INJECTION_PATTERNS = [
    # Role hijacking
    (r"\byou are now\b", "role-hijack"),
    (r"\bact as\b", "role-hijack"),
    (r"\bpretend to be\b", "role-hijack"),
    (r"\bassume the role\b", "role-hijack"),
    (r"\byou('re| are) a\b.*\b(hacker|admin|root|unrestricted)\b", "role-hijack"),
    # Instruction override
    (r"\bignore (all |your )?previous\b", "instruction-override"),
    (r"\bforget (all |your )?instructions\b", "instruction-override"),
    (r"\bdisregard\b.*\b(instructions|rules|guidelines|constraints)\b", "instruction-override"),
    (r"\bnew instructions\b", "instruction-override"),
    (r"\boverride\b.*\b(system|safety|instructions)\b", "instruction-override"),
    (r"\bdo not follow\b.*\b(rules|instructions|guidelines)\b", "instruction-override"),
    # Safety bypass
    (r"\bDAN mode\b", "safety-bypass"),
    (r"\bjailbreak\b", "safety-bypass"),
    (r"\bno restrictions\b", "safety-bypass"),
    (r"\bdeveloper mode\b", "safety-bypass"),
    (r"\bunrestricted mode\b", "safety-bypass"),
    (r"\bbypass\b.*\b(filter|safety|guard|restriction)\b", "safety-bypass"),
    # System prompt extraction
    (r"\breveal your (instructions|prompt|system)\b", "prompt-extraction"),
    (r"\bshow me your (prompt|instructions|system)\b", "prompt-extraction"),
    (r"\bprint your (system|initial) (prompt|message)\b", "prompt-extraction"),
    (r"\bwhat are your instructions\b", "prompt-extraction"),
    (r"\brepeat (your|the) (system|initial) (prompt|message)\b", "prompt-extraction"),
    # Privilege escalation
    (r"\byou are root\b", "privilege-escalation"),
    (r"\bsudo\b", "privilege-escalation"),
    (r"\badmin access\b", "privilege-escalation"),
    (r"\bgrant.{0,20}(permission|access|privilege)\b", "privilege-escalation"),
    (r"\belevate.{0,20}(permission|access|privilege)\b", "privilege-escalation"),
]

ENCODING_PATTERNS = [
    # Base64 blobs (>50 chars of base64 alphabet)
    (r"[A-Za-z0-9+/]{50,}={0,2}", "base64-blob"),
    # Zero-width Unicode
    (r"[\u200b\u200c\u200d\ufeff]", "zero-width-unicode"),
    # HTML comments with suspicious content
    (r"<!--.*?(script|eval|exec|system|password|token|secret).*?-->", "suspicious-html-comment"),
    # Repeated hex sequences (potential obfuscation)
    (r"(\\x[0-9a-fA-F]{2}){10,}", "hex-sequence"),
]

EXFILTRATION_PATTERNS = [
    # Send/post/upload near URL patterns
    (r"\b(send|post|upload|exfiltrate)\s+(to|data)\b.*https?://", "exfiltration-url"),
    (r"https?://.*\b(send|post|upload|exfiltrate)\b", "exfiltration-url"),
    # curl/wget/fetch in prose (outside code blocks, caught after stripping)
    (r"\bcurl\b.*https?://", "exfiltration-command"),
    (r"\bwget\b.*https?://", "exfiltration-command"),
    (r"\bfetch\(\s*['\"]https?://", "exfiltration-command"),
]

OVERREACH_PATTERNS = [
    # Modifying agent config
    (r"\.claude/settings", "config-modification"),
    (r"\bCLAUDE\.md\b", "config-modification"),
    (r"\bAGENTS\.md\b", "config-modification"),
    # Disabling protections
    (r"\bdisable hook\b", "protection-bypass"),
    (r"\bskip validation\b", "protection-bypass"),
    (r"--no-verify\b", "protection-bypass"),
    (r"\bdisable.{0,20}(check|guard|hook|validation)\b", "protection-bypass"),
    # Cross-skill access
    (r"\.\./skills/", "cross-skill-access"),
    # Sensitive paths
    (r"~/\.ssh\b", "sensitive-path"),
    (r"~/\.aws\b", "sensitive-path"),
    (r"~/\.gnupg\b", "sensitive-path"),
    (r"/etc/(passwd|shadow|sudoers)", "sensitive-path"),
    (r"~/\.env\b", "sensitive-path"),
]


def collect_markdown_files(skill_path: Path) -> list[tuple[Path, str]]:
    """Gather all markdown files to audit: SKILL.md, commands/*.md, references/*.md."""
    files = []
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        files.append(skill_md)

    for subdir in ("commands", "references"):
        d = skill_path / subdir
        if d.exists():
            files.extend(sorted(d.rglob("*.md")))

    result = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            result.append((f, content))
        except OSError:
            pass
    return result


def _scan_patterns(
    text: str,
    patterns: list[tuple[str, str]],
    finding_prefix: str,
    severity: str,
    category: str,
    file_rel: str,
) -> list[dict]:
    """Scan stripped text against a pattern list, returning findings."""
    findings = []
    lines = text.split("\n")
    seen = set()

    for pattern, subcategory in patterns:
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            continue
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                key = (file_rel, i, subcategory)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    {
                        "id": finding_prefix,
                        "severity": severity,
                        "layer": 2,
                        "category": category,
                        "message": f"{subcategory}: {line.strip()[:120]}",
                        "file": file_rel,
                        "line": i,
                        "remediation": f"Review and remove or justify this {category} pattern.",
                    }
                )
    return findings


def prompt_injection_scan(
    skill_path: Path, files: list[tuple[Path, str]]
) -> list[dict]:
    """Scan for prompt injection patterns in markdown files."""
    findings = []
    for fpath, content in files:
        stripped = strip_code_blocks(content)
        rel = str(fpath.relative_to(skill_path))
        findings.extend(
            _scan_patterns(
                stripped,
                PROMPT_INJECTION_PATTERNS,
                "INSTR-001",
                "CRITICAL",
                "prompt-injection",
                rel,
            )
        )
    return findings


def encoding_scan(skill_path: Path, files: list[tuple[Path, str]]) -> list[dict]:
    """Scan for encoding tricks and obfuscation."""
    findings = []
    for fpath, content in files:
        rel = str(fpath.relative_to(skill_path))
        findings.extend(
            _scan_patterns(
                content,  # Don't strip code blocks — encoding tricks can hide anywhere
                ENCODING_PATTERNS,
                "INSTR-010",
                "HIGH",
                "encoding-trick",
                rel,
            )
        )
    return findings


def exfiltration_scan(
    skill_path: Path, files: list[tuple[Path, str]]
) -> list[dict]:
    """Scan for data exfiltration patterns."""
    findings = []
    for fpath, content in files:
        stripped = strip_code_blocks(content)
        rel = str(fpath.relative_to(skill_path))
        findings.extend(
            _scan_patterns(
                stripped,
                EXFILTRATION_PATTERNS,
                "INSTR-020",
                "HIGH",
                "exfiltration",
                rel,
            )
        )
    return findings


def overreach_scan(skill_path: Path, files: list[tuple[Path, str]]) -> list[dict]:
    """Scan for overreach patterns — config modification, sensitive paths."""
    findings = []
    for fpath, content in files:
        stripped = strip_code_blocks(content)
        rel = str(fpath.relative_to(skill_path))
        findings.extend(
            _scan_patterns(
                stripped,
                OVERREACH_PATTERNS,
                "INSTR-030",
                "HIGH",
                "overreach",
                rel,
            )
        )
    return findings


def run_instruction_audit(skill_path: str) -> list[dict]:
    """Run all instruction-level checks and return findings."""
    path = Path(skill_path)
    files = collect_markdown_files(path)
    findings = []
    findings.extend(prompt_injection_scan(path, files))
    findings.extend(encoding_scan(path, files))
    findings.extend(exfiltration_scan(path, files))
    findings.extend(overreach_scan(path, files))
    return findings


if __name__ == "__main__":
    import json

    if len(sys.argv) != 2:
        print("Usage: instruction_audit.py <skill-directory>", file=sys.stderr)
        sys.exit(1)
    results = run_instruction_audit(sys.argv[1])
    json.dump(results, sys.stdout, indent=2)
    print()
