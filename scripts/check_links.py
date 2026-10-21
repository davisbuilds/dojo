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
single-line setext headings (an ATX heading above `---` is not setext text),
and explicit `id`/`name` attributes, in any case, on HTML tags outside inline
code (entity-decoded once, so `id="a&amp;b"` answers `#a%26b`). A heading's
slug is its rendered text lowercased, with characters other than letters,
digits, `_`, `-` and space removed and each space turned into `-`; inline
code, emphasis, link text, backslash escapes and HTML entities are reduced to
their text first. Backslash-escaped punctuation is literal: it forms no markup
and starts no entity (`\\&amp;` slugs as `amp`). Repeated slugs get `-1`,
`-2`, ... skipping any slug already taken. Fragments are percent-decoded and
compared case-insensitively; GitHub's `#user-content-` id prefix is accepted. Headings
and IDs inside fenced code blocks, closed HTML comments and YAML frontmatter are
not anchors, nor are IDs in indented code (four spaces past the list margin
and any block-quote markers, after a blank line, heading -- setext underline
included -- or thematic break, not continuing a paragraph). Links
inside fences, inline code spans or closed HTML comments are not checked
(`skills/<name>/` paths in inline code and comments still are), nor is link
syntax after an escaped `\\[`. A fence opener or closer may be
indented at most three spaces past the margin, or past its list item's content
column; anything deeper is indented code, which is scanned like prose. Fence
markers inside an HTML comment block do not open fences. Fences opened on a
list marker line (`- ```lang`) or inside block quotes are masked too; quoted
prose is checked like any other text.

Deliberately unsupported, so never reported:
- fragments on non-Markdown targets (`run.py#L10`) and directories: only the
  file's existence is checked;
- any target file with a heading containing raw HTML (processing
  instructions included; escaped `\\<kbd>` is text), an image, a
  `{#custom-id}` attribute, an `:emoji:` shortcode, a private-use character
  in any plane (literal or from an entity), a reference-style link
  (`[x][ref]` or `[x][]`, defined or not), escaped link syntax (`\\[x](y)`) or a link it cannot parse;
  or with setext heading text spanning several lines or following a line it
  may continue (anything but a blank line, ATX heading, thematic break or
  fence), because its anchors depend on the renderer. Headings in list items,
  ATX or setext, are read only when indented at most three spaces in total
  (`- item` then `  ## Title`); a target with a heading deeper in a list item
  (`10. Item` then `    ## Title`), on or under the marker line (`- ## Title`,
  `- Title` then `  ---`) or in a block quote (`> ## Title`, `> Title` then
  `> ---`) is skipped too. Heading
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
import unicodedata
from html.parser import HTMLParser
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
QUOTE_MARKER = re.compile(r" {0,3}>[ \t]?")
# A heading inside a block quote, possibly nested, is rendered but not parsed.
QUOTED_HEADING = re.compile(r"^(?: {0,3}>[ \t]?)+ {0,3}#{1,6}(?:[ \t]|$)")
FRONTMATTER = re.compile(r"---[ \t]*\r?\n.*?^---[ \t]*$", re.M | re.S)
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
THEMATIC_BREAK = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
# Lines that cannot be setext heading text: list items, quotes, headings, HTML.
NOT_SETEXT_TEXT = re.compile(r"^(?: {4}|\s*(?:[-*+>#<]|\d+[.)])(?:\s|$))")
# A start tag, allowing `>` inside quoted attribute values.
HTML_TAG = re.compile(r"<[A-Za-z](?:[^<>\"']|\"[^\"]*\"|'[^']*')*>")
# A code span closes on a backtick run of exactly the opener's length and may
# wrap lines but not cross a blank line; an unmatched opener is literal text.
CODE_SPAN_BODY = r"(?P<ticks>`+)(?!`)(?P<code>(?:(?!\n[ \t]*\n)[\s\S])+?)(?<!`)(?P=ticks)(?!`)"
CODE_SPAN = re.compile(r"(?<![`\\])" + CODE_SPAN_BODY)
# In heading text, backslash escapes and code spans are read together left to
# right, so `\`` cannot open a span, `\\` before one leaves it open, and a
# backslash inside one is literal.
HEADING_LITERAL = re.compile(r"\\(?P<esc>[!-/:-@\[-`{-~])|(?<!`)" + CODE_SPAN_BODY)
# Link destinations may hold one level of balanced parentheses; deeper nesting
# or an escaped `\[` leaves a `](` behind and marks the heading unsupported.
INLINE_LINK = re.compile(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
UNDERSCORE_EMPHASIS = re.compile(r"(?<!\w)(_{1,3})(?=\S)(.+?)(?<=\S)\1(?!\w)")
# Raw HTML (tags, comments, declarations, processing instructions), images and
# reference-style links (`[x][ref]`, whose text depends on whether `ref` is
# defined) make a heading's anchor renderer-dependent. Escaped punctuation
# cannot form them, so this runs after escapes are set aside.
HEADING_MARKUP = re.compile(r"<[A-Za-z/!?]|!\[|\]\[")
# Custom-id attributes and emoji shortcodes are read from the rendered text, so
# one spelled with escapes or entities is still caught.
HEADING_TEXT_MARKUP = re.compile(r"\{#|:[a-z0-9_+-]+:")
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


def strip_fences(text: str, margins: list[int] | None = None) -> str:
    """Blank out fenced code blocks, keeping line structure.

    They routinely illustrate hypothetical skills with placeholder filenames --
    skill-creator shows a PDF skill linking to FORMS.md and REFERENCE.md that
    were never meant to exist -- so checking inside them produces noise only.
    Shell comments and Markdown examples inside them are not headings either.
    Fence openers and closers use backticks or tildes and may be indented up
    to three spaces past their margin: the content column of the enclosing list
    item, or zero at top level. Four spaces more is indented code. A fence
    closes on a line of the same character at least as long, when a non-blank
    line outdents past its margin (ending the list item), or at end of file.
    A line starting an HTML comment block (`<!--`) keeps fence detection off
    through the line holding `-->`. Fences inside block quotes (`> ```) are
    read after the quote markers and end with the line that has fewer of them.
    List items are tracked by indentation only: a non-blank line indented less
    than an item's content ends it, so lazy continuation lines and lists inside
    block quotes are not modelled.

    If `margins` is given, each output line's list margin is appended to it.
    """
    out: list[str] = []
    fence = ""
    fence_margin = fence_depth = 0
    in_comment = False
    items: list[int] = []  # content columns of the enclosing list items
    for line in text.splitlines():
        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        if fence and expanded.strip() and indent < fence_margin:
            fence = ""  # outdent ended the list item, and the fence with it
        if fence:
            depth, body = _unquote(expanded[fence_margin:], fence_depth)
            if depth < fence_depth:
                fence = ""  # the block quote holding the fence ended
            else:
                m = FENCE_OPEN.match(body)
                if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                        and not body.strip().lstrip(fence[0]) and _indent(body) <= 3:
                    fence = ""
                out.append("")
                if margins is not None:
                    margins.append(items[-1] if items else 0)
                continue
        if expanded.strip():
            while items and indent < items[-1]:
                items.pop()
        margin = items[-1] if items else 0
        depth, body = _unquote(expanded[margin:], None)
        m = FENCE_OPEN.match(body)
        if in_comment or (_indent(body) <= 3 and body.lstrip().startswith("<!--")):
            in_comment = "-->" not in line
            out.append(line)
        elif m and _indent(body) <= 3:
            fence, fence_margin, fence_depth = m.group(1), margin, depth
            out.append("")
        else:
            item = LIST_ITEM.match(expanded)
            if item:
                gap = len(item.group(3))
                items.append(item.start(3) + (gap if 1 <= gap <= 4 else 1))
                m = FENCE_OPEN.match(expanded[items[-1]:])
                if m and _indent(expanded[items[-1]:]) <= 3:  # `- ```lang` opens a fence
                    fence, fence_margin, fence_depth = m.group(1), items[-1], 0
                    line = ""
            out.append(line)
        if margins is not None:
            margins.append(items[-1] if items else 0)
    return "\n".join(out)


def _indent(text: str) -> int:
    return len(text) - len(text.lstrip(" "))


def _unquote(text: str, depth: int | None) -> tuple[int, str]:
    """Strip up to `depth` block-quote markers (all if None); return how many."""
    n = 0
    while depth is None or n < depth:
        m = QUOTE_MARKER.match(text)
        if not m:
            break
        text, n = text[m.end() :], n + 1
    return n, text


class _AnchorAttrs(HTMLParser):
    """Collect `id`/`name` values from start tags. HTMLParser lowercases
    attribute names and entity-decodes values, so they are used as given."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.found.update(v.lower() for k, v in attrs if k in ("id", "name") and v)


def html_anchors(text: str) -> set[str]:
    parser = _AnchorAttrs()
    for tag in HTML_TAG.findall(text):
        parser.reset()
        parser.feed(tag)
    return parser.found


def heading_text(raw: str) -> str | None:
    """Reduce heading Markdown to its rendered text, or None if unsupported.

    Backslash escapes and code spans are swapped for lone-surrogate
    placeholders first, so their text stays literal -- it neither forms markup
    nor starts an entity -- while links and emphasis around them are still
    reduced. Escapes are restored before the rendered-text checks, code spans
    after them. Strict UTF-8 text cannot hold lone surrogates and html.unescape
    maps surrogate references to U+FFFD, so no input can forge a placeholder.
    """
    if re.search(r"[\ud800-\udfff]", raw):
        return None
    held: list[str] = []
    escapes: set[int] = set()

    def hold(m: re.Match[str]) -> str:
        if m.group("esc"):
            escapes.add(len(held))
            held.append(m.group("esc"))
        else:
            code = m.group("code")
            held.append(code[1:-1] if code.startswith(" ") and code.endswith(" ") and code.strip() else code)
        return chr(0xD800 + len(held) - 1)  # past 2048 this lands in private use: unsupported

    def restore(text: str, only: set[int] | None = None) -> str:
        def put(m: re.Match[str]) -> str:
            i = ord(m.group()) - 0xD800
            return held[i] if only is None or i in only else m.group()
        return re.sub(r"[\ud800-\udfff]", put, text)

    text = HEADING_LITERAL.sub(hold, raw)
    if HEADING_MARKUP.search(text):
        return None
    text = INLINE_LINK.sub(r"\1", text)
    if "](" in text:
        return None  # a link this checker could not parse, or escaped link syntax
    while (reduced := UNDERSCORE_EMPHASIS.sub(r"\2", text)) != text:
        text = reduced  # nested emphasis: `_outer __inner__ end_`
    text = restore(html.unescape(text), escapes)
    if HEADING_TEXT_MARKUP.search(text):
        return None
    text = restore(text)
    # Private-use glyphs (any plane), literal or from entities, slug differently per renderer.
    return None if any(unicodedata.category(ch) == "Co" for ch in text) else text


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
    margins: list[int] = []
    text = CODE_OR_COMMENT.sub(
        lambda m: m.group() if m.group(1) else "\n" * m.group().count("\n"), strip_fences(text, margins))
    lines = text.splitlines()
    seen: dict[str, int] = {}
    code = _indented_code_lines(lines, margins)
    found = html_anchors(CODE_SPAN.sub("", "\n".join("" if i in code else ln for i, ln in enumerate(lines))))
    for i, line in enumerate(lines):
        m = ATX_HEADING.match(line)
        body = line.expandtabs(4)[margins[i]:]
        depth, inner = _unquote(body, None)
        if not m and (margins[i] and ATX_HEADING.match(body) or QUOTED_HEADING.match(body)):
            return None  # heading in a block quote, past column 3 of a list item, or on its marker
        if m:
            raw = (m.group(1) or "").strip()
        elif i and SETEXT_UNDERLINE.match(line) and _setext_text(lines[i - 1]):
            if i > 1 and lines[i - 2].strip() and not _ends_block(lines[i - 2]):
                return None  # multi-line, or possibly continued, setext heading text
            raw = lines[i - 1].strip()
        elif i and (margins[i] or depth) and SETEXT_UNDERLINE.match(inner) \
                and _setext_text(_unquote(lines[i - 1].expandtabs(4)[margins[i - 1]:], None)[1]):
            return None  # setext heading in a list item or block quote
        else:
            continue
        rendered = heading_text(raw)
        if rendered is None:
            return None
        found.add(slugify(rendered, seen))
    return found


def _ends_block(line: str) -> bool:
    """Whether a line is a whole block that a following line cannot continue."""
    return bool(ATX_HEADING.match(line) or THEMATIC_BREAK.match(line))


def _indented_code_lines(lines: list[str], margins: list[int]) -> set[int]:
    """Indices of indented-code lines: four or more spaces past the list margin
    and any block-quote markers, where no paragraph is open to continue.

    A paragraph ends at a blank line (a bare `>` inside a quote), a heading or
    thematic break, or the setext underline below it in the same container. A
    deeper quote starts afresh; a shallower line continues it lazily.
    """
    code: set[int] = set()
    para: tuple[int, int] | None = None  # quote depth and list margin of the open paragraph
    for i, line in enumerate(lines):
        depth, body = _unquote(line.expandtabs(4)[margins[i]:], None)
        if not body.strip():
            para = None  # blank lines may sit inside an indented code block
            continue
        fresh = para is None or depth > para[0]
        if fresh and _indent(body) >= 4:
            code.add(i)
            para = None
        elif _ends_block(body) or (depth, margins[i]) == para and SETEXT_UNDERLINE.match(body):
            para = None
        elif fresh:
            para = (depth, margins[i])
    return code


def _setext_text(line: str) -> bool:
    """Whether a line can be the text of a setext heading underlined below it."""
    return bool(line.strip()) and not NOT_SETEXT_TEXT.match(line) and not ATX_HEADING.match(line)


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
