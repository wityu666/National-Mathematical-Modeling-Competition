from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "audit_submission.py"
FIXTURE = Path(__file__).parent / "fixtures" / "fake_submission"


def prepare_submission(
    tmp_path: Path,
    *,
    include_exe: bool = False,
    include_keygen_name: bool = False,
) -> Path:
    submission = tmp_path / "submission"
    shutil.copytree(FIXTURE, submission)
    if not include_exe:
        (submission / "evil.exe").unlink()
    if not include_keygen_name:
        (submission / "注册机.txt").unlink()
    return submission


def run_audit(
    submission: Path,
    *extra_args: str,
) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(submission),
            "--json",
            *extra_args,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout) if completed.stdout else {}
    return completed, report


def test_normal_submission_passes_with_exit_zero(tmp_path: Path) -> None:
    submission = prepare_submission(tmp_path)

    completed, report = run_audit(submission)

    # 锁：正常提交目录必须以退出码 0 完成。
    assert completed.returncode == 0
    # 锁：正常提交目录的总体状态必须为 PASS。
    assert report["status"] == "PASS"
    # 锁：正常提交必须识别到有效 PDF。
    assert report["checks"]["has_valid_pdf"]["passed"] is True
    # 锁：正常提交不得误报危险文件。
    assert report["checks"]["no_dangerous_items"]["passed"] is True


def test_missing_pdf_blocks_has_valid_pdf(tmp_path: Path) -> None:
    submission = prepare_submission(tmp_path)
    (submission / "paper.pdf").unlink()

    completed, report = run_audit(submission)

    # 锁：缺少 PDF 必须以业务阻断退出码返回。
    assert completed.returncode == 1
    # 锁：缺少 PDF 时总体状态必须为 BLOCKED。
    assert report["status"] == "BLOCKED"
    # 锁：缺少 PDF 必须使 has_valid_pdf 检查失败。
    assert report["checks"]["has_valid_pdf"]["passed"] is False


def test_exe_blocks_no_dangerous_items(tmp_path: Path) -> None:
    submission = prepare_submission(tmp_path, include_exe=True)

    completed, report = run_audit(submission)

    # 锁：提交目录含 EXE 时必须阻断。
    assert completed.returncode == 1
    # 锁：EXE 必须使危险项检查失败。
    assert report["checks"]["no_dangerous_items"]["passed"] is False
    evil = next(item for item in report["files"] if item["path"] == "evil.exe")
    # 锁：EXE 文件本身必须被标记为危险。
    assert evil["dangerous"] is True
    # 锁：EXE 风险必须分类为 Windows 可执行文件。
    assert "windows-executable" in evil["risk_flags"]


def test_keygen_name_is_dangerous(tmp_path: Path) -> None:
    submission = prepare_submission(tmp_path, include_keygen_name=True)

    completed, report = run_audit(submission)

    # 锁：文件名含注册机特征时必须阻断。
    assert completed.returncode == 1
    flagged = next(
        item for item in report["files"] if item["path"] == "注册机.txt"
    )
    # 锁：注册机命名文件必须被标记为危险。
    assert flagged["dangerous"] is True
    # 锁：注册机命名风险必须记录 keygen-name 标识。
    assert "keygen-name" in flagged["risk_flags"]


def test_pdf_over_max_size_limit_is_flagged(tmp_path: Path) -> None:
    submission = prepare_submission(tmp_path)

    completed, report = run_audit(
        submission,
        "--max-pdf-mb",
        "0.000001",
    )

    # 锁：PDF 超过声明大小上限时必须阻断。
    assert completed.returncode == 1
    # 锁：超大 PDF 必须使大小门检查失败。
    assert report["checks"]["pdf_size_limit"]["passed"] is False
    pdf = next(item for item in report["files"] if item["path"] == "paper.pdf")
    # 锁：超大 PDF 必须记录稳定风险码。
    assert "pdf-over-size-limit" in pdf["risk_flags"]


def test_nonexistent_directory_returns_exit_two(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"

    completed, report = run_audit(missing)

    # 锁：不存在的输入路径必须返回参数错误退出码 2。
    assert completed.returncode == 2
    # 锁：参数错误不得伪造审计报告。
    assert report == {}
    # 锁：不存在路径的错误信息必须可直接定位原因。
    assert "directory does not exist" in completed.stderr
