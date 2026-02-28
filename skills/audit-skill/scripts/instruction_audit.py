#!/usr/bin/env python3
"""Layer 2: Instruction audit for agent skills — prompt injection,
encoding tricks, exfiltration, and overreach detection."""

import re
import sys
import math
from pathlib import Path
from typing import Callable

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
    # Zero-width Unicode
    (r"[\u200b\u200c\u200d\ufeff]", "zero-width-unicode"),
    # HTML comments with suspicious content
    (r"<!--.*?(script|eval|exec|system|password|token|secret).*?-->", "suspicious-html-comment"),
    # Repeated hex sequences (potential obfuscation)
    (r"(\\x[0-9a-fA-F]{2}){10,}", "hex-sequence"),
]

BASE64_BLOB_RE = re.compile(r"(?<![A-Za-z0-9+/=])(?:[A-Za-z0-9+/]{4}){16,}(?:==|=)?(?![A-Za-z0-9+/=])")
BASE64_SHORT_RE = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{12,}={0,2}(?![A-Za-z0-9+/=])")
BASE64_DECODE_HINTS = (
    "base64",
    "decode",
    "b64decode",
    "frombase64string",
    "atob",
    "powershell -enc",
    "eval(",
    "exec(",
)

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
    # Modifying agent/harness config
    (
        r"(?:modify|edit|change|update|write\s+to|add\s+to|overwrite|delete|remove|tamper\s+with)\b.{0,120}(?:\.claude|\.agents|\.codex)/settings(?:\.json)?\b",
        "config-modification",
    ),
    (r"(?:modify|edit|change|update|write\s+to|add\s+to|overwrite|delete|remove)\s+.*\bCLAUDE\.md\b", "config-modification"),
    (r"(?:modify|edit|change|update|write\s+to|add\s+to|overwrite|delete|remove)\s+.*\bAGENTS\.md\b", "config-modification"),
    # Disabling protections
    (r"\bdisable hook\b", "protection-bypass"),
    (r"\bskip validation\b", "protection-bypass"),
    (r"--no-verify\b", "protection-bypass"),
    (r"\b(?:disable|turn off|bypass|skip)\b.{0,30}\b(?:hook|guard|validation|safety|protection)\b", "protection-bypass"),
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
    line_filter: Callable[[str], bool] | None = None,
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
                if line_filter and not line_filter(line):
                    continue
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


PROTECTIVE_GUIDANCE_RE = re.compile(
    r"\b(?:never|must not|should not|do not|don't|avoid|prevent)\b.{0,60}\b"
    r"(?:modify|edit|change|update|write|add|overwrite|delete|remove|disable|skip|bypass)\b",
    re.IGNORECASE,
)


def _is_path_like_token(token: str) -> bool:
    """Heuristic: slash-heavy tokens without padding/operators are usually paths, not payloads."""
    return "/" in token and "+" not in token and "=" not in token


def _shannon_entropy(token: str) -> float:
    if not token:
        return 0.0
    counts = {c: token.count(c) for c in set(token)}
    total = len(token)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def _base64_findings(skill_path: Path, files: list[tuple[Path, str]]) -> list[dict]:
    findings = []
    seen = set()
    for fpath, content in files:
        rel = str(fpath.relative_to(skill_path))
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            context_lines = lines[max(0, i - 2):min(len(lines), i + 1)]
            context = " ".join(context_lines).lower()
            has_decode_hint = any(h in context for h in BASE64_DECODE_HINTS)
            pattern = BASE64_SHORT_RE if has_decode_hint else BASE64_BLOB_RE
            for match in pattern.finditer(line):
                blob = match.group(0)
                key = (rel, i, blob[:32])
                if key in seen:
                    continue
                seen.add(key)

                if _is_path_like_token(blob) and not has_decode_hint:
                    continue
                # In decode-heavy prose/code, short alphabetic identifiers are common noise.
                if has_decode_hint and re.fullmatch(r"[A-Za-z]+", blob) and len(blob) < 24:
                    continue

                entropy = _shannon_entropy(blob)
                if has_decode_hint:
                    sev = "HIGH"
                    mode = "decode-context"
                elif ("+" in blob or "=" in blob) and len(blob) >= 80 and entropy >= 2.4:
                    sev = "HIGH"
                    mode = "high-entropy"
                elif len(blob) >= 140 and entropy >= 3.0:
                    sev = "LOW"
                    mode = "ambiguous"
                else:
                    continue

                findings.append(
                    {
                        "id": "INSTR-010",
                        "severity": sev,
                        "layer": 2,
                        "category": "encoding-trick",
                        "message": f"base64-blob ({mode}): {line.strip()[:120]}",
                        "file": rel,
                        "line": i,
                        "remediation": "Review and remove or justify this encoding-trick pattern.",
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
    findings.extend(_base64_findings(skill_path, files))
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
        file_findings = _scan_patterns(
            stripped,
            OVERREACH_PATTERNS,
            "INSTR-030",
            "HIGH",
            "overreach",
            rel,
        )
        lines = stripped.split("\n")
        for f in file_findings:
            ln = f.get("line")
            if not ln or ln < 1 or ln > len(lines):
                findings.append(f)
                continue

            line_text = lines[ln - 1]
            if PROTECTIVE_GUIDANCE_RE.search(line_text):
                f["severity"] = "LOW"
                f["category"] = "overreach-protective-guidance"
                f["message"] = f"protective-guidance mention: {line_text.strip()[:120]}"
                f["remediation"] = (
                    "Informational guidance only. Ensure wording remains prohibitive and not actionable bypass instructions."
                )
            findings.append(f)
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
