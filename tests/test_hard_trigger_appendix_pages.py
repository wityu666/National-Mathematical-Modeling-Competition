from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_page_gate_has_explicit_blocking_states_across_pipeline() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")

    for content in (writer, layout, auditor):
        # 锁：页数边界缺失与正文越界必须使用不同的显式阻断状态。
        assert "BLOCKED_PAGE_BOUNDARY" in content
        assert "BLOCKED_PAGE_RANGE" in content
    # 锁：排版预检不得再把未核验页数当作可通过结果。
    assert "`UNVERIFIED`" in layout and "退出码 1" in layout


def test_appendix_key_model_code_has_hard_blocking_state() -> None:
    paths = (
        "cumcm-live-paper-writer/SKILL.md",
        "cumcm-live-layout-verifier/SKILL.md",
        "cumcm-live-final-auditor/SKILL.md",
        "README.md",
        "SUITE.md",
    )
    for path in paths:
        content = read(path)
        # 锁：附录主要建模代码缺失或未核验时必须阻断全链路。
        assert "BLOCKED_APPENDIX_CODE" in content, path


def test_layout_preflight_requires_appendix_code_page_locator() -> None:
    script = read("cumcm-live-layout-verifier/scripts/layout_preflight.py")
    skill = read("cumcm-live-layout-verifier/SKILL.md")

    # 锁：CLI 必须要求操作者登记主要建模代码的 PDF 物理页。
    assert '"--appendix-code-page"' in script
    assert "--appendix-code-page 31" in skill
    # 锁：缺少正文边界与附录代码页必须产生稳定的 P0 问题码。
    assert '"page-limit-unverified"' in script
    assert '"appendix-key-model-code-unverified"' in script


def test_reports_record_page_and_appendix_code_evidence() -> None:
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    for content in (layout_report, audit_report, skeleton):
        # 锁：每个交接表都必须记录附录主要代码的物理页，而非仅口头确认。
        assert "appendix_code_pdf_page" in content
        # 锁：报告必须保留正文边界缺失与越界的状态码。
        assert "BLOCKED_PAGE_BOUNDARY" in content
        assert "BLOCKED_PAGE_RANGE" in content


def test_skill_descriptions_expose_page_and_appendix_triggers() -> None:
    skill_roots = (
        "cumcm-live-paper-writer",
        "cumcm-live-layout-verifier",
        "cumcm-live-final-auditor",
    )
    for root in skill_roots:
        skill = read(f"{root}/SKILL.md").splitlines()[2]
        agent = read(f"{root}/agents/openai.yaml")
        # 锁：自动路由描述必须显式暴露页数硬门，避免只在正文深处出现。
        assert "26–30 页" in skill
        # 锁：三个对外入口都必须让用户看到附录主要建模代码要求。
        assert "附录主要建模代码" in skill
        assert "附录" in agent and "页" in agent
