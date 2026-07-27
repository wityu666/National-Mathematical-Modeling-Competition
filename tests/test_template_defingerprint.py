from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_content_gates_remain_after_sentence_template_removal() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    patterns = read(
        "cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"
    )

    for content in (skeleton, patterns):
        for keyword in ("数据", "处理", "模型", "求解", "结果", "验证"):
            assert keyword in content
    assert "第一屏至少放一条 CONTRIB-PROVEN" in skeleton
    assert "24" in skeleton
    assert "30 页" in skeleton


def test_literal_abstract_sentence_skeleton_is_removed() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    assert "针对问题一，基于" not in skeleton
    assert "只规定必须写什么，不规定句式" in skeleton
    assert "开头语、句序、连接方式" in skeleton


def test_standard_paper_section_names_are_preserved() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    standard_sections = (
        "## 一、问题重述",
        "## 二、问题分析",
        "## 三、模型假设",
        "## 四、符号说明",
        "模型建立与求解",
        "检验",
        "## 九、模型评价与改进",
        "## 参考文献",
        "## 附录",
    )

    for section in standard_sections:
        assert section in skeleton


def test_arrow_specs_are_labeled_as_content_not_copyable_sentences() -> None:
    patterns = read(
        "cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"
    )
    evidence = read(
        "cumcm-live-paper-writer/references/evidence-driven-writing-playbook.md"
    )

    for content in (patterns, evidence):
        assert "内容规格" in content
        assert "不得逐字沿用" in content
    assert "不得沿用该示例的句式结构" in evidence


def test_plot_styles_offer_explicit_multiple_palette_sets() -> None:
    python_style = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    matlab_style = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    for palette_set in ("SET-A", "SET-B", "SET-C", "SET-D"):
        assert palette_set in python_style
        assert palette_set in matlab_style
        assert palette_set in playbook
    for content in (python_style, matlab_style):
        assert "palette_set" in content or "paletteSet" in content
    assert "def apply_cumcm_style(palette_set: str" in python_style
    assert "PaletteRequired" in matlab_style
    assert "不指定唯一默认" in playbook
    assert "同一篇论文只能使用这一组" in playbook


def test_figure_accessibility_and_color_map_guards_remain() -> None:
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    assert "灰度打印" in playbook
    assert "色觉缺陷" in playbook
    assert "颜色仍不得作为唯一编码" in playbook
    assert "禁止 `jet`、彩虹" in playbook


def test_final_auditor_has_template_fingerprint_gate() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    assert "## 5. 模板指纹审计" in skill
    assert "P0" in skill and "P1" in skill
    assert "指纹短语清单" in protocol
    assert "template_fingerprint_checked" in protocol
    assert "template_fingerprint_checked" in report


def test_suite_declares_substantive_differentiation() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        assert "分化必须来自实质" in content
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
            assert fragment not in content, (path, fragment)
