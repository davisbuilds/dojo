"""Opt-in tests of the real pinned npm CLI; no fake executable or default network.

Run: DOJO_TEST_DESIGN_MD_CLI=1 uv run --locked pytest tests/test_design_md_cli.py -q
Requires Node/npm; npx may download the pinned package into its normal cache.
"""
import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / 'skills/design-md/scripts/run_cli.sh'
FIXTURES = ROOT / 'tests/fixtures/design_md'
pytestmark = pytest.mark.skipif(
    os.environ.get('DOJO_TEST_DESIGN_MD_CLI') != '1',
    reason='opt-in real npm integration; set DOJO_TEST_DESIGN_MD_CLI=1',
)


def cli(*args, text=None):
    return subprocess.run(['bash', str(WRAPPER), *map(str, args)], input=text,
                          capture_output=True, text=True, timeout=90)


def test_css_variables_accept_modern_colors_preserve_alpha_and_apply_prefix():
    result = cli('export', '--format', 'css-vars', '--prefix', 'demo', FIXTURES / 'modern.md')
    assert result.returncode == 0, result.stderr
    assert ':root {' in result.stdout
    assert '--demo-color-primary: #2784d5' in result.stdout
    assert '--demo-color-overlay: #00000080' in result.stdout


@pytest.mark.parametrize('format', ['json-tailwind', 'css-tailwind', 'dtcg'])
def test_existing_exports_retain_legacy_tokens(format):
    result = cli('export', '--format', format, FIXTURES / 'legacy.md')
    assert result.returncode == 0, result.stderr
    if format == 'css-tailwind':
        assert '@theme' in result.stdout
        assert '#123456' in result.stdout
    else:
        parsed = json.loads(result.stdout)
        assert parsed
        assert '#123456' in result.stdout


def test_omissions_remove_only_applicable_missing_section_findings():
    source = (FIXTURES / 'modern.md').read_text()
    with_omissions = cli('lint', '--format', 'json', '--', '-', text=source)
    assert with_omissions.returncode == 0, with_omissions.stderr
    findings = json.loads(with_omissions.stdout)['findings']
    assert not [f for f in findings if f['rule'] == 'missing-sections']
    without = source[:source.index('omitted:')] + source[source.index('\n---', 4):]
    control = cli('lint', '--format', 'json', '--', '-', text=without)
    control_findings = json.loads(control.stdout)['findings']
    assert any(f['rule'] == 'missing-sections' for f in control_findings)


def test_successful_export_does_not_certify_valid_input(tmp_path):
    invalid = tmp_path / 'invalid.md'
    invalid.write_text('---\ncolors:\n  primary: "not-a-color"\n---\n## Colors\n')
    lint = cli('lint', invalid)
    assert lint.returncode == 1
    assert json.loads(lint.stdout)['summary']['errors'] > 0
    exported = cli('export', '--format', 'json-tailwind', invalid)
    assert exported.returncode == 0, exported.stderr
    assert isinstance(json.loads(exported.stdout), dict)
    missing = cli('lint', tmp_path / 'missing.md')
    assert missing.returncode == 2


def test_diff_reports_token_changes_separately_from_diagnostic_regressions(tmp_path):
    before = FIXTURES / 'legacy.md'
    after = tmp_path / 'after.md'
    after.write_text(before.read_text().replace('#123456', '#234567'))
    changed = cli('diff', before, after)
    assert changed.returncode == 0, changed.stderr
    report = json.loads(changed.stdout)
    assert report['tokens']['colors']['modified']
    assert report['regression'] is False
    after.write_text(before.read_text().replace('{colors.primary}', '{colors.absent}'))
    regression = cli('diff', before, after)
    assert regression.returncode == 1
    assert json.loads(regression.stdout)['findings']['delta']['errors'] > 0
