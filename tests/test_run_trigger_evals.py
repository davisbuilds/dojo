from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "skill-evals" / "scripts" / "run_trigger_evals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_trigger_evals", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_skill(skills_root: Path, name: str, description: str, triggers: list[str]) -> None:
    skill_dir = skills_root / name
    skill_dir.mkdir(parents=True)
    trig_block = "".join(f"  - {t}\n" for t in triggers)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\nversion: 1.0.0\ntriggers:\n{trig_block}---\n\n# {name}\n",
        encoding="utf-8",
    )


def test_declared_triggers_self_route(tmp_path: Path) -> None:
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    write_skill(
        skills_root,
        "diagnose",
        "Use when debugging hard bugs and performance regressions.",
        ["diagnose this", "diagnose this bug"],
    )
    write_skill(
        skills_root,
        "handoff",
        "Use when creating a session summary for context handoff.",
        ["create a handoff", "write a handoff summary"],
    )

    skills = module.build_skill_index(skills_root, None)
    result = module.evaluate_declared_triggers(skills)

    assert result["summary"]["failed"] == 0
    assert result["summary"]["skills_with_triggers"] == 2
    assert all(a["routes"] and a["collision_with"] is None for a in result["assertions"])


def test_declared_trigger_collision_is_flagged(tmp_path: Path) -> None:
    module = load_module()
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    # Two skills claiming an identical trigger phrase -> guaranteed collision.
    write_skill(
        skills_root,
        "review-swarm",
        "Use when running a parallel multi-agent review of a diff.",
        ["review this diff"],
    )
    write_skill(
        skills_root,
        "local-review",
        "Use when reviewing local workspace changes without posting to GitHub.",
        ["review this diff"],
    )

    skills = module.build_skill_index(skills_root, None)
    result = module.evaluate_declared_triggers(skills)

    assert result["summary"]["failed"] >= 1
    flagged = [a for a in result["assertions"] if a["collision_with"] is not None]
    assert flagged, "expected at least one collision to be flagged"


# --- Scorer rewrite: TF-IDF cosine + stemming + ranking assertions ---------


def write_plain_skill(skills_root: Path, name: str, description: str) -> None:
    skill_dir = skills_root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\nversion: 1.0.0\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def test_stemming_matches_singular_and_plural(tmp_path: Path) -> None:
    """A plural in the prompt must match a singular in the description, and win clearly.

    The old token-overlap scorer treats 'articles' and 'article' as distinct, so
    it scores this 0.0 for both skills and only 'wins' by dict order. Stemming must
    give the matching skill a strictly positive score that beats the distractor.
    """
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "article-store", "Manage one article record.")
    write_plain_skill(root, "publish-tool", "Publish site content quickly.")
    skills = module.build_skill_index(root, None)
    scores = {s: module.score_trigger("list my articles", "implicit", s, d) for s, d in skills.items()}
    assert scores["article-store"] > scores["publish-tool"]
    assert scores["article-store"] > 0


def test_hyphenated_compounds_split_into_components() -> None:
    """'citation-ready' in a description must match a plain 'citation' in a prompt."""
    module = load_module()
    tokens = set(module.normalize_tokens("citation-ready web-backed multi-model synthesis"))
    assert "citation" in tokens
    assert "web" in tokens
    assert "model" in tokens


def test_stem_folds_regular_plurals_and_gerunds() -> None:
    module = load_module()
    # Regular plurals must not be over-stripped, and doubled-consonant gerunds
    # must undouble so 'scanning' meets 'scan'.
    assert module.stem("articles") == module.stem("article")
    assert module.stem("spots") == module.stem("spot")
    assert module.stem("scanning") == module.stem("scan")
    assert module.stem("deployments") == module.stem("deployment")
    # But do not mangle these.
    assert module.stem("class") == "class"
    assert module.stem("us") == "us"


def test_idf_downweights_corpus_wide_tokens(tmp_path: Path) -> None:
    """A rare shared token must decide routing; corpus-wide tokens must not tie the field.

    The winner shares one rare token ('trifecta'); the distractor shares two
    corpus-wide tokens ('repository', 'workspace'). The old scorer counts raw
    overlap, so the distractor's two common tokens beat the winner's one rare one.
    IDF must invert that.
    """
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "secure-code", "Detect the trifecta risk.")
    write_plain_skill(root, "review-tool", "Review repository workspace files and layout.")
    # Filler skills make 'repository' and 'workspace' corpus-wide (low IDF).
    for i in range(5):
        write_plain_skill(root, f"filler-{i}", "Operate on the repository workspace.")
    skills = module.build_skill_index(root, None)
    scores = {s: module.score_trigger("repository workspace trifecta", "implicit", s, d) for s, d in skills.items()}
    assert max(scores, key=scores.get) == "secure-code"
    assert scores["secure-code"] > scores["review-tool"]


def test_ranking_picks_winner_over_generic_sibling(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "write-spec", "Pin the falsifiable contract for a change: what must be true.")
    write_plain_skill(root, "blind-spots", "Quiz the user on a change to find the gaps in their understanding.")
    cases = {"cases": [{
        "id": "quiz", "type": "implicit",
        "prompt": "quiz me on this change to find gaps in my understanding",
        "expected": {"trigger": ["blind-spots"], "avoid": ["write-spec"]},
    }]}
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases["cases"], mode="ranking")
    assert result["summary"]["failed"] == 0
    assert result["summary"]["mode"] == "ranking"
    # self-improve smoke greps for this exact token
    assert all(a["passed"] for a in result["assertions"])


def test_ranking_accepts_any_of_multiple_valid_triggers(tmp_path: Path) -> None:
    """trigger: [A, B] means routing to EITHER is correct; the non-winner must not fail."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "obsidian-bases", "Build database views and dashboards over a vault.")
    write_plain_skill(root, "obsidian-canvas", "Build a canvas map of linked nodes over a vault.")
    write_plain_skill(root, "vercel-deploy", "Deploy an app to Vercel.")
    cases = [{
        "id": "either", "type": "implicit",
        "prompt": "make a canvas map for this vault",
        "expected": {"trigger": ["obsidian-bases", "obsidian-canvas"], "avoid": ["vercel-deploy"]},
    }]
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases, mode="ranking")
    assert result["summary"]["failed"] == 0


def test_declared_trigger_not_in_scored_vector(tmp_path: Path) -> None:
    """A trigger unrelated to name/description must NOT self-route.

    If declared triggers were folded into the owner's vector, the self-route check
    would be circular — a database skill could declare 'paint watercolors' and pass.
    """
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_skill(root, "db-tool", "Manage relational databases and queries.", ["paint watercolors"])
    skills = module.build_skill_index(root, None)
    result = module.evaluate_declared_triggers(skills)
    assert any(a["skill"] == "db-tool" and not a["passed"] for a in result["assertions"])


def test_declared_trigger_echoing_description_still_self_routes(tmp_path: Path) -> None:
    """The legitimate case must keep working: a trigger echoed by the description routes."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_skill(root, "db-tool", "Manage relational databases and run queries.", ["run a query"])
    write_skill(root, "paint-tool", "Paint watercolors on a canvas.", ["paint watercolors"])
    skills = module.build_skill_index(root, None)
    result = module.evaluate_declared_triggers(skills)
    assert result["summary"]["failed"] == 0


def test_ranking_winner_must_clear_score_floor(tmp_path: Path) -> None:
    """A vacuous win (only-skill selected, or a total-miss prompt) must not pass."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "only-skill", "Manage relational databases.")
    write_plain_skill(root, "other", "Render three-dimensional animations.")
    cases = [{
        "id": "vacuous", "type": "implicit",
        "prompt": "qzxwv mmnbb gibberish tokens",
        "expected": {"trigger": ["only-skill"], "avoid": []},
    }]
    skills = module.build_skill_index(root, {"only-skill"})  # narrow to the one skill
    result = module.evaluate_cases(skills, cases, mode="ranking")
    assert result["summary"]["failed"] >= 1


def test_known_hard_case_reported_but_not_counted_as_failure(tmp_path: Path) -> None:
    """A case flagged known_hard that fails is tallied separately, not as a failure."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "alpha", "Alpha widget configuration.")
    write_plain_skill(root, "beta", "Beta gadget assembly.")
    cases = [{
        "id": "ambiguous", "type": "implicit", "known_hard": True,
        "prompt": "configure the alpha widget",
        "expected": {"trigger": ["beta"], "avoid": ["alpha"]},
    }]
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases, mode="ranking")
    assert result["summary"]["failed"] == 0
    assert result["summary"]["known_hard_failed"] >= 1


def test_ranking_flags_wrong_winner(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "alpha", "Handle alpha widget configuration and tuning.")
    write_plain_skill(root, "beta", "Handle beta gadget assembly and testing.")
    cases = [{
        "id": "mismatch", "type": "implicit",
        "prompt": "configure the alpha widget tuning",
        "expected": {"trigger": ["beta"], "avoid": ["alpha"]},
    }]
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases, mode="ranking")
    assert result["summary"]["failed"] >= 1
    assert any(not a["passed"] for a in result["assertions"])


def test_ranking_matches_nothing_case(tmp_path: Path) -> None:
    """A negative case (empty trigger) passes only if avoided skills stay under the floor."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "blind-spots", "Quiz the user on a change to find gaps in understanding.")
    write_plain_skill(root, "playwright", "Drive a real browser: navigate, fill forms, screenshot.")
    cases = [{
        "id": "generic", "type": "negative",
        "prompt": "what does this function do",
        "expected": {"trigger": [], "avoid": ["blind-spots"]},
    }]
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases, mode="ranking")
    assert result["summary"]["failed"] == 0


def test_threshold_mode_escape_hatch_available(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "diagnose", "Debug broken behavior and find the root cause.")
    write_plain_skill(root, "handoff", "Write a session summary for context handoff.")
    cases = [{
        "id": "dbg", "type": "implicit",
        "prompt": "debug this broken behavior and find the root cause",
        "expected": {"trigger": ["diagnose"], "avoid": ["handoff"]},
    }]
    skills = module.build_skill_index(root, None)
    result = module.evaluate_cases(skills, cases, mode="threshold")
    assert result["summary"]["mode"] == "threshold"
    assert "passed" in result["summary"]


def test_idf_computed_over_full_corpus_not_selected_subset(tmp_path: Path) -> None:
    """Scoring a subset must still weight by corpus-wide IDF, so subset scores are stable."""
    module = load_module()
    root = tmp_path / "skills"
    root.mkdir()
    write_plain_skill(root, "secure-code", "Scan code with semgrep for the lethal trifecta.")
    for i in range(6):
        write_plain_skill(root, f"filler-{i}", "Work with code in the repository workspace.")
    full = module.build_skill_index(root, None)
    subset = module.build_skill_index(root, {"secure-code", "filler-0"})
    # "semgrep" idf must be identical whether or not we filter the returned set.
    assert full["secure-code"]["idf"]["semgrep"] == subset["secure-code"]["idf"]["semgrep"]
