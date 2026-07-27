from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def section_between(content: str, start: str, end: str) -> str:
    return content.split(start, 1)[1].split(end, 1)[0]


def body_sections() -> dict[str, str]:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    return {
        "Q1": section_between(
            skeleton,
            "## 六、问题一的模型建立与求解",
            "## 七、问题二的模型建立与求解",
        ),
        "Q2": section_between(
            skeleton,
            "## 七、问题二的模型建立与求解",
            "## 八、问题三的模型建立与求解",
        ),
        "Q3": section_between(
            skeleton,
            "## 八、问题三的模型建立与求解",
            "## 九、模型评价与改进",
        ),
    }


def test_all_three_body_section_titles_exist() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    for title in (
        "## 六、问题一的模型建立与求解",
        "## 七、问题二的模型建立与求解",
        "## 八、问题三的模型建立与求解",
    ):
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
            assert section.count(f"| {gate} |") == 1, (question, gate)

    assert sections["Q1"].count("| 直接答案与下问接口 |") == 1
    assert sections["Q2"].count("| 直接答案与下问接口 |") == 1
    assert sections["Q3"].count("| 直接答案与最终交付 |") == 1


def test_each_question_has_one_content_gate_table_and_contribution_table() -> None:
    sections = body_sections()

    for question, section in sections.items():
        assert section.count("| 必含内容 | 本队填写 |") == 1, question
        assert section.count("| contrib_id | 可证伪 claim |") == 1, question
        assert f"`CONTRIB-{question}-001`" in section
        assert "无当前冻结的 `CONTRIB-PROVEN` 时删除洞察内容" in section


def test_defingerprint_rule_remains_in_each_question_section() -> None:
    sections = body_sections()

    for question, section in sections.items():
        assert "不是固定小节顺序" in section, question
        assert "不得在三问之间机械复用同一套子结构" in section, question
        assert "不得与其他队伍形成一致的固定子结构" in section, question


def test_skeleton_has_one_shared_gate_but_variable_structure_principle() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    assert skeleton.count("三问必须覆盖同一套内容门") == 1
    assert "任一问缺项即视为漏答" in skeleton
    assert "小节命名、组合与排列必须按各问自身的数学逻辑组织" in skeleton
    assert "不得三问雷同" in skeleton


def test_paper_writer_requires_equal_gate_coverage_without_word_quota() -> None:
    skill = read("cumcm-live-paper-writer/SKILL.md")

    assert "主体各问必须覆盖同一套七项内容门" in skill
    assert "最后一问尤其不得只给结论而缺少模型、求解与真实检验" in skill
    assert "本门禁约束内容覆盖度，不按字数或篇幅机械配平" in skill


def test_final_auditor_grades_missing_question_gates() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    assert "逐问核对七项内容门" in skill
    assert "任一问缺项按 `P1` 处理" in skill
    assert "按 `P0` 处理" in skill
    assert "## 逐问七项内容门覆盖核对" in report
    for question in ("问题一", "问题二", "问题三"):
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
        assert gate in report
