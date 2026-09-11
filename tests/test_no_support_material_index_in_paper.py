from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
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


def test_skeleton_places_filename_table_before_question_code() -> None:
    appendix = appendix_from_skeleton()
    # 文件名称三线表必须是附录 A，代码必须是附录 B。
    a = appendix.index("### 附录 A 文件名称表")
    b = appendix.index("### 附录 B 问题求解代码")
    assert a < b
    table = appendix[a:b]
    assert "| 文件名称 | 文件说明 |" in table
    for border in ("顶线", "表头下横线", "底线", "无竖线", "逐行横线"):
        assert border in table
    assert "实际交付" in table and "不虚构文件" in table


def test_appendix_has_per_question_code_and_conditional_q4() -> None:
    appendix = appendix_from_skeleton()
    titles = (
        "#### B.1 Q1（问题一）代码",
        "#### B.2 Q2（问题二）代码",
        "#### B.3 Q3（问题三）代码",
        "#### B.4 Q4（问题四）代码",
    )
    positions = [appendix.index(title) for title in titles]
    assert positions == sorted(positions)
    assert "仅当题目包含 Q4 时保留" in appendix
    assert "无 Q4 时删除本节标题、说明和占位内容" in appendix
    for i, start in enumerate(positions):
        section = appendix[start:positions[i + 1]] if i + 1 < len(positions) else appendix[start:]
        assert "文件名称：与附录 A 一致" in section
        assert "可复制文本" in section and "不使用代码截图" in section
    assert "### B. 补充结果" not in appendix


def test_writer_allows_delivery_filenames_but_keeps_internal_evidence_external() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    assert "文件名称表是论文的正式内容" in writer
    assert "内部工作表和审计材料中登记" in writer
    assert "论文之外的内部交付清单" in writer
    assert "不得列出完整程序文件名" not in writer
    for marker in INTERNAL_ARTIFACT_MARKERS:
        assert marker in writer
    reference = read("cumcm-live-paper-writer/references/appendix-structure.md")
    assert "多个小问共用同一文件时只列一行" in reference
    assert "不能因为默认模板只有三问而漏掉实际第四问" in reference
    assert "现有静态脚本不自动验证" in reference


def test_layout_and_audit_keep_valid_filename_table_and_all_question_code() -> None:
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")
    for document in (layout, auditor):
        assert "附录 A 文件名称表" in document
        assert "附录 B" in document and "Q4" in document
        assert "顶线" in document and "表头下横线" in document and "底线" in document
        assert "BLOCKED_APPENDIX_CODE/P0" in document
        assert "敏感信息" in document and "P0" in document
    assert "保留有效的附录 A 文件名称表" in layout
    assert "有效的文件名称表不能因此删除" in auditor


def test_reports_record_table_question_coverage_and_internal_index_boundary() -> None:
    paths = (
        "cumcm-live-layout-verifier/assets/layout-report.md",
        "cumcm-live-final-auditor/assets/audit-report-template.md",
    )
    for path in paths:
        report = read(path)
        assert "附录 A 文件名称三线表" in report
        assert "附录 B" in report and "Q4" in report
        assert "appendix_file_table_pdf_page" in report
        assert "appendix_question_pages" in report
    audit_report = read(paths[1])
    assert "## 论文附录内部索引排除核对" in audit_report
    assert "论文外部保存位置" in audit_report and "PASS/P1/P0" in audit_report
    assert "不含有效的附录 A 文件名称表" in audit_report


def test_public_contracts_state_the_same_ab_structure() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        assert "附录 A 文件名称表 → 附录 B 问题求解代码" in content
        assert "文件名称、文件说明" in content and "两列三线表" in content
        assert "有 Q4 时增加 Q4，无 Q4 时删除该节" in content
        assert "论文外部" in content
        assert "AI 使用披露仍按当届官方规则单独处理" in content


def test_existing_appendix_and_ai_gates_remain() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    assert "附录必须收录实际参与最终模型" in writer
    assert "可复制文本" in writer and "不使用截图" in writer
    assert "## AI 使用记录" in skeleton and "按当届官方规则决定" in skeleton
    assert "26–30 页" in skeleton and "三线表" in skeleton
    assert "VS-CODE-LIGHT-PLUS" in skeleton
