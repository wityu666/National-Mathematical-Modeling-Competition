from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SINGLE_OCCURRENCE = 1
NOT_FIXED_ORDER_GUARDS = (
    "不是固定小节顺序",
    "不规定固定小节顺序",
    "不作为固定小节顺序",
)
NO_CROSS_QUESTION_REUSE_GUARDS = (
    "不得在三问之间机械复用同一套子结构",
    "不得三问机械复用同一子结构",
    "三问子结构不得机械雷同",
)
NO_CROSS_TEAM_TEMPLATE_GUARDS = (
    "不得与其他队伍形成一致的固定子结构",
    "不得形成跨队伍统一的固定子结构",
    "不得照搬其他队伍的固定子结构",
)


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def section_between(content: str, start: str, end: str) -> str:
    return content.split(start, 1)[1].split(end, 1)[0]


def body_sections() -> dict[str, str]:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    return {
        "Q1": section_between(
            skeleton,
            "## 六、问题一的建立与求解",
            "## 七、问题二的建立与求解",
        ),
        "Q2": section_between(
            skeleton,
            "## 七、问题二的建立与求解",
            "## 八、问题三的建立与求解",
        ),
        "Q3": section_between(
            skeleton,
            "## 八、问题三的建立与求解",
            "## 九、模型评估改进与推广",
        ),
    }


def test_all_three_body_section_titles_exist() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    for title in (
        "## 六、问题一的建立与求解",
        "## 七、问题二的建立与求解",
        "## 八、问题三的建立与求解",
    ):
        # 锁：论文骨架必须保留逐问独立的三个主体章节。
        assert title in skeleton


def test_all_questions_have_seven_symmetric_content_gates() -> None:
    sections = body_sections()
    common_gates = (
        "目标、难点与上下问接口",
        "数据与处理",
        "模型或数学构造",
        "求解与复现",
        "结果与解释",
        "真实检验",
    )

    for question, section in sections.items():
        for gate in common_gates:
            # 锁：每个问题都必须且只能出现一次对应核心内容门。
            assert section.count(f"| {gate} |") == EXPECTED_SINGLE_OCCURRENCE, (
                question,
                gate,
            )

    # 锁：问题一必须交付题面答案并明确向下问传递的接口。
    assert (
        sections["Q1"].count("| 直接答案与下问接口 |")
        == EXPECTED_SINGLE_OCCURRENCE
    )
    # 锁：问题二必须交付题面答案并明确向下问传递的接口。
    assert (
        sections["Q2"].count("| 直接答案与下问接口 |")
        == EXPECTED_SINGLE_OCCURRENCE
    )
    # 锁：最后一问必须交付题面答案和最终产物而非虚构下问。
    assert (
        sections["Q3"].count("| 直接答案与最终交付 |")
        == EXPECTED_SINGLE_OCCURRENCE
    )


def test_each_question_has_one_content_gate_table_and_contribution_table() -> None:
    sections = body_sections()

    for question, section in sections.items():
        # 锁：每问必须且只能有一张主体内容门表。
        assert (
            section.count("| 必含内容 | 本队填写 |")
            == EXPECTED_SINGLE_OCCURRENCE
        ), question
        # 锁：每问必须且只能有一张亮点登记表。
        assert (
            section.count("| contrib_id | 可证伪 claim |")
            == EXPECTED_SINGLE_OCCURRENCE
        ), question
        # 锁：每问的亮点示例标识必须与问题编号一致。
        assert f"`CONTRIB-{question}-001`" in section
        # 锁：没有冻结已证亮点时必须删除空泛洞察。
        assert "无当前冻结的 `CONTRIB-PROVEN` 时删除洞察内容" in section


def test_defingerprint_rule_remains_in_each_question_section() -> None:
    sections = body_sections()

    for question, section in sections.items():
        # 锁：内容门表不得被误用为固定小节顺序。
        assert any(marker in section for marker in NOT_FIXED_ORDER_GUARDS), question
        # 锁：三问之间不得机械复制同一子结构。
        assert any(
            marker in section for marker in NO_CROSS_QUESTION_REUSE_GUARDS
        ), question
        # 锁：论文不得形成跨队伍一致的套件子结构指纹。
        assert any(
            marker in section for marker in NO_CROSS_TEAM_TEMPLATE_GUARDS
        ), question


def test_skeleton_has_one_shared_gate_but_variable_structure_principle() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：统一内容门总纲只出现一次，避免变成重复模板正文。
    assert (
        skeleton.count("三问必须覆盖同一套内容门")
        == EXPECTED_SINGLE_OCCURRENCE
    )
    # 锁：任一问缺少内容门都必须判为漏答。
    assert "任一问缺项即视为漏答" in skeleton
    # 锁：各问小节结构必须服从本问数学逻辑。
    assert "小节命名、组合与排列必须按各问自身的数学逻辑组织" in skeleton
    # 锁：统一内容门不能导致三问结构雷同。
    assert "不得三问雷同" in skeleton


def test_paper_writer_requires_equal_gate_coverage_without_word_quota() -> None:
    skill = read("cumcm-live-paper-writer/SKILL.md")

    # 锁：paper-writer 必须要求各问覆盖相同七项核心内容门。
    assert "主体各问必须覆盖同一套七项内容门" in skill
    # 锁：最后一问不能只有结论而缺少建模闭环。
    assert "最后一问尤其不得只给结论而缺少模型、求解与真实检验" in skill
    # 锁：完整性按内容覆盖判断，不能机械按字数配平。
    assert "本门禁约束内容覆盖度，不按字数或篇幅机械配平" in skill


def test_final_auditor_grades_missing_question_gates() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：终审必须逐问核对全部七项内容门。
    assert "逐问核对七项内容门" in skill
    # 锁：普通内容门缺失至少按 P1 处理。
    assert "任一问缺项按 `P1` 处理" in skill
    # 锁：实质作答项缺失必须升级到 P0。
    assert "按 `P0` 处理" in skill
    # 锁：审计报告必须提供逐问覆盖核对表。
    assert "## 逐问七项内容门覆盖核对" in report
    for question in ("问题一", "问题二", "问题三"):
        # 锁：审计报告必须为每个问题保留独立核对行。
        assert f"| {question} |" in report
    for gate in (
        "目标/难点/接口",
        "数据与处理",
        "模型或数学构造",
        "求解与复现",
        "结果与解释",
        "真实检验",
        "直接答案/最终交付",
    ):
        # 锁：审计报告必须为每项核心内容门提供定位列。
        assert gate in report
