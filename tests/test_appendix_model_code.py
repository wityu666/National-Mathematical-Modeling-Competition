from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_QUESTION_COUNT = 3


def read(relative_path: str) -> str:
    return (SUITE_ROOT / relative_path).read_text(encoding="utf-8")


def test_skeleton_requires_key_modeling_code_in_appendix() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    appendix = skeleton.split("## 附录", 1)[1].split("## 提交前同步表", 1)[0]

    # 锁：附录必须有独立的关键建模代码与运行说明小节。
    assert "### B. 关键建模代码与运行说明" in appendix
    # 锁：关键代码必须来自最终模型、求解结果或关键验证。
    assert "实际生成最终模型、求解结果或关键验证的建模代码" in appendix
    # 锁：三个问题都必须有可定位的关键代码登记项。
    assert appendix.count("`CODE-Q") >= EXPECTED_QUESTION_COUNT
    for question in ("问题一", "问题二", "问题三"):
        # 锁：每个问题都必须有独立的关键代码展示位置。
        assert f"{question}关键代码" in appendix
    # 锁：附录代码必须映射回冻结运行和正文证据。
    assert "MODEL/RUN/RID/FIG/TAB" in appendix and "冻结版本" in appendix
    # 锁：代码必须以文本提供，不能用截图代替。
    assert "可复制文本" in appendix and "不使用代码截图" in appendix
    # 锁：完整工程仍须在支撑材料中提供并记录哈希。
    assert "完整源代码在支撑材料中的相对路径与 SHA-256" in appendix


def test_appendix_code_gate_reaches_writer_layout_and_auditor() -> None:
    writer = read("cumcm-live-paper-writer/SKILL.md")
    layout = read("cumcm-live-layout-verifier/SKILL.md")
    layout_report = read("cumcm-live-layout-verifier/assets/layout-report.md")
    auditor = read("cumcm-live-final-auditor/SKILL.md")
    audit_report = read("cumcm-live-final-auditor/assets/audit-report-template.md")

    # 锁：写作阶段必须把关键建模代码作为附录硬门。
    assert "附录必须收录实际参与最终模型、求解结果或关键验证的建模代码" in writer
    # 锁：写作完成条件必须核对关键代码与冻结版本和正文结果的映射。
    assert "附录已收录关键建模代码" in writer and "冻结版本和正文结果" in writer
    # 锁：排版复核必须检查代码是可复制文本且清晰可读。
    assert "附录关键建模代码使用可复制的等宽文本而非截图" in layout
    # 锁：排版报告必须记录代码页面的视觉与复制抽查证据。
    assert "附录关键建模代码清晰可读且不是截图" in layout_report
    # 锁：终审必须把完全缺少关键建模代码升级为 P0。
    assert "附录完全缺少关键建模代码" in auditor and "按 `P0` 处理" in auditor
    # 锁：终审报告必须提供代码到冻结源和结果证据的逐项核对表。
    assert "## 附录关键建模代码核对" in audit_report


def test_appendix_code_policy_preserves_body_and_support_package_boundaries() -> None:
    skeleton = read("cumcm-live-paper-writer/assets/cumcm-paper-skeleton.md")
    writer = read("cumcm-live-paper-writer/SKILL.md")
    patterns = read(
        "cumcm-live-paper-writer/references/abc-award-paper-writing-patterns.md"
    )

    # 锁：关键结论、关键验证和复现入口仍必须保留在正文。
    assert "核心结论、关键验证和复现入口必须留在正文" in skeleton
    # 锁：完整工程应放支撑材料，不能用附录代码片段替代正式源文件。
    assert "完整工程放入支撑材料" in writer
    # 锁：通用导包、绘图和未采用算法不能冒充关键建模代码。
    for noncore in ("导包", "通用绘图", "未采用算法"):
        assert noncore in writer
    # 锁：写作模式手册必须保持正文、附录和支撑材料的边界。
    assert "论文附录中实际生成最终模型" in patterns
    assert "支撑材料中的完整代码" in patterns
