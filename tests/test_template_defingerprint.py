from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
CONTENT_SPEC_MARKERS = ("内容规格", "内容要求", "内容门规格")
NO_VERBATIM_COPY_MARKERS = (
    "不得逐字沿用",
    "不得机械复用",
    "不得照抄",
)
SUBSTANTIVE_DIFFERENTIATION_MARKERS = (
    "分化必须来自实质",
    "差异必须来自实质",
    "实质差异而非表层改写",
)


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_content_gates_remain_after_sentence_template_removal() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    patterns = read(
        "cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"
    )

    for content in (skeleton, patterns):
        for keyword in ("数据", "处理", "模型", "求解", "结果", "验证"):
            # 锁：移除句式模板后，摘要五要素和验证内容门不能被削弱。
            assert keyword in content
    # 锁：摘要第一屏必须同时出现已证明亮点及量化证据要求。
    assert all(
        marker in skeleton for marker in ("第一屏", "CONTRIB-PROVEN", "量化")
    )
    # 锁：去指纹改动不能删除正文 24 页下限。
    assert "24" in skeleton
    # 锁：去指纹改动不能删除正文 30 页上限。
    assert "30 页" in skeleton


def test_literal_abstract_sentence_skeleton_is_removed() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：被识别出的统一摘要句式不得继续作为可填写模板出现。
    assert "针对问题一，基于" not in skeleton
    # 锁：摘要骨架必须说明表格只规定内容而不规定句式。
    assert "只规定必须写什么，不规定句式" in skeleton
    # 锁：摘要表达顺序与连接方式必须由本队自行组织。
    assert "开头语、句序、连接方式" in skeleton


def test_standard_paper_section_names_are_preserved() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    standard_sections = (
        "## 一、问题重述",
        "## 二、问题分析",
        "## 三、模型假设",
        "## 四、符号说明",
        "问题一的建立与求解",
        "检验",
        "## 九、模型评估改进与推广",
        "## 参考文献",
        "## 附录",
    )

    for section in standard_sections:
        # 锁：去指纹不得误删或改坏国赛通行章节结构。
        assert section in skeleton


def test_arrow_specs_are_labeled_as_content_not_copyable_sentences() -> None:
    patterns = read(
        "cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"
    )
    evidence = read(
        "cumcm-live-paper-writer/references/evidence-driven-writing-playbook.md"
    )

    for content in (patterns, evidence):
        # 锁：箭头清单必须被标注为内容要求而非可复制句式。
        assert any(marker in content for marker in CONTENT_SPEC_MARKERS)
        # 锁：写作参考必须禁止逐字或机械复制示例表达。
        assert any(marker in content for marker in NO_VERBATIM_COPY_MARKERS)
    # 锁：结果叙事示例的句式结构本身也不得被沿用。
    assert "不得沿用该示例的句式结构" in evidence


def test_plot_styles_offer_explicit_multiple_palette_sets() -> None:
    python_style = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_style = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    for palette_set in ("SET-A", "SET-B", "SET-C", "SET-D", "SET-E", "SET-F"):
        # 锁：Python 样式必须提供全部六组候选配色。
        assert palette_set in python_style
        # 锁：MATLAB 样式必须提供相同六组候选配色。
        assert palette_set in matlab_style
        # 锁：图表手册必须展示相同六组候选配色。
        assert palette_set in playbook
    for content in (python_style, matlab_style):
        # 锁：两种出图资产都必须要求显式选择配色组。
        assert "palette_set" in content or "paletteSet" in content
    # 锁：Python 出图入口必须把 palette_set 作为必传参数。
    assert "def apply_cumcm_style(palette_set: str" in python_style
    # 锁：MATLAB 未选择配色组时必须显式报错。
    assert "PaletteRequired" in matlab_style
    # 锁：图表手册不得把任一组设为唯一默认。
    assert "不指定唯一默认" in playbook
    # 锁：同一论文必须固定使用已选配色组。
    assert "同一篇论文只能使用这一组" in playbook


def test_figure_accessibility_and_color_map_guards_remain() -> None:
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    # 锁：图表手册必须要求灰度打印可辨。
    assert "灰度打印" in playbook
    # 锁：图表手册必须要求色觉缺陷条件下可辨。
    assert "色觉缺陷" in playbook
    # 锁：颜色不得成为唯一信息编码。
    assert "颜色仍不得作为唯一编码" in playbook
    # 锁：学术图必须继续禁止 jet 和彩虹色带。
    assert "禁止 `jet`、彩虹" in playbook


def test_final_auditor_has_template_fingerprint_gate() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：final-auditor 必须保留独立模板指纹审计章节。
    assert "## 5. 模板指纹审计" in skill
    # 锁：模板指纹审计必须保留 P0/P1 两级处置。
    assert "P0" in skill and "P1" in skill
    # 锁：审计协议必须提供可执行的指纹短语清单。
    assert "指纹短语清单" in protocol
    # 锁：审计协议必须包含机器可读的指纹检查字段。
    assert "template_fingerprint_checked" in protocol
    # 锁：审计报告必须记录模板指纹检查结果。
    assert "template_fingerprint_checked" in report


def test_suite_declares_substantive_differentiation() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        # 锁：公开规则必须要求差异来自实质建模与证据。
        assert any(
            marker in content for marker in SUBSTANTIVE_DIFFERENTIATION_MARKERS
        )
        # 锁：公开规则必须禁止用同义词替换伪装差异。
        assert "同义词替换" in content


def test_no_automatic_rewrite_or_palette_randomization_implementation() -> None:
    implementation_files = (
        "cumcm-live-final-auditor/scripts/audit_submission.py",
        "cumcm-live-layout-verifier/scripts/layout_preflight.py",
        "cumcm-live-result-verifier/scripts/compare_runs.py",
        "cumcm-live-python-coder/assets/cumcm_plot_style.py",
        "cumcm-live-matlab-coder/assets/cumcm_plot_style.m",
    )
    forbidden_implementation_fragments = (
        "random.choice(",
        "random.shuffle(",
        "secrets.choice(",
        "shuffle(",
        "randperm(",
        "同义词替换器",
        "同义词映射",
    )

    for path in implementation_files:
        content = read(path)
        for fragment in forbidden_implementation_fragments:
            # 锁：脚本和样式资产不得实现自动改写或随机配色扰动。
            assert fragment not in content, (path, fragment)
