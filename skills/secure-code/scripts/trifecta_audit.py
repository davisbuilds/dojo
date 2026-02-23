#!/usr/bin/env python3
"""Detect the lethal trifecta: co-occurrence of private data access,
untrusted input processing, and external communication in a single file."""

import json
import re
import sys
from pathlib import Path

# Patterns for each leg (language-agnostic regex heuristics)
LEG_PATTERNS = {
    "private_data": {
        "description": "Private/sensitive data access",
        "patterns": [
            # Database queries
            r"\b(execute|query|cursor|SELECT|INSERT|UPDATE|DELETE)\b.*\b(FROM|INTO|SET)\b",
            r"\.(execute|executemany|fetchone|fetchall|rawQuery|query)\s*\(",
            r"\b(prisma|knex|sequelize|mongoose|typeorm)\b.*\.(find|create|update|delete|query)",
            # Credential/secret access
            r"(password|passwd|secret|token|api_key|apikey|private_key|credential)",
            # Environment secrets
            r"(os\.environ|process\.env|getenv)\s*[\[\(].*?(secret|key|token|password|credential)",
            # PII fields
            r"\b(ssn|social_security|date_of_birth|credit_card|bank_account)\b",
        ],
    },
    "untrusted_input": {
        "description": "Untrusted input processing",
        "patterns": [
            # HTTP request data
            r"(request\.(body|params|query|form|args|files|headers|cookies|json))",
            r"(req\.(body|params|query|files|headers|cookies))",
            r"(flask\.request|django\.http|fastapi\.(Body|Query|Path|Form))",
            # Deserialization
            r"\b(json\.loads|pickle\.loads|yaml\.load|yaml\.unsafe_load|deserialize|unmarshal)\b",
            # File uploads
            r"(upload|multipart|FormData|UploadFile|FileField)",
            # Webhook payloads
            r"(webhook|payload|event_data|callback_body)",
            # User-supplied path/URL
            r"(user_url|user_path|redirect_url|return_url|next_url)",
        ],
    },
    "external_comms": {
        "description": "External communication",
        "patterns": [
            # HTTP client calls
            r"\b(requests\.(get|post|put|patch|delete)|fetch|axios|httpx|urllib|http\.client)\b",
            r"\b(HttpClient|WebClient|RestTemplate|OkHttp)\b",
            # Email
            r"\b(send_mail|sendmail|smtp|send_email|EmailMessage|MIMEText)\b",
            # Subprocess with network potential
            r"\b(subprocess\.(run|call|Popen)|child_process\.exec|execSync)\b.*?(curl|wget|nc|ssh)",
            # Queue/message publishing
            r"\b(publish|send_message|enqueue|produce)\s*\(.*?(queue|topic|channel|exchange)",
            # Webhook dispatch
            r"\b(webhook|callback)\b.*?\b(send|post|dispatch|trigger)\b",
            r"\b(send|post|dispatch|trigger)\b.*?\b(webhook|callback)\b",
        ],
    },
}


def scan_file(filepath: str) -> dict:
    """Scan a single file for trifecta leg indicators."""
    try:
        content = Path(filepath).read_text(errors="replace")
    except (OSError, IOError) as e:
        return {"file": filepath, "error": str(e)}

    lines = content.split("\n")
    result = {"file": filepath, "legs": {}, "trifecta_detected": False}

    for leg_name, leg_info in LEG_PATTERNS.items():
        matches = []
        for pattern in leg_info["patterns"]:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                continue
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    matches.append({"line": i, "content": line.strip()[:120], "pattern": pattern})

        if matches:
            # Deduplicate by line number
            seen_lines = set()
            unique = []
            for m in matches:
                if m["line"] not in seen_lines:
                    seen_lines.add(m["line"])
                    unique.append(m)
            result["legs"][leg_name] = {
                "description": leg_info["description"],
                "match_count": len(unique),
                "sample_matches": unique[:5],
            }

    detected_legs = list(result["legs"].keys())
    result["trifecta_detected"] = len(detected_legs) == 3
    result["detected_legs"] = detected_legs
    result["leg_count"] = len(detected_legs)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: trifecta_audit.py <file1> [file2] ...", file=sys.stderr)
        print("  Scans files for lethal trifecta co-occurrence.", file=sys.stderr)
        sys.exit(1)

    files = sys.argv[1:]
    results = []
    trifecta_files = []

    for f in files:
        path = Path(f)
        if path.is_dir():
            # Scan common source files in directory
            for ext in ("*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.go", "*.java", "*.rb"):
                for child in path.rglob(ext):
                    r = scan_file(str(child))
                    results.append(r)
                    if r.get("trifecta_detected"):
                        trifecta_files.append(r["file"])
        elif path.is_file():
            r = scan_file(str(path))
            results.append(r)
            if r.get("trifecta_detected"):
                trifecta_files.append(r["file"])

    output = {
        "total_files_scanned": len(results),
        "trifecta_detected_count": len(trifecta_files),
        "trifecta_files": trifecta_files,
        "results": results,
    }

    # TODO: --broader flag to trace across imports within a directory

    json.dump(output, sys.stdout, indent=2)
    print()  # trailing newline

    if trifecta_files:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
