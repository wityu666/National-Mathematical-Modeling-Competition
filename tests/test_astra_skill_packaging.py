import re
from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = sorted(SUITE_ROOT.glob("cumcm-live-*"))
SHARED_CONTRACT = (
    SUITE_ROOT
    / "cumcm-live-problem-analyst/references/astra-execution-contract.md"
)
# Codex UI 元数据支持的顶层键；模型选择由宿主负责，不是技能 YAML 字段。
SUPPORTED_METADATA_KEYS = {"interface", "dependencies", "policy"}


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_every_skill_resolves_the_bundled_astra_contract() -> None:
    # 锁：共享执行说明必须随套件实际存在，不能指向作者私有路径。
    assert SHARED_CONTRACT.is_file(), SHARED_CONTRACT.relative_to(SUITE_ROOT)
    for skill_dir in SKILL_DIRS:
        skill_path = skill_dir / "SKILL.md"
        links = re.findall(
            r"\[[^\]]+\]\(([^)]*astra-execution-contract\.md)\)",
            read(str(skill_path.relative_to(SUITE_ROOT))),
        )
        # 锁：每个阶段直接调用时都能发现共享运行约定。
        assert links, f"{skill_dir.name}: missing execution-contract link"
        for link in links:
            target = (skill_dir / link).resolve()
            # 锁：换机器、复制整套九技能后仍解析到同一个随包文件。
            assert target == SHARED_CONTRACT.resolve(), (skill_dir.name, link)
            assert target.is_file(), (skill_dir.name, link)


def test_astra_invocation_metadata_uses_supported_fields() -> None:
    for skill_dir in SKILL_DIRS:
        metadata = read(
            str((skill_dir / "agents/openai.yaml").relative_to(SUITE_ROOT))
        )
        keys = set(re.findall(r"^([a-z_]+):", metadata, re.MULTILINE))
        # 锁：模型适配不能给 Codex 元数据加入不存在的模型/推理调度键。
        assert "interface" in keys and keys <= SUPPORTED_METADATA_KEYS, (
            skill_dir.name,
            keys,
        )
        prompts = re.findall(r'^  default_prompt: "(.+)"$', metadata, re.MULTILINE)
        # 锁：UI 入口实际调用对应技能，不只是提到模型名的普通对话。
        assert prompts and all(
            f"$" + skill_dir.name in prompt for prompt in prompts
        ), skill_dir.name
