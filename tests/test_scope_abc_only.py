from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "cumcm-live-problem-analyst",
    "cumcm-live-case-retriever",
    "cumcm-live-model-designer",
    "cumcm-live-python-coder",
    "cumcm-live-matlab-coder",
    "cumcm-live-result-verifier",
    "cumcm-live-paper-writer",
    "cumcm-live-layout-verifier",
    "cumcm-live-final-auditor",
)


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def description_line(skill_name: str) -> str:
    content = read(f"{skill_name}/SKILL.md")
    return next(line for line in content.splitlines() if line.startswith("description:"))


def test_all_nine_skill_descriptions_declare_abc_scope() -> None:
    for skill_name in SKILL_NAMES:
        # 锁：每个公开 Skill 描述都必须主动声明只面向 A、B、C 题。
        assert "A、B、C 题" in description_line(skill_name), skill_name


def test_problem_analyst_description_no_longer_claims_abcde_support() -> None:
    description = description_line("cumcm-live-problem-analyst")

    # 锁：入口描述不得重新宣称支持 A/B/C/D/E。
    assert "A/B/C/D/E" not in description
    # 锁：入口触发短语只能列 A/B/C 题。
    assert "分析 A/B/C 题" in description
    # 锁：入口描述必须显式排除 D、E 题。
    assert "不支持 D、E 题" in description


def test_problem_analyst_blocks_scope_before_downstream_work() -> None:
    skill = read("cumcm-live-problem-analyst/SKILL.md")
    blockers = skill.split("## 阻断条件", 1)[1].split("## 资源路由", 1)[0]

    # 锁：范围不匹配必须返回稳定状态码 BLOCKED_SCOPE。
    assert "BLOCKED_SCOPE" in skill
    # 锁：范围门禁必须在启动下游流程之前执行。
    assert skill.index("BLOCKED_SCOPE") < skill.index("## 启动流程")
    # 锁：D/E 请求必须停止拆题、检索和建模建议。
    assert "停止拆题、模式匹配和建模建议" in skill
    # 锁：阻断条件必须包含题号不属于 A、B、C。
    assert "用户选择的题号不属于 A、B、C" in blockers
    # 锁：问题合同字段必须只允许 A、B、C 三个值。
    assert "`problem_id` 只允许 `A`、`B`、`C`" in skill
    # 锁：范围阻断的合同不得交给下游角色。
    assert "不得交给下游角色" in skill


def test_readme_and_suite_declare_abc_only_scope() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")

    # 锁：README 开篇必须完整声明 ABC-only 及 D/E 排除范围。
    assert "本套件只支持国赛 A、B、C 题，不支持 D、E 题" in readme
    # 锁：README 共同门禁必须再次声明 ABC-only。
    assert "本套件只支持 A、B、C 题" in readme
    # 锁：README 必须公开范围阻断状态码。
    assert "BLOCKED_SCOPE" in readme
    # 锁：SUITE 共同规则必须声明 ABC-only。
    assert "本套件只支持 A、B、C 题" in suite
    # 锁：SUITE 必须要求在第一阶段终止 D/E 请求。
    assert "第 1 阶段" in suite
    # 锁：SUITE 必须使用与入口一致的范围阻断状态码。
    assert "BLOCKED_SCOPE" in suite


def test_problem_contract_rejects_non_abc_problem_id() -> None:
    contract = read("cumcm-live-problem-analyst/assets/problem-contract.md")

    # 锁：问题合同模板必须限制 problem_id 的取值域。
    assert "`problem_id` 只能填写 `A`、`B`、`C`" in contract
    # 锁：合同模板必须显式列出 D/E 和其他竞赛为拒绝示例。
    assert "D、E 或其他竞赛题目" in contract
    # 锁：范围不匹配必须把合同状态设为 BLOCKED。
    assert "状态设为 `BLOCKED`" in contract
    # 锁：被阻断合同必须停止下游交接。
    assert "停止下游交接" in contract


def test_agent_short_descriptions_do_not_claim_abcde_scope() -> None:
    for skill_name in SKILL_NAMES:
        agent = read(f"{skill_name}/agents/openai.yaml")
        short_description = next(
            line for line in agent.splitlines() if "short_description:" in line
        )
        # 锁：UI 短描述不得含有宣称支持 D/E 的旧范围串。
        assert "A/B/C/D/E" not in short_description, skill_name

    problem_agent = read("cumcm-live-problem-analyst/agents/openai.yaml")
    # 锁：入口 UI 描述必须明确 A/B/C 题范围。
    assert "赛时拆解国赛 A/B/C 题目" in problem_agent
