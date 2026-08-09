from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
OVERVIEW_FIGURE_ID = "FIG-OVERVIEW-001"
EXPECTED_QUESTION_MARKERS = ("Q1", "Q2", "Q3")
OVERVIEW_CHAIN_GATES = (
    ("输入", "数据", "上问产物"),
    ("关键处理", "假设"),
    ("模型", "数学构造"),
    ("算法", "求解器"),
    ("真实检验", "验证"),
    ("输出", "答案", "交付"),
)
ALLOWED_STRUCTURE_MARKERS = ("单链式", "多面板", "共用主干＋分问分支")


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def section_between(content: str, start: str, end: str) -> str:
    return content.split(start, 1)[1].split(end, 1)[0]


def test_skeleton_places_overview_diagram_after_question_analysis() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    analysis = section_between(skeleton, "## 二、问题分析", "## 三、模型假设")

    # 锁：总体思路图必须位于问题分析末尾而不是埋入某一问的主体章节。
    assert analysis.index("### 2.3 问题三") < analysis.index("### 2.4 总体思路图")
    # 锁：总体思路图必须使用稳定图号以接入图源和冻结证据链。
    assert OVERVIEW_FIGURE_ID in analysis
    for question in EXPECTED_QUESTION_MARKERS:
        # 锁：骨架中的总体思路图内容门必须覆盖三个实际小问。
        assert question in analysis


def test_overview_diagram_preserves_full_solution_chain() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    combined = skeleton + paper_skill

    for equivalent_markers in OVERVIEW_CHAIN_GATES:
        # 锁：总体思路图不能退化为只写模型名的空流程图。
        assert any(marker in combined for marker in equivalent_markers)
    # 锁：问间共享模块和传递接口必须显式表达。
    assert "共享模块" in combined and "传递变量/文件" in combined
    # 锁：相互独立的问题也必须明确标注而不是虚构依赖箭头。
    assert "相互独立时" in combined or "各问相互独立时" in combined


def test_structure_is_selected_from_real_dependencies_not_fixed_template() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    for marker in ALLOWED_STRUCTURE_MARKERS:
        # 锁：高依赖、低依赖和共享主干三类题都必须有合适的结构选择。
        assert marker in skeleton or marker in playbook
    # 锁：图的排列与连接方式必须由本队真实合同决定，不能形成新模板指纹。
    assert "不得机械套用固定版式" in skeleton
    # 锁：参考论文和示例图片的成套布局不得被复制到最终成稿。
    assert "不得照抄参考论文、示例图片" in skeleton


def test_overview_diagram_is_traceable_and_not_result_evidence() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    for content in (paper_skill, playbook):
        # 锁：总体思路图必须绑定可编辑源和生成入口，不能只保存不可维护截图。
        assert "可编辑源" in content and (
            "生成命令" in content or "生成入口" in content
        )
        # 锁：总体思路图必须绑定冻结版本，避免图与正文版本漂移。
        assert "冻结版本" in content
    # 锁：导航图不得替代结果证据或亮点专门证明产物。
    assert "不能被当作结果证据" in paper_skill
    assert "不得被当作结果证据" in playbook


def test_visual_rules_keep_palette_consistent_and_diagram_readable() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )
    combined = paper_skill + playbook

    # 锁：总体思路图必须沿用全文冻结的配色和对象映射。
    assert "palette_set" in combined and "object_color_map" in combined
    # 锁：流程图必须保留颜色之外的冗余编码。
    assert "颜色不是唯一" in combined or "颜色必须辅以" in combined
    # 锁：总体思路图优先保留矢量输出以确保小字和箭头清晰。
    assert "PDF/SVG" in combined and "矢量" in combined
    # 锁：最终插入尺寸下的中文文字必须满足既有可读性底线。
    assert "8 pt" in combined


def test_layout_and_final_audit_gate_the_overview_diagram() -> None:
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    for content in (layout_skill, layout_report, auditor_skill, audit_report):
        # 锁：写作后的排版和终审链都必须识别同一总体思路图。
        assert OVERVIEW_FIGURE_ID in content
    # 锁：排版报告必须记录总体思路图的 Word/PDF 一致性证据。
    assert "Word/PDF" in layout_report and "总体思路图" in layout_report
    # 锁：终审必须区分一般缺图与图义造假的 P1/P0 级别。
    assert "缺图或漏掉任一小问按 `P1`" in auditor_skill
    assert "虚构依赖" in auditor_skill and "按 `P0`" in auditor_skill
    # 锁：终审报告必须提供可逐项填写的总体思路图审计表。
    assert "## 总体思路图审计" in audit_report


def test_public_rules_and_existing_gates_remain() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    question_body = section_between(
        skeleton,
        "## 六、问题一的建立与求解",
        "## 九、模型评估改进与推广",
    )

    for content in (readme, suite):
        # 锁：公开入口必须让下载套件的队伍知道总体思路图是必做项。
        assert OVERVIEW_FIGURE_ID in content and "总体思路图" in content
        # 锁：公开入口必须禁止用空框或放大图片进行内容注水。
        assert "通用空框" in content and "凑页数" in content
    # 锁：新增总体思路图不得放宽 26–30 页内部质量门。
    assert "26–30 页" in skeleton
    # 锁：新增总体思路图不得削弱模板去指纹禁令。
    assert "不得照抄" in skeleton and "固定版式" in skeleton
    # 锁：新增总体思路图不得取代三问七项内容门。
    assert question_body.count("| 模型或数学构造 |") == 3
    assert question_body.count("| 真实检验 |") == 3
