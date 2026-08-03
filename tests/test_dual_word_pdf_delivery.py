from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
DUAL_HASH_FIELDS = ("docx_sha256", "pdf_sha256")
PAIR_CONTENT_MARKERS = ("题目", "摘要", "关键词", "关键数值", "附录")


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_paper_writer_requires_word_and_pdf_from_one_freeze() -> None:
    skill = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：最终交付必须同时包含真实可编辑 Word 与冻结 PDF，而非二选一。
    assert "可编辑 `.docx`" in skill and "冻结 `.pdf`" in skill
    # 锁：两版必须绑定同一冻结稿，不能独立编辑后仅做表面同步。
    assert "两版共享同一 `paper_freeze_id`" in skill
    assert "不得把两版当作两份独立稿件分别修改" in skill
    # 锁：骨架内部控制表必须留下双文件与双哈希证据。
    assert "| Word 交付版 |" in skeleton and "| PDF 冻结版 |" in skeleton
    for field in DUAL_HASH_FIELDS:
        assert field in skeleton, field


def test_word_and_latex_routes_keep_explicit_pdf_lineage() -> None:
    skill = read("cumcm-live-paper-writer/SKILL.md")

    # 锁：Word 主路线的 PDF 必须直接从当前冻结 Word 导出。
    assert "由该冻结 Word 主稿导出 PDF" in skill
    # 锁：LaTeX 主路线仍须生成 Word 伴随版，但不能虚构逐页像素一致。
    assert "docx_role=editable_companion" in skill
    assert "两版不要求逐页像素一致" in skill
    # 锁：无论路线都必须记录 PDF 的真实生成源。
    assert "pdf_generation_source" in skill


def test_layout_contract_binds_pair_hashes_and_editability() -> None:
    skill = read("cumcm-live-layout-verifier/SKILL.md")
    report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    protocol = read(
        "cumcm-live-layout-verifier/references/layout-verification-protocol.md"
    )

    for field in ("paper_freeze_id", *DUAL_HASH_FIELDS, "pdf_generation_source"):
        # 锁：排版 PASS 必须绑定双版本身份与生成链。
        assert field in skill and field in report, field
    # 锁：Word 不能只通过存在性检查，必须实际打开并验证可编辑。
    assert "无修复提示" in skill and "可选择和编辑" in skill
    # 锁：双版本内容一致性必须覆盖主要论文结构与关键证据。
    for marker in PAIR_CONTENT_MARKERS:
        assert marker in protocol, marker
    # 锁：任一文件变化都会使成对 PASS 失效。
    assert "任一文件变化都会失效" in skill


def test_final_auditor_blocks_missing_or_drifted_delivery_version() -> None:
    skill = read("cumcm-live-final-auditor/SKILL.md")
    report = read("cumcm-live-final-auditor/assets/audit-report-template.md")
    protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    # 锁：缺少任一交付版、Word 不可编辑或关键内容漂移必须是 P0。
    assert "缺少 Word/PDF 任一交付版" in skill
    assert "Word 不可编辑" in skill
    assert "双版本冻结标识/哈希/关键内容不一致" in skill
    # 锁：终审报告必须有独立的双版本一致性证据表。
    assert "## Word/PDF 双版本一致性" in report
    for field in ("paper_freeze_id", *DUAL_HASH_FIELDS):
        assert field in report and field in protocol, field


def test_official_submission_bundle_does_not_inherit_local_word_requirement() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    auditor_skill = read("cumcm-live-final-auditor/SKILL.md")
    protocol = read(
        "cumcm-live-final-auditor/references/submission-audit-protocol.md"
    )

    # 锁：本地必须交付 Word，但官方只收 PDF 时不得把 Word 擅自塞入提交包。
    assert "Word 只进入本地交付包" in paper_skill
    assert "不得被上传或压入官方提交包" in protocol
    # 锁：静态目录审计只针对当届规则允许的官方提交候选目录。
    assert "只扫描按当届规则整理的“官方提交候选目录”" in auditor_skill


def test_public_suite_documents_expose_dual_delivery_gate() -> None:
    readme = read("README.md")
    suite = read("SUITE.md")

    for document in (readme, suite):
        # 锁：使用者必须从公共入口知道最终输出是 Word 与 PDF 两版。
        assert "可编辑 `.docx` 与冻结 `.pdf`" in document
        # 锁：公共合同必须公开双哈希和禁止独立改稿要求。
        assert all(field in document for field in DUAL_HASH_FIELDS)
        assert "不得分别修改" in document
        # 锁：公共合同必须区分本地交付与官方提交边界。
        assert "不得混入官方提交包" in document


def test_dual_delivery_change_preserves_existing_paper_gates() -> None:
    paper_skill = read("cumcm-live-paper-writer/SKILL.md")
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")

    # 锁：双版本交付不能放宽 26–30 页正文门或摘要排除规则。
    assert "26 <= main_body_pages <= 30" in paper_skill
    assert "摘要、关键词和目录等正文前置部分不计入" in paper_skill
    # 锁：双版本交付不能删除逐问内容门、亮点与附录关键代码门。
    for gate in ("七项内容门", "CONTRIB-PROVEN", "附录必须收录"):
        assert gate in paper_skill, gate
    assert "| 本问专有假设 |" in skeleton
