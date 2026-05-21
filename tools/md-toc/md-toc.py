#!/usr/bin/env python3
"""
为 Markdown 文档在标题下插入/更新「目录」小节（GitHub / VS Code 锚点兼容）。

已有「## 目录」时：保留现有条目与顺序，仅按正文标题顺序补充未列入的章节。
无目录时：在 # 文档标题后新建完整目录。

每条目录项带 toc-pos-* 锚点；对应章节标题下插入右对齐 ↑ 链接，可回到目录中的点击位置。

用法:
  md-toc.py doc.md                    # 写入文件
  md-toc.py --dry-run doc.md          # 仅预览变更
  md-toc.py --check doc.md            # CI：目录/回链已是最新则退出 0
  md-toc.py --no-back-links doc.md    # 不插入章节 ↑ 回链
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
TOC_ITEM_INLINE_RE = re.compile(
    r'^(\s*)- <a id="(toc-pos-[^"]+)"></a>\[([^\]]+)\]\(#([^)]+)\)\s*$',
    re.MULTILINE,
)
TOC_ANCHOR_LINE_RE = re.compile(
    r"^(\s*)<a id=\"(toc-pos-[^\"]+)\"></a>\s*$", re.MULTILINE
)
BACK_LINK_BLOCK_RE = re.compile(
    r'^<p align="right"><a href="#(toc-pos-[^"]+)">↑</a></p>\s*$'
)
BACK_LINK_LEGACY_RE = re.compile(
    r"^\[↑\s*返回目录\]\(#(toc-pos-[^)]+)\)\s*$"
)
BACK_LINK_STYLE = "float:right;text-decoration:none;color:#5c6370"
INLINE_BACK_LINK_RE = re.compile(
    r'\s*<a href="#(toc-pos-[^"]+)" style="[^"]*">↑</a>\s*'
)
HEADING_SECTION_ID_RE = re.compile(
    r'\s*<a id="(?!toc-pos-)[^"]+"></a>\s*'
)
TOC_NAV_HINT_RE = re.compile(r"^>\s*章节内点击", re.MULTILINE)
CUSTOM_ID_RE = re.compile(r"\s*\{#[^}]+\}\s*$")
INLINE_MD_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


@dataclass
class TocEntry:
    level: int
    title: str
    anchor: str
    toc_pos_anchor: str
    raw_line: str


def clean_heading_title(raw: str) -> str:
    title = INLINE_BACK_LINK_RE.sub("", raw)
    title = HEADING_SECTION_ID_RE.sub("", title)
    title = CUSTOM_ID_RE.sub("", title.strip())
    title = INLINE_MD_RE.sub(r"\1", title)
    return title.strip()


def toc_pos_anchor(section_anchor: str) -> str:
    return f"toc-pos-{section_anchor}"


def _toc_section_pattern(toc_title: str, *, with_separator: bool) -> re.Pattern[str]:
    title = re.escape(toc_title)
    if with_separator:
        body = rf"^##\s+{title}\s*\n.*?(?:^---\s*\n+)"
    else:
        body = rf"^##\s+{title}\s*\n.*?(?=\n##\s+|\Z)"
    return re.compile(body, re.MULTILINE | re.DOTALL)


def parse_toc_entries(toc_body: str, *, min_level: int) -> list[TocEntry]:
    """解析目录正文（支持同行锚点 + 列表项，兼容旧版分行锚点）。"""
    entries: list[TocEntry] = []
    pending_pos: str | None = None

    for line in toc_body.splitlines():
        inline = TOC_ITEM_INLINE_RE.match(line)
        if inline:
            spaces, pos, title, anchor = (
                inline.group(1),
                inline.group(2),
                inline.group(3),
                inline.group(4),
            )
            level = min_level + len(spaces) // 2
            entries.append(
                TocEntry(
                    level=level,
                    title=title,
                    anchor=anchor,
                    toc_pos_anchor=pos,
                    raw_line=line,
                )
            )
            pending_pos = None
            continue

        am = TOC_ANCHOR_LINE_RE.match(line)
        if am:
            pending_pos = am.group(2)
            continue

        m = TOC_LINE_RE.match(line)
        if not m:
            pending_pos = None
            continue

        spaces, title, anchor = m.group(1), m.group(2), m.group(3)
        level = min_level + len(spaces) // 2
        pos = pending_pos or toc_pos_anchor(anchor)
        entries.append(
            TocEntry(
                level=level,
                title=title,
                anchor=anchor,
                toc_pos_anchor=pos,
                raw_line=line,
            )
        )
        pending_pos = None

    return entries


def render_toc_entry_lines(entry: TocEntry, *, min_level: int) -> list[str]:
    """单行列表项：锚点与链接同在 li 内，避免破坏 Markdown 列表。"""
    indent = "  " * (entry.level - min_level)
    line = (
        f'{indent}- <a id="{entry.toc_pos_anchor}"></a>'
        f"[{entry.title}](#{entry.anchor})"
    )
    return [line]


def make_toc_entry(
    level: int,
    title: str,
    anchor: str,
    *,
    min_level: int,
) -> TocEntry:
    pos = toc_pos_anchor(anchor)
    lines = render_toc_entry_lines(
        TocEntry(level, title, anchor, pos, ""), min_level=min_level
    )
    return TocEntry(
        level=level,
        title=title,
        anchor=anchor,
        toc_pos_anchor=pos,
        raw_line=lines[0],
    )


def entries_need_nav_upgrade(entries: list[TocEntry], toc_body: str) -> bool:
    if not entries:
        return False
    # 旧版：锚点单独占一行，会破坏列表解析（MULTILINE 扫描全文）
    if TOC_ANCHOR_LINE_RE.search(toc_body) is not None:
        return True
    if not TOC_ITEM_INLINE_RE.search(toc_body):
        return True
    for e in entries:
        if f'id="{e.toc_pos_anchor}"' not in toc_body:
            return True
    return False


def extract_toc_section(
    content: str, toc_title: str, *, with_separator: bool
) -> tuple[str, str, str] | None:
    pat = _toc_section_pattern(toc_title, with_separator=with_separator)
    m = pat.search(content)
    if not m:
        return None
    start, end = m.start(), m.end()
    block = m.group(0)
    lines = block.splitlines()
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


def inline_back_link_html(pos_anchor: str) -> str:
    return f'<a href="#{pos_anchor}" style="{BACK_LINK_STYLE}">↑</a>'


def strip_inline_back_link(line: str) -> str:
    return INLINE_BACK_LINK_RE.sub("", line).rstrip()


def strip_heading_section_id(line: str) -> str:
    return HEADING_SECTION_ID_RE.sub("", line).rstrip()


def heading_section_id_html(section_anchor: str) -> str:
    return f'<a id="{section_anchor}"></a>'


def heading_has_section_id(line: str, section_anchor: str) -> bool:
    return f'id="{section_anchor}"' in line


def append_back_link_to_heading(
    line: str, pos_anchor: str, section_anchor: str
) -> str:
    """标题行：显式章节 id（供目录跳转）+ 右侧 ↑（回目录条目）。"""
    need_id = not heading_has_section_id(line, section_anchor)
    need_back = not heading_has_inline_back_link(line, pos_anchor)
    if not need_id and not need_back:
        return line
    base = strip_heading_section_id(strip_inline_back_link(line))
    parts = [base, heading_section_id_html(section_anchor)]
    parts.append(inline_back_link_html(pos_anchor))
    return " ".join(parts)


def heading_has_inline_back_link(line: str, pos_anchor: str) -> bool:
    m = INLINE_BACK_LINK_RE.search(line)
    return (
        m is not None
        and m.group(1) == pos_anchor
        and BACK_LINK_STYLE in line
    )


def parse_separate_back_link_pos(line: str) -> str | None:
    s = line.strip()
    for pat in (BACK_LINK_BLOCK_RE, BACK_LINK_LEGACY_RE):
        m = pat.match(s)
        if m:
            return m.group(1)
    return None


def is_separate_back_link_line(line: str) -> bool:
    return parse_separate_back_link_pos(line) is not None


def heading_back_links_need_update(
    content: str,
    doc_headings: list[tuple[int, str]],
    title_to_pos: dict[str, str],
    title_to_section: dict[str, str],
    *,
    min_depth: int,
    max_depth: int,
) -> bool:
    if any(is_separate_back_link_line(line) for line in content.splitlines()):
        return True
    for line in content.splitlines():
        hm = HEADING_RE.match(line)
        if not hm:
            continue
        level = len(hm.group(1))
        if level < min_depth or level > max_depth:
            continue
        title = clean_heading_title(hm.group(2))
        if title not in title_to_pos:
            continue
        if not heading_has_section_id(line, title_to_section[title]):
            return True
        if not heading_has_inline_back_link(line, title_to_pos[title]):
            return True
    return False


def toc_body_has_legacy_hint(toc_body: str) -> bool:
    return TOC_NAV_HINT_RE.search(toc_body) is not None


def render_toc_block(
    entries: list[TocEntry],
    *,
    toc_title: str,
    separator: bool,
    min_level: int,
    nav_hint: bool = False,
) -> str:
    if not entries:
        return ""
    lines = [f"## {toc_title}", ""]
    if nav_hint:
        lines.append("> 点击章节右侧 **↑** 回到目录对应条目。")
        lines.append("")
    for entry in entries:
        lines.extend(render_toc_entry_lines(entry, min_level=min_level))
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
        entry = make_toc_entry(level, title, anchor, min_level=min_level)
        pos = find_insert_index(
            result, doc_headings, doc_idx, existing_titles
        )
        result.insert(pos, entry)
        existing_titles.add(title)
        added.append(entry)

    return result, added


def rebuild_toc_section(
    content: str,
    entries: list[TocEntry],
    *,
    toc_title: str,
    separator: bool,
    min_level: int,
    nav_hint: bool,
) -> str:
    section = extract_toc_section(content, toc_title, with_separator=separator)
    if section is None:
        return content
    prefix, _, suffix = section
    block = render_toc_block(
        entries,
        toc_title=toc_title,
        separator=separator,
        min_level=min_level,
        nav_hint=nav_hint,
    )
    return prefix + block + suffix


def inject_back_links(
    content: str,
    title_to_pos: dict[str, str],
    title_to_section: dict[str, str],
    *,
    toc_title: str,
    min_depth: int,
    max_depth: int,
) -> tuple[str, int]:
    """在目录涵盖的标题下插入右对齐 ↑ 回链。返回 (新文本, 变更处数)。"""
    if not title_to_pos:
        return content, 0

    lines = content.splitlines()
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    skipping_toc = False
    changed = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        fence_m = FENCE_RE.match(line)
        if fence_m:
            marker = fence_m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[:3]
            elif line.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            out.append(line)
            i += 1
            continue

        if in_fence:
            out.append(line)
            i += 1
            continue

        if re.match(rf"^##\s+{re.escape(toc_title)}\s*$", line):
            skipping_toc = True
            out.append(line)
            i += 1
            continue
        if skipping_toc:
            out.append(line)
            if line.strip() == "---":
                skipping_toc = False
            i += 1
            continue

        hm = HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            title = clean_heading_title(hm.group(2))
            i += 1

            if min_depth <= level <= max_depth and title in title_to_pos:
                pos_anchor = title_to_pos[title]
                section_anchor = title_to_section[title]
                new_line = append_back_link_to_heading(
                    line, pos_anchor, section_anchor
                )
                if new_line != line:
                    changed += 1
                out.append(new_line)
                while i < len(lines) and is_separate_back_link_line(lines[i]):
                    changed += 1
                    i += 1
            else:
                out.append(line)
            continue

        out.append(line)
        i += 1

    new_text = "\n".join(out)
    if content.endswith("\n"):
        new_text += "\n"
    return new_text, changed


def build_title_to_pos(entries: list[TocEntry]) -> dict[str, str]:
    return {e.title: e.toc_pos_anchor for e in entries}


def build_title_to_section(entries: list[TocEntry]) -> dict[str, str]:
    return {e.title: e.anchor for e in entries}


def apply_document_toc(
    content: str,
    doc_headings: list[tuple[int, str]],
    *,
    toc_title: str,
    separator: bool,
    min_depth: int,
    max_depth: int,
    back_links: bool,
    nav_hint: bool,
) -> tuple[str, list[TocEntry], bool, int, bool]:
    """
    返回 (新全文, 新增目录条目, 是否新建目录, 新增回链数, 是否升级了目录锚点)。
    """
    if not doc_headings:
        return content, [], False, 0, False

    min_level = min(level for level, _ in doc_headings)
    anchor_map = build_anchor_map(doc_headings)
    section = extract_toc_section(content, toc_title, with_separator=separator)
    toc_upgraded = False
    added: list[TocEntry] = []
    created = False

    if section is None:
        entries = [
            make_toc_entry(level, title, anchor_map[title], min_level=min_level)
            for level, title in doc_headings
        ]
        block = render_toc_block(
            entries,
            toc_title=toc_title,
            separator=separator,
            min_level=min_level,
            nav_hint=nav_hint,
        )
        h1 = re.search(r"^#\s+.+$", content, re.MULTILINE)
        if h1:
            insert_at = h1.end()
            while insert_at < len(content) and content[insert_at] in "\r\n":
                insert_at += 1
            content = content[:insert_at] + "\n\n" + block + content[insert_at:]
        else:
            content = block + content
        created = True
        all_entries = entries
    else:
        prefix, toc_part, suffix = section
        header_end = toc_part.index("\n") + 1
        body = toc_part[header_end:]
        existing = parse_toc_entries(body, min_level=min_level)
        merged, added = supplement_toc_entries(
            existing, doc_headings, anchor_map, min_level=min_level
        )
        all_entries = merged

        need_rebuild = (
            added
            or entries_need_nav_upgrade(merged, body)
            or (not nav_hint and toc_body_has_legacy_hint(body))
        )
        if need_rebuild:
            content = rebuild_toc_section(
                content,
                merged,
                toc_title=toc_title,
                separator=separator,
                min_level=min_level,
                nav_hint=nav_hint,
            )
            toc_upgraded = True

    links_added = 0
    if back_links:
        content, links_added = inject_back_links(
            content,
            build_title_to_pos(all_entries),
            build_title_to_section(all_entries),
            toc_title=toc_title,
            min_depth=min_depth,
            max_depth=max_depth,
        )

    return content, added, created, links_added, toc_upgraded


def document_needs_update(
    content: str,
    doc_headings: list[tuple[int, str]],
    *,
    toc_title: str,
    separator: bool,
    min_depth: int,
    max_depth: int,
    back_links: bool,
    nav_hint: bool,
) -> bool:
    min_level = min(level for level, _ in doc_headings)
    anchor_map = build_anchor_map(doc_headings)
    section = extract_toc_section(content, toc_title, with_separator=separator)

    if section is None:
        return True

    _, toc_part, _ = section
    header_end = toc_part.index("\n") + 1
    body = toc_part[header_end:]
    existing = parse_toc_entries(body, min_level=min_level)
    existing_titles = {e.title for e in existing}
    if any(title not in existing_titles for _, title in doc_headings):
        return True
    if entries_need_nav_upgrade(existing, body):
        return True

    if back_links:
        title_to_pos = build_title_to_pos(existing)
        title_to_section = build_title_to_section(existing)
        if heading_back_links_need_update(
            content,
            doc_headings,
            title_to_pos,
            title_to_section,
            min_depth=min_depth,
            max_depth=max_depth,
        ):
            return True
        if not nav_hint and toc_body_has_legacy_hint(body):
            return True

    return False


def process_file(
    path: Path,
    *,
    min_depth: int,
    max_depth: int,
    toc_title: str,
    separator: bool,
    back_links: bool,
    nav_hint: bool,
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

    needs = document_needs_update(
        text,
        headings,
        toc_title=toc_title,
        separator=separator,
        min_depth=min_depth,
        max_depth=max_depth,
        back_links=back_links,
        nav_hint=nav_hint,
    )

    new_text, added, created, links_added, toc_upgraded = apply_document_toc(
        text,
        headings,
        toc_title=toc_title,
        separator=separator,
        min_depth=min_depth,
        max_depth=max_depth,
        back_links=back_links,
        nav_hint=nav_hint,
    )

    changed = new_text != text

    if check:
        if not needs:
            print(f"{path}: 目录已是最新")
            return 0
        print(f"{path}: 目录或返回链接需要更新", file=sys.stderr)
        return 1

    if dry_run:
        print(f"--- {path} ---")
        if not changed:
            print("（无变化）")
        else:
            if created:
                print("（将新建目录）")
            if added:
                print(f"（将补充目录 {len(added)} 条）")
            if toc_upgraded:
                print("（将升级目录 toc-pos 锚点）")
            if links_added:
                print(f"（将更新章节 ↑ 回链 {links_added} 处）")
        print()
        return 0

    if stdout_mode:
        sys.stdout.write(new_text)
        return 0

    if not changed:
        print(f"{path}: 无变化")
        return 0

    path.write_text(new_text, encoding="utf-8")
    parts: list[str] = []
    if created:
        parts.append(f"新建目录 {len(headings)} 条")
    elif added:
        parts.append(f"补充 {len(added)} 条")
    if toc_upgraded and not created:
        parts.append("升级目录锚点")
    if links_added:
        parts.append(f"↑ 回链 {links_added} 处")
    print(f"{path}: 已更新（{', '.join(parts)}）")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="为 Markdown 插入/补充目录；支持章节内 ↑ 回到目录对应条目"
    )
    parser.add_argument("files", nargs="+", type=Path, help="目标 .md 文件")
    parser.add_argument("--max-depth", type=int, default=3, metavar="N")
    parser.add_argument("--min-depth", type=int, default=2, metavar="N")
    parser.add_argument("--title", default="目录", help="目录小节标题")
    parser.add_argument("--no-separator", action="store_true")
    parser.add_argument(
        "--no-back-links",
        action="store_true",
        help="不在章节标题下插入 ↑ 回链",
    )
    parser.add_argument(
        "--nav-hint",
        action="store_true",
        help="在目录块顶部插入一行简短用法提示",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
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
            back_links=not args.no_back_links,
            nav_hint=args.nav_hint,
            dry_run=args.dry_run,
            check=args.check,
            stdout_mode=args.stdout,
        )
        if r != 0:
            rc = r
    return rc


if __name__ == "__main__":
    sys.exit(main())
