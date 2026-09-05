from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKELETON = (
    REPO_ROOT / "skills" / "research-architect" / "references" / "skeleton.md"
).read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    return SKELETON.split(start, 1)[1].split(end, 1)[0]


def shipped_quote(block: str) -> str:
    return " ".join(
        line.removeprefix(">").strip()
        for line in block.splitlines()
        if line.startswith(">")
    )


def test_domain_fit_and_uningested_artifact_rules_ship_to_executors():
    a4 = shipped_quote(section("### A4 —", "### A5 —"))
    a6 = shipped_quote(section("### A6 —", "### A7 —"))

    assert "what it measures and on what population" in a4
    assert "Treat adjacent-domain evidence as unsupported" in a4
    assert 'label it "not ingested"' in a6
    assert "contents, size, structure, or metadata" in a6


def test_rubric_and_merge_lessons_remain_drafting_guidance():
    a9 = section("### A9 —", "### A10 —")
    m1 = section("### M1 —", "### M2 —")

    assert "without that cost, the item cannot" in a9
    assert "include exact section-order compliance" in m1
    assert "without that cost" not in shipped_quote(a9)
    assert "include exact section-order compliance" not in shipped_quote(m1)
