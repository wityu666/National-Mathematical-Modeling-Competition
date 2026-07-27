from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def section_between(content: str, start: str, end: str) -> str:
    return content.split(start, 1)[1].split(end, 1)[0]


def test_target_top_level_sections_exist_in_order() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    target_sections = (
        "## 摘要",
        "## 关键词",
        "## 一、问题重述",
        "## 二、问题分析",
        "## 三、模型假设",
        "## 四、符号说明",
        "## 五、数据收集与预处理",
        "## 六、问题一的建立与求解",
        "## 七、问题二的建立与求解",
        "## 八、问题三的建立与求解",
        "## 九、模型评估改进与推广",
        "## 参考文献",
        "## 附录",
    )

    positions = [skeleton.index(title) for title in target_sections]
    assert positions == sorted(positions)
    for title in target_sections:
        assert skeleton.count(title) == 1

    assert skeleton.index("## 参考文献") < skeleton.index(
        "## AI 使用记录"
    ) < skeleton.index("## 附录")


def test_required_subsection_titles_exist() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    for title in (
        "### 1.1 问题背景",
        "### 1.2 问题提出",
        "### 9.1 优点",
        "### 9.2 不足",
        "### 9.3 推广",
    ):
        assert title in skeleton
    assert "### 9.4 可执行改进" not in skeleton


def test_data_chapter_has_required_gates_and_flexible_placement() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    chapter = section_between(
        skeleton,
        "## 五、数据收集与预处理",
        "## 六、问题一的建立与求解",
    )

    for gate in ("缺失值处理", "数据清洗与标准化", "数据分析"):
        assert gate in chapter
    for exploration in ("分布", "相关", "异常识别"):
        assert exploration in chapter
    assert "问题专有数据处理就近写" in chapter
    assert "数据来源、统计口径、`DATA-*` 标识与可追溯性要求都不得降低" in chapter


def test_each_question_has_per_question_assumption_gate() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    boundaries = (
        ("## 六、问题一的建立与求解", "## 七、问题二的建立与求解"),
        ("## 七、问题二的建立与求解", "## 八、问题三的建立与求解"),
        ("## 八、问题三的建立与求解", "## 九、模型评估改进与推广"),
    )

    for start, end in boundaries:
        chapter = section_between(skeleton, start, end)
        assert chapter.count("| 本问专有假设 |") == 1
        assert "无本问专有假设" in chapter
    assert "本章集中列出三问共用的全局假设" in skeleton
    assert "不得使用未说明的隐含假设" in skeleton


def test_chapter_equation_numbering_contract_reaches_all_roles() -> None:
    paths = (
        "cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md",
        "cumcm-live-paper-writer/SKILL.md",
        "cumcm-live-final-auditor/SKILL.md",
        "cumcm-live-layout-verifier/SKILL.md",
    )

    for path in paths:
        content = read(path)
        assert "6-1" in content, path
        assert "章号-序号" in content, path
    for path in paths[:3]:
        content = read(path)
        assert "自动" in content, path
        assert "上式" in content and "下式" in content, path


def test_chapter_nine_keeps_contribution_ledger_mappings() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    chapter = section_between(skeleton, "## 九、模型评估改进与推广", "## 参考文献")

    assert "优点只来自当前冻结亮点账本中的 `CONTRIB-PROVEN`" in chapter
    assert "仅使用 delta_type=更好泛化" in chapter
    assert "跨场景/外推证据的 CONTRIB-PROVEN" in chapter
    assert "否则明确“不主张推广”" in chapter
    assert "改进方向来自仍有价值的 `DROPPED` 候选" in chapter


def test_ai_and_internal_work_tables_remain_but_are_not_paper_sections() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    control = section_between(skeleton, "## 成稿控制", "## 摘要")
    sync = skeleton.split("## 提交前同步表", 1)[1]

    assert "本骨架默认不给本节分配正文章节序号" in skeleton
    for internal in (control, sync):
        assert "不进入提交论文" in internal
        assert "导出前必须删除" in internal


def test_existing_content_and_page_gates_are_preserved() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    body = section_between(
        skeleton,
        "## 六、问题一的建立与求解",
        "## 九、模型评估改进与推广",
    )
    core_gates = (
        "目标、难点与上下问接口",
        "数据与处理",
        "模型或数学构造",
        "求解与复现",
        "结果与解释",
        "真实检验",
    )

    for gate in core_gates:
        assert body.count(f"| {gate} |") == 3
    assert body.count("| 直接答案与下问接口 |") == 2
    assert body.count("| 直接答案与最终交付 |") == 1
    assert "不得在三问之间机械复用同一套子结构" in skeleton
    assert "24–30 页" in skeleton
    assert "CONTRIB-PROVEN" in skeleton
