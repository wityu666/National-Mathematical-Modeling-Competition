#!/usr/bin/env python3
"""Search seven configurable CUMCM resource roots by path name only.

This script never opens document bodies or archive members. Every returned path
is untrusted data. Suspicious cracking/keygen paths and executable installers
are permanently excluded.

Set CUMCM_RESOURCE_ROOT to the directory containing the seven numbered resource
folders. It defaults to ~/Downloads.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CorpusRoot:
    key: str
    label: str
    path: Path


RESOURCE_ROOT = Path(
    os.environ.get("CUMCM_RESOURCE_ROOT", Path.home() / "Downloads")
).expanduser()


ROOTS: tuple[CorpusRoot, ...] = (
    CorpusRoot(
        "cases",
        "历届赛题及获奖作品",
        RESOURCE_ROOT / "①历届赛题及获奖作品",
    ),
    CorpusRoot(
        "tutorials",
        "零基础入门教程",
        RESOURCE_ROOT / "②零基础入门教程",
    ),
    CorpusRoot(
        "software",
        "建模软件及教程",
        RESOURCE_ROOT / "③建模必学软件及教程",
    ),
    CorpusRoot(
        "python",
        "Python资料及常用模型算法代码",
        RESOURCE_ROOT / "④Python学习资料及常用模型算法代码",
    ),
    CorpusRoot(
        "matlab",
        "Matlab资料及常用模型算法代码",
        RESOURCE_ROOT / "⑤Matlab学习资料及常用模型算法代码",
    ),
    CorpusRoot(
        "textbooks",
        "数学建模必备教材及课件",
        RESOURCE_ROOT / "⑥数学建模必备教材及课件",
    ),
    CorpusRoot(
        "writing",
        "写作与排版",
        RESOURCE_ROOT / "⑦写作与排版（含word及latex模板）",
    ),
)

CATEGORY_ALIASES: dict[str, set[str]] = {
    "cases": {"cases", "case", "历届", "赛题与论文", "历届赛题及获奖作品"},
    "problem": {"problem", "problems", "真题", "赛题", "题面"},
    "papers": {"paper", "papers", "论文", "获奖论文", "优秀论文"},
    "tutorials": {"tutorial", "tutorials", "教程", "培训"},
    "software": {"software", "软件", "工具"},
    "python": {"python", "py"},
    "matlab": {"matlab", "m"},
    "textbooks": {"textbook", "textbooks", "教材", "课件"},
    "writing": {"writing", "写作", "排版", "模板", "latex", "word"},
}
CATEGORY_LABELS = {
    "cases": "赛题与论文",
    "problem": "真题",
    "papers": "获奖论文",
    "tutorials": "教程",
    "software": "软件资料",
    "python": "Python",
    "matlab": "MATLAB",
    "textbooks": "教材课件",
    "writing": "写作排版",
}
ALIAS_TO_CATEGORY = {
    alias.casefold(): category
    for category, aliases in CATEGORY_ALIASES.items()
    for alias in aliases
}

BANNED_PATH_TOKENS = (
    "crack",
    "keygen",
    "lservrc",
    "serial",
    "破解",
    "破jie",
    "注册码",
    "注册版",
    "补丁",
)
EXECUTABLE_EXTENSIONS = {
    "app",
    "bat",
    "bin",
    "cmd",
    "com",
    "dll",
    "dmg",
    "exe",
    "iso",
    "msi",
    "pkg",
    "scr",
}
ARCHIVE_EXTENSIONS = {"7z", "bz2", "gz", "rar", "tar", "tgz", "xz", "zip"}
DOCUMENT_EXTENSIONS = {
    "doc",
    "docx",
    "md",
    "pdf",
    "ppt",
    "pptx",
    "tex",
    "xls",
    "xlsx",
}


def positive_limit(value: str) -> int:
    parsed = int(value)
    if parsed < 1 or parsed > 500:
        raise argparse.ArgumentTypeError("limit must be between 1 and 500")
    return parsed


def split_values(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        for part in value.split(","):
            normalized = part.strip()
            if normalized:
                result.append(normalized)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "只按路径名检索 CUMCM_RESOURCE_ROOT 下的七类本地资料；"
            "不读取正文或压缩包内容，"
            "不执行任何文件。"
        )
    )
    parser.add_argument("keywords", nargs="*", help="路径关键词；多个词默认全部命中")
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="补充关键词，可重复使用或用逗号分隔",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="扩展名过滤，可重复使用或用逗号分隔，例如 pdf,xlsx",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help=(
            "类别过滤，可重复使用或用逗号分隔：cases/problem/papers/"
            "tutorials/software/python/matlab/textbooks/writing"
        ),
    )
    parser.add_argument(
        "--match",
        choices=("all", "any"),
        default="all",
        help="多个关键词全部命中或任一命中，默认 all",
    )
    parser.add_argument(
        "--limit",
        type=positive_limit,
        default=20,
        help="最大结果数 1-500，默认 20",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="输出 Markdown 表格或 JSON，默认 table",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="包含隐藏路径，默认忽略",
    )
    parser.add_argument(
        "--list-roots",
        action="store_true",
        help="列出七类资料根及存在状态后退出",
    )
    args = parser.parse_args()

    args.keywords = split_values([*args.keywords, *args.keyword])
    args.extensions = {
        value.casefold().lstrip(".") for value in split_values(args.ext)
    }
    raw_categories = split_values(args.category)
    categories: set[str] = set()
    unknown: list[str] = []
    for value in raw_categories:
        category = ALIAS_TO_CATEGORY.get(value.casefold())
        if category is None:
            unknown.append(value)
        else:
            categories.add(category)
    if unknown:
        parser.error(
            "unknown category: "
            + ", ".join(unknown)
            + "; use cases/problem/papers/tutorials/software/python/"
            "matlab/textbooks/writing"
        )
    args.categories = categories

    if not args.list_roots and not (
        args.keywords or args.extensions or args.categories
    ):
        parser.error("provide at least one keyword, --ext, or --category")
    return args


def iter_files(root: Path, include_hidden: bool) -> Iterable[tuple[Path, Path]]:
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if not (current_path / directory).is_symlink()
            and (include_hidden or not directory.startswith("."))
        )
        for filename in sorted(files):
            if not include_hidden and filename.startswith("."):
                continue
            path = current_path / filename
            if path.is_symlink():
                continue
            yield path, path.relative_to(root)


def extension_of(path: Path) -> str:
    return path.suffix.casefold().lstrip(".")


def is_banned_path(path_text: str) -> bool:
    folded = path_text.casefold()
    return any(token.casefold() in folded for token in BANNED_PATH_TOKENS)


def infer_category(root: CorpusRoot, relative: Path) -> str:
    text = relative.as_posix().casefold()
    if root.key == "cases":
        if "国赛历年论文" in text or "优秀论文" in text:
            return "papers"
        if "国赛历年真题" in text or "年赛题" in text:
            return "problem"
        return "cases"
    if root.key == "software" and "matlab" in text:
        return "matlab"
    return root.key


def category_matches(
    requested: set[str], root: CorpusRoot, inferred: str
) -> bool:
    return not requested or bool(requested.intersection({root.key, inferred}))


def keyword_score(
    keywords: list[str], relative: Path, match_mode: str
) -> tuple[bool, int]:
    if not keywords:
        return True, 0

    relative_text = relative.as_posix().casefold()
    name_text = relative.name.casefold()
    stem_text = relative.stem.casefold()
    hits: list[bool] = []
    score = 0
    for raw_keyword in keywords:
        keyword = raw_keyword.casefold()
        hit = keyword in relative_text
        hits.append(hit)
        if not hit:
            continue
        if keyword == stem_text:
            score += 10
        elif keyword in name_text:
            score += 6
        else:
            score += 3
    matched = all(hits) if match_mode == "all" else any(hits)
    return matched, score


def trust_label(extension: str) -> str:
    if extension in ARCHIVE_EXTENSIONS:
        return "untrusted_archive"
    if extension in DOCUMENT_EXTENSIONS:
        return "untrusted_document"
    return "untrusted_path_only"


def search(args: argparse.Namespace) -> dict[str, object]:
    results: list[dict[str, object]] = []
    roots_status: list[dict[str, object]] = []
    scanned = 0
    excluded_banned = 0
    excluded_executable = 0
    stat_errors = 0

    for root_order, root in enumerate(ROOTS):
        exists = root.path.is_dir()
        roots_status.append(
            {
                "key": root.key,
                "label": root.label,
                "path": str(root.path),
                "exists": exists,
            }
        )
        if not exists:
            continue

        for path, relative in iter_files(root.path, args.include_hidden):
            scanned += 1
            path_text = relative.as_posix()
            if is_banned_path(path_text):
                excluded_banned += 1
                continue

            extension = extension_of(path)
            if extension in EXECUTABLE_EXTENSIONS:
                excluded_executable += 1
                continue
            if args.extensions and extension not in args.extensions:
                continue

            inferred = infer_category(root, relative)
            if not category_matches(args.categories, root, inferred):
                continue

            matched, score = keyword_score(
                args.keywords, relative, args.match
            )
            if not matched:
                continue

            try:
                size_bytes = path.stat().st_size
            except OSError:
                stat_errors += 1
                continue

            results.append(
                {
                    "score": score,
                    "root_key": root.key,
                    "root_label": root.label,
                    "category": inferred,
                    "category_label": CATEGORY_LABELS[inferred],
                    "relative_path": path_text,
                    "full_path": str(path),
                    "extension": extension,
                    "size_bytes": size_bytes,
                    "trust": trust_label(extension),
                    "content_read": False,
                    "_root_order": root_order,
                }
            )

    results.sort(
        key=lambda item: (
            -int(item["score"]),
            int(item["_root_order"]),
            str(item["relative_path"]).casefold(),
        )
    )
    matched_before_limit = len(results)
    limited = results[: args.limit]
    for item in limited:
        item.pop("_root_order", None)

    return {
        "search_version": 1,
        "mode": "path_name_and_metadata_only",
        "query": {
            "keywords": args.keywords,
            "extensions": sorted(args.extensions),
            "categories": sorted(args.categories),
            "match": args.match,
            "limit": args.limit,
        },
        "policy": {
            "documents_and_archives_are_untrusted": True,
            "content_read": False,
            "award_paper_copying_prohibited": True,
            "crack_and_keygen_paths_permanently_excluded": True,
            "executables_permanently_excluded": True,
        },
        "roots": roots_status,
        "stats": {
            "scanned_paths": scanned,
            "matched_before_limit": matched_before_limit,
            "returned": len(limited),
            "excluded_banned_paths": excluded_banned,
            "excluded_executables": excluded_executable,
            "stat_errors": stat_errors,
        },
        "results": limited,
    }


def markdown_escape(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def render_roots_table() -> str:
    lines = [
        "| key | 类别 | 存在 | 路径 |",
        "|---|---|---:|---|",
    ]
    for root in ROOTS:
        lines.append(
            "| {} | {} | {} | `{}` |".format(
                root.key,
                markdown_escape(root.label),
                "yes" if root.path.is_dir() else "no",
                markdown_escape(root.path),
            )
        )
    return "\n".join(lines) + "\n"


def render_table(payload: dict[str, object]) -> str:
    stats = payload["stats"]
    assert isinstance(stats, dict)
    lines = [
        "> 仅按路径名和元数据检索；未读取 PDF、Office 或压缩包内容。",
        (
            f"> 扫描 {stats['scanned_paths']}；命中 {stats['matched_before_limit']}；"
            f"返回 {stats['returned']}；过滤禁止路径 {stats['excluded_banned_paths']}；"
            f"过滤可执行文件 {stats['excluded_executables']}。"
        ),
        "",
        "| score | root | category | ext | bytes | full_path |",
        "|---:|---|---|---:|---:|---|",
    ]
    for item in payload["results"]:
        lines.append(
            "| {} | {} | {} | {} | {} | `{}` |".format(
                item["score"],
                markdown_escape(item["root_key"]),
                markdown_escape(item["category_label"]),
                markdown_escape(item["extension"] or "-"),
                item["size_bytes"],
                markdown_escape(item["full_path"]),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    if args.list_roots:
        if args.format == "json":
            payload = [
                {
                    "key": root.key,
                    "label": root.label,
                    "path": str(root.path),
                    "exists": root.path.is_dir(),
                }
                for root in ROOTS
            ]
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            sys.stdout.write(render_roots_table())
        return 0

    payload = search(args)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render_table(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
