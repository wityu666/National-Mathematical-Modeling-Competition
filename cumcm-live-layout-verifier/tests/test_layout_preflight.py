import json
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "layout_preflight.py"
EXIT_OK = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 2
DEFAULT_MIN_MAIN_PAGES = 26
DEFAULT_MAX_MAIN_PAGES = 30
UNDER_FLOOR_BODY_PAGES = 25
OVER_LIMIT_BODY_PAGES = 31
EXPECTED_APPENDIX_PAGES = 17
NO_APPENDIX_PAGES = 0
OFFICIAL_CAP_PAGES = 20
OFFICIAL_AUTO_FLOOR = 1
EXPECTED_UNEMBEDDED_FONT_COUNT = 1


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("layout_preflight", SCRIPT)
    # 锁：排版预检脚本必须能被测试环境安全加载。
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_safe_pdf_without_page_or_appendix_evidence_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    source = tmp_path / "paper.tex"
    write_minimal_pdf(pdf)
    source.write_text(r"\section{Model} Final content.", encoding="utf-8")

    result = run_preflight(pdf, "--source", str(source))
    report = json.loads(result.stdout)

    # 锁：干净文件不能绕过正文页数与附录代码两项硬门。
    assert result.returncode == EXIT_BLOCKED
    # 锁：缺少硬门证据时总体状态必须为 BLOCKED。
    assert report["status"] == "BLOCKED"
    # 锁：静态预检不能替代后续真实视觉 QA。
    assert report["visual_qa_required"] is True
    # 锁：预检报告必须保留默认正文页数下限。
    assert report["page_limit"]["min_main_pages"] == DEFAULT_MIN_MAIN_PAGES
    # 锁：预检报告必须保留默认正文页数上限。
    assert report["page_limit"]["max_main_pages"] == DEFAULT_MAX_MAIN_PAGES
    # 锁：工具不得默认从 PDF 第 1 页计数而把摘要误算进正文。
    assert report["page_limit"]["main_start_pdf_page"] is None
    # 锁：未知页边界必须产生 P0，而不是仅留下不阻断的警告。
    assert any(item["code"] == "page-limit-unverified" for item in report["issues"])
    # 锁：未登记附录关键代码页必须产生稳定 P0 问题码。
    assert any(
        item["code"] == "appendix-key-model-code-missing"
        for item in report["issues"]
    )


def test_invalid_pdf_header_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"not a pdf\n%%EOF\n")

    result = run_preflight(pdf)
    report = json.loads(result.stdout)

    # 锁：无效 PDF 头必须阻断预检。
    assert result.returncode == EXIT_BLOCKED
    # 锁：无效 PDF 头必须产生稳定问题码。
    assert any(item["code"] == "invalid-pdf-header" for item in report["issues"])


def test_placeholder_in_source_is_blocked(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    source = tmp_path / "paper.tex"
    write_minimal_pdf(pdf)
    source.write_text("结论为【待复核】。", encoding="utf-8")

    result = run_preflight(pdf, "--source", str(source))
    report = json.loads(result.stdout)

    # 锁：源文件仍含占位符时必须阻断。
    assert result.returncode == EXIT_BLOCKED
    # 锁：占位符问题必须以稳定问题码记录。
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

    # 锁：LaTeX 未定义引用或溢出版面必须阻断。
    assert result.returncode == EXIT_BLOCKED
    # 锁：LaTeX 日志必须同时识别引用和 overfull 风险。
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

    # 锁：Word 修订或批注残留必须阻断提交。
    assert result.returncode == EXIT_BLOCKED
    # 锁：Word 修订必须单独分类。
    assert "word-tracked-changes" in codes
    # 锁：Word 批注必须单独分类。
    assert "word-comments" in codes


def test_missing_pdf_path_returns_exit_2(tmp_path: Path) -> None:
    result = run_preflight(tmp_path / "missing.pdf")

    # 锁：不存在的 PDF 路径必须返回参数错误。
    assert result.returncode == EXIT_USAGE
    # 锁：错误信息必须能直接说明路径不存在。
    assert "不存在" in result.stderr


def test_pdffonts_fixed_width_parser_detects_unembedded_font() -> None:
    module = load_preflight_module()
    output = (
        "name                                 type              encoding         emb sub uni object ID\n"
        "------------------------------------ ----------------- ---------------- --- --- --- ---------\n"
        "ABCDEE+CMR10                        Type 1            Builtin          yes yes yes      5  0\n"
        "SimSun                               TrueType          WinAnsi          no  no  yes      8  0\n"
    )

    unembedded = module.find_unembedded_fonts(output)

    # 锁：固定宽度解析器必须只识别真正未嵌入的字体。
    assert len(unembedded) == EXPECTED_UNEMBEDDED_FONT_COUNT
    # 锁：未嵌入字体报告必须保留具体字体名。
    assert "SimSun" in unembedded[0]


def test_26_body_pages_excluding_front_matter_with_unlimited_appendix_passes(
    tmp_path: Path,
) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=47,
        main_start_page=5,
        appendix_start_page=31,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=2,
    )

    # 锁：正文恰达下限且附录较长时仍须通过。
    assert result["status"] == "PASS"
    # 锁：页数结果必须回显默认下限。
    assert result["min_main_pages"] == DEFAULT_MIN_MAIN_PAGES
    # 锁：页数结果必须回显默认上限。
    assert result["max_main_pages"] == DEFAULT_MAX_MAIN_PAGES
    # 锁：摘要、关键词和目录等前置页不得计入 26 页编号正文。
    assert result["main_body_pages"] == DEFAULT_MIN_MAIN_PAGES
    # 锁：页数报告必须明确摘要页不计入编号正文。
    assert result["abstract_pages_counted"] is False
    # 锁：页数报告必须明确使用第一章到附录前一页的计算口径。
    assert result["count_basis"] == "first_numbered_body_page_to_before_appendix"
    # 锁：附录页数必须保持无硬上限。
    assert result["appendix_page_limit"] is None
    # 锁：附录页数不限但必须正确计算。
    assert result["appendix_pages"] == EXPECTED_APPENDIX_PAGES
    # 锁：合法下限案例不得生成页数问题。
    assert issues == []


def test_25_body_pages_is_blocked_by_page_floor(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=46,
        main_start_page=5,
        appendix_start_page=30,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=2,
    )

    # 锁：正文低于下限一页必须阻断。
    assert result["status"] == "BLOCKED"
    # 锁：下限案例必须准确计算为 25 页。
    assert result["main_body_pages"] == UNDER_FLOOR_BODY_PAGES
    # 锁：低于下限必须产生稳定问题码。
    assert any(item["code"] == "main-body-under-page-floor" for item in issues)
    # 锁：正文低于下限必须按 P0 处理。
    assert any(item["severity"] == "P0" for item in issues)


def test_30_body_pages_with_unlimited_appendix_passes(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=51,
        main_start_page=5,
        appendix_start_page=35,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=2,
    )

    # 锁：正文恰达 30 页上限时必须通过。
    assert result["status"] == "PASS"
    # 锁：上限案例必须准确计算为 30 页。
    assert result["main_body_pages"] == DEFAULT_MAX_MAIN_PAGES
    # 锁：正文上限不限制独立附录页数。
    assert result["appendix_pages"] == EXPECTED_APPENDIX_PAGES
    # 锁：合法上限案例不得生成页数问题。
    assert issues == []


def test_31_body_pages_is_blocked_even_with_appendix(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=52,
        main_start_page=5,
        appendix_start_page=36,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=2,
    )

    # 锁：正文超过上限一页必须阻断。
    assert result["status"] == "BLOCKED"
    # 锁：超上限案例必须准确计算为 31 页。
    assert result["main_body_pages"] == OVER_LIMIT_BODY_PAGES
    # 锁：超过上限必须产生稳定问题码。
    assert any(item["code"] == "main-body-over-page-limit" for item in issues)


def test_no_appendix_counts_body_through_last_page(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=35,
        main_start_page=5,
        appendix_start_page=None,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=2,
    )

    # 锁：没有附录时附录页数必须归零。
    assert result["appendix_pages"] == NO_APPENDIX_PAGES
    # 锁：没有附录时正文必须计算到 PDF 最后一页。
    assert result["main_body_pages"] == OVER_LIMIT_BODY_PAGES
    # 锁：无附录的 31 页正文仍必须阻断。
    assert result["status"] == "BLOCKED"


def test_cli_cannot_relax_30_page_hard_limit(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    write_minimal_pdf(pdf)

    result = run_preflight(pdf, "--max-main-pages", "31")

    # 锁：命令行不得把 30 页内部上限放宽到 31 页。
    assert result.returncode == EXIT_USAGE
    # 锁：错误信息必须明确不能放宽 30 页硬门。
    assert "不能放宽 30 页硬门" in result.stderr


def test_missing_abstract_boundary_blocks_page_gate(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=47,
        main_start_page=5,
        appendix_start_page=31,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
    )

    # 锁：未记录摘要结束页时必须阻断，不能把 UNVERIFIED 当作可继续状态。
    assert result["status"] == "BLOCKED"
    # 锁：摘要排除证据缺失时不得计算可通过的正文页数。
    assert result["main_body_pages"] is None
    # 锁：摘要边界缺失必须生成稳定 P0 问题码。
    assert any(item["code"] == "abstract-boundary-unverified" for item in issues)


def test_abstract_end_page_must_precede_first_body_page(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=47,
        main_start_page=5,
        appendix_start_page=31,
        min_main_pages=26,
        max_main_pages=30,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=5,
    )

    # 锁：摘要结束页不得与编号正文第一章起始页重叠。
    assert result["status"] == "BLOCKED"
    # 锁：错误摘要边界必须产生稳定问题码。
    assert any(item["code"] == "invalid-abstract-body-boundary" for item in issues)


def test_cli_rejects_minimum_above_maximum(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    write_minimal_pdf(pdf)

    result = run_preflight(
        pdf,
        "--min-main-pages",
        "30",
        "--max-main-pages",
        "29",
    )

    # 锁：正文下限高于上限的参数组合必须拒绝。
    assert result.returncode == EXIT_USAGE
    # 锁：参数错误信息必须说明上下限顺序。
    assert "--min-main-pages 不能高于 --max-main-pages" in result.stderr


def test_cli_cannot_lower_floor_without_official_cap_below_26(
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "paper.pdf"
    write_minimal_pdf(pdf)

    result = run_preflight(
        pdf,
        "--min-main-pages",
        "25",
        "--max-main-pages",
        "30",
    )

    # 锁：官方上限未低于 26 页时不得降低默认下限。
    assert result.returncode == EXIT_USAGE
    # 锁：错误信息必须说明降低下限所需的官方低上限条件。
    assert "仅当 --max-main-pages 同时低于 26" in result.stderr


def test_human_output_displays_allowed_page_range(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    write_minimal_pdf(pdf)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(pdf),
            "--skip-external-tools",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    # 锁：未提供页数边界和附录代码定位时，人类可读模式也必须阻断。
    assert result.returncode == EXIT_BLOCKED
    # 锁：人类输出必须显示正文页数允许区间。
    assert "main_body_pages=None allowed_range=26–30" in result.stdout
    # 锁：人类可读输出必须显示附录关键代码尚未核验。
    assert "appendix_code_status=BLOCKED" in result.stdout


def test_appendix_key_model_code_page_inside_appendix_is_declared(
    tmp_path: Path,
) -> None:
    module = load_preflight_module()
    issues = []

    result = module.evaluate_appendix_code_locator(
        total_pages=47,
        appendix_start_page=31,
        appendix_code_page=32,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
    )

    # 锁：主要建模代码页位于附录范围内时允许进入人工逐页确认。
    assert result["status"] == "DECLARED"
    # 锁：静态定位通过不能替代 Round B 对代码内容的视觉核验。
    assert result["visual_confirmation_required"] is True
    # 锁：合法附录代码定位不得生成问题。
    assert issues == []


def test_missing_appendix_key_model_code_page_is_p0(tmp_path: Path) -> None:
    module = load_preflight_module()
    issues = []

    result = module.evaluate_appendix_code_locator(
        total_pages=47,
        appendix_start_page=31,
        appendix_code_page=None,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
    )

    # 锁：有附录但未登记主要建模代码页时必须阻断。
    assert result["status"] == "BLOCKED"
    # 锁：缺少附录代码定位必须使用稳定问题码并按 P0 处理。
    assert any(
        item["code"] == "appendix-key-model-code-unverified"
        and item["severity"] == "P0"
        for item in issues
    )


def test_official_20_page_cap_allows_matching_20_page_floor(tmp_path: Path) -> None:
    module = load_preflight_module()
    args = module.parse_args(
        [
            str(tmp_path / "paper.pdf"),
            "--max-main-pages",
            "20",
            "--min-main-pages",
            "20",
        ]
    )
    min_pages, max_pages = module.resolve_main_page_range(
        args.min_main_pages,
        args.max_main_pages,
        min_was_explicit=True,
    )
    issues = []
    warnings = []

    result = module.evaluate_page_limit(
        total_pages=36,
        main_start_page=2,
        appendix_start_page=22,
        min_main_pages=min_pages,
        max_main_pages=max_pages,
        pdf=tmp_path / "paper.pdf",
        issues=issues,
        warnings=warnings,
        abstract_end_page=1,
    )

    # 锁：官方 20 页上限可将内部区间收敛为 20–20。
    assert (min_pages, max_pages) == (OFFICIAL_CAP_PAGES, OFFICIAL_CAP_PAGES)
    # 锁：官方低上限案例必须准确计算 20 页正文。
    assert result["main_body_pages"] == OFFICIAL_CAP_PAGES
    # 锁：满足更严格官方上限时必须通过。
    assert result["status"] == "PASS"
    # 锁：合法官方例外不得生成页数问题。
    assert issues == []


def test_official_cap_below_26_auto_disables_default_floor(tmp_path: Path) -> None:
    module = load_preflight_module()

    min_pages, max_pages = module.resolve_main_page_range(
        26,
        20,
        min_was_explicit=False,
    )

    # 锁：官方上限低于 26 页时默认内部下限必须自动失效。
    assert (min_pages, max_pages) == (OFFICIAL_AUTO_FLOOR, OFFICIAL_CAP_PAGES)
