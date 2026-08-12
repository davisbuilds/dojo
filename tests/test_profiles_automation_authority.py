"""Task 9 — no automated path may mutate installed skill state.

Hooks and CI run without a human reading their output. If one of them acquires a
path that applies, removes, relinks, or widens skills on a real machine, the
first symptom is a changed global root that nothing reports — the same shape as
the adapter link that put a dojo session at 177% of budget, and the connector
sync that refilled recovered headroom within a day.

The distribution-profiles work is read-only through phase 1 by design. This
module pins that, two ways:

**Statically**, over the shell sources and the imported symbols, because a
mutation path is usually introduced as an import or a flag rather than as new
logic. **Dynamically**, by running every hook against a fixture HOME and hashing
its skills roots before and after.

Every detector here is paired with a negative control that injects the violation
it looks for. A static check that cannot see a planted `--apply` is not evidence
that none exists; the whole value of a clean result is that the instrument was
shown capable of a dirty one.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS = REPO_ROOT / "hooks"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-contract-pilot.yml"
AUDIT = REPO_ROOT / "skills" / "skill-standardizer" / "scripts" / "audit.py"

# Entrypoints and flags that can change installed skill state. Matched as whole
# tokens so a substring in prose or a filename cannot trip them.
MUTATING_TOKENS = (
    r"--apply",
    r"\bsync\.py\b",
    r"\binstall-skill-from-github\.py\b",
    r"\bapply_actions\b",
    r"profiles[/.]apply\b",
)

# `audit.py` is the read-only half of the standardizer and the only entrypoint a
# hook invokes. Its import list is the seam: `apply_actions` lives in the same
# library, one line away.
AUDIT_READONLY_SYMBOLS = {
    "build_audit_report", "print_json", "resolve_context",
    "summarize_report", "write_json",
}


def hook_scripts() -> list[Path]:
    scripts = sorted(HOOKS.glob("*.sh"))
    assert scripts, "no hook scripts found — the detector is looking in the wrong place"
    return scripts


def mutating_tokens_in(text: str) -> list[str]:
    return [t for t in MUTATING_TOKENS if re.search(t, text)]


# --------------------------------------------------------------------------
# Static: hooks
# --------------------------------------------------------------------------


def test_no_hook_references_a_mutating_entrypoint():
    """Every hook runs unattended; none may hold a path to installed state."""
    offenders = {
        script.name: found
        for script in hook_scripts()
        if (found := mutating_tokens_in(script.read_text()))
    }
    assert not offenders, f"hooks reference mutating entrypoints: {offenders}"


def test_the_hook_detector_sees_a_planted_violation(tmp_path):
    """Negative control. A clean result means nothing without this."""
    planted = tmp_path / "hook.sh"
    planted.write_text("#!/usr/bin/env bash\npython3 scripts/sync.py --apply\n")
    assert mutating_tokens_in(planted.read_text()), "detector cannot see a planted --apply"


def test_the_detector_does_not_fire_on_ordinary_hook_text(tmp_path):
    """…and does not fire on everything, which would be equally uninformative."""
    benign = tmp_path / "hook.sh"
    benign.write_text("#!/usr/bin/env bash\npython3 audit.py --format json\n")
    assert mutating_tokens_in(benign.read_text()) == []


# --------------------------------------------------------------------------
# Static: the standardizer's read-only entrypoint
# --------------------------------------------------------------------------


def test_audit_imports_only_read_only_symbols():
    """`apply_actions` sits one line away in the same library.

    Asserted as an exact set rather than an absence: a new mutating symbol with
    a different name would pass an `apply_actions not in` check.
    """
    source = AUDIT.read_text()
    match = re.search(r"from skill_standardizer_lib import \(([^)]*)\)", source)
    assert match, "audit.py's import block changed shape; re-verify this check"
    imported = {s.strip().rstrip(",") for s in match.group(1).split() if s.strip().rstrip(",")}
    assert imported == AUDIT_READONLY_SYMBOLS, (
        f"audit.py's imports changed: {imported ^ AUDIT_READONLY_SYMBOLS}")


# --------------------------------------------------------------------------
# Static: CI
# --------------------------------------------------------------------------


def test_ci_never_creates_the_whole_catalog_links():
    """`gen_harness_adapters.py` without `--skip-symlinks` links the whole catalog
    into project scope — the defect that put a dojo session at 177% of budget."""
    text = WORKFLOW.read_text()
    for line in text.splitlines():
        if "gen_harness_adapters.py" in line:
            assert "--skip-symlinks" in line, f"CI may create catalog links: {line.strip()}"
            assert "--check" in line, f"CI invocation is not read-only: {line.strip()}"


def test_ci_holds_no_mutating_entrypoint():
    assert mutating_tokens_in(WORKFLOW.read_text()) == []


# --------------------------------------------------------------------------
# Dynamic: hooks leave a skills root byte-identical
# --------------------------------------------------------------------------


def hash_tree(root: Path) -> str:
    """Content hash over a directory tree, including names and symlink targets."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(str(path.relative_to(root)).encode())
        if path.is_symlink():
            digest.update(b"\0link\0" + os.readlink(path).encode())
        elif path.is_file():
            digest.update(b"\0file\0" + path.read_bytes())
    return digest.hexdigest()


@pytest.fixture
def fixture_home(tmp_path):
    """A HOME with populated skills roots, in both topologies hooks might meet."""
    home = tmp_path / "home"
    canonical = home / ".agents" / "skills" / "example-skill"
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: A fixture skill.\nversion: 1.0.0\n---\n\nBody.\n")
    codex = home / ".codex" / "skills"
    codex.mkdir(parents=True)
    (codex / "example-skill").symlink_to(canonical)
    return home


@pytest.fixture
def hook_repo(tmp_path):
    """A real git checkout for hooks to run in.

    Most hooks exit at `git rev-parse --show-toplevel`, so running them in a bare
    scratch directory exercises nothing: 10 of 11 return silently with exit 0 and
    the mutation check passes vacuously. That is the degenerate pass this task
    exists to avoid, so the hooks get a repository they will actually work in —
    a copy, never this one, since some legitimately write to their own checkout.
    """
    import shutil

    repo = tmp_path / "repo"
    repo.mkdir()
    for part in ("hooks", "scripts"):
        shutil.copytree(REPO_ROOT / part, repo / part, symlinks=True)
    (repo / "skills").mkdir()
    shutil.copytree(REPO_ROOT / "skills" / "skill-standardizer",
                    repo / "skills" / "skill-standardizer", symlinks=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def test_every_hook_leaves_the_skills_roots_untouched(fixture_home, hook_repo):
    """The runtime half. A static check cannot see a mutation reached indirectly.

    HOME points at the fixture, so a hook resolving global roots from the
    environment writes there rather than to the real machine. Non-zero exits are
    ignored — a hook declining its input is not the property under test.
    """
    before = hash_tree(fixture_home)
    env = {
        **os.environ, "HOME": str(fixture_home),
        "CLAUDE_PROJECT_DIR": str(hook_repo), "PATH": os.environ.get("PATH", ""),
    }
    # A realistic tool payload. With bare `{}` the tool-use hooks exit at their
    # first `jq` extraction, so the sweep would cover only the session hooks —
    # notably skipping the one that regenerates artifacts.
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(hook_repo / "skills" / "skill-standardizer" / "SKILL.md")},
    })
    executed = []
    for script in hook_scripts():
        target = hook_repo / "hooks" / script.name
        try:
            result = subprocess.run(
                ["bash", str(target)], cwd=hook_repo, env=env, input=payload,
                capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            pytest.fail(f"{script.name} hung; it may be waiting on input")
        executed.append((script.name, result.returncode))

    assert len(executed) == len(hook_scripts()), "not every hook was exercised"
    assert hash_tree(fixture_home) == before, "a hook mutated the fixture skills roots"


def test_the_drift_hook_actually_reaches_its_audit(fixture_home, hook_repo):
    """Non-degeneracy control for the sweep above.

    `session-start-skill-drift.sh` is the one hook that reads a global skills
    root, so it is the one whose real path must be proven to run. Without this,
    the sweep asserts only that hooks which exit at their first guard do not
    mutate anything — true, and worthless.
    """
    env = {**os.environ, "HOME": str(fixture_home), "PATH": os.environ.get("PATH", "")}
    hook = hook_repo / "hooks" / "session-start-skill-drift.sh"

    # It must get past `git rev-parse` in this repo, and not in a non-repo.
    inside = subprocess.run(["bash", "-x", str(hook)], cwd=hook_repo, env=env,
                            capture_output=True, text=True, timeout=120)
    trace = inside.stderr
    assert "audit.py" in trace, (
        "the drift hook never reached its audit; the runtime sweep is vacuous")
    assert "--global-policy" in trace


def test_the_tree_hash_detects_each_mutation_shape(fixture_home):
    """Negative control for the runtime detector, over all three shapes."""
    baseline = hash_tree(fixture_home)
    skills = fixture_home / ".agents" / "skills"

    added = skills / "new-skill"
    added.mkdir()
    (added / "SKILL.md").write_text("x")
    assert hash_tree(fixture_home) != baseline, "an added skill is invisible"
    (added / "SKILL.md").unlink()
    added.rmdir()
    assert hash_tree(fixture_home) == baseline

    target = skills / "example-skill" / "SKILL.md"
    original = target.read_text()
    target.write_text(original + "edited\n")
    assert hash_tree(fixture_home) != baseline, "edited content is invisible"
    target.write_text(original)
    assert hash_tree(fixture_home) == baseline

    link = fixture_home / ".codex" / "skills" / "example-skill"
    link.unlink()
    link.symlink_to(skills / "example-skill" / "SKILL.md")
    assert hash_tree(fixture_home) != baseline, "a relinked target is invisible"


# --------------------------------------------------------------------------
# The CI gate itself
# --------------------------------------------------------------------------


def run_ci_check(capsys):
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from profiles import ci_check

    code = ci_check.main()
    return code, capsys.readouterr()


def test_the_ci_gate_passes_and_says_what_it_evaluated(capsys):
    """A green step that evaluated nothing is the failure this gate guards against."""
    code, captured = run_ci_check(capsys)
    assert code == 0, captured.err
    out = captured.out
    assert "compositions resolved: 6 of 6" in out
    assert re.search(r"scored core\+engineering: \d+ skills, [1-9]\d* tokens", out), (
        "the gate must score a real composition, not merely load files")
    assert "NOT checked here" in out, (
        "the gate must state its boundary; CI cannot observe an effective catalog")


def test_the_ci_gate_refuses_a_provisional_deployable_policy(monkeypatch, capsys):
    """Negative control. SC-04: a limit never checked against behaviour may not gate."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import dataclasses

    from profiles import ci_check
    from profiles.budget import load_policy as real_load

    def fake_load(path):
        policy = real_load(path)
        if policy.harness == "codex":
            return dataclasses.replace(policy, limit_basis="vendor")
        return policy

    monkeypatch.setattr(ci_check, "load_policy", fake_load)
    code = ci_check.main()
    captured = capsys.readouterr()
    assert code == 1
    assert "provisional limit" in captured.err


def test_the_ci_gate_refuses_a_scoring_that_evaluated_nothing(monkeypatch, capsys):
    """Non-degeneracy guard, tested rather than assumed.

    Found by mutation probe: deleting this check survived, because the guard
    only fires when demand is zero and the real catalog never is. A guard for a
    condition the happy path cannot reach needs the condition constructed.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import dataclasses

    from profiles import ci_check
    from profiles.budget import assess as real_assess

    def zero_assess(*args, **kwargs):
        return dataclasses.replace(real_assess(*args, **kwargs), demand=0)

    monkeypatch.setattr(ci_check, "assess", zero_assess)
    code = ci_check.main()
    assert code == 1
    assert "evaluated nothing" in capsys.readouterr().err
