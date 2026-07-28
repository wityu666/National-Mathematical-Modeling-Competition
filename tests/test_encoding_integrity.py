from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".m", ".yaml", ".yml", ".txt"}
ROOT_TEXT_FILES = {"LICENSE", ".gitignore"}
CJK_START = "\u4e00"
CJK_END = "\u9fff"
# 阈值依据：33 个中文主文档实测最小占比 0.260702，留余量至 0.15。
MIN_CJK_RATIO = 0.15


def relative(path: Path) -> str:
    return path.relative_to(SUITE_ROOT).as_posix()


def repository_text_files() -> list[Path]:
    return sorted(
        path
        for path in SUITE_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and (
            path.suffix.lower() in TEXT_SUFFIXES
            or (path.parent == SUITE_ROOT and path.name in ROOT_TEXT_FILES)
        )
    )


def chinese_document_files() -> list[Path]:
    files = {SUITE_ROOT / "README.md", SUITE_ROOT / "SUITE.md"}
    files.update(SUITE_ROOT.glob("cumcm-live-*/SKILL.md"))
    files.update(SUITE_ROOT.glob("cumcm-live-*/references/*.md"))
    files.update(SUITE_ROOT.glob("cumcm-live-*/assets/*.md"))
    return sorted(files)


def decode_strict(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise AssertionError(
            f"{relative(path)}: UTF-8 严格解码失败，"
            f"首个坏字节位置={error.start}，原因={error.reason}"
        ) from error


def cjk_ratio(text: str) -> float:
    compact = "".join(text.split())
    if not compact:
        return 0.0
    cjk_count = sum(CJK_START <= character <= CJK_END for character in compact)
    return cjk_count / len(compact)


def test_repository_text_files_have_clean_utf8() -> None:
    files = repository_text_files()

    # 锁：编码守卫必须实际覆盖仓库中的白名单文本文件。
    assert files, "未收集到任何待检查文本文件"
    for path in files:
        text = decode_strict(path)
        replacement_index = text.find("\ufffd")
        # 锁：有损解码固化的替换字符不得进入任何受检文本。
        assert replacement_index == -1, (
            f"{relative(path)}: 含 U+FFFD 替换字符，"
            f"首个异常字符位置={replacement_index}"
        )
        # 锁：UTF-8 BOM 不得干扰 YAML、Markdown 或脚本解析。
        assert not text.startswith("\ufeff"), (
            f"{relative(path)}: 文件以 U+FEFF BOM 开头，异常位置=0"
        )
        first_control = next(
            (
                (index, character)
                for index, character in enumerate(text)
                if ord(character) < 0x20 and character not in "\n\t"
            ),
            None,
        )
        # 锁：乱码伴随的非法 C0 控制字符不得潜入文本资产。
        assert first_control is None, (
            f"{relative(path)}: 含非法 C0 控制字符 "
            f"U+{ord(first_control[1]):04X}，"
            f"首个异常字符位置={first_control[0]}"
            if first_control is not None
            else ""
        )
        # 锁：受检文本必须含有实际内容，不能以空文件占位。
        assert text, f"{relative(path)}: 文件为空"
        # 锁：所有文本必须以换行结尾，避免拼接和差异工具异常。
        assert text.endswith("\n"), (
            f"{relative(path)}: 文件末尾缺少换行符，"
            f"最后字符位置={len(text) - 1}"
        )


def test_chinese_documents_keep_minimum_cjk_ratio() -> None:
    files = chinese_document_files()
    ratios = [(path, cjk_ratio(decode_strict(path))) for path in files]

    # 锁：中文占比守卫必须覆盖 README、SUITE 和全部中文 Skill 文档资产。
    assert files, "未收集到任何中文主文档"
    for path, ratio in ratios:
        # 锁：合法 UTF-8 但整体转码成乱码的中文文档必须被占比门拦截。
        assert ratio >= MIN_CJK_RATIO, (
            f"{relative(path)}: CJK 占比 {ratio:.6f} "
            f"低于阈值 {MIN_CJK_RATIO:.2f}"
        )
