from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
CROSS_DEVICE_GATE_KEYWORDS = {
    "跨设备复核",
    "事先声明",
    "浮点容差",
    "排序",
    "方案选择",
    "分类",
    "可行性判定",
    "结论性陈述",
    "环境指纹",
    "PASS",
}


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_same_environment_round_a_stays_exact() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )

    # 锁：Round A 必须明确限定为同环境可复现复跑。
    assert "### Round A：同环境可复现复跑" in skill
    # 锁：同环境确定性结果必须保持精确一致。
    assert "确定性结果要求精确一致" in skill
    # 锁：详细协议必须保留同环境 Round A 的定义。
    assert "同环境 Round A" in protocol
    # 锁：详细协议不能放宽同环境精确一致要求。
    assert "确定性结果要求精确一致" in protocol
    # 锁：跨设备容差不得反向用于同环境 Round A。
    assert "不得用来放宽同环境 Round A" in skill


def test_cross_device_policy_is_conditional_not_a_third_round() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")

    # 锁：结果复核 Skill 必须提供条件性的跨设备容差政策。
    assert "### 跨设备复核的容差政策" in skill
    # 锁：跨设备政策不能演变为强制第三轮。
    assert "不是强制新增第三轮复核" in skill
    # 锁：Skill 必须给出可直接执行的相对容差示例。
    assert "--rtol 1e-9 --json" in skill
    # 锁：跨设备比较必须同时支持相对与绝对容差参数。
    assert "--rtol" in skill and "--atol" in skill
    # 锁：套件不得悄然新增 Round C。
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
        # 锁：每类结论级不变量都必须跨设备完全一致。
        assert keyword in skill
    # 锁：Skill 必须明确结论级不变量逐字或逐项一致。
    assert "跨设备必须逐字或逐项完全一致" in skill


def test_environment_noise_is_separated_from_real_defects() -> None:
    skill = read("cumcm-live-result-verifier/SKILL.md")
    protocol = read(
        "cumcm-live-result-verifier/references/repeated-verification-protocol.md"
    )

    # 锁：Skill 必须定义容差内环境噪声类别。
    assert "环境噪声" in skill
    # 锁：详细协议必须使用同一环境噪声分类。
    assert "环境噪声" in protocol
    for signal in (
        "问题规模",
        "迭代次数",
        "方向一致",
        "特定模块",
        "固定线程数",
    ):
        # 锁：Skill 必须列出每类系统性差异信号。
        assert signal in skill
        # 锁：协议必须复述每类缺陷判据以便执行。
        assert signal in protocol
    # 锁：呈现缺陷特征的差异不得伪装成环境噪声。
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
        # 锁：环境指纹表必须记录每个跨设备复核字段。
        assert field in report
    # 锁：报告必须并列记录首次运行和复核两侧环境。
    assert "首次运行侧" in report and "复核侧" in report
    # 锁：报告必须记录环境噪声的判定依据。
    assert "环境噪声及依据" in report
    # 锁：报告必须逐项核对跨设备结论级不变量。
    assert "跨设备结论级不变量核对" in report


def test_readme_and_suite_share_cross_device_gate() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")
    # 锁：README 必须完整表达容差、结论不变量与环境指纹三层门禁。
    assert all(keyword in readme for keyword in CROSS_DEVICE_GATE_KEYWORDS)
    # 锁：SUITE 必须与 README 保持同等强度的跨设备门禁。
    assert all(keyword in suite for keyword in CROSS_DEVICE_GATE_KEYWORDS)


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
        # 锁：版本库必须忽略每类运行缓存和临时文件。
        assert pattern in gitignore

    fixture_root = (
        SUITE_ROOT
        / "cumcm-live-final-auditor"
        / "tests"
        / "fixtures"
        / "fake_submission"
    )
    # 锁：清理缓存时不得误删安全审计所需的四个夹具。
    assert {path.name for path in fixture_root.iterdir()} == {
        "evil.exe",
        "model.py",
        "paper.pdf",
        "注册机.txt",
    }
