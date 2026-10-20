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
tags outside inline code. A heading's slug is its rendered text lowercased,
with characters other than letters, digits, `_`, `-` and space removed and each
space turned into `-`; inline code, emphasis, link text, backslash escapes and HTML entities are
reduced to their text first. Repeated slugs get `-1`, `-2`, ... skipping any
slug already taken. Fragments are percent-decoded and compared
case-insensitively; GitHub's `#user-content-` id prefix is accepted. Headings
and IDs inside fenced code blocks, closed HTML comments and YAML frontmatter are
not anchors, and links inside fences, inline code spans or closed HTML comments
are not checked (`skills/<name>/` paths in inline code and comments still are),
nor is link syntax after an escaped `\\[`. A fence opener may be indented at most
three spaces past the margin, or past its list item's content column; anything
deeper is indented code, which is scanned like prose.

Deliberately unsupported, so never reported:
- fragments on non-Markdown targets (`run.py#L10`) and directories: only the
  file's existence is checked;
- any target file with a heading containing raw HTML, an image, a
  `{#custom-id}` attribute, an `:emoji:` shortcode, a private-use character
  (literal or from an entity), a reference-style link (`[x][ref]` or `[x][]`,
  defined or not), escaped link syntax (`\\[x](y)`), or a link it cannot parse,
  or a setext heading spanning several lines, because its anchors depend on
  the renderer. Heading
  link destinations may contain one level of balanced parentheses
  (`guide_(v2).md`); deeper nesting (`a_((b)).md`) is skipped;
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

# An odd run of backslashes before `[` escapes it; an even run escapes only
# itself and leaves a real link.
MD_LINK = re.compile(r"(?<!\\)(?:\\\\)*\[[^\]]*\]\((?!https?://|mailto:)([^)\s]+)\)")
SKILL_PATH = re.compile(r"(?<!/)\bskills/([a-z0-9][a-z0-9-]*)/")
# Sibling entries are list heads: "- `name` — description". Matching only that
# position keeps model names and inline mentions out of the check.
SIBLING_ENTRY = re.compile(r"^\s*[-*]\s+`([a-z0-9][a-z0-9-]{2,})`", re.M)
SIBLING_HEADING = re.compile(r"^#{1,4}\s+Sibling skills\s*$", re.M)
# A backtick fence's info string cannot contain backticks (```x``` is inline code).
FENCE_OPEN = re.compile(r"^\s*(`{3,}(?=[^`]*$)|~{3,})")
LIST_ITEM = re.compile(r"^( *)([-*+]|\d{1,9}[.)])( +|$)")
FRONTMATTER = re.compile(r"---[ \t]*\r?\n.*?^---[ \t]*$", re.M | re.S)
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
# Lines that cannot be setext heading text: list items, quotes, headings, HTML.
NOT_SETEXT_TEXT = re.compile(r"^(?: {4}|\s*(?:[-*+>#<]|\d+[.)])(?:\s|$))")
HTML_ID = re.compile(r"<[A-Za-z][^>]*?\s(?:id|name)=[\"']?([^\"'\s>]+)")
# A code span closes on a backtick run of exactly the opener's length and may
# wrap lines but not cross a blank line; an unmatched opener is literal text.
CODE_SPAN = re.compile(r"(?<![`\\])(`+)(?!`)((?:(?!\n[ \t]*\n)[\s\S])+?)(?<!`)\1(?!`)")
# Link destinations may hold one level of balanced parentheses; deeper nesting
# or an escaped `\[` leaves a `](` behind and marks the heading unsupported.
INLINE_LINK = re.compile(r"(?<!\\)((?:\\\\)*)\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
UNDERSCORE_EMPHASIS = re.compile(r"(?<![\w\\])(_{1,3})(?=\S)(.+?)(?<=[^\s\\])\1(?!\w)")
BACKSLASH_ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
# Raw HTML, images, custom-id attributes, emoji shortcodes and reference-style
# links (`[x][ref]`, whose text depends on whether `ref` is defined) make a
# heading's anchor renderer-dependent.
UNSUPPORTED_HEADING_MARKUP = re.compile(r"<[A-Za-z/!]|!\[|\{#|:[a-z0-9_+-]+:|\]\[")
# A closed HTML comment, unless it sits inside an inline code span.
CODE_OR_COMMENT = re.compile(CODE_SPAN.pattern + r"|<!--(?s:.*?)-->")

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
    Fences use backticks or tildes and may be indented up to three spaces past
    the content column of the list item they sit in (zero at top level); four
    spaces more is indented code, not a fence. A fence closes on a line of the
    same character at least as long, or at end of file. List items are tracked
    by indentation only: a non-blank line indented less than an item's content
    ends it, so lazy continuation lines and block quotes are not modelled.
    """
    out: list[str] = []
    fence = ""
    items: list[int] = []  # content columns of the enclosing list items
    for line in text.splitlines():
        m = FENCE_OPEN.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip().lstrip(fence[0]):
                fence = ""
            out.append("")
            continue
        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        if expanded.strip():
            while items and indent < items[-1]:
                items.pop()
        if m and indent - (items[-1] if items else 0) <= 3:
            fence = m.group(1)
            out.append("")
            continue
        item = LIST_ITEM.match(expanded)
        if item:
            gap = len(item.group(3))
            items.append(item.start(3) + (gap if 1 <= gap <= 4 else 1))
        out.append(line)
    return "\n".join(out)


def heading_text(raw: str) -> str | None:
    """Reduce heading Markdown to its rendered text, or None if unsupported.

    Code spans are swapped for lone-surrogate placeholders first, so their
    contents stay literal while links and emphasis around them are still
    reduced. Strict UTF-8 text cannot hold lone surrogates and html.unescape
    maps surrogate references to U+FFFD, so no input can forge a placeholder.
    """
    if re.search(r"[\ud800-\udfff]", raw):
        return None
    codes: list[str] = []

    def hold(m: re.Match[str]) -> str:
        code = m.group(2)
        codes.append(code[1:-1] if code.startswith(" ") and code.endswith(" ") and code.strip() else code)
        return chr(0xD800 + len(codes) - 1)  # past 2048 spans this lands in PUA: unsupported

    text = CODE_SPAN.sub(hold, raw)
    if UNSUPPORTED_HEADING_MARKUP.search(text):
        return None
    text = INLINE_LINK.sub(r"\1\2", text)
    if "](" in text:
        return None  # a link this checker could not parse, or escaped link syntax
    while (reduced := UNDERSCORE_EMPHASIS.sub(r"\2", text)) != text:
        text = reduced  # nested emphasis: `_outer __inner__ end_`
    text = html.unescape(BACKSLASH_ESCAPE.sub(r"\1", text))
    text = re.sub(r"[\ud800-\udfff]", lambda m: codes[ord(m.group()) - 0xD800], text)
    # Private-use glyphs, literal or from entities, slug differently per renderer.
    return None if re.search(r"[\ue000-\uf8ff]", text) else text


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
        # Link syntax inside a code span is an example and inside a comment is
        # not rendered; a space keeps the neighbours from joining into a link
        # that is not in the source.
        link_text = CODE_OR_COMMENT.sub(lambda m: re.sub(r"[^\n]+", " ", m.group()), text)

        for link in MD_LINK.findall(link_text):
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
