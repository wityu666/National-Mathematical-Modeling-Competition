from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SINGLE_SECTION = 1
EXPECTED_QUESTION_COUNT = 3
EXPECTED_NONFINAL_QUESTION_COUNT = 2
# skeleton、paper-writer、final-auditor 是公式内容合同角色；layout-verifier 只做视觉 QA。
EXPECTED_EQUATION_CONTENT_ROLE_COUNT = 3
DATA_PLACEMENT_GUARDS = (
    "问题专有数据处理就近写",
    "问题专有的数据处理就近写",
    "专有数据处理写入对应问题章节",
)
HIDDEN_ASSUMPTION_GUARDS = (
    "不得使用未说明的隐含假设",
    "不得引入未说明的隐含假设",
    "禁止未披露的隐含假设",
)
DEPRINT_STRUCTURE_GUARDS = (
    "不得在三问之间机械复用同一套子结构",
    "三问子结构不得机械雷同",
    "不得三问机械复用同一子结构",
)


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def section_between(content: str, start: str, end: str) -> str:
    return content.split(start, 1)[1].split(end, 1)[0]


def test_target_top_level_sections_exist_in_order() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    target_sections = (
        "## 摘要",
        "## 关键词",
        "## 目录",
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
    # 锁：十四个正式顶层节必须严格按目标结构排序。
    assert positions == sorted(positions)
    for title in target_sections:
        # 锁：每个正式顶层节必须唯一，不能遗漏或重复。
        assert skeleton.count(title) == EXPECTED_SINGLE_SECTION

    # 锁：AI 使用记录必须位于参考文献之后、附录之前。
    assert skeleton.index("## 参考文献") < skeleton.index(
        "## AI 使用记录"
    ) < skeleton.index("## 附录")


def test_keywords_follow_abstract_before_synchronized_table_of_contents() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：正式结构必须按摘要、关键词、目录顺序排列。
    assert skeleton.index("## 摘要") < skeleton.index("## 关键词") < skeleton.index(
        "## 目录"
    )
    # 锁：目录必须由 Word 或 LaTeX 排版工具自动生成。
    assert "Word 自动目录" in skeleton and r"\tableofcontents" in skeleton
    # 锁：目录页码不得由参赛队手工维护。
    assert "不得手工输入或维护目录页码" in skeleton
    # 锁：paper-writer 必须在分页冻结后更新目录。
    assert "内容与分页冻结后生成目录" in paper_skill
    # 锁：排版复核不得再把目录视为可选项。
    assert "目录（如有）" not in layout_skill
    # 锁：排版复核必须核对目录位置及标题、层级、页码。
    assert "目录位置、自动生成状态、标题层级和页码一致性已检查" in layout_skill
    # 锁：排版报告必须记录目录核对证据。
    assert "目录位置与标题、层级、页码一致" in layout_report
    # 锁：终审必须独立核对摘要关键词与目录顺序。
    assert "关键词紧随摘要，目录位于关键词之后、正文之前" in auditor_skill
    # 锁：终审报告必须有独立目录硬门。
    assert "摘要后含关键词，目录位于关键词之后" in audit_report


def test_required_subsection_titles_exist() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    for title in (
        "### 1.1 问题背景",
        "### 1.2 问题提出",
        "### 9.1 优点",
        "### 9.2 不足",
        "### 9.3 推广",
    ):
        # 锁：问题重述与模型评估章节必须保留目标小节。
        assert title in skeleton
    # 锁：原 9.4 必须已合并，不能继续作为第四个小节存在。
    assert "### 9.4 可执行改进" not in skeleton


def test_data_chapter_has_required_gates_and_flexible_placement() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    chapter = section_between(
        skeleton,
        "## 五、数据收集与预处理",
        "## 六、问题一的建立与求解",
    )

    for gate in ("缺失值处理", "数据清洗与标准化", "数据分析"):
        # 锁：第五章必须覆盖每类基础数据处理门。
        assert gate in chapter
    for exploration in ("分布", "相关", "异常识别"):
        # 锁：第五章必须覆盖每类探索性数据分析。
        assert exploration in chapter
    # 锁：问题专有数据处理必须允许回到对应问题章节就近叙述。
    assert any(marker in chapter for marker in DATA_PLACEMENT_GUARDS)
    # 锁：灵活放置数据处理不能降低来源和 DATA 标识追溯。
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
        # 锁：每个问题必须且只能有一行专有假设门。
        assert chapter.count("| 本问专有假设 |") == EXPECTED_SINGLE_SECTION
        # 锁：没有额外假设时也必须显式说明无专有假设。
        assert "无本问专有假设" in chapter
    # 锁：第三章必须明确只集中管理全局假设。
    assert "本章集中列出三问共用的全局假设" in skeleton
    # 锁：模型不得引入未披露的隐含假设。
    assert any(marker in skeleton for marker in HIDDEN_ASSUMPTION_GUARDS)


def test_chapter_equation_numbering_contract_reaches_all_roles() -> None:
    paths = (
        "cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md",
        "cumcm-live-paper-writer/SKILL.md",
        "cumcm-live-final-auditor/SKILL.md",
        "cumcm-live-layout-verifier/SKILL.md",
    )

    for path in paths:
        content = read(path)
        # 锁：每个相关角色都必须给出按章公式编号示例。
        assert "6-1" in content, path
        # 锁：每个相关角色都必须声明章号-序号格式。
        assert "章号-序号" in content, path
    for path in paths[:EXPECTED_EQUATION_CONTENT_ROLE_COUNT]:
        content = read(path)
        # 锁：内容角色必须要求排版工具自动编号或交叉引用。
        assert "自动" in content, path
        # 锁：内容角色必须禁止以上式、下式替代明确引用。
        assert "上式" in content and "下式" in content, path


def test_chapter_nine_keeps_contribution_ledger_mappings() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    chapter = section_between(skeleton, "## 九、模型评估改进与推广", "## 参考文献")

    # 锁：模型优点只能来自当前冻结的已证明亮点。
    assert "优点只来自当前冻结亮点账本中的 `CONTRIB-PROVEN`" in chapter
    # 锁：推广只能使用更好泛化类型的亮点。
    assert "仅使用 delta_type=更好泛化" in chapter
    # 锁：推广亮点必须有跨场景或外推证据。
    assert "跨场景/外推证据的 CONTRIB-PROVEN" in chapter
    # 锁：没有泛化证据时必须明确不主张推广。
    assert "否则明确“不主张推广”" in chapter
    # 锁：改进方向只能来自仍有价值但尚未证明的 DROPPED 候选。
    assert "改进方向来自仍有价值的 `DROPPED` 候选" in chapter


def test_ai_and_internal_work_tables_remain_but_are_not_paper_sections() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    control = section_between(skeleton, "## 成稿控制", "## 摘要")
    sync = skeleton.split("## 提交前同步表", 1)[1]

    # 锁：AI 使用记录默认不占用正文章节序号。
    assert "本骨架默认不给本节分配正文章节序号" in skeleton
    for internal in (control, sync):
        # 锁：内部工作表不得进入提交论文。
        assert "不进入提交论文" in internal
        # 锁：内部工作表必须在导出前删除。
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
        # 锁：七项核心内容门必须在三问中对称出现。
        assert body.count(f"| {gate} |") == EXPECTED_QUESTION_COUNT
    # 锁：前两问必须各自包含向下问交接的直接答案门。
    assert (
        body.count("| 直接答案与下问接口 |")
        == EXPECTED_NONFINAL_QUESTION_COUNT
    )
    # 锁：最后一问必须包含唯一的最终交付门。
    assert body.count("| 直接答案与最终交付 |") == EXPECTED_SINGLE_SECTION
    # 锁：统一内容门不能导致三问机械复用子结构。
    assert any(marker in skeleton for marker in DEPRINT_STRUCTURE_GUARDS)
    # 锁：26–30 页内部质量区间必须保留。
    assert "26–30 页" in skeleton
    # 锁：摘要不得计入编号正文页数。
    assert "摘要" in skeleton and "不计入" in skeleton
    # 锁：论文骨架必须继续只接受已证明亮点。
    assert "CONTRIB-PROVEN" in skeleton
