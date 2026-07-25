import json
import subprocess
import sys
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "layout_preflight.py"


def run_preflight(pdf: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(pdf),
            "--json",
            "--skip-external-tools",
            *extra,
        ],
        check=False,
        text=True,
        capture_output=True,
    )


def write_minimal_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n")


def test_safe_pdf_and_source_only_precheck_pass(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    source = tmp_path / "paper.tex"
    write_minimal_pdf(pdf)
    source.write_text(r"\section{Model} Final content.", encoding="utf-8")

    result = run_preflight(pdf, "--source", str(source))
    report = json.loads(result.stdout)

    assert result.returncode == 0
    assert report["status"] == "PRECHECK_PASS"
    assert report["visual_qa_required"] is True


def test_invalid_pdf_header_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"not a pdf\n%%EOF\n")

    result = run_preflight(pdf)
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert any(item["code"] == "invalid-pdf-header" for item in report["issues"])


def test_placeholder_in_source_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    source = tmp_path / "paper.tex"
    write_minimal_pdf(pdf)
    source.write_text("结论为【待复核】。", encoding="utf-8")

    result = run_preflight(pdf, "--source", str(source))
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert any(item["code"] == "placeholder" for item in report["issues"])


def test_latex_log_hard_warning_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    source = tmp_path / "source"
    source.mkdir()
    write_minimal_pdf(pdf)
    (source / "paper.log").write_text(
        "LaTeX Warning: There were undefined references.\n"
        "Overfull \\hbox (10.0pt too wide)\n",
        encoding="utf-8",
    )

    result = run_preflight(pdf, "--source", str(source))
    report = json.loads(result.stdout)
    codes = {item["code"] for item in report["issues"]}

    assert result.returncode == 1
    assert {"undefined-reference", "overfull-box"}.issubset(codes)


def test_docx_comments_and_tracked_changes_are_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    docx = tmp_path / "paper.docx"
    write_minimal_pdf(pdf)
    with zipfile.ZipFile(docx, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="x"><w:body><w:ins><w:t>text</w:t></w:ins>'
            '<w:commentRangeStart w:id="0"/></w:body></w:document>',
        )
        archive.writestr("word/comments.xml", "<w:comments/>")

    result = run_preflight(pdf, "--source", str(docx))
    report = json.loads(result.stdout)
    codes = {item["code"] for item in report["issues"]}

    assert result.returncode == 1
    assert "word-tracked-changes" in codes
    assert "word-comments" in codes


def test_missing_pdf_path_returns_exit_2(tmp_path: Path) -> None:
    result = run_preflight(tmp_path / "missing.pdf")

    assert result.returncode == 2
    assert "不存在" in result.stderr
