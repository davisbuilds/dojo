from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_links.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_links", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def make_skill(root: Path, name: str, body: str) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: x\nskill-type: workflow\nversion: 1.0.0\n---\n\n{body}",
        encoding="utf-8",
    )
    return d


def test_clean_catalog_has_no_problems(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "See [detail](./references/detail.md).\n\n## Sibling skills\n\n- `beta` — the other one.\n")
    (a / "references").mkdir()
    (a / "references" / "detail.md").write_text("x", encoding="utf-8")
    make_skill(root, "beta", "Nothing to see.\n")
    assert MODULE.check(root, []) == []


def test_broken_relative_link_is_reported(tmp_path: Path) -> None:
    """The reference-cut failure: an index still lists a deleted file."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "See [gone](./references/deleted.md).\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "broken link" in problems[0] and "deleted.md" in problems[0]


def test_sibling_pointing_at_retired_skill_is_reported(tmp_path: Path) -> None:
    """The retirement failure: a sibling section names a deleted skill."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- `gh-review-pr` — retired.\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "gh-review-pr" in problems[0]


def test_skills_path_reference_to_missing_skill_is_reported(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Run `python3 skills/removed-thing/scripts/go.py`.\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "removed-thing" in problems[0]


def test_sibling_section_ignores_non_skill_words(tmp_path: Path) -> None:
    """Conservative by design: a sibling section mentioning ordinary terms is fine."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- Use `git` and `main`; see `pull-request` flow.\n")
    problems = MODULE.check(root, [])
    # `git` and `main` have no hyphen so are skipped; `pull-request` does and is flagged.
    assert all("`git`" not in p and "`main`" not in p for p in problems)


def test_external_links_are_skipped(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "[docs](https://example.com/x.md) and [mail](mailto:a@example.com).\n")
    assert MODULE.check(root, []) == []


def test_real_repo_passes() -> None:
    """The live catalog must stay clean; this is the gate CI enforces."""
    assert MODULE.check() == []


def test_fenced_code_blocks_are_ignored(tmp_path: Path) -> None:
    """skill-creator illustrates a hypothetical PDF skill linking to files that
    were never meant to exist. Checking inside fences is pure noise."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Example:\n\n```markdown\nSee [FORMS.md](FORMS.md)\n```\n")
    assert MODULE.check(root, []) == []


def test_urls_containing_skills_path_are_ignored(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Fetched from https://github.com/openai/skills/tree/main/skills/.curated here.\n")
    assert MODULE.check(root, []) == []


def test_documentation_placeholders_are_ignored(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Run `python3 skills/my-skill/scripts/run.py` on your own skill.\n")
    assert MODULE.check(root, []) == []


def test_asset_templates_are_skipped(tmp_path: Path) -> None:
    """Templates carry placeholder paths by design."""
    root = tmp_path / "skills"
    d = make_skill(root, "alpha", "Nothing.\n")
    (d / "assets").mkdir()
    (d / "assets" / "template.md").write_text("See [related](../category/related-problem.md).\n", encoding="utf-8")
    assert MODULE.check(root, []) == []


def test_inline_sibling_mention_is_not_flagged(tmp_path: Path) -> None:
    """Only list heads are sibling entries; a model name mid-sentence is not."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "## Sibling skills\n\n- `beta` — use when the user asks for `gpt-image-2`.\n")
    make_skill(root, "beta", "x\n")
    assert MODULE.check(root, []) == []


def test_links_into_local_only_archive_are_skipped(tmp_path: Path, monkeypatch) -> None:
    """docs/archive/ is gitignored, so its contents exist locally and never in CI.

    Regression guard for the failure this gate shipped with: it passed on the
    author's machine and failed on a clean checkout, because two living docs
    cite an archived analysis that is deliberately unpublished.
    """
    repo = tmp_path
    (repo / "docs" / "project").mkdir(parents=True)
    (repo / "docs" / "project" / "ROADMAP.md").write_text(
        "Based on the [analysis](../archive/skill-analysis/old.md).\n", encoding="utf-8"
    )
    root = repo / "skills"
    make_skill(root, "alpha", "Nothing.\n")
    monkeypatch.setattr(MODULE, "REPO_ROOT", repo)
    assert MODULE.check(root, [repo / "docs" / "project"]) == []


def test_clean_checkout_matches_working_tree() -> None:
    """The gate must not depend on untracked files being present.

    Anything the checker resolves through a gitignored path is a false pass that
    turns into a CI failure, which is exactly how this shipped broken once.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files", "docs", "skills", "README.md"],
        cwd=MODULE.REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    for problem in MODULE.check():
        assert False, f"working tree is not clean for the gate: {problem}"
    # Every living doc the checker scans must itself be tracked.
    for path in MODULE.markdown_files(MODULE.SKILLS_ROOT, MODULE.LIVING_DOCS):
        rel = path.relative_to(MODULE.REPO_ROOT).as_posix()
        assert rel in tracked, f"{rel} is scanned by the gate but not tracked in git"


# --- Heading fragments -------------------------------------------------------
#
# Expected anchors below are written out by hand from GitHub's documented
# heading-id behavior, not derived from the checker's slug function.


def write_doc(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def fragment_problems(problems: list[str]) -> list[str]:
    return [p for p in problems if "missing heading anchor" in p]


def test_fragment_into_existing_heading_passes(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "See [setup](references/guide.md#install-and-run).\n")
    write_doc(a, "references/guide.md", "# Guide\n\n## Install and run\n\nSteps.\n")
    assert MODULE.check(root, []) == []


def test_fragment_into_renamed_heading_is_reported(tmp_path: Path) -> None:
    """The motivating failure: a reference heading is renamed, the file stays."""
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "See [setup](references/guide.md#install-and-run).\n")
    write_doc(a, "references/guide.md", "# Guide\n\n## Installation\n\nSteps.\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "missing heading anchor" in problems[0]
    assert "references/guide.md#install-and-run" in problems[0]


def test_same_file_fragments_are_checked(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "Jump to [usage](#usage) or [gone](#removed-section).\n\n## Usage\n\nx\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "#removed-section" in problems[0] and "missing heading anchor" in problems[0]


def test_duplicate_headings_get_numbered_anchors(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "[a](#example) [b](#example-1) [c](#example-2) [d](#example-3)\n\n"
        "## Example\n\nx\n\n### Example\n\ny\n\n## Example\n\nz\n",
    )
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#example-3" in problems[0]


def test_numbered_slug_collisions_follow_github_slugger(tmp_path: Path) -> None:
    """A literal heading can already own the suffixed slug a duplicate would take.

    github-slugger skips taken slugs: "a", "a", "a-1" -> a, a-1, a-1-1; and
    "b-1", "b", "b" -> b-1, b, b-2.
    """
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "[1](#a) [2](#a-1) [3](#a-1-1) [4](#b-1) [5](#b) [6](#b-2)\n\n"
        "## a\n\n## a\n\n## a-1\n\n## b-1\n\n## b\n\n## b\n",
    )
    assert MODULE.check(root, []) == []
    make_skill(root, "beta", "[x](#a-2)\n\n## a\n\n## a\n\n## a-1\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#a-2" in problems[0]


def test_inline_formatting_in_headings_is_slugged_like_rendered_text(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    headings = {
        "## `run_task` — **Fast** _mode_ & [Docs](other.md)": "run_task--fast-mode--docs",
        "## Claude Code harness (WebFetch/WebSearch) — as of 2026-07-12": "claude-code-harness-webfetchwebsearch--as-of-2026-07-12",
        "### 1.1 Defer `await` Until Needed": "11-defer-await-until-needed",
        "## snake_case_name stays": "snake_case_name-stays",
        "## Closing hashes ##": "closing-hashes",
        "## Escaped \\*stars\\* and ~~strike~~": "escaped-stars-and-strike",
        "## Unicode Café Ünïcode": "unicode-café-ünïcode",
    }
    body = "\n".join(f"[x](#{slug})" for slug in headings.values()) + "\n\n" + "\n\n".join(headings) + "\n"
    make_skill(root, "alpha", body)
    write_doc(root / "alpha", "other.md", "x\n")
    assert MODULE.check(root, []) == []
    # Positive control: the same document with one heading renamed must fail.
    make_skill(root, "alpha", body.replace("## snake_case_name stays", "## renamed"))
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#snake_case_name-stays" in problems[0]


def test_percent_encoded_and_mixed_case_fragments_match(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", "[x](#caf%C3%A9-menu) [y](#Usage-Notes)\n\n## Café menu\n\n## Usage notes\n")
    assert MODULE.check(root, []) == []


def test_headings_inside_fences_are_not_anchors(tmp_path: Path) -> None:
    """Shell comments and Markdown examples in fences are not document headings."""
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "[cmd](references/guide.md#install-deps) [ex](references/guide.md#example-title)\n")
    write_doc(
        a, "references/guide.md",
        "# Guide\n\n```bash\n# install deps\nnpm ci\n```\n\n"
        "1. Step\n\n   ~~~~markdown\n   ## Example title\n   ```\n   still fenced\n   ```\n   ~~~~\n",
    )
    problems = fragment_problems(MODULE.check(root, []))
    assert sorted(p.split("-> ")[1] for p in problems) == [
        "references/guide.md#example-title",
        "references/guide.md#install-deps",
    ]


def test_fragment_links_inside_fences_are_not_checked(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "Example:\n\n```markdown\nSee [usage](#usage) and [ref](REFERENCE.md#api)\n```\n\n"
        "  ~~~\n  [nested](#nowhere)\n  ~~~\n",
    )
    assert MODULE.check(root, []) == []


def test_frontmatter_is_not_a_setext_heading_but_setext_headings_are(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    # make_skill frontmatter ends "version: 1.0.0\n---"; that is not a heading.
    make_skill(root, "alpha", "[a](#overview) [b](#details) [c](#version-100)\n\nOverview\n========\n\nDetails\n-------\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#version-100" in problems[0]


def test_explicit_html_anchors_are_targets(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(root, "alpha", '[x](#custom-spot) [y](#named)\n\n<a id="custom-spot"></a>\n<a name="named"></a>\n')
    assert MODULE.check(root, []) == []


def test_fragment_exclusions_are_retained(tmp_path: Path, monkeypatch) -> None:
    """External URLs, archive links, and asset templates stay unchecked."""
    repo = tmp_path
    (repo / "docs" / "project").mkdir(parents=True)
    (repo / "docs" / "project" / "ROADMAP.md").write_text(
        "From the [analysis](../archive/old.md#gone) and "
        "[spec](https://example.com/spec.md#missing) or [mail](mailto:a@b.c#x).\n",
        encoding="utf-8",
    )
    root = repo / "skills"
    d = make_skill(root, "alpha", "Nothing.\n")
    write_doc(d, "assets/template.md", "See [section](#placeholder-section) and [other](../SKILL.md#nope).\n")
    monkeypatch.setattr(MODULE, "REPO_ROOT", repo)
    assert MODULE.check(root, [repo / "docs" / "project"]) == []


def test_fragments_into_non_markdown_targets_check_existence_only(tmp_path: Path) -> None:
    """Unsupported boundary: line anchors and other file types are not parsed."""
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "[code](scripts/run.py#L10) [dir](references/#top) [gone](scripts/missing.py#L1)\n")
    write_doc(a, "scripts/run.py", "print()\n")
    write_doc(a, "references/x.md", "x\n")
    problems = MODULE.check(root, [])
    assert len(problems) == 1
    assert "broken link" in problems[0] and "missing.py" in problems[0]


def test_targets_with_unsupported_heading_markup_are_not_reported(tmp_path: Path) -> None:
    """Unsupported boundary: raw HTML or images in a heading make its anchor
    renderer-dependent, so misses into that file are not reported at all."""
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "[x](references/html.md#anything) [y](references/img.md#whatever)\n")
    write_doc(a, "references/html.md", "## Press <kbd>Ctrl</kbd> twice\n")
    write_doc(a, "references/img.md", "## ![logo](logo.png) Brand\n")
    write_doc(a, "references/logo.png", "")
    assert MODULE.check(root, []) == []


def test_custom_id_and_emoji_headings_make_target_unsupported(tmp_path: Path) -> None:
    """`{#custom-id}` and `:emoji:` render differently across renderers, so the
    checker must neither validate a guessed slug nor report a miss."""
    root = tmp_path / "skills"
    a = make_skill(
        root, "alpha",
        "[a](references/custom.md#custom-id) [b](references/custom.md#title-custom-id) "
        "[c](references/custom.md#stale) [d](references/emoji.md#smile-hello) "
        "[e](references/emoji.md#stale)\n",
    )
    write_doc(a, "references/custom.md", "# Title {#custom-id}\n")
    write_doc(a, "references/emoji.md", "## :smile: Hello\n")
    assert MODULE.anchors("# Title {#custom-id}\n") is None
    assert MODULE.anchors("## :smile: Hello\n") is None
    assert MODULE.check(root, []) == []
    # Positive control: plain headings in the same files are checked again.
    write_doc(a, "references/custom.md", "# Title\n")
    write_doc(a, "references/emoji.md", "## Hello\n")
    problems = sorted(p.split("-> ")[1] for p in fragment_problems(MODULE.check(root, [])))
    assert problems == [
        "references/custom.md#custom-id",
        "references/custom.md#stale",
        "references/custom.md#title-custom-id",
        "references/emoji.md#smile-hello",
        "references/emoji.md#stale",
    ]


def test_user_content_prefixed_fragments_resolve_to_the_heading(tmp_path: Path) -> None:
    """GitHub renders heading ids as `user-content-<slug>`; both forms link."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", "[x](#user-content-usage) [y](#user-content-gone)\n\n## Usage\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#user-content-gone" in problems[0]


def test_html_ids_inside_inline_code_are_not_anchors(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "[x](#not-real) [y](#real) [z](#--flag-usage)\n\n"
        'Write `<a id="not-real"></a>` to add one.\n\n<a id="real"></a>\n\n## `--flag` usage\n',
    )
    assert MODULE.anchors('`<a id="not-real"></a>`\n') == set()
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#not-real" in problems[0]


def test_headings_inside_html_comments_are_not_anchors(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "[x](#ghost) [y](#after) [z](#kept)\n\n<!--\n# Ghost\n-->\n\n"
        "<!-- INCLUDE: rules/example -->\n## After\n\n## Kept <!-- note -->\n",
    )
    assert MODULE.anchors("<!--\n# Ghost\n-->\n") == set()
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#ghost" in problems[0]


def test_invalid_backtick_fence_openers_do_not_hide_later_content(tmp_path: Path) -> None:
    """A backtick fence's info string cannot contain backticks, so ```x``` and
    ``` a`b are inline text, not unclosed fences that swallow the file."""
    root = tmp_path / "skills"
    for name, opener in (("alpha", "```literal```"), ("beta", "``` info`tick")):
        make_skill(
            root, name,
            f"{opener}\n\n[gone](missing.md) [frag](#nowhere) [ok](#real)\n\n## Real\n\n"
            "```markdown\n[example](FORMS.md) [example](#example-only)\n```\n\n"
            "~~~ tilde`info is valid\n[tilde](TILDE.md)\n~~~\n",
        )
    problems = sorted(p.split("/skills/")[1] for p in MODULE.check(root, []))
    assert problems == [
        "alpha/SKILL.md: broken link -> missing.md",
        "alpha/SKILL.md: missing heading anchor -> #nowhere",
        "beta/SKILL.md: broken link -> missing.md",
        "beta/SKILL.md: missing heading anchor -> #nowhere",
    ]


def test_heading_links_with_balanced_parentheses(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    a = make_skill(
        root, "alpha",
        "[a](references/ref.md#api) [b](references/ref.md#cfg-file) [c](references/ref.md#guide)\n"
        "[d](references/deep.md#anything)\n",
    )
    write_doc(a, "references/ref.md", "## [API](https://example.test/guide_(v2).md)\n\n## [`cfg`](https://example.test/c) file\n")
    write_doc(a, "references/deep.md", "## [Deep](https://example.test/a_((b)).md)\n")
    assert MODULE.anchors("## [API](https://example.test/guide_(v2).md)\n") == {"api"}
    # Deeper nesting is outside the supported subset: skipped, not guessed.
    assert MODULE.anchors("## [Deep](https://example.test/a_((b)).md)\n") is None
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "references/ref.md#guide" in problems[0]


def test_combined_and_nested_underscore_emphasis(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "[a](#important) [b](#strong-and-em) [c](#outer-inner-end) "
        "[d](#snake_case_name-and-__dunder__) [e](#_important_)\n\n"
        "## ___Important___\n\n## __Strong__ and _em_\n\n## _outer __inner__ end_\n\n"
        "## snake_case_name and `__dunder__`\n",
    )
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#_important_" in problems[0]


def test_private_use_characters_in_headings_are_unsupported_not_a_crash(tmp_path: Path) -> None:
    """Code spans are held as placeholder characters while a heading is reduced;
    neither literal nor entity-produced private-use characters may be mistaken
    for one. Their slugging is renderer-dependent, so the file is skipped."""
    for heading in ("## Entity &#xE000;\n", "## `x` &#xE000;\n", "## Glyph  here\n", "## ``\n"):
        assert MODULE.anchors(heading) is None, heading
    # A surrogate reference unescapes to U+FFFD, never to a code placeholder.
    assert MODULE.heading_text("`x` &#xD800;") == "x �"
    # Controls: real code spans and ordinary entities are still reduced; code stays literal.
    assert MODULE.anchors("## `a_b` &amp; `c`\n") == {"a_b--c"}
    assert MODULE.anchors("## Fish &amp; Chips\n## Caf&eacute;\n") == {"fish--chips", "café"}
    assert MODULE.anchors("## `&amp;` op\n") == {"amp-op"}
    root = tmp_path / "skills"
    a = make_skill(root, "alpha", "[x](references/pua.md#stale) [y](#gone)\n\n## Fish &amp; Chips\n")
    write_doc(a, "references/pua.md", "## Entity &#xE000;\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "#gone" in problems[0]


def test_inline_code_link_examples_are_not_checked(tmp_path: Path) -> None:
    """Link syntax inside a code span is an example, not a link. Real links
    beside or after one, and skills/ paths in code, are still checked."""
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "Write `[example](#placeholder)` or ``[a `tick` b](missing-a.md)``, "
        "then [real](missing-real.md).\n\n"
        "`[x](gone.md)`[adjacent](#adjacent-gone)\n\n"
        "Multi `line\n[ex](multi.md) span` then [after](#after-gone).\n\n"
        "Unmatched `` opener [still](unmatched-gone.md) checked.\n\n"
        "Run `python3 skills/removed-thing/go.py`. [ok](#heading-cfg-code)\n\n"
        "## Heading [`cfg`](cfg.md) code\n",
    )
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> cfg.md",
        "broken link -> missing-real.md",
        "broken link -> unmatched-gone.md",
        "missing heading anchor -> #adjacent-gone",
        "missing heading anchor -> #after-gone",
        "references skills/removed-thing/ which does not exist",
    ]


def test_reference_style_links_in_headings_are_skipped(tmp_path: Path) -> None:
    """`[API][ref]` renders as a link only if `ref` is defined (slug `api`),
    otherwise literally (slug `apiref`). Definitions are not resolved, so such
    headings make the target unsupported rather than guessed."""
    for text in ("## [API][undefined]\n", "[api]: x.md\n\n## [API][api]\n", "## [API][]\n"):
        assert MODULE.anchors(text) is None, text
    assert MODULE.anchors("## API\n") == {"api"}
    root = tmp_path / "skills"
    a = make_skill(
        root, "alpha",
        "[a](references/ref.md#api) [b](references/ref.md#apiundefined) [c](references/ref.md#stale)\n"
        "[d](references/plain.md#api) [e](references/plain.md#stale)\n",
    )
    write_doc(a, "references/ref.md", "## [API][undefined]\n")
    write_doc(a, "references/plain.md", "## API\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "references/plain.md#stale" in problems[0]


def test_links_inside_html_comments_are_not_checked(tmp_path: Path) -> None:
    """A closed comment is not rendered, so links in it are not links. Real
    links beside it are checked, and comment delimiters inside code spans do
    not open or close a comment."""
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "<!-- [example](#placeholder) -->\n"
        "<!--\n[relative](references/missing.md) and [same](#gone-too)\n-->[adjacent](adjacent-gone.md)\n\n"
        "Write `<!--` then [opened](opened-gone.md) and close with `-->`; [after](#after-gone).\n\n"
        "Run `python3 skills/removed-thing/go.py`. <!-- skills/also-removed/x -->\n\n"
        "[real](#real)\n\n## Real\n",
    )
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> adjacent-gone.md",
        "broken link -> opened-gone.md",
        "missing heading anchor -> #after-gone",
        "references skills/also-removed/ which does not exist",
        "references skills/removed-thing/ which does not exist",
    ]


def test_top_level_four_space_fence_lookalikes_do_not_hide_later_content(tmp_path: Path) -> None:
    """Four spaces before ``` at top level make indented code, not a fence; in
    a list item a fence may sit up to three spaces past the item's content
    column. Real fences, list fences and unclosed fences stay excluded."""
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "Intro.\n\n    ```\n[top](missing-top.md) and [frag](#gone-top)\n\n"
        "    ~~~~\n## After pseudo\n\n[ok](#after-pseudo)\n\n"
        "   ```\n[hidden](hidden.md)\n   ```\n\n"
        "- item\n\n  ```markdown\n  [listed](#list-example)\n  ```\n\n"
        "1. Step\n\n   ~~~~markdown\n   ## Example title\n   ```\n   [inner](inner.md)\n   ```\n   ~~~~\n\n"
        "- deep\n\n      ```\n[deep](missing-deep.md) [x](#example-title)\n\n"
        "````\n[eof](eof-hidden.md)\n```\n",
    )
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> missing-deep.md",
        "broken link -> missing-top.md",
        "missing heading anchor -> #example-title",
        "missing heading anchor -> #gone-top",
    ]


def test_escaped_opening_brackets_are_not_links(tmp_path: Path) -> None:
    """An odd number of backslashes escapes `[`; an even number escapes only
    themselves, leaving a real link."""
    root = tmp_path / "skills"
    make_skill(
        root, "alpha",
        "\\[example](#placeholder) and \\\\[even](missing-even.md) and "
        "\\\\\\[odd](#odd-gone) then [real](missing-real.md)\\[lit](#lit)[adjacent](#adjacent-gone)\n",
    )
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> missing-even.md",
        "broken link -> missing-real.md",
        "missing heading anchor -> #adjacent-gone",
    ]


def test_escaped_opening_brackets_in_headings_are_not_links() -> None:
    # Escaped: literal `[API](...)` text, which this checker does not guess.
    assert MODULE.anchors("## \\[API](https://e.test/x)\n") is None
    # Even backslashes and plain links are real links: the label is the text.
    assert MODULE.anchors("## \\\\[API](https://e.test/x)\n") == {"api"}
    assert MODULE.anchors("## [API](https://e.test/x)\n") == {"api"}
    # An escaped bracket beside a real link stays literal text.
    assert MODULE.anchors("## \\[a [b](https://e.test) c\n") == {"a-b-c"}


CLOSER_FIXTURE = (
    "```\n    ```\n[hidden](hidden-a.md)\n```\n[after](missing-after-a.md)\n\n"
    "- item\n\n  ```\n      ```\n  [hidden](hidden-b.md)\n  ```\n[after](missing-after-b.md)\n\n"
    "- item\n\n  ```\n\n  [still](hidden-c.md)\n  ```\n\n"
    "- item\n\n  ```\n  code\n[outer](missing-outer.md) [o](#outer)\n\n## Outer\n"
)


def test_fence_closers_obey_the_container_indent_rule(tmp_path: Path) -> None:
    """A closer four spaces past its container margin is code, not a closer;
    a non-blank line outdented past a list fence's margin ends the item and
    the fence with it. Blank lines inside a list fence do not."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", CLOSER_FIXTURE)
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> missing-after-a.md",
        "broken link -> missing-after-b.md",
        "broken link -> missing-outer.md",
    ]


COMMENT_FENCE_FIXTURE = (
    "<!--\n```\n-->\n[real](missing-c1.md)\n\n"
    "<!--\n~~~\n-->\n[real](missing-c2.md) [h](#real-heading)\n\n## Real heading\n\n"
    "```\n<!--\n```\n[after-fence](missing-c3.md)\n-->\n\n"
    "`<!--`\n\n```\n[in-fence](hidden-c4.md)\n```\n\n`-->` [real](missing-c4.md)\n"
)


def test_comment_and_fence_masking_order(tmp_path: Path) -> None:
    """Fence markers inside an HTML comment block do not open fences; comment
    markers inside a fence or a code span are literal and mask nothing."""
    root = tmp_path / "skills"
    make_skill(root, "alpha", COMMENT_FENCE_FIXTURE)
    problems = sorted(p.split("SKILL.md: ")[1] for p in MODULE.check(root, []))
    assert problems == [
        "broken link -> missing-c1.md",
        "broken link -> missing-c2.md",
        "broken link -> missing-c3.md",
        "broken link -> missing-c4.md",
    ]


def test_headings_nested_in_wide_list_items_make_target_unsupported(tmp_path: Path) -> None:
    """`10. Item` puts content at column 4, so `    ## Nested` is a real heading,
    as is `- ## Inline`. Container headings are not parsed: such targets are
    skipped rather than reported. Shallow list headings remain supported."""
    assert MODULE.anchors("10. Item\n\n    ## Nested heading\n") is None
    assert MODULE.anchors("- ## Inline item heading\n") is None
    # Controls: top-level indented code is not a heading; shallow nesting parses.
    assert MODULE.anchors("Text.\n\n    ## not a heading\n") == set()
    assert MODULE.anchors("## Plain heading\n\n- item\n\n  ## Shallow nested\n") == {"plain-heading", "shallow-nested"}
    root = tmp_path / "skills"
    a = make_skill(
        root, "alpha",
        "[a](references/nested.md#nested-heading) [b](references/nested.md#stale)\n"
        "[c](references/plain.md#plain-heading) [d](references/plain.md#shallow-nested) "
        "[e](references/plain.md#stale)\n",
    )
    write_doc(a, "references/nested.md", "10. Item\n\n    ## Nested heading\n")
    write_doc(a, "references/plain.md", "## Plain heading\n\n- item\n\n  ## Shallow nested\n")
    problems = fragment_problems(MODULE.check(root, []))
    assert len(problems) == 1 and "references/plain.md#stale" in problems[0]
