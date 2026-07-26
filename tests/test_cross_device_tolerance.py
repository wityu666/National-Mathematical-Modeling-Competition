from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_same_environment_round_a_stays_exact() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )

    assert "### Round A：同环境可复现复跑" in skill
    assert "确定性结果要求精确一致" in skill
    assert "同环境 Round A" in protocol
    assert "确定性结果要求精确一致" in protocol
    assert "不得用来放宽同环境 Round A" in skill


def test_cross_device_policy_is_conditional_not_a_third_round() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")

    assert "### 跨设备复核的容差政策" in skill
    assert "不是强制新增第三轮复核" in skill
    assert "--rtol 1e-9 --json" in skill
    assert "--rtol" in skill and "--atol" in skill
    assert "Round C" not in skill


def test_conclusion_level_invariants_must_match_across_devices() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")

    for keyword in (
        "排序与排名",
        "方案选择",
        "分类标签",
        "聚类归属",
        "可行性判定",
        "最优解结构",
        "图表的定性结论",
        "结论性陈述",
        "CONTRIB-PROVEN",
    ):
        assert keyword in skill
    assert "跨设备必须逐字或逐项完全一致" in skill


def test_environment_noise_is_separated_from_real_defects() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )

    assert "环境噪声" in skill
    assert "环境噪声" in protocol
    for signal in (
        "问题规模",
        "迭代次数",
        "方向一致",
        "特定模块",
        "固定线程数",
    ):
        assert signal in skill
        assert signal in protocol
    assert "不得归类为环境噪声" in protocol


def test_report_records_both_environment_fingerprints_and_invariants() -> None:
    report = read("cumcm-live-result-verifier/assets/verification-report.md")

    for field in (
        "设备标识",
        "OS 及版本",
        "Python/MATLAB 运行时版本",
        "关键数值库与 BLAS 后端",
        "线程数与配置",
        "CPU 架构",
    ):
        assert field in report
    assert "首次运行侧" in report and "复核侧" in report
    assert "环境噪声及依据" in report
    assert "跨设备结论级不变量核对" in report


def test_readme_and_suite_share_cross_device_gate() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")
    gate = (
        "跨设备复核允许使用事先声明的浮点容差，但排序、方案选择、分类、"
        "可行性判定和结论性陈述必须完全一致；未记录两侧环境指纹的跨设备"
        "结果不得计入 `PASS`。"
    )

    assert gate in readme
    assert gate in suite


def test_gitignore_covers_runtime_caches_and_fixtures_remain() -> None:
    gitignore = read(".gitignore")

    for pattern in (
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        ".DS_Store",
        "~$*",
    ):
        assert pattern in gitignore

    fixture_root = (
        SUITE_ROOT
        / "cumcm-live-final-auditor"
        / "tests"
        / "fixtures"
        / "fake_submission"
    )
    assert {path.name for path in fixture_root.iterdir()} == {
        "evil.exe",
        "model.py",
        "paper.pdf",
        "注册机.txt",
    }
