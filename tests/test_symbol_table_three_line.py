from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
THREE_RULE_NAMES = ("顶线", "表头下横线", "底线")
FORBIDDEN_GRID_MARKERS = ("竖线", "逐行横线", "全边框")
SYMBOL_COLUMNS = ("符号", "含义", "单位", "取值范围/类型", "首次出现位置")


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def symbol_section(skeleton: str) -> str:
    return skeleton.split("## 四、符号说明", 1)[1].split(
        "## 五、数据收集与预处理", 1
    )[0]


def test_skeleton_requires_a_three_line_symbol_table() -> None:
    section = symbol_section(
        read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    )

    # 锁：符号说明的最终版式必须明确命名为三线表。
    assert "必须排成三线表" in section
    for rule in THREE_RULE_NAMES:
        # 锁：三线表必须同时保留顶线、表头分隔线和底线。
        assert rule in section
    for marker in FORBIDDEN_GRID_MARKERS:
        # 锁：符号表不得退化为带竖线或逐行横线的全网格表。
        assert marker in section
    # 锁：Markdown 内容占位符的管道符不能被误解为最终版竖线。
    assert "当前 Markdown 竖线仅用于表示内容列" in section


def test_symbol_content_columns_and_location_are_preserved() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    section = symbol_section(skeleton)

    for column in SYMBOL_COLUMNS:
        # 锁：改成三线表不能删除符号表的任何既有内容字段。
        assert column in section
    # 锁：符号说明仍须位于模型假设之后、数据章节之前。
    assert skeleton.index("## 三、模型假设") < skeleton.index(
        "## 四、符号说明"
    ) < skeleton.index("## 五、数据收集与预处理")
    # 锁：符号说明仍然属于正文，不能借排版调整移入附录。
    assert "不得把完整符号表移到附录" in section


def test_paper_writer_specifies_word_and_latex_implementation() -> None:
    skill = read("cumcm-live-paper-writer/SKILL.md")

    # 锁：Word 路线必须通过表格边框精确设置三条线。
    assert "Word 路线用表格边框精确设置这三条线" in skill
    for command in (r"\toprule", r"\midrule", r"\bottomrule"):
        # 锁：LaTeX 路线必须提供标准三线表命令或等价实现。
        assert command in skill
    # 锁：LaTeX 不得用竖线列格式或逐行 hline 伪装三线表。
    assert "列格式中不得加入竖线" in skill
    assert "逐行" in skill and r"\hline" in skill
    # 锁：三线表未修复时 paper-writer 不得宣告完成。
    assert "未按三线表修复时状态为 `BLOCKED`" in skill


def test_layout_verifier_checks_real_three_line_rendering() -> None:
    skill = read("cumcm-live-layout-verifier/SKILL.md")
    protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )
    report = read("cumcm-live-layout-verifier/assets/layout-report.md")

    for content in (skill, protocol, report):
        # 锁：排版角色及其报告必须显式识别符号说明三线表。
        assert "三线表" in content
        # 锁：排版复核必须检查竖线和逐行横线是否被清除。
        assert "竖线" in content and "逐行横线" in content
        # 锁：跨页符号表必须重复表头，不能因三线表要求丢失表头。
        assert "跨页" in content and "表头" in content
    # 锁：排版报告必须留下 Word/PDF 实际页面证据位置。
    assert "Word-PDF 一致性" in report and "页码/截图" in report


def test_final_auditor_blocks_non_three_line_symbol_table() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    for content in (skill, protocol, report):
        # 锁：终审链必须保留符号说明三线表硬门。
        assert "三线表" in content
    # 锁：非三线表属于会阻止 PASS 的 P1，而非可忽略建议。
    assert "未采用三线表按 `P1` 处理，修复前不得 `PASS`" in skill
    # 锁：终审报告必须核对三条线和被禁止的网格线。
    assert all(rule in report for rule in THREE_RULE_NAMES)
    assert "无竖线/逐行横线" in report
    # 锁：最终签核必须单独确认符号说明三线表。
    assert "正文符号说明采用三线表" in report


def test_public_contract_and_existing_gates_remain() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        # 锁：下载者必须从公共入口知道符号说明采用三线表。
        assert "正文“符号说明”必须使用三线表" in content
        # 锁：公共规则必须明确三条线与禁用竖线。
        assert all(rule in content for rule in THREE_RULE_NAMES)
        assert "不使用竖线" in content

    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    # 锁：新增三线表门不能放宽正文 26–30 页区间。
    assert "26–30 页" in skeleton
    # 锁：新增三线表门不能删除总体思路图要求。
    assert "FIG-OVERVIEW-001" in skeleton
    # 锁：新增三线表门不能删除三问真实检验内容门。
    assert skeleton.count("| 真实检验 |") == 3
