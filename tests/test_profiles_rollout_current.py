"""Synthetic Codex session logs exercising current rollout catalog evidence."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from profiles import probe_codex, rollout_codex as rc  # noqa: E402

START = "2026-11-01T13:00:00.000Z"
MIDDLE = "2026-11-02T13:00:00.000Z"
LATEST = "2026-11-03T13:00:00.000Z"
CWD = "/Users/example/initial"
NEW_CWD = "/Users/example/current"
ROOT = "/Users/example/.agents/skills"
PLUGIN_ROOT = "/Users/example/.codex/plugins/cache/openai-curated-remote/example/1/skills"


def record(kind, timestamp, **payload):
    return {"type": kind, "timestamp": timestamp, "payload": payload}


def header(timestamp=START, *, originator="codex-tui", cwd=CWD):
    return record("session_meta", timestamp, id="native-session", originator=originator,
                  cli_version="0.170.0", cwd=cwd)


def context(timestamp, *, cwd=CWD, model="example-model"):
    return record("turn_context", timestamp, cwd=cwd, model=model)


def message(timestamp, *texts, role="developer"):
    return record("response_item", timestamp, type="message", role=role,
                  content=[{"type": "input_text", "text": text} for text in texts])


def entry(name, description="Original.", locator=None):
    return f"- {name}: {description} (file: {locator or f'{ROOT}/{name}/SKILL.md'})"


def full(*lines, roots=()):
    body = probe_codex.render_available_skills_body(list(roots), list(lines))
    return f"<skills_instructions>\n## Host skills\n{body}</skills_instructions>"


def update(*lines, roots=()):
    body = "## Host skills update\n"
    if roots:
        body += "### Skill roots\nThese mappings replace earlier mappings for the same aliases.\n"
        body += "\n".join(roots) + "\n"
    return "<skills_instructions>\n" + body + "### Added or updated skills:\n" + (
        "\n".join(lines) + "\n</skills_instructions>"
    )


def write(path, *records):
    path.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    return path


def test_latest_complete_catalog_owns_timestamp_model_and_cwd(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-resumed.jsonl",
        header(),
        message(START, full(entry("original"))),
        context(START, model="old-model"),
        message(LATEST, full(entry("replacement"))),
        context(LATEST, cwd=NEW_CWD, model="new-model"),
        context("2026-11-04T13:00:00Z", cwd="/Users/example/later", model="later-model"),
    )

    observation = rc.read_rollout(path)
    assert observation.entry_names == {"replacement"}
    assert observation.meta.cwd == NEW_CWD
    assert observation.meta.model == "new-model"
    assert observation.meta.observed_at.startswith("2026-11-03T13:00:00")
    assert observation.meta.cli_version == "unknown"


def test_supported_host_delta_updates_matching_locator_and_keeps_duplicates(tmp_path):
    original = entry("sample", locator="r0/sample/SKILL.md")
    bundled = entry("sample", "Bundled.", "r1/sample/SKILL.md")
    baseline = full(original, bundled, roots=(
        f"- `r0` = `{ROOT}`",
        "- `r1` = `/Users/example/.codex/skills/.system`",
    ))
    updated = entry("sample", "Updated.", "r0/sample/SKILL.md")
    added = entry("example:catalog", "Added.", "r2/catalog/SKILL.md")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-delta.jsonl",
        header(),
        message(START, baseline),
        context(START),
        message(LATEST, update(updated, added, roots=(f"- `r2` = `{PLUGIN_ROOT}`",))),
        context(LATEST),
    )

    observation = rc.read_rollout(path)
    assert [item.rendered for item in observation.listing.entries] == [updated, bundled, added]
    assert observation.uncontrolled_entries == {"harness-bundled:sample", "connector:example:catalog"}
    assert observation.listing.entry_cost_tokens == sum(
        probe_codex.line_cost_tokens(line) for line in (updated, bundled, added)
    )
    assert observation.meta.observed_at.startswith("2026-11-03T13:00:00")


def test_alias_redefinition_preserves_previously_published_origin(tmp_path):
    baseline = full(entry("sample", locator="r0/sample/SKILL.md"), roots=(f"- `r0` = `{ROOT}`",))
    delta = update(entry("different", "Also listed.", "r0/different/SKILL.md"),
                   roots=(f"- `r0` = `{PLUGIN_ROOT}`",))
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-rebound.jsonl",
        header(), message(START, baseline), context(START), message(LATEST, delta), context(LATEST),
    )

    observation = rc.read_rollout(path)
    assert observation.meta.catalog_kind == "delta"
    assert observation.listing.entry_cost_tokens == sum(
        probe_codex.line_cost_tokens(item.rendered) for item in observation.listing.entries
    )
    assert [observation.origin_of(item.locator) for item in observation.listing.entries] == [
        rc.ORIGIN_DOJO, rc.ORIGIN_CONNECTOR,
    ]


def test_catalog_and_metadata_come_only_from_typed_fields(tmp_path):
    decoy = record(
        "event_msg", START, originator="codex_exec", cwd="/Users/example/decoy",
        cli_version="99.0.0", id="decoy", model="decoy-model", role="developer",
    )
    decoy["payload"]["text"] = full(entry("impostor"))
    developer_other_field = message(MIDDLE, "Ordinary developer instruction")
    developer_other_field["payload"]["metadata"] = {"text": full(entry("side-field-impostor"))}
    instructions_paste = typed_message(MIDDLE, full(entry("typed-impostor")), provenance="agents_md")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-typed.jsonl",
        decoy, header(), developer_other_field, message(LATEST, full(entry("authentic"))),
        instructions_paste,
        context(LATEST),
        message(LATEST, full(entry("user-paste")), role="user"),
        record("compacted", LATEST, message=full(entry("summary-paste"))),
    )

    observation = rc.read_rollout(path)
    assert observation.entry_names == {"authentic"}
    assert observation.meta.session_id == "native-session"
    assert observation.meta.surface == "codex-tui"
    assert observation.meta.cli_version == "0.170.0"
    assert observation.meta.cwd == CWD
    assert observation.meta.model == "example-model"


@pytest.mark.parametrize("newest", [
    "<skills_instructions>\n## Host skills update\n### Removed skills:\n- original\n</skills_instructions>",
    "<skills_instructions>\n## Host skills\n### Available skills\n- malformed\n</skills_instructions>",
    "<skills_instructions>\n## Host skills update\n### Added or updated skills:",
    "<skills_instructions>\n## Host skills update\n"
    "Some previously listed skills are no longer available. "
    "Verify current access before relying on a skill from this source.\n</skills_instructions>",
])
def test_unreadable_newest_catalog_has_scoped_evidence_error(tmp_path, newest):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-unsupported.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        message(LATEST, newest), context(LATEST, cwd=NEW_CWD),
    )

    errors = []
    assert rc.observations(tmp_path, cwd=NEW_CWD, evidence_errors=errors) == []
    assert len(errors) == 1
    assert errors[0].meta.observed_at.startswith("2026-11-03T13:00:00")
    assert errors[0].meta.cwd == NEW_CWD
    assert errors[0].meta.path == path


def test_replayed_compaction_cannot_give_an_old_catalog_a_new_timestamp(tmp_path):
    original = message(START, full(entry("original")))
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-compact.jsonl",
        header(), original, context(START),
        record("compacted", LATEST, message=full(entry("summary-paste")),
               replacement_history=[original["payload"]]),
        context(LATEST),
    )

    observation = rc.read_rollout(path)
    assert observation.entry_names == {"original"}
    assert observation.meta.observed_at.startswith("2026-11-01T13:00:00")


def test_unattributable_compaction_catalog_does_not_fall_back(tmp_path):
    original = message(START, full(entry("original")))
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-compact.jsonl",
        header(), original, context(START),
        record("compacted", LATEST, message="", replacement_history=[
            message(LATEST, full(entry("different")))["payload"],
        ]),
        context(LATEST),
    )

    with pytest.raises(ValueError):
        rc.read_rollout(path)


def test_limit_applied_after_sorting_by_catalog_record_not_start_time(tmp_path):
    older_name = write(
        tmp_path / "rollout-2026-11-01T13-00-00-resumed.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        message(LATEST, full(entry("resumed"))), context(LATEST),
    )
    write(
        tmp_path / "rollout-2026-11-02T13-00-00-fresh.jsonl",
        header(MIDDLE), message(MIDDLE, full(entry("middle"))), context(MIDDLE),
    )

    assert [observation.meta.path for observation in rc.observations(tmp_path, limit=1)] == [
        older_name,
    ]


@pytest.mark.skipif(shutil.which("zstd") is None, reason="requires zstd")
def test_compressed_rollout_is_discovered_and_parsed(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-compressed.jsonl",
        header(), message(START, full(entry("compressed"))), context(START),
    )
    compressed = path.with_suffix(".jsonl.zst")
    subprocess.run(["zstd", "-q", "-o", str(compressed), "--", str(path)], check=True)
    assert rc.find_rollouts(tmp_path) == [path]
    path.unlink()

    assert rc.find_rollouts(tmp_path) == [compressed]
    assert rc.observations(tmp_path)[0].entry_names == {"compressed"}


def typed_message(timestamp, text, *, provenance="skills", kind="host_skills.instructions"):
    item = message(timestamp, text)
    item["payload"]["internal_chat_message_metadata_passthrough"] = {
        "content_item_kinds": [kind],
        "content_item_metadata": [{"provenance": {"type": provenance}}],
    }
    return item


def test_same_name_locator_change_is_ambiguous_without_catalog_id(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-ambiguous.jsonl",
        header(), message(START, full(entry("sample"))), context(START),
        message(LATEST, update(entry("sample", "Changed.", f"{PLUGIN_ROOT}/sample/SKILL.md"))),
        context(LATEST),
    )

    with pytest.raises(rc.RolloutReadError, match="changes the locator"):
        rc.read_rollout(path)


def test_child_with_tui_originator_does_not_supply_interactive_evidence(tmp_path):
    write(
        tmp_path / "rollout-2026-11-01T13-00-00-parent.jsonl",
        header(), message(START, full(entry("parent"))), context(START),
    )
    child_header = header(LATEST)
    child_header["payload"]["source"] = {"subagent": {"thread_spawn": {"parent_thread_id": "parent"}}}
    child = write(
        tmp_path / "rollout-2026-11-03T13-00-00-child.jsonl",
        child_header, message(LATEST, full(entry("child"))), context(LATEST),
    )
    malformed_child = write(
        tmp_path / "rollout-2026-11-03T13-00-01-child.jsonl",
        child_header, message(LATEST, "<skills_instructions>"), context(LATEST),
    )

    errors = []
    observations = rc.observations(tmp_path, surface=rc.INTERACTIVE_SURFACES, evidence_errors=errors)
    assert [observation.entry_names for observation in observations] == [{"parent"}]
    assert errors == []
    assert rc.read_rollout(child).entry_names == {"child"}
    with pytest.raises(rc.RolloutReadError):
        rc.read_rollout(malformed_child)


@pytest.mark.parametrize("checkpoint", ["matching", "mismatched", "empty", "unrelated"])
def test_fresh_compaction_catalog_requires_matching_typed_checkpoint(tmp_path, checkpoint):
    text = full(entry("replacement"))
    replacement = typed_message(LATEST, text)["payload"]
    body = text.removeprefix("<skills_instructions>").removesuffix("</skills_instructions>")
    source_snapshot = {"body": body, "includeInstructions": True}
    if checkpoint == "mismatched":
        source_snapshot["body"] = body.replace("replacement", "different")
    elif checkpoint == "empty":
        source_snapshot = {}
    source = "unrelated" if checkpoint == "unrelated" else "host_skills"
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-fresh-compaction.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        record("compacted", LATEST, message="", replacement_history=[replacement],
               replacement_history_metadata=[{}]),
        record("world_state", LATEST, full=True, state={source: source_snapshot}),
        context(LATEST, cwd=NEW_CWD),
    )

    if checkpoint == "matching":
        observation = rc.read_rollout(path)
        assert observation.entry_names == {"replacement"}
        assert observation.meta.cwd == NEW_CWD
        assert observation.meta.observed_at.startswith("2026-11-03T13:00:00")
        assert observation.meta.cli_version == "unknown"
    else:
        with pytest.raises(rc.RolloutReadError, match="compaction catalog"):
            rc.read_rollout(path)


def test_retained_typed_compaction_catalog_can_never_claim_new_timestamp(tmp_path):
    text = full(entry("previous-turn"))
    replacement = typed_message(LATEST, text)["payload"]
    body = text.removeprefix("<skills_instructions>").removesuffix("</skills_instructions>")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-retained-compaction.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        record("compacted", LATEST, message="", replacement_history=[replacement],
               replacement_history_metadata=[{"history_sequence": 1}]),
        record("world_state", LATEST, full=True, state={
            "host_skills": {"body": body, "includeInstructions": True},
        }),
        context(LATEST),
    )
    with pytest.raises(rc.RolloutReadError, match="compaction catalog"):
        rc.read_rollout(path)


def test_multiple_current_source_catalogs_are_read_together(tmp_path):
    cloud = full("- example:catalog: Cloud skill. (cloud package: c0/catalog)",
                 roots=("- `c0` = `skill://example`",)).replace("## Host skills", "## Cloud skills")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-source-scoped.jsonl",
        header(), message(START, full(entry("original")), cloud), context(START),
        message(LATEST, full(entry("replacement"))), context(LATEST),
    )

    observation = rc.read_rollout(path)
    assert observation.entry_names == {"replacement", "example:catalog"}
    assert observation.meta.catalog_kind == "composed"
    assert observation.absolute_locator("c0/catalog") == "skill://example/catalog"


def test_name_only_catalog_does_not_report_clipped_descriptions(tmp_path):
    listing = full(*(f"- {name}: (file: {ROOT}/{name}/SKILL.md)" for name in ("a", "b", "c")))
    listing = listing.replace("name, description, and", "name and")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-name-only.jsonl",
        header(), message(START, listing), context(START),
    )

    observation = rc.read_rollout(path)
    assert observation.entry_names == {"a", "b", "c"}
    assert rc.clipped_entry_names(observation) == []


def test_malformed_catalog_record_cannot_be_skipped(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-malformed.jsonl",
        header(), message(START, full(entry("original"))), context(START),
    )
    with path.open("a") as file:
        file.write('{"type":"response_item","payload":{"type":"message","role":"developer","content":'
                   '[{"type":"input_text","text":"<skills_instructions>')

    with pytest.raises(rc.RolloutReadError, match="malformed rollout record"):
        rc.read_rollout(path)


@pytest.mark.skipif(shutil.which("zstd") is None, reason="requires zstd")
def test_compressed_rollout_cannot_return_partial_good_catalog(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-corrupt.jsonl",
        header(), message(START, full(entry("original"))), context(START),
    )
    compressed = path.with_suffix(".jsonl.zst")
    subprocess.run(["zstd", "-q", "-o", str(compressed), "--", str(path)], check=True)
    with compressed.open("ab") as file:
        file.write(b"corrupt")
    path.unlink()

    with pytest.raises(rc.RolloutReadError, match="could not be decompressed completely"):
        rc.read_rollout(compressed)


def test_current_typed_catalog_with_missing_timestamp_cannot_use_startup_filename(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-typed-missing-time.jsonl",
        header(), typed_message(None, full(entry("current"))), context(START),
    )
    with pytest.raises(rc.RolloutReadError, match="record timestamp") as failure:
        rc.read_rollout(path)
    assert failure.value.meta.observed_at is None


def test_delta_renames_existing_skill_by_stable_path(tmp_path):
    locator = f"{ROOT}/original/SKILL.md"
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-renamed.jsonl",
        header(), message(START, full(entry("original", locator=locator))), context(START),
        message(LATEST, update(entry("renamed", locator=locator))), context(LATEST),
    )
    assert rc.read_rollout(path).entry_names == {"renamed"}


def test_windows_absolute_catalog_locator_is_supported(tmp_path):
    locator = "C:/Users/example/.agents/skills/current/SKILL.md"
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-windows.jsonl",
        header(), message(START, full(entry("current", locator=locator))), context(START),
    )
    observation = rc.read_rollout(path)
    assert [entry.locator for entry in observation.listing.entries] == [locator]


@pytest.mark.parametrize("format_change", ["wrapper", "source"])
def test_new_typed_catalog_shape_cannot_hide_behind_old_healthy_catalog(tmp_path, format_change):
    changed = full(entry("latest"))
    if format_change == "wrapper":
        changed = changed.replace("skills_instructions", "skill_catalog")
    else:
        changed = changed.replace("## Host skills", "## Remote skills")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-new-format.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        typed_message(LATEST, changed), context(LATEST, cwd=NEW_CWD),
    )
    with pytest.raises(ValueError, match="unsupported") as failure:
        rc.read_rollout(path)
    assert failure.value.meta.cwd == NEW_CWD
    assert failure.value.meta.observed_at.startswith("2026-11-03T13:00:00")


@pytest.mark.parametrize("with_full_recovery", [False, True])
def test_rollback_invalidates_delta_basis_until_fresh_full_catalog(tmp_path, with_full_recovery):
    recovery = [message(LATEST, full(entry("restored"))), context(LATEST)] if with_full_recovery else []
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-rolled-back.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        message(MIDDLE, update(entry("discarded"))), context(MIDDLE),
        record("event_msg", LATEST, type="thread_rolled_back", num_turns=1),
        *recovery,
        message(LATEST, update(entry("retained"))), context(LATEST),
    )
    if with_full_recovery:
        assert rc.read_rollout(path).entry_names == {"restored", "retained"}
    else:
        with pytest.raises(ValueError, match="no verified full listing"):
            rc.read_rollout(path)


@pytest.mark.parametrize("context_records", [
    (),
    (context(LATEST, cwd="", model="m"),),
    (context(LATEST, cwd=NEW_CWD, model=None),),
    (context(LATEST, cwd="relative"),),
    ({"type": "turn_context", "timestamp": LATEST, "payload": None},),
])
def test_incomplete_resumed_catalog_cannot_borrow_startup_scope(tmp_path, context_records):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-incomplete-context.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        typed_message(LATEST, full(entry("newer"))), *context_records,
    )
    for scope in (CWD, NEW_CWD):
        errors = []
        assert rc.observations(tmp_path, cwd=scope, evidence_errors=errors) == []
        assert len(errors) == 1
        assert errors[0].meta.path == path
        assert errors[0].meta.cwd == ""
        assert errors[0].meta.observed_at.startswith("2026-11-03T13:00:00")
        assert "turn context" in str(errors[0])


def test_simultaneous_source_catalogs_are_an_estimate(tmp_path):
    cloud = full("- example:catalog: Cloud skill. (cloud package: skill://example/catalog)")
    cloud = cloud.replace("## Host skills", "## Cloud skills")
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-estimated-total.jsonl",
        header(), message(START, full(entry("host")), cloud), context(START),
    )
    observation = rc.read_rollout(path)
    assert observation.entry_names == {"host", "example:catalog"}
    assert observation.meta.catalog_kind == "composed"
    assert rc.derive_limit([observation], clipped_only=False).samples == ()


def test_name_only_catalog_with_normal_description_intro_reports_clipping(tmp_path):
    names = ("alpha", "beta", "gamma")
    listing = full(*(f"- {name}: (file: {ROOT}/{name}/SKILL.md)" for name in names))
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-clipped-to-name-only.jsonl",
        header(), message(START, listing), context(START),
    )
    assert rc.clipped_entry_names(rc.read_rollout(path)) == list(names)


def test_malformed_serialized_context_does_not_borrow_later_turn(tmp_path):
    path = write(
        tmp_path / "rollout-2026-11-01T13-00-00-damaged-context.jsonl",
        header(), message(START, full(entry("original"))), context(START),
        typed_message(MIDDLE, full(entry("newer"))),
    )
    with path.open("a", encoding="utf-8") as file:
        file.write('{"type": "turn_context", "payload":\n')
        file.write(json.dumps(context(LATEST, cwd=NEW_CWD)) + "\n")
    with pytest.raises(rc.RolloutReadError, match="turn context") as failure:
        rc.read_rollout(path)
    assert failure.value.meta.cwd == ""
    assert failure.value.meta.observed_at.startswith("2026-11-02T13:00:00")
