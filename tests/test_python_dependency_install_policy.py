from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
INSTALL_RECORD_FIELDS = (
    "dependency_install_policy",
    "package_index_or_mirror",
    "dependency_install_log",
    "dependency_lockfile",
)
ISOLATION_GUARDS = ("独立 `.venv`", "系统 Python", "全局 Conda base")


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_python_skill_explicitly_allows_required_package_installation() -> None:
    skill = read("cumcm-live-python-coder/SKILL.md")

    # 锁：缺少预装包时允许安装必要的新 Python 包，而不是自动放弃正确模型。
    assert "本套件默认 `dependency_install_policy=ALLOW`" in skill
    assert "可以安装" in skill
    # 锁：安装许可不能被解释为允许改变冻结模型或验证标准。
    assert "不等于允许更改冻结模型、数据口径或验证标准" in skill


def test_package_installation_is_isolated_and_source_restricted() -> None:
    skill = read("cumcm-live-python-coder/SKILL.md")
    recipes = read(
        "cumcm-live-python-coder/references/python-contest-recipes.md"
    )

    for marker in ISOLATION_GUARDS:
        # 锁：依赖安装必须隔离，不能污染系统解释器或共享环境。
        assert marker in skill and marker in recipes, marker
    # 锁：允许安装不等于允许执行未知来源的包、wheel 或远程安装脚本。
    assert "https://pypi.org/simple" in skill and "https://pypi.org/simple" in recipes
    assert "未知 wheel" in skill and "未知 wheel" in recipes
    assert "远程安装脚本" in recipes
    # 锁：需要管理员权限或风险来源时必须阻断，不能静默扩大权限。
    assert "BLOCKED_DEPENDENCY_RISK" in skill and "BLOCKED_DEPENDENCY_RISK" in recipes


def test_run_manifest_records_dependency_installation_and_checks() -> None:
    manifest = read("cumcm-live-python-coder/assets/run-manifest.md")

    for field in INSTALL_RECORD_FIELDS:
        # 锁：每次安装必须在运行清单中留下可复现字段。
        assert field in manifest, field
    # 锁：安装记录必须覆盖来源、命令、实际版本和可取得的制品哈希。
    for column in ("实际版本", "来源/索引", "安装命令", "制品 SHA-256"):
        assert column in manifest, column
    # 锁：环境冻结前必须执行依赖一致性和新进程导入检查。
    assert "python -m pip check" in manifest
    assert "全新进程导入与版本冒烟测试" in manifest
    assert "requirements-frozen.txt" in manifest


def test_dependency_changes_invalidate_frozen_results() -> None:
    skill = read("cumcm-live-python-coder/SKILL.md")
    recipes = read(
        "cumcm-live-python-coder/references/python-contest-recipes.md"
    )

    # 锁：包版本属于运行血缘，依赖变化必须创建新运行并重跑验证。
    assert "新增、删除或升级任何影响结果的包" in skill
    assert "创建新 `run_id`" in skill and "创建新 `run_id`" in recipes
    # 锁：依赖变化后的旧结果与下游论文不得继续冒充当前版本。
    assert "标记为 `STALE`" in skill and "标为 `STALE`" in recipes
    # 锁：依赖安装失败不得拖垮已经定义的 baseline。
    assert "依赖缺失或安装失败不得阻断已经定义的 baseline" in recipes


def test_public_contract_documents_install_permission_and_guardrails() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")

    for document in (readme, suite):
        # 锁：下载者必须从公共入口知道 Python 新包安装已获允许。
        assert "Python 实现允许按冻结模型的实际需要安装新包" in document
        # 锁：公共规则必须同时声明隔离环境、依赖快照和失效语义。
        assert "独立 `.venv`" in document
        assert "冻结依赖快照" in document
        assert "下游结果立即 `STALE`" in document
        # 锁：公共许可不能弱化供应链与系统环境安全边界。
        assert "未知 wheel" in document and "系统 Python" in document

