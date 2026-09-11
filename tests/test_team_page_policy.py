import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "cumcm-live-layout-verifier/scripts/layout_preflight.py"


def policy_file(tmp_path, **overrides):
    value = {
        "schema_version": 1, "policy_id": "team-18-24",
        "rationale": "Team declared a shorter body for this problem.",
        "min_main_pages": 18, "max_main_pages": 24,
    }
    value.update(overrides)
    path = tmp_path / "team-policy.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def run_policy(tmp_path, policy, *extra):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(pdf), "--json", "--skip-external-tools",
         "--team-policy", str(policy), *extra],
        capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("minimum,maximum", [(18, 24), (32, 36), (1, 1)])
def test_team_range_overrides_legacy_constants_and_keeps_missing_evidence_blocked(
    tmp_path, minimum, maximum,
):
    path = policy_file(tmp_path, min_main_pages=minimum, max_main_pages=maximum)
    result = run_policy(tmp_path, path)
    report = json.loads(result.stdout)
    assert result.returncode == 1  # missing real PDF/page evidence, not bad policy
    assert report["page_policy"]["selection"] == "team_policy"
    assert report["page_policy"]["source"] == str(path.resolve())
    assert report["page_policy"]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert report["page_limit"]["min_main_pages"] == minimum
    assert report["page_limit"]["max_main_pages"] == maximum
    assert report["visual_qa_required"] is True
    assert report["page_limit"]["status"] == "BLOCKED"
    assert report["appendix_code"]["status"] == "BLOCKED"


@pytest.mark.parametrize("cap,minimum,maximum,disabled", [
    (20, 18, 20, False), (16, 1, 16, True), (40, 18, 24, False),
])
def test_official_cap_takes_priority_and_retains_source(
    tmp_path, cap, minimum, maximum, disabled,
):
    result = run_policy(
        tmp_path, policy_file(tmp_path),
        "--official-max-main-pages", str(cap),
        "--official-page-rule", "Frozen official rules section 2",
    )
    report = json.loads(result.stdout)
    policy = report["page_policy"]
    assert (policy["effective_min_main_pages"], policy["effective_max_main_pages"]) == (
        minimum, maximum,
    )
    assert policy["official_page_rule"] == "Frozen official rules section 2"
    assert policy["internal_floor_disabled_by_official_cap"] is disabled


@pytest.mark.parametrize("extra", [
    ("--min-main-pages", "18"),
    ("--max-main-pages=24",),
    ("--official-max-main-pages", "20"),
    ("--official-max-main-pages", "0", "--official-page-rule", "rules"),
    ("--official-max-main-pages", "20", "--official-page-rule", " "),
    ("--official-page-rule", "rules"),
])
def test_ambiguous_or_unattributed_policy_is_rejected(tmp_path, extra):
    result = run_policy(tmp_path, policy_file(tmp_path), *extra)
    assert result.returncode == 2
    assert result.stdout == ""


@pytest.mark.parametrize("overrides", [
    {"min_main_pages": True}, {"max_main_pages": 24.0},
    {"min_main_pages": 0}, {"min_main_pages": 25},
    {"policy_id": ""}, {"rationale": " "}, {"schema_version": 2},
    {"schema_version": True}, {"unexpected": "ignored would be unsafe"},
])
def test_invalid_policy_fields_are_rejected(tmp_path, overrides):
    result = run_policy(tmp_path, policy_file(tmp_path, **overrides))
    assert result.returncode == 2
    assert result.stdout == ""


@pytest.mark.parametrize("content", ["[]", "{", '{"schema_version":1,"schema_version":1}'])
def test_invalid_json_or_duplicate_keys_are_rejected(tmp_path, content):
    path = tmp_path / "team-policy.json"
    path.write_text(content, encoding="utf-8")
    assert run_policy(tmp_path, path).returncode == 2


def test_missing_policy_file_is_not_silently_replaced_by_defaults(tmp_path):
    result = run_policy(tmp_path, tmp_path / "missing.json")
    assert result.returncode == 2
    assert result.stdout == ""


def test_changed_policy_has_new_fingerprint_and_effective_range(tmp_path):
    path = policy_file(tmp_path)
    first = json.loads(run_policy(tmp_path, path).stdout)["page_policy"]
    policy_file(tmp_path, min_main_pages=20)
    second = json.loads(run_policy(tmp_path, path).stdout)["page_policy"]
    assert first["sha256"] != second["sha256"]
    assert (first["effective_min_main_pages"], second["effective_min_main_pages"]) == (18, 20)
