from __future__ import annotations

import importlib.util
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_harness_adapters.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gen_harness_adapters", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_repo(tmp_path: Path):
    skills_root = tmp_path / "skills"
    skills_root.mkdir()

    def make_skill(name: str, description: str, agents_file: str | None = None, content: str | None = None):
        d = skills_root / name
        d.mkdir()
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n", encoding="utf-8"
        )
        if agents_file is not None:
            (d / "agents").mkdir()
            (d / "agents" / "openai.yaml").write_text(content or "", encoding="utf-8")
        return d

    # Pre-seed harness dirs as plain directories (mimicking the drifted state)
    for harness in (".claude", ".agents", ".agent"):
        (tmp_path / harness / "skills").mkdir(parents=True)

    return skills_root, make_skill


def _invoke(module, tmp_path, args):
    import sys

    argv = ["gen", "--repo-root", str(tmp_path), "--skills-root", str(tmp_path / "skills"), *args]
    old = sys.argv
    sys.argv = argv
    try:
        return module.main()
    finally:
        sys.argv = old


def test_generates_symlinks_and_sidecars(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    make_skill("diagnose", "Disciplined debugging loop. Use when debugging hard bugs.")

    assert _invoke(module, tmp_path, []) == 0

    for harness in (".claude", ".agents", ".agent"):
        link = tmp_path / harness / "skills"
        assert link.is_symlink()
        assert os.readlink(link) == "../skills"

    sidecar = skills_root / "diagnose" / "agents" / "openai.yaml"
    assert sidecar.exists()
    text = sidecar.read_text()
    assert text.startswith(module.MARKER)
    assert 'display_name: "Diagnose"' in text
    # default_prompt must mention the skill as $name (explicit invocation)
    assert "$diagnose" in text
    # short_description must respect the 25-64 char contract
    sd = next(line for line in text.splitlines() if "short_description:" in line)
    value = sd.split('"', 1)[1].rsplit('"', 1)[0]
    assert 25 <= len(value) <= 64, value


def test_idempotent_check_after_generate(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    make_skill("diagnose", "Use when debugging.")

    assert _invoke(module, tmp_path, []) == 0
    assert _invoke(module, tmp_path, ["--check"]) == 0  # clean after generate


def test_check_reports_drift_before_generate(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    make_skill("diagnose", "Use when debugging.")

    assert _invoke(module, tmp_path, ["--check"]) == 1  # symlinks + sidecar missing


def test_skip_symlinks_writes_sidecars_only(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    make_skill("diagnose", "Use when debugging.")

    assert _invoke(module, tmp_path, ["--skip-symlinks"]) == 0
    # sidecar written
    assert (skills_root / "diagnose" / "agents" / "openai.yaml").exists()
    # harness skills/ left as the original plain dir (not converted to a symlink)
    assert not (tmp_path / ".claude" / "skills").is_symlink()
    # sidecars-only check passes regardless of symlink state
    assert _invoke(module, tmp_path, ["--check", "--skip-symlinks"]) == 0


def test_refuses_to_delete_nonempty_real_dir(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    make_skill("diagnose", "Use when debugging.")
    # A developer's real harness dir with untracked local content
    local = tmp_path / ".claude" / "skills" / "my-local-skill"
    local.mkdir(parents=True)
    (local / "SKILL.md").write_text("local", encoding="utf-8")

    assert _invoke(module, tmp_path, []) == 1  # errors -> non-zero
    # untouched: the local skill is preserved, not rmtree'd
    assert (local / "SKILL.md").read_text() == "local"
    assert not (tmp_path / ".claude" / "skills").is_symlink()


def test_short_description_truncates_long_first_sentence(tmp_path: Path):
    module = load_module()
    long = "This is an intentionally very long first sentence that runs well beyond the sixty four character ceiling"
    out = module.short_description(long, "Demo")
    assert len(out) <= 64
    assert " " in out  # truncated on a word boundary, not mid-word


def test_hand_authored_sidecar_preserved(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    curated = 'interface:\n  display_name: "Fancy"\n  icon_small: "./assets/x.svg"\n'
    make_skill("fancy", "Use when fancy.", agents_file="openai.yaml", content=curated)

    assert _invoke(module, tmp_path, []) == 0
    # untouched: no marker, original content intact
    out = (skills_root / "fancy" / "agents" / "openai.yaml").read_text()
    assert out == curated
    # and --check is satisfied by its existence
    assert _invoke(module, tmp_path, ["--check"]) == 0


# --- Command wrapper wiring into .claude/commands/ -------------------------


def _add_command(skill_dir: Path, rel: str, body: str = "# cmd\n"):
    target = skill_dir / "commands" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def test_wires_commands_into_claude_commands(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    d = make_skill("local-review", "Use when reviewing local diffs.")
    _add_command(d, "review.md")
    d2 = make_skill("brainstorming", "Use when clarifying what to build.")
    _add_command(d2, "workflows/brainstorm.md")

    assert _invoke(module, tmp_path, []) == 0

    flat = tmp_path / ".claude" / "commands" / "review.md"
    nested = tmp_path / ".claude" / "commands" / "workflows" / "brainstorm.md"
    assert flat.is_symlink() and flat.resolve() == (skills_root / "local-review" / "commands" / "review.md")
    assert nested.is_symlink() and nested.resolve() == (
        skills_root / "brainstorming" / "commands" / "workflows" / "brainstorm.md"
    )


def test_command_links_are_clean_on_recheck(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    assert _invoke(module, tmp_path, []) == 0
    assert _invoke(module, tmp_path, ["--check"]) == 0


def test_check_reports_missing_command_link(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    # Symlinks + sidecar + command link all missing -> drift.
    assert _invoke(module, tmp_path, ["--check"]) == 1


def test_collision_across_skills_errors(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    _add_command(make_skill("gh-review-pr", "Use when reviewing PRs."), "review.md")
    # Two skills map to .claude/commands/review.md -> refuse, non-zero, no clobber.
    assert _invoke(module, tmp_path, []) == 1
    link = tmp_path / ".claude" / "commands" / "review.md"
    assert not link.exists()


def test_prunes_stale_command_symlink(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    d = make_skill("local-review", "Use when reviewing.")
    cmd = _add_command(d, "review.md")
    assert _invoke(module, tmp_path, []) == 0
    link = tmp_path / ".claude" / "commands" / "review.md"
    assert link.is_symlink()
    # Remove the source command; re-run must prune the now-dangling managed link.
    cmd.unlink()
    assert _invoke(module, tmp_path, []) == 0
    assert not link.exists() and not link.is_symlink()


def test_does_not_touch_a_real_command_file(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    # A user's hand-authored command that maps to no skill source.
    hand = tmp_path / ".claude" / "commands" / "my-own.md"
    hand.parent.mkdir(parents=True, exist_ok=True)
    hand.write_text("mine", encoding="utf-8")
    assert _invoke(module, tmp_path, []) == 0
    assert hand.is_file() and not hand.is_symlink() and hand.read_text() == "mine"


def test_foreign_command_symlink_is_reported_not_clobbered(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    # A user's own symlink at the generated target, pointing outside skills/*/commands/.
    foreign_source = tmp_path / "dotfiles" / "review.md"
    foreign_source.parent.mkdir(parents=True, exist_ok=True)
    foreign_source.write_text("mine", encoding="utf-8")
    link = tmp_path / ".claude" / "commands" / "review.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(os.path.relpath(foreign_source, link.parent), link)
    # Must refuse (like a real file), leaving the foreign symlink intact.
    assert _invoke(module, tmp_path, []) == 1
    assert link.is_symlink()
    assert link.resolve().read_text() == "mine"


def test_skip_symlinks_skips_commands(tmp_path: Path):
    module = load_module()
    skills_root, make_skill = make_repo(tmp_path)
    _add_command(make_skill("local-review", "Use when reviewing."), "review.md")
    assert _invoke(module, tmp_path, ["--skip-symlinks"]) == 0
    assert not (tmp_path / ".claude" / "commands" / "review.md").exists()
    assert _invoke(module, tmp_path, ["--check", "--skip-symlinks"]) == 0
