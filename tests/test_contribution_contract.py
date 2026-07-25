from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_contribution_ledger_has_required_schema_and_guards() -> None:
    ledger = read("cumcm-live-model-designer/assets/contribution-ledger.md")
    required_fields = {
        "contrib_id",
        "claim",
        "baseline_expectation",
        "delta_type",
        "evidence_ids",
        "proof",
        "cost_risk",
        "status",
        "placement",
        "fallback",
    }

    assert required_fields.issubset(set(ledger.split("`")))
    assert "CANDIDATE / PROVEN / DROPPED" in ledger
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in ledger
    assert "无证据即删" in ledger
    assert "可证伪性门" in ledger
    assert "代价强制申报" in ledger


def test_suite_handoff_chain_and_ids_include_contributions() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        assert "contribution_ledger" in content
        assert "CONTRIB-*" in content
        assert "亮点是被证明的差异，不是被主张的复杂度" in content


def test_model_and_pattern_stages_register_differentiation() -> None:
    model_skill = read("cumcm-live-model-designer/SKILL.md")
    model_playbook = read(
        "cumcm-live-model-designer/references/model-design-playbook.md"
    )
    model_contract = read("cumcm-live-model-designer/assets/model-contract.md")
    retriever = read("cumcm-live-case-retriever/SKILL.md")
    atlas = read("cumcm-live-case-retriever/references/model-pattern-atlas.md")

    assert "CONTRIB-CANDIDATE" in model_skill
    assert "contribution_candidates[]" in model_skill
    assert "contribution_candidates[]" in model_playbook
    assert "contribution_candidates[]" in model_contract
    assert "differentiation_hint" in retriever
    assert atlas.count("differentiation_hint") >= 12


def test_coders_require_dedicated_frozen_evidence() -> None:
    for language in ("python", "matlab"):
        skill = read(f"cumcm-live-{language}-coder/SKILL.md")
        manifest = read(f"cumcm-live-{language}-coder/assets/run-manifest.md")

        assert "CONTRIB-PROVEN" in skill
        assert "专门运行产物" in skill
        assert "亮点证明产物" in manifest
        assert "RID/FIG/TAB" in manifest


def test_paper_and_auditor_enforce_proven_only_and_p0() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    paper_refs = [
        read("cumcm-live-paper-writer/references/evidence-driven-writing-playbook.md"),
        read("cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"),
        read("cumcm-live-paper-writer/references/abc-figure-design-playbook.md"),
    ]
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    assert "第一屏" in paper_skill
    assert "CONTRIB-PROVEN" in paper_skill
    assert all("CONTRIB-" in reference for reference in paper_refs)
    assert "亮点真实性" in auditor_skill
    assert "P0" in auditor_skill
    assert "contributions_verified" in audit_protocol


def test_every_question_completeness_gate_is_present() -> None:
    problem_skill = read("cumcm-live-problem-analyst/SKILL.md")
    problem_contract = read("cumcm-live-problem-analyst/assets/problem-contract.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")

    assert "全局配平" in problem_skill
    assert "全局完整性配平" in problem_contract
    assert "每个小问都有可提交的实质答案" in paper_skill


def test_result_verifier_is_integrated_across_the_suite() -> None:
    verifier = read("cumcm-live-result-verifier/SKILL.md")
    report = read("cumcm-live-result-verifier/assets/verification-report.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )
    readme = read("README.md")
    suite = read("SUITE.md")
    python_skill = read("cumcm-live-python-coder/SKILL.md")
    matlab_skill = read("cumcm-live-matlab-coder/SKILL.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")

    assert "cumcm-live-result-verifier" in readme
    assert "result_verifier" in suite
    assert "Round A" in verifier and "Round B" in verifier
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in report
    assert "同一错误重复两次" in protocol
    assert "cumcm-live-result-verifier" in python_skill
    assert "cumcm-live-result-verifier" in matlab_skill
    assert "VER-* PASS" in paper_skill
    assert "VER-* PASS" in auditor


def test_layout_verifier_is_integrated_after_paper_and_before_final_audit() -> None:
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    layout_protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )
    readme = read("README.md")
    suite = read("SUITE.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    assert "cumcm-live-layout-verifier" in readme
    assert suite.index("cumcm-live-paper-writer") < suite.index(
        "cumcm-live-layout-verifier"
    ) < suite.index("cumcm-live-final-auditor")
    assert "PRECHECK_PASS" in layout_skill
    assert "Round A" in layout_skill and "Round B" in layout_skill
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in layout_report
    assert "visual_scope_complete" in layout_protocol
    assert "LAYOUT-* PASS" in paper_skill
    assert "LAYOUT-* PASS" in auditor_skill
    assert "same_hash_layout_pass" in audit_protocol
