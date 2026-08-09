from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
OPTIONAL_CHART_TYPES = ("扇形图", "水平条形图", "折线图", "竖向柱形图")
OPTIONALITY_MARKERS = ("允许其中几种或全部不出现", "不要求全部出现", "允许有几种或全部不出现")
NO_PENALTY_MARKERS = (
    "不构成缺陷",
    "不得判为 `P0/P1`",
    "不因缺少图型判错",
    "不视为缺陷",
    "未出现某种图不判错",
)
PYTHON_DRAW_CALLS = ("ax.pie(", "ax.barh(", "ax.plot(", "ax.bar(")
MATLAB_DRAW_CALLS = ("`pie`", "`barh`", "`plot`", "`bar`")


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_paper_writer_exposes_optional_basic_chart_library() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    for chart_type in OPTIONAL_CHART_TYPES:
        # 锁：写作入口和图表手册都必须明确提供四类基础候选图型。
        assert chart_type in paper_skill and chart_type in playbook
    # 锁：候选图型库不能退化为要求论文逐类打卡的强制清单。
    assert any(marker in paper_skill for marker in OPTIONALITY_MARKERS)
    assert "不是论文图型清单" in playbook


def test_each_basic_chart_type_keeps_its_task_semantics() -> None:
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )

    # 锁：扇形图只能服务于类别较少且总量有意义的部分—整体关系。
    assert "部分—整体" in playbook and "5–6" in playbook and "非负" in playbook
    # 锁：水平条形图必须用于排序或长标签等横向比较任务。
    assert "水平条形图" in playbook and "排序" in playbook and "长标签" in playbook
    # 锁：折线图只能连接真正有序的横轴，不能制造虚假趋势。
    assert "折线图只连接" in playbook and "真正有序" in playbook
    # 锁：竖向柱形图必须保留零基线门禁。
    assert "竖向柱形图的数值轴原则上从零起" in playbook


def test_python_and_matlab_recipes_implement_all_optional_types() -> None:
    python_recipe = read(
        "cumcm-live-python-coder/references/python-figure-recipes.md"
    )
    matlab_recipe = read(
        "cumcm-live-matlab-coder/references/matlab-figure-recipes.md"
    )

    for draw_call in PYTHON_DRAW_CALLS:
        # 锁：Python 配方必须给出四类基础图型的可执行绘制入口。
        assert draw_call in python_recipe
    for draw_call in MATLAB_DRAW_CALLS:
        # 锁：MATLAB 配方必须给出与 Python 对应的四类绘制入口。
        assert draw_call in matlab_recipe
    # 锁：测试只读取配方文本，不导入 Matplotlib 或 MATLAB 运行时。
    import_lines = [
        line.strip()
        for line in Path(__file__).read_text(encoding="utf-8").splitlines()
        if line.startswith(("import ", "from "))
    ]
    assert all("matplotlib" not in line.lower() for line in import_lines)


def test_coders_do_not_autofill_missing_chart_types() -> None:
    coder_paths = (
        "cumcm-live-python-coder/SKILL.md",
        "cumcm-live-matlab-coder/SKILL.md",
        "cumcm-live-python-coder/references/python-figure-recipes.md",
        "cumcm-live-matlab-coder/references/matlab-figure-recipes.md",
    )

    for relative_path in coder_paths:
        content = read(relative_path)
        # 锁：两条编码路线都必须允许不适用图型缺席，禁止自动补图。
        assert any(marker in content for marker in OPTIONALITY_MARKERS), relative_path
        assert "不得" in content and ("补图" in content or "造图" in content), relative_path


def test_run_manifests_capture_task_and_chart_choice_without_coverage_quota() -> None:
    manifest_paths = (
        "cumcm-live-python-coder/assets/run-manifest.md",
        "cumcm-live-matlab-coder/assets/run-manifest.md",
    )

    for relative_path in manifest_paths:
        manifest = read(relative_path)
        # 锁：每张实际图必须登记分析任务和图型选择理由。
        assert "分析任务" in manifest and "图型及选择理由" in manifest
        # 锁：未使用的候选图型可明确记为不适用，不得按失败处理。
        assert "NOT_APPLICABLE" in manifest and "不要求全部出现" in manifest


def test_layout_and_final_audit_ignore_absent_types_but_gate_bad_choices() -> None:
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：排版复核不能因为某种候选图未出现就制造 P0/P1。
    assert any(marker in layout_skill for marker in NO_PENALTY_MARKERS)
    # 锁：终审必须区分一般选型错误与导致结论失真的严重错误。
    assert "不适配任务" in auditor_skill and "按 `P1`" in auditor_skill
    assert "导致结论失真时按 `P0`" in auditor_skill
    # 锁：终审报告必须能把每种候选图记录为 NOT_APPLICABLE。
    assert "## 图型选择审计" in audit_report
    assert audit_report.count("NOT_APPLICABLE") >= 5


def test_public_rules_state_optional_types_and_no_padding() -> None:
    for relative_path in ("README.md", "SUITE.md"):
        content = read(relative_path)
        for chart_type in OPTIONAL_CHART_TYPES:
            # 锁：公开入口必须告知下载者可用的基础候选图型。
            assert chart_type in content, relative_path
        # 锁：公开规则必须明确缺少某种图不扣分且不允许为丰富或页数造图。
        assert any(marker in content for marker in NO_PENALTY_MARKERS), relative_path
        assert "凑" in content and "装饰图" in content, relative_path


def test_existing_palette_and_anti_padding_gates_remain() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    combined = paper_skill + skeleton

    # 锁：扩展图型后仍由一个 palette_set 和一个对象映射约束全文视觉系统。
    assert "palette_set" in combined and "object_color_map" in combined
    # 锁：扩展图型不得放宽既有正文页数区间与反注水门禁。
    assert "26–30 页" in combined and "反注水" in paper_skill
    # 锁：总体思路图和三线符号表等既有版式内容门不能被图型改动覆盖。
    assert "FIG-OVERVIEW-001" in combined and "三线表" in combined
