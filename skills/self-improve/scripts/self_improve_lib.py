from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STORE_DIRNAME = ".self-improve"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def slugify(value: str, max_length: int = 48) -> str:
    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    if not cleaned:
        cleaned = "item"
    return cleaned[:max_length].rstrip("-") or "item"


def resolve_store_root(path_str: str) -> Path:
    base = Path(path_str).expanduser().resolve()
    if base.name == STORE_DIRNAME:
        return base
    return base / STORE_DIRNAME


def ensure_store(path_str: str) -> dict[str, Path]:
    root = resolve_store_root(path_str)
    paths = {
        "root": root,
        "inbox": root / "inbox",
        "summaries": root / "summaries",
        "proposals": root / "proposals",
        "candidates": root / "candidates",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_template(path: Path, replacements: dict[str, str]) -> str:
    text = read_template(path)
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def asset_path(name: str) -> Path:
    return script_dir().parent / "assets" / name


def list_records(store_root: Path) -> list[dict[str, Any]]:
    inbox = store_root / "inbox"
    records: list[dict[str, Any]] = []
    for path in sorted(inbox.glob("*.json")):
        record = read_json(path)
        record["_path"] = str(path)
        records.append(record)
    records.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return records


def latest_markdown(dir_path: Path) -> Path | None:
    latest = dir_path / "latest.md"
    if latest.exists():
        return latest
    candidates = sorted(dir_path.glob("*.md"))
    return candidates[-1] if candidates else None


def copy_latest(path: Path, latest_path: Path) -> None:
    latest_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
