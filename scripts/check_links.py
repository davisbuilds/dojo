#!/usr/bin/env python3
"""Fail on references that point at things which no longer exist.

Deleting a skill or a reference file is easy; finding everything that pointed at
it is not. Two cleanups on 2026-07-31 each left stale pointers behind — a
retirement left sibling sections naming deleted skills across sixteen files, and
a reference cut left three separate indexes listing files that were gone. Both
were caught by hand. This makes it mechanical.

Four checks, all conservative — they only fire on references with an
unambiguous target:

1. Relative markdown links (`[text](./references/foo.md)`) resolve on disk.
2. A heading fragment on a link to a local `.md` file (`foo.md#usage`, or
   `#usage` within the same file) names an anchor that file defines.
3. `skills/<name>/` paths name a skill that exists.
4. Skill names in a `## Sibling skills` section name a skill that exists.

Supported anchors approximate GitHub's heading ids (github-slugger); this is
not a full Markdown renderer. Anchors come from ATX headings (`## Title`),
single-line setext headings, and explicit `id=`/`name=` attributes on HTML
tags outside inline code. A heading's slug is its rendered text lowercased, with characters other
than letters, digits, `_`, `-` and space removed and each space turned into
`-`; inline code, emphasis, link text, backslash escapes and HTML entities are
reduced to their text first. Repeated slugs get `-1`, `-2`, ... skipping any
slug already taken. Fragments are percent-decoded and compared
case-insensitively; GitHub's `#user-content-` id prefix is accepted. Headings
and IDs inside fenced code blocks, closed HTML comments and YAML frontmatter are
not anchors, and links inside fences are not checked.

Deliberately unsupported, so never reported:
- fragments on non-Markdown targets (`run.py#L10`) and directories: only the
  file's existence is checked;
- any target file with a heading containing raw HTML, an image, a
  `{#custom-id}` attribute or an `:emoji:` shortcode, or a setext heading
  spanning several lines, because its anchors depend on the renderer;
- reference-style links (`[x][ref]`), links with titles, and HTML `href`s,
  which are not scanned at all.

Usage:  python3 scripts/check_links.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"

# Docs that describe current state. Dated artifacts (plans, specs, designs,
# research, replay results) are deliberately excluded: they record what was true
# when written, and rewriting them to match today would destroy the record.
LIVING_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "system",
    REPO_ROOT / "docs" / "project",
]

MD_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:)([^)\s]+)\)")
SKILL_PATH = re.compile(r"(?<!/)\bskills/([a-z0-9][a-z0-9-]*)/")
# Sibling entries are list heads: "- `name` — description". Matching only that
# position keeps model names and inline mentions out of the check.
SIBLING_ENTRY = re.compile(r"^\s*[-*]\s+`([a-z0-9][a-z0-9-]{2,})`", re.M)
SIBLING_HEADING = re.compile(r"^#{1,4}\s+Sibling skills\s*$", re.M)
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
FRONTMATTER = re.compile(r"---[ \t]*\r?\n.*?^---[ \t]*$", re.M | re.S)
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
# Lines that cannot be setext heading text: list items, quotes, headings, HTML.
NOT_SETEXT_TEXT = re.compile(r"^(?: {4}|\s*(?:[-*+>#<]|\d+[.)])(?:\s|$))")
HTML_ID = re.compile(r"<[A-Za-z][^>]*?\s(?:id|name)=[\"']?([^\"'\s>]+)")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
INLINE_LINK = re.compile(r"\[([^\]]*)\](?:\([^)]*\)|\[[^\]]*\])")
UNDERSCORE_EMPHASIS = re.compile(r"(?<![\w\\])(_{1,2})(?=\S)(.+?)(?<=[^\s\\])\1(?!\w)")
BACKSLASH_ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
# Raw HTML, images, custom-id attributes and emoji shortcodes make a heading's
# anchor renderer-dependent.
UNSUPPORTED_HEADING_MARKUP = re.compile(r"<[A-Za-z/!]|!\[|\{#|:[a-z0-9_+-]+:")
# A closed HTML comment, unless it sits inside an inline code span.
CODE_OR_COMMENT = re.compile(r"(`+)[^\n]+?\1|<!--(?s:.*?)-->")

# Documentation placeholders that stand in for "whatever skill you are working
# on". Kept explicit and small rather than loosening the path check, which would
# stop catching the real thing.
PLACEHOLDERS = {"my-skill", "your-skill", "example-skill", "skill-name", "some-skill"}

# docs/archive/ is gitignored: completed plans and superseded analyses are kept
# locally, not published. Living docs legitimately cite them for the local
# reader, so those links resolve on the author's machine and nowhere else.
# Checking them would fail every CI run for a reason that is not a defect.
LOCAL_ONLY_PREFIXES = ("docs/archive/",)


def strip_fences(text: str) -> str:
    """Blank out fenced code blocks, keeping line structure.

    They routinely illustrate hypothetical skills with placeholder filenames --
    skill-creator shows a PDF skill linking to FORMS.md and REFERENCE.md that
    were never meant to exist -- so checking inside them produces noise only.
    Shell comments and Markdown examples inside them are not headings either.
    Fences may be indented (list items) and use backticks or tildes; a fence
    closes on a line of the same character at least as long, or at end of file.
    """
    out: list[str] = []
    fence = ""
    for line in text.splitlines():
        m = FENCE_OPEN.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip().lstrip(fence[0]):
                fence = ""
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def heading_text(raw: str) -> str | None:
    """Reduce heading Markdown to its rendered text, or None if unsupported."""
    if UNSUPPORTED_HEADING_MARKUP.search(CODE_SPAN.sub("", raw)):
        return None
    parts: list[str] = []
    pos = 0
    for m in CODE_SPAN.finditer(raw):
        parts.append(_inline_text(raw[pos : m.start()]))
        code = m.group(2)
        parts.append(code[1:-1] if code.startswith(" ") and code.endswith(" ") and code.strip() else code)
        pos = m.end()
    parts.append(_inline_text(raw[pos:]))
    return "".join(parts)


def _inline_text(text: str) -> str:
    text = INLINE_LINK.sub(r"\1", text)
    text = UNDERSCORE_EMPHASIS.sub(r"\2", text)
    return html.unescape(BACKSLASH_ESCAPE.sub(r"\1", text))


def slugify(text: str, seen: dict[str, int]) -> str:
    """github-slugger: strip punctuation, dash spaces, number repeats."""
    base = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
    slug = base
    while slug in seen:
        seen[base] += 1
        slug = f"{base}-{seen[base]}"
    seen[slug] = 0
    return slug


def anchors(text: str) -> set[str] | None:
    """Lowercased anchors a Markdown document defines, or None if any heading
    uses markup whose anchor this checker cannot predict."""
    m = FRONTMATTER.match(text)
    if m:
        text = text[m.end() :]
    text = CODE_OR_COMMENT.sub(
        lambda m: m.group() if m.group(1) else "\n" * m.group().count("\n"), strip_fences(text))
    lines = text.splitlines()
    seen: dict[str, int] = {}
    found = {a.lower() for a in HTML_ID.findall(CODE_SPAN.sub("", text))}
    for i, line in enumerate(lines):
        m = ATX_HEADING.match(line)
        if m:
            raw = (m.group(1) or "").strip()
        elif i and SETEXT_UNDERLINE.match(line) and lines[i - 1].strip() \
                and not NOT_SETEXT_TEXT.match(lines[i - 1]):
            if i > 1 and lines[i - 2].strip():
                return None  # multi-line setext heading text
            raw = lines[i - 1].strip()
        else:
            continue
        rendered = heading_text(raw)
        if rendered is None:
            return None
        found.add(slugify(rendered, seen))
    return found


def known_skills(skills_root: Path) -> set[str]:
    return {p.parent.name for p in skills_root.glob("*/SKILL.md")}


def markdown_files(skills_root: Path, living_docs: list[Path]) -> list[Path]:
    files: list[Path] = sorted(skills_root.glob("**/*.md"))
    # A skill's own evals/replay-results-*.md is a dated record, like the docs above.
    files = [f for f in files if not f.name.startswith("replay-results-")]
    for target in living_docs:
        if target.is_dir():
            files.extend(sorted(target.glob("**/*.md")))
        elif target.is_file():
            files.append(target)
    return files


def sibling_section(text: str) -> str:
    """Return the text of the Sibling skills section, or '' if absent."""
    m = SIBLING_HEADING.search(text)
    if not m:
        return ""
    rest = text[m.end() :]
    nxt = re.search(r"^#{1,4}\s+\S", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def check(skills_root: Path = SKILLS_ROOT, living_docs: list[Path] | None = None,
          files: list[Path] | None = None, repo_root: Path | None = None) -> list[str]:
    repo_root = REPO_ROOT if repo_root is None else repo_root
    living = LIVING_DOCS if living_docs is None else living_docs
    skills = known_skills(skills_root)
    problems: list[str] = []
    anchor_cache: dict[Path, set[str] | None] = {}

    def anchors_of(target: Path) -> set[str] | None:
        if target not in anchor_cache:
            try:
                anchor_cache[target] = anchors(target.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                anchor_cache[target] = None
        return anchor_cache[target]

    for path in markdown_files(skills_root, living) if files is None else files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        # assets/ holds templates whose links are placeholders by design.
        if "assets" in path.parts:
            continue
        text = strip_fences(text)

        for link in MD_LINK.findall(text):
            target_part, _, fragment = link.partition("#")
            target = (path.parent / target_part).resolve() if target_part else path.resolve()
            try:
                as_rel = target.relative_to(repo_root).as_posix()
            except ValueError:
                as_rel = ""
            if as_rel.startswith(LOCAL_ONLY_PREFIXES):
                continue
            if not target.exists():
                problems.append(f"{rel}: broken link -> {link}")
            elif fragment and target.suffix.lower() == ".md" and target.is_file():
                found = anchors_of(target)
                anchor = unquote(fragment).lower()
                if found is not None and anchor not in found \
                        and anchor.removeprefix("user-content-") not in found:
                    problems.append(f"{rel}: missing heading anchor -> {link}")

        for name in set(SKILL_PATH.findall(text)):
            if name not in skills and name not in PLACEHOLDERS:
                problems.append(f"{rel}: references skills/{name}/ which does not exist")

        for name in set(SIBLING_ENTRY.findall(sibling_section(text))):
            if name not in skills:
                problems.append(f"{rel}: sibling section names `{name}`, which is not a skill")

    return sorted(set(problems))


def main() -> int:
    problems = check()
    if problems:
        print(f"Link check failed ({len(problems)} problems):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"Link check passed ({len(known_skills(SKILLS_ROOT))} skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
