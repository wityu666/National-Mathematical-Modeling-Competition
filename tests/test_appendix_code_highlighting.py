from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
THEME_NAME = "VS-CODE-LIGHT-MUTED"
SEMANTIC_ROLES = (
    "关键字、控制语句与内置类型",
    "函数与方法名",
    "类名与装饰器",
    "字符串与路径字面量",
    "注释",
    "数值与常量",
)
THEME_COLORS = {
    "#1F2328",
    "#264F78",
    "#795E26",
    "#7A3E9D",
    "#A31515",
    "#2E7D32",
    "#098658",
    "#6B7280",
    "#FFFFFF",
    "#D1D5DB",
}


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_appendix_code_theme_defines_semantic_multicolor_contract() -> None:
    reference = read(
        "cumcm-live-paper-writer/references/appendix-code-highlighting.md"
    )

    # 锁：附录代码必须使用一套可登记、可复核的统一浅色主题。
    assert f"code_theme={THEME_NAME}" in reference
    for role in SEMANTIC_ROLES:
        # 锁：多色高亮必须按代码语义角色映射，不能逐行任意配色。
        assert role in reference
    for color in THEME_COLORS:
        # 锁：冻结主题的字体、背景和边框色值必须完整可复现。
        assert color in reference
    # 锁：颜色必须有加粗、斜体和语法结构作为灰度冗余。
    assert "关键字加粗" in reference and "注释斜体" in reference
    assert "灰度" in reference and "颜色只是辅助编码" in reference
    # 锁：附录代码主题与数据图表配色是两个独立合同。
    assert "与论文图表的 `palette_set/object_color_map` 相互独立" in reference


def test_writer_and_skeleton_require_editable_highlighted_code() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：写作技能和论文骨架都必须激活统一的附录代码主题。
    assert f"code_theme={THEME_NAME}" in writer
    assert f"code_theme={THEME_NAME}" in skeleton
    # 锁：多色字体不能牺牲代码的复制、编辑和源代码一致性。
    assert "可复制文本" in writer and "纯文本" in writer
    assert "不使用代码截图" in skeleton
    # 锁：Word 路线必须使用真实文本的 token/run 级格式，而不是图片。
    assert "token 级字体颜色" in writer and "run 级格式" in writer
    # 锁：LaTeX 路线必须使用无需 shell escape 的稳定本地方案。
    assert "`listings` 与 `xcolor`" in writer
    assert "不得为了高亮引入 `minted`、shell escape" in writer
    # 锁：官方黑白要求可以覆盖内部彩色偏好，但必须有规则证据。
    assert "MONOCHROME_OFFICIAL_OVERRIDE" in writer
    assert "MONOCHROME_OFFICIAL_OVERRIDE" in skeleton


def test_layout_and_final_audit_verify_code_theme() -> None:
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    layout_protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：排版复核必须检查统一主题、双版本、灰度和复制抽查。
    for document in (layout, layout_protocol, layout_report):
        assert "code_theme" in document
        assert "Word/PDF" in document
        assert "灰度" in document
        assert "复制" in document
    # 锁：终审必须检查代码高亮没有改变冻结源代码且有 P0/P1 分级。
    assert "缺少统一主题" in auditor and "按 `P1` 处理" in auditor
    assert "代码字符变化" in auditor and "按 `P0` 处理" in auditor
    assert "高亮只改变字体格式，不改变任何源代码字符" in auditor
    # 锁：终审协议与报告都必须留存主题和双版本检查证据。
    assert f"code_theme={THEME_NAME}" in audit_protocol
    assert "附录代码主题与字体" in audit_report
    assert "code_theme/Word-PDF/灰度/复制" in audit_report


def test_suite_public_rules_expose_appendix_highlighting_gate() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")

    for document in (readme, suite):
        # 锁：下载者必须从套件入口文档知道附录采用统一多色代码主题。
        assert f"code_theme={THEME_NAME}" in document
        # 锁：套件级规则必须禁止逐块换色、随机配色和代码截图。
        assert "不得逐块换色、随机配色" in document
        assert "代码截图" in document
        # 锁：代码主题不能破坏既有图表 palette_set 合同。
        assert "代码主题与图表 `palette_set` 分开登记" in document


def test_highlighting_does_not_weaken_existing_appendix_and_page_gates() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")

    for document in (writer, layout, auditor):
        # 锁：增加语法高亮后，附录主要建模代码缺失仍必须显式阻塞。
        assert "BLOCKED_APPENDIX_CODE" in document
        # 锁：增加语法高亮后，编号正文 26–30 页硬门仍然存在。
        assert "26–30" in document
    # 锁：附录仍不得重新引入完整程序与支撑材料索引。
    assert "不得设置或撰写“完整程序与支撑材料索引”" in writer
    # 锁：图表 palette_set 仍是全文一致的独立视觉合同。
    assert "palette_set" in writer and "object_color_map" in writer
