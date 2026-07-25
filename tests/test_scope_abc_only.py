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
        assert "A、B、C 题" in description_line(skill_name), skill_name


def test_problem_analyst_description_no_longer_claims_abcde_support() -> None:
    description = description_line("cumcm-live-problem-analyst")

    assert "A/B/C/D/E" not in description
    assert "分析 A/B/C 题" in description
    assert "不支持 D、E 题" in description


def test_problem_analyst_blocks_scope_before_downstream_work() -> None:
    skill = read("cumcm-live-problem-analyst/SKILL.md")
    blockers = skill.split("## 阻断条件", 1)[1].split("## 资源路由", 1)[0]

    assert "BLOCKED_SCOPE" in skill
    assert skill.index("BLOCKED_SCOPE") < skill.index("## 启动流程")
    assert "停止拆题、模式匹配和建模建议" in skill
    assert "用户选择的题号不属于 A、B、C" in blockers
    assert "`problem_id` 只允许 `A`、`B`、`C`" in skill
    assert "不得交给下游角色" in skill


def test_readme_and_suite_declare_abc_only_scope() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")

    assert "本套件只支持国赛 A、B、C 题，不支持 D、E 题" in readme
    assert "本套件只支持 A、B、C 题" in readme
    assert "BLOCKED_SCOPE" in readme
    assert "本套件只支持 A、B、C 题" in suite
    assert "第 1 阶段" in suite
    assert "BLOCKED_SCOPE" in suite


def test_problem_contract_rejects_non_abc_problem_id() -> None:
    contract = read("cumcm-live-problem-analyst/assets/problem-contract.md")

    assert "`problem_id` 只能填写 `A`、`B`、`C`" in contract
    assert "D、E 或其他竞赛题目" in contract
    assert "状态设为 `BLOCKED`" in contract
    assert "停止下游交接" in contract


def test_agent_short_descriptions_do_not_claim_abcde_scope() -> None:
    for skill_name in SKILL_NAMES:
        agent = read(f"{skill_name}/agents/openai.yaml")
        short_description = next(
            line for line in agent.splitlines() if "short_description:" in line
        )
        assert "A/B/C/D/E" not in short_description, skill_name

    problem_agent = read("cumcm-live-problem-analyst/agents/openai.yaml")
    assert "赛时拆解国赛 A/B/C 题目" in problem_agent
