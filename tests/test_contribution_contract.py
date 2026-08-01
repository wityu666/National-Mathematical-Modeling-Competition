from pathlib import Path
import re


SUITE_ROOT = Path(__file__).resolve().parents[1]
LEDGER_FIELD_PATTERN = re.compile(r"`(\w+)`")
PATTERN_CARD_HEADING = re.compile(r"^## ([A-Z][A-Z-]*-\d+) .+$", re.MULTILINE)
# 当前模式图谱包含 14 张模式卡；每张卡必须恰有一条差异化提示。
EXPECTED_PATTERN_CARD_COUNT = 14
EXPECTED_HINTS_PER_PATTERN_CARD = 1


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_contribution_ledger_has_required_schema_and_guards() -> None:
    ledger = read("cumcm-live-model-designer/assets/contribution-ledger.md")
    required_fields = {
        "contrib_id",
        "claim",
        "baseline_expectation",
        "delta_type",
        "evidence_ids",
        "proof",
        "cost_risk",
        "status",
        "placement",
        "fallback",
    }

    extracted_fields = set(LEDGER_FIELD_PATTERN.findall(ledger))
    # 锁：亮点账本的全部必填字段必须可被精确标识符解析出来。
    assert required_fields.issubset(extracted_fields)
    # 锁：单条亮点必须保留候选、已证明、放弃三态。
    assert "CANDIDATE / PROVEN / DROPPED" in ledger
    # 锁：账本文件本身必须保留套件统一生命周期状态机。
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in ledger
    # 锁：没有证据绑定的亮点必须删除而非进入正文。
    assert "无证据即删" in ledger
    # 锁：亮点 claim 必须通过可证伪性门。
    assert "可证伪性门" in ledger
    # 锁：亮点必须申报代价、风险和边界。
    assert "代价强制申报" in ledger


def test_suite_handoff_chain_and_ids_include_contributions() -> None:
    for path in ("README.md", "SUITE.md"):
        content = read(path)
        # 锁：总览文档必须把亮点账本接入交接链。
        assert "contribution_ledger" in content
        # 锁：总览文档必须声明统一的 CONTRIB 证据标识。
        assert "CONTRIB-*" in content
        # 锁：公开规则必须强调亮点来自已证明差异而非复杂度包装。
        assert "亮点是被证明的差异，不是被主张的复杂度" in content


def test_model_and_pattern_stages_register_differentiation() -> None:
    model_skill = read("cumcm-live-model-designer/SKILL.md")
    model_playbook = read(
        "cumcm-live-model-designer/references/model-design-playbook.md"
    )
    model_contract = read("cumcm-live-model-designer/assets/model-contract.md")
    retriever = read("cumcm-live-case-retriever/SKILL.md")
    atlas = read("cumcm-live-case-retriever/references/model-pattern-atlas.md")

    # 锁：模型设计阶段必须显式登记亮点候选。
    assert "CONTRIB-CANDIDATE" in model_skill
    # 锁：模型设计 Skill 必须把候选写入合同字段。
    assert "contribution_candidates[]" in model_skill
    # 锁：模型设计手册必须说明候选字段的使用方法。
    assert "contribution_candidates[]" in model_playbook
    # 锁：冻结模型合同必须实际承载亮点候选。
    assert "contribution_candidates[]" in model_contract
    # 锁：案例检索 Skill 必须输出差异化提示。
    assert "differentiation_hint" in retriever
    card_matches = list(PATTERN_CARD_HEADING.finditer(atlas))
    # 锁：模式卡数量变化必须显式更新合同依据，不能依赖裸魔数。
    assert len(card_matches) == EXPECTED_PATTERN_CARD_COUNT
    for index, match in enumerate(card_matches):
        next_start = (
            card_matches[index + 1].start()
            if index + 1 < len(card_matches)
            else len(atlas)
        )
        card = atlas[match.start():next_start]
        # 锁：每张模式卡都必须恰好提供一处 differentiation_hint。
        assert (
            card.count("differentiation_hint")
            == EXPECTED_HINTS_PER_PATTERN_CARD
        ), match.group(1)


def test_coders_require_dedicated_frozen_evidence() -> None:
    for language in ("python", "matlab"):
        skill = read(f"cumcm-live-{language}-coder/SKILL.md")
        manifest = read(f"cumcm-live-{language}-coder/assets/run-manifest.md")

        # 锁：两种代码路线都只能把已证明亮点交给论文阶段。
        assert "CONTRIB-PROVEN" in skill
        # 锁：两种代码路线都要求为亮点生成专门运行产物。
        assert "专门运行产物" in skill
        # 锁：运行清单必须登记亮点证明产物。
        assert "亮点证明产物" in manifest
        # 锁：亮点证明产物必须绑定可追溯的结果、图或表标识。
        assert "RID/FIG/TAB" in manifest


def test_paper_and_auditor_enforce_proven_only_and_p0() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    paper_refs = [
        read("cumcm-live-paper-writer/references/evidence-driven-writing-playbook.md"),
        read("cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"),
        read("cumcm-live-paper-writer/references/abc-figure-design-playbook.md"),
    ]
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    # 锁：摘要必须把已证明亮点前置到第一屏。
    assert "第一屏" in paper_skill
    # 锁：论文只能使用达到 PROVEN 状态的亮点。
    assert "CONTRIB-PROVEN" in paper_skill
    # 锁：写作参考资料必须共同采用 CONTRIB 标识追溯亮点。
    assert all("CONTRIB-" in reference for reference in paper_refs)
    # 锁：终审必须包含独立的亮点真实性审计。
    assert "亮点真实性" in auditor_skill
    # 锁：无证据亮点必须按最高阻塞等级处理。
    assert "P0" in auditor_skill
    # 锁：审计协议必须记录亮点真实性核验状态。
    assert "contributions_verified" in audit_protocol


def test_every_question_completeness_gate_is_present() -> None:
    problem_skill = read("cumcm-live-problem-analyst/SKILL.md")
    problem_contract = read("cumcm-live-problem-analyst/assets/problem-contract.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")

    # 锁：拆题阶段必须优先保障全部小问完整作答。
    assert "全局配平" in problem_skill
    # 锁：问题合同必须记录全局完整性配平结果。
    assert "全局完整性配平" in problem_contract
    # 锁：写作阶段不得留下没有实质答案的小问。
    assert "每个小问都有可提交的实质答案" in paper_skill


def test_result_verifier_is_integrated_across_the_suite() -> None:
    verifier = read("cumcm-live-result-verifier/SKILL.md")
    report = read("cumcm-live-result-verifier/assets/verification-report.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )
    readme = read("README.md")
    suite = read("SUITE.md")
    python_skill = read("cumcm-live-python-coder/SKILL.md")
    matlab_skill = read("cumcm-live-matlab-coder/SKILL.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")

    # 锁：README 必须公开重复结果复核阶段。
    assert "cumcm-live-result-verifier" in readme
    # 锁：SUITE 交接链必须包含 result_verifier。
    assert "result_verifier" in suite
    # 锁：结果复核必须同时保留复跑与独立方法两轮。
    assert "Round A" in verifier and "Round B" in verifier
    # 锁：复核报告必须使用统一生命周期状态机。
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in report
    # 锁：重复失败必须触发停止循环的保护条件。
    assert "同一错误重复两次" in protocol
    # 锁：Python 产物必须交给 result-verifier。
    assert "cumcm-live-result-verifier" in python_skill
    # 锁：MATLAB 产物必须交给 result-verifier。
    assert "cumcm-live-result-verifier" in matlab_skill
    # 锁：paper-writer 只接收通过验证的冻结结果。
    assert "VER-* PASS" in paper_skill
    # 锁：final-auditor 必须反查相同版本的验证通过状态。
    assert "VER-* PASS" in auditor


def test_layout_verifier_is_integrated_after_paper_and_before_final_audit() -> None:
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    layout_protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )
    readme = read("README.md")
    suite = read("SUITE.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    # 锁：README 必须公开独立排版复核阶段。
    assert "cumcm-live-layout-verifier" in readme
    # 锁：交接顺序必须是写作、排版复核、最终审计。
    assert suite.index("cumcm-live-paper-writer") < suite.index(
        "cumcm-live-layout-verifier"
    ) < suite.index("cumcm-live-final-auditor")
    # 锁：排版复核必须保留自动预检通过状态。
    assert "PRECHECK_PASS" in layout_skill
    # 锁：排版复核必须同时保留自动预检和真实渲染两轮。
    assert "Round A" in layout_skill and "Round B" in layout_skill
    # 锁：排版报告必须使用统一生命周期状态机。
    assert "DRAFT / FROZEN / STALE / BLOCKED / PASS" in layout_report
    # 锁：排版协议必须记录视觉检查范围是否完整。
    assert "visual_scope_complete" in layout_protocol
    # 锁：paper-writer 必须等待独立排版复核通过。
    assert "LAYOUT-* PASS" in paper_skill
    # 锁：final-auditor 必须要求同一 PDF 的排版通过证据。
    assert "LAYOUT-* PASS" in auditor_skill
    # 锁：终审协议必须核验同哈希排版通过状态。
    assert "same_hash_layout_pass" in audit_protocol


def test_symbol_table_is_required_in_main_body_and_audited() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read(
        "cumcm-live-final-auditor/assets/audit-report-template.md"
    )

    # 锁：符号说明必须作为正文独立章节存在。
    assert "符号说明”必须是正文独立章节" in paper_skill
    # 锁：完整符号表不得被移到附录。
    assert "不得只放在附录" in paper_skill
    # 锁：符号说明必须处于假设与数据建模章节之间。
    assert "模型假设”之后、“数据收集与预处理/问题一的建立与求解”之前" in paper_skill
    # 锁：论文骨架必须明确符号说明属于正文。
    assert "本节属于正文" in skeleton
    # 锁：符号表必须记录取值范围或数据类型。
    assert "取值范围/类型" in skeleton
    # 锁：排版复核必须检查正文符号表。
    assert "正文“符号说明”表" in layout_skill
    # 锁：排版报告必须记录符号表位置和可读性结论。
    assert "正文符号表位置正确且清晰可读" in layout_report
    # 锁：终审必须把符号表仅在附录视为缺陷。
    assert "完整符号表只放在附录" in auditor_skill
    # 锁：终审报告必须记录符号表与公式定义一致性。
    assert "符号说明表位于正文且与公式定义一致" in audit_report


def test_main_body_page_range_24_to_30_with_unlimited_appendix() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    layout_protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read(
        "cumcm-live-final-auditor/assets/audit-report-template.md"
    )
    audit_protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    for content in (
        readme,
        suite,
        paper_skill,
        skeleton,
        layout_skill,
        layout_report,
        auditor_skill,
        audit_report,
    ):
        # 锁：所有相关角色与总览都必须保留正文 24 页下限。
        assert "24" in content
        # 锁：所有相关角色与总览都必须保留正文 30 页上限。
        assert "30" in content
        # 锁：所有相关角色与总览都必须声明附录页数不限。
        assert "附录" in content and (
            "不限" in content or "不设上限" in content or "不设页数上限" in content
        )
    # 锁：排版协议必须使用可计算的 24–30 页闭区间。
    assert "24 <= main_body_pages <= 30" in layout_protocol
    # 锁：终审协议必须独立使用同一个页数闭区间。
    assert "24 <= main_body_pages <= 30" in audit_protocol
    # 锁：paper-writer 必须说明页数区间是用户内部质量门。
    assert "用户已确认的内部质量门" in paper_skill
    # 锁：final-auditor 必须说明页数区间是用户内部质量门。
    assert "用户已确认的内部质量门" in auditor_skill
    # 锁：排版角色必须允许更严格官方上限覆盖内部下限。
    assert "官方上限低于 24 页" in layout_skill
    # 锁：终审协议必须执行官方低上限例外。
    assert "官方上限低于 24 页" in audit_protocol
    # 锁：正文上限不能通过搬走核心交付物规避。
    assert "核心结果、关键验证、符号说明或复现入口" in paper_skill
    # 锁：paper-writer 必须明确禁止用附录规避 30 页上限。
    assert "规避 30 页上限" in paper_skill


def test_page_floor_has_anti_padding_guards() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    required_guards = (
        "放大图片",
        "增大字号行距",
        "完整代码",
        "复述题面",
        "装饰性图表",
        "候选算法",
    )

    for content in (paper_skill, auditor_skill):
        for guard in required_guards:
            # 锁：写作与终审必须共同覆盖每一种反注水手段。
            assert guard in content
        # 锁：命中反注水行为必须达到 P0 阻塞等级。
        assert "P0" in content
    # 锁：页数不足必须回到内容缺口，而不是调整版式。
    assert "页数不足通常是漏答的症状，不是排版问题" in paper_skill


def test_palette_sets_are_explicit_and_consistent_across_plotting_and_audit() -> None:
    python_skill = read("cumcm-live-python-coder/SKILL.md")
    python_style = read("cumcm-live-python-coder/assets/cumcm_plot_style.py")
    python_recipe = read(
        "cumcm-live-python-coder/references/python-figure-recipes.md"
    )
    matlab_skill = read("cumcm-live-matlab-coder/SKILL.md")
    matlab_style = read("cumcm-live-matlab-coder/assets/cumcm_plot_style.m")
    matlab_recipe = read(
        "cumcm-live-matlab-coder/references/matlab-figure-recipes.md"
    )
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    playbook = read(
        "cumcm-live-paper-writer/references/abc-figure-design-playbook.md"
    )
    layout_skill = read("cumcm-live-layout-verifier/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")

    palette_sets = ("SET-A", "SET-B", "SET-C", "SET-D", "SET-E", "SET-F")
    set_a_hex = {"#3B3B90", "#A5A54A", "#D9B7D9", "#818181", "#B82E2E"}
    for palette_set in palette_sets:
        # 锁：Python 样式必须提供每个已批准配色组。
        assert palette_set in python_style
        # 锁：MATLAB 样式必须提供同名配色组。
        assert palette_set in matlab_style
        # 锁：图表手册必须记录所有可选配色组。
        assert palette_set in playbook
    for color in set_a_hex:
        # 锁：Python SET-A 必须保留已验证的系列色。
        assert color in python_style
        # 锁：图表手册中的 SET-A 色值必须与代码一致。
        assert color in playbook
    for content in (
        python_skill,
        matlab_skill,
        python_recipe,
        matlab_recipe,
        paper_skill,
        layout_skill,
        auditor_skill,
    ):
        # 锁：出图、写作、排版和终审全链路必须传递 palette_set。
        assert "palette_set" in content
    # 锁：MATLAB SET-A 的主色 RGB 必须与十六进制定义一致。
    assert "59 59 144" in matlab_style
    # 锁：MATLAB SET-A 的重点色 RGB 必须与十六进制定义一致。
    assert "184 46 46" in matlab_style
    # 锁：MATLAB 样式必须保留顺序色带。
    assert "style.sequential" in matlab_style
    # 锁：MATLAB 样式必须保留双向色带。
    assert "style.diverging" in matlab_style
    # 锁：Python 样式必须要求通过组名取得配色。
    assert "get_palette_set" in python_style
    # 锁：Python 不得退回旧的单一默认配色标识。
    assert "CUMCM_PALETTE_ID" not in python_style
    # 锁：MATLAB 不得退回旧的单一默认配色字段。
    assert "style.paletteId" not in matlab_style
