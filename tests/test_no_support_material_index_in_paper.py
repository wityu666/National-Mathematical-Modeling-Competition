from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
BANNED_PAPER_SECTION_TITLES = (
    "### A. 支撑材料清单",
    "完整程序与支撑材料索引",
    "运行与完整工程说明",
)
INTERNAL_ARTIFACT_MARKERS = (
    "冻结清单",
    "验证报告",
    "事实追踪表",
    "图形注册表",
)


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def appendix_from_skeleton() -> str:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    return skeleton.split("## 附录", 1)[1].split("## 提交前同步表", 1)[0]


def test_skeleton_omits_support_material_index_section() -> None:
    appendix = appendix_from_skeleton()

    # 锁：提交论文骨架不得重新出现支撑材料清单或完整程序索引标题。
    assert BANNED_PAPER_SECTION_TITLES[0] not in appendix
    assert BANNED_PAPER_SECTION_TITLES[2] not in appendix
    # 锁：禁止项只能作为删除说明出现，不能作为可填写的论文小节。
    assert "不得设置或撰写“完整程序与支撑材料索引”" in appendix


def test_appendix_keeps_key_code_and_supplementary_results() -> None:
    appendix = appendix_from_skeleton()

    # 锁：删除索引不能误删用户要求的关键建模代码附录。
    assert "### A. 关键建模代码" in appendix
    for question in ("问题一", "问题二", "问题三"):
        # 锁：三个小问仍各有关键代码展示位置。
        assert f"{question}关键代码" in appendix
    # 锁：附录仍允许承载确有复核价值的补充结果。
    assert "### B. 补充结果" in appendix


def test_writer_separates_paper_from_internal_audit_artifacts() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")

    # 锁：写作技能必须直接禁止生成截图所示索引章节。
    assert "提交论文不得设置或撰写“完整程序与支撑材料索引”" in writer
    # 锁：内部证据链仍须保留在论文外，而不是因删节而丢失。
    assert "内部工作表和审计材料中登记" in writer
    assert "论文之外的内部交付清单" in writer
    for marker in INTERNAL_ARTIFACT_MARKERS:
        # 锁：各类内部工程产物都必须被纳入论文外保存规则。
        assert marker in writer


def test_layout_and_final_audit_block_visible_internal_index() -> None:
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")

    # 锁：排版复核发现索引后必须退回删除，不能仅提示。
    assert "命中时记为 `P1` 并退回删除" in layout
    # 锁：终审区分普通内部索引和敏感信息泄露的 P1/P0。
    assert "论文中出现时按 `P1` 处理并删除" in auditor
    assert "敏感信息则按 `P0` 处理" in auditor
    # 锁：关键代码与官方 AI 披露不能被索引禁令误删。
    assert "关键建模代码附录和官方要求的 AI 披露不因此删除" in auditor


def test_reports_have_an_explicit_index_exclusion_gate() -> None:
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：排版报告必须留下 Word/PDF 附录排除检查证据。
    assert "附录索引排除检查" in layout_report
    assert "论文附录不含完整程序与支撑材料索引" in layout_report
    # 锁：终审报告必须单独登记禁止项、外部保存位置和风险分级。
    assert "## 论文附录内部索引排除核对" in audit_report
    assert "论文外部保存位置" in audit_report
    assert "PASS/P1/P0" in audit_report


def test_public_contracts_state_the_same_boundary() -> None:
    for relative_path in ("README.md", "SUITE.md"):
        content = read(relative_path)
        # 锁：下载者必须从两个公开入口都看到论文与内部清单的边界。
        assert "提交论文附录只保留关键建模代码和必要补充结果" in content
        assert "不写“完整程序与支撑材料索引”" in content
        assert "论文外部" in content
        # 锁：删除索引不得削弱按官方规则维护 AI 披露的要求。
        assert "AI 使用披露仍按当届官方规则单独处理" in content


def test_existing_appendix_and_ai_gates_remain() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：关键建模代码仍是附录硬门，不能因去除索引而降级。
    assert "附录必须收录实际参与最终模型" in writer
    assert "可复制文本" in writer and "不使用截图" in writer
    # 锁：AI 使用记录节仍然存在并继续服从官方规则。
    assert "## AI 使用记录" in skeleton
    assert "按当届官方规则决定" in skeleton
    # 锁：正文页数与关键代码等既有门禁保持不变。
    assert "26–30 页" in skeleton and "三线表" in skeleton
