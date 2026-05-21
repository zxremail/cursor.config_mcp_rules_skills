#!/usr/bin/env python3
"""
为 Markdown 文档在标题下插入/更新「目录」小节（GitHub / VS Code 锚点兼容）。

已有「## 目录」时：保留现有条目与顺序，仅按正文标题顺序补充未列入的章节。
无目录时：在 # 文档标题后新建完整目录。

用法:
  md-toc.py doc.md                    # 写入文件
  md-toc.py doc1.md doc2.md           # 批量处理
  md-toc.py --dry-run doc.md          # 仅打印将插入的目录块
  md-toc.py --check doc.md            # CI：目录已是最新则退出 0，否则 1
  md-toc.py --stdout doc.md           # 输出完整文档到 stdout，不改文件

选项:
  --max-depth N   目录最大标题级别（默认 3，即含 ###）
  --min-depth N   目录最小标题级别（默认 2，跳过 # 文档标题）
  --title TEXT    目录小节标题（默认「目录」）
  --no-separator  目录后不加 --- 分隔线
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from md_toc_slug import Slugger

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^(```+|~~~+)")
TOC_LINE_RE = re.compile(r"^(\s*)-\s+\[([^\]]+)\]\(#([^)]+)\)\s*$")
CUSTOM_ID_RE = re.compile(r"\s*\{#[^}]+\}\s*$")
INLINE_MD_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


@dataclass
class TocEntry:
    level: int
    title: str
    anchor: str
    raw_line: str


def clean_heading_title(raw: str) -> str:
    title = CUSTOM_ID_RE.sub("", raw.strip())
    title = INLINE_MD_RE.sub(r"\1", title)
    return title.strip()


def _toc_section_pattern(toc_title: str, *, with_separator: bool) -> re.Pattern[str]:
    title = re.escape(toc_title)
    if with_separator:
        body = rf"^##\s+{title}\s*\n.*?(?:^---\s*\n+)"
    else:
        body = rf"^##\s+{title}\s*\n.*?(?=\n##\s+|\Z)"
    return re.compile(body, re.MULTILINE | re.DOTALL)


def parse_toc_entries(toc_body: str, *, min_level: int) -> list[TocEntry]:
    """解析目录正文（不含 ## 目录 与 ---）。"""
    entries: list[TocEntry] = []
    for line in toc_body.splitlines():
        m = TOC_LINE_RE.match(line)
        if not m:
            continue
        spaces, title, anchor = m.group(1), m.group(2), m.group(3)
        indent_units = len(spaces) // 2
        level = min_level + indent_units
        entries.append(TocEntry(level=level, title=title, anchor=anchor, raw_line=line))
    return entries


def extract_toc_section(
    content: str, toc_title: str, *, with_separator: bool
) -> tuple[str, str, str] | None:
    """返回 (前缀, 目录正文含标题行, 后缀) 或 None。"""
    pat = _toc_section_pattern(toc_title, with_separator=with_separator)
    m = pat.search(content)
    if not m:
        return None
    start, end = m.start(), m.end()
    block = m.group(0)
    lines = block.splitlines()
    # 第一行 ## 目录；其余为条目，末尾可能含 ---
    body_lines: list[str] = []
    for line in lines[1:]:
        if with_separator and line.strip() == "---":
            break
        body_lines.append(line)
    header = lines[0] + "\n"
    body = "\n".join(body_lines)
    if body:
        body += "\n"
    return content[:start], header + body, content[end:]


def extract_headings(
    text: str,
    *,
    min_depth: int,
    max_depth: int,
    toc_title: str,
) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    in_fence = False
    fence_marker = ""
    skipping_toc = False

    for line in text.splitlines():
        fence_m = FENCE_RE.match(line)
        if fence_m:
            marker = fence_m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[:3]
            elif line.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue

        if in_fence:
            continue

        if re.match(rf"^##\s+{re.escape(toc_title)}\s*$", line):
            skipping_toc = True
            continue
        if skipping_toc:
            if line.strip() == "---":
                skipping_toc = False
            continue

        hm = HEADING_RE.match(line)
        if not hm:
            continue

        level = len(hm.group(1))
        if level < min_depth or level > max_depth:
            continue

        title = clean_heading_title(hm.group(2))
        if not title:
            continue
        headings.append((level, title))

    return headings


def build_anchor_map(headings: list[tuple[int, str]]) -> dict[str, str]:
    slugger = Slugger()
    return {title: slugger.slug(title) for _, title in headings}


def render_toc_line(
    level: int, title: str, anchor: str, *, min_level: int
) -> str:
    indent = "  " * (level - min_level)
    return f"{indent}- [{title}](#{anchor})"


def render_toc_block(
    entries: list[TocEntry],
    *,
    toc_title: str,
    separator: bool,
) -> str:
    if not entries:
        return ""
    lines = [f"## {toc_title}", ""]
    lines.extend(e.raw_line for e in entries)
    if separator:
        lines.extend(["", "---", ""])
        return "\n".join(lines).rstrip("\n") + "\n\n"
    return "\n".join(lines) + "\n"


def find_insert_index(
    result: list[TocEntry],
    doc_headings: list[tuple[int, str]],
    doc_idx: int,
    existing_titles: set[str],
) -> int:
    """在 result 中确定新条目的插入位置（按正文顺序夹在已有条目之间）。"""
    for i in range(doc_idx - 1, -1, -1):
        title = doc_headings[i][1]
        if title in existing_titles:
            for j, entry in enumerate(result):
                if entry.title == title:
                    return j + 1
            break

    for i in range(doc_idx + 1, len(doc_headings)):
        title = doc_headings[i][1]
        if title in existing_titles:
            for j, entry in enumerate(result):
                if entry.title == title:
                    return j
            break

    return len(result)


def supplement_toc_entries(
    existing: list[TocEntry],
    doc_headings: list[tuple[int, str]],
    anchor_map: dict[str, str],
    *,
    min_level: int,
) -> tuple[list[TocEntry], list[TocEntry]]:
    """
    在已有目录上补充缺失章节。
    返回 (合并后的条目列表, 新增的条目列表)。
    """
    existing_titles = {e.title for e in existing}
    missing_indices = [
        idx
        for idx, (_, title) in enumerate(doc_headings)
        if title not in existing_titles
    ]
    if not missing_indices:
        return existing, []

    result = list(existing)
    added: list[TocEntry] = []

    for doc_idx in missing_indices:
        level, title = doc_headings[doc_idx]
        anchor = anchor_map[title]
        line = render_toc_line(level, title, anchor, min_level=min_level)
        entry = TocEntry(level=level, title=title, anchor=anchor, raw_line=line)
        pos = find_insert_index(
            result, doc_headings, doc_idx, existing_titles
        )
        result.insert(pos, entry)
        existing_titles.add(title)
        added.append(entry)

    return result, added


def build_toc_content(
    content: str,
    doc_headings: list[tuple[int, str]],
    *,
    toc_title: str,
    separator: bool,
    min_depth: int,
) -> tuple[str, list[TocEntry], bool]:
    """
    生成更新后的全文。
    返回 (新全文, 新增条目列表, 是否为新建目录)。
    """
    if not doc_headings:
        return content, [], False

    min_level = min(level for level, _ in doc_headings)
    anchor_map = build_anchor_map(doc_headings)
    section = extract_toc_section(
        content, toc_title, with_separator=separator
    )

    if section is None:
        entries = [
            TocEntry(
                level=level,
                title=title,
                anchor=anchor_map[title],
                raw_line=render_toc_line(
                    level, title, anchor_map[title], min_level=min_level
                ),
            )
            for level, title in doc_headings
        ]
        block = render_toc_block(
            entries, toc_title=toc_title, separator=separator
        )
        h1 = re.search(r"^#\s+.+$", content, re.MULTILINE)
        if h1:
            insert_at = h1.end()
            while insert_at < len(content) and content[insert_at] in "\r\n":
                insert_at += 1
            new_text = content[:insert_at] + "\n\n" + block + content[insert_at:]
        else:
            new_text = block + content
        return new_text, entries, True

    prefix, toc_part, suffix = section
    # toc_part = "## 目录\n" + body
    header_end = toc_part.index("\n") + 1
    header = toc_part[:header_end]
    body = toc_part[header_end:]
    existing = parse_toc_entries(body, min_level=min_level)
    merged, added = supplement_toc_entries(
        existing, doc_headings, anchor_map, min_level=min_level
    )
    if not added:
        return content, [], False

    new_body_lines = [header.rstrip("\n"), ""]
    new_body_lines.extend(e.raw_line for e in merged)
    if separator:
        new_body_lines.extend(["", "---", ""])
        new_block = "\n".join(new_body_lines).rstrip("\n") + "\n\n"
    else:
        new_block = "\n".join(new_body_lines)
        if not new_block.endswith("\n"):
            new_block += "\n"
    return prefix + new_block + suffix, added, False


def process_file(
    path: Path,
    *,
    min_depth: int,
    max_depth: int,
    toc_title: str,
    separator: bool,
    dry_run: bool,
    check: bool,
    stdout_mode: bool,
) -> int:
    text = path.read_text(encoding="utf-8")
    headings = extract_headings(
        text,
        min_depth=min_depth,
        max_depth=max_depth,
        toc_title=toc_title,
    )

    if not headings:
        print(f"{path}: 未找到 h{min_depth}-h{max_depth} 标题，跳过", file=sys.stderr)
        return 0

    new_text, added, created = build_toc_content(
        text,
        headings,
        toc_title=toc_title,
        separator=separator,
        min_depth=min_depth,
    )

    if check:
        if not added:
            print(f"{path}: 目录已是最新")
            return 0
        print(f"{path}: 目录缺少 {len(added)} 条", file=sys.stderr)
        return 1

    if dry_run:
        print(f"--- {path} ---")
        if created:
            section = extract_toc_section(
                new_text, toc_title, with_separator=separator
            )
            if section:
                print(section[1].rstrip())
        elif added:
            print(f"（补充 {len(added)} 条）")
            for e in added:
                print(e.raw_line)
        else:
            print("（无变化）")
        print()
        return 0

    if stdout_mode:
        sys.stdout.write(new_text)
        return 0

    if not added:
        print(f"{path}: 无变化")
        return 0

    path.write_text(new_text, encoding="utf-8")
    if created:
        print(f"{path}: 已新建目录（{len(headings)} 条）")
    else:
        titles = "、".join(e.title for e in added[:5])
        if len(added) > 5:
            titles += f" 等 {len(added)} 条"
        print(f"{path}: 已补充 {len(added)} 条（{titles}）")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="为 Markdown 插入/补充可跳转的「目录」小节（已有目录时仅追加缺失章节）"
    )
    parser.add_argument("files", nargs="+", type=Path, help="目标 .md 文件")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        metavar="N",
        help="目录包含的最大标题级别（默认 3）",
    )
    parser.add_argument(
        "--min-depth",
        type=int,
        default=2,
        metavar="N",
        help="目录包含的最小标题级别（默认 2）",
    )
    parser.add_argument("--title", default="目录", help="目录小节标题")
    parser.add_argument(
        "--no-separator",
        action="store_true",
        help="目录块后不插入 --- 分隔线",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只预览变更，不写文件",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查是否有未列入目录的章节",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="将处理后的全文输出到 stdout",
    )
    args = parser.parse_args(argv)

    if args.min_depth > args.max_depth:
        parser.error("--min-depth 不能大于 --max-depth")

    rc = 0
    for f in args.files:
        if not f.is_file():
            print(f"{f}: 文件不存在", file=sys.stderr)
            rc = 1
            continue
        r = process_file(
            f,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
            toc_title=args.title,
            separator=not args.no_separator,
            dry_run=args.dry_run,
            check=args.check,
            stdout_mode=args.stdout,
        )
        if r != 0:
            rc = r
    return rc


if __name__ == "__main__":
    sys.exit(main())
