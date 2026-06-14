#!/usr/bin/env python3
"""
为 Markdown 文档在标题下插入/更新「目录」小节（GitHub / VS Code 锚点兼容）。

已有「## 目录」时：保留现有条目与顺序，仅按正文标题顺序补充未列入的章节。
无目录时：在 # 文档标题后新建完整目录。

默认生成纯 Markdown 目录（无 HTML 锚点/回链）。可选 --back-links / --index-link 启用 HTML 导航。

用法:
  md-toc.py doc.md                    # 写入文件（纯 Markdown 目录）
  md-toc.py --dry-run doc.md          # 仅预览变更
  md-toc.py --check doc.md            # CI：目录已是最新则退出 0
  md-toc.py --back-links doc.md       # 插入 toc-pos 锚点与章节 ↑ 回链
  md-toc.py --index-link doc.md       # 目录标题添加指向 _INDEX_.md 的箭头
"""
from __future__ import annotations

import argparse
import os
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
BACK_LINK_CLASS = "md-toc-back"
INDEX_FILE = "_INDEX_.md"
TOC_DOC_TITLE_SEP = " • "
INDEX_LINK_CLASS = "md-toc-index"
INDEX_LINK_RE = re.compile(
    r'\s*<a href="[^"]*" class="md-toc-index"[^>]*>.*?</a>\s*'
)
# 中国字号「五号」= 10.5pt，各级标题统一此尺寸
BACK_LINK_ICON_SIZE = "10.5pt"
BACK_LINK_STYLE = "float:right;text-decoration:none;color:#5c6370"
INLINE_BACK_LINK_RE = re.compile(
    r'\s*<a href="#toc-pos-[^"]+"[^>]*>.*?</a>\s*'
)
HEADING_SECTION_ID_RE = re.compile(
    r'\s*<a id="(?!toc-pos-)[^"]+"></a>\s*'
)
TOC_NAV_HINT_RE = re.compile(r"^>\s*章节内点击", re.MULTILINE)
TOC_NUMBER_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+")
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


def has_number_prefix(title: str) -> bool:
    return bool(TOC_NUMBER_PREFIX_RE.match(title))


def strip_number_prefix(title: str) -> str:
    """去掉目录链接文字中的层级序号前缀（如 ``1.`` / ``1.2.3. `` / ``2.1 ``）。"""
    prev = None
    while prev != title:
        prev = title
        title = TOC_NUMBER_PREFIX_RE.sub("", title, count=1)
    return title


def headings_need_number_injection(headings: list[tuple[int, str]]) -> bool:
    """正文标题中是否存在未带层级序号前缀的章节。"""
    return any(not has_number_prefix(title) for _, title in headings)


def apply_counters_from_numbered_title(
    counters: dict[int, int], level: int, min_level: int, title: str
) -> None:
    """从已有 ``1.`` / ``2.1`` 标题同步层级计数器。"""
    m = TOC_NUMBER_PREFIX_RE.match(title)
    if not m:
        update_toc_level_counters(counters, level)
        return
    segments = [int(x) for x in m.group(1).split(".")]
    for lv in list(counters):
        if lv > level:
            del counters[lv]
    for offset, lv in enumerate(range(min_level, level + 1)):
        if offset < len(segments):
            counters[lv] = segments[offset]
        elif lv in counters:
            del counters[lv]


def update_toc_level_counters(counters: dict[int, int], level: int) -> None:
    for lv in list(counters):
        if lv > level:
            del counters[lv]
    counters[level] = counters.get(level, 0) + 1


def format_toc_number_prefix(counters: dict[int, int], level: int, min_level: int) -> str:
    """h2 为 ``1. ``，h3+ 为 ``1.1 `` / ``1.1.2 ``（末段后空格，无多余句点）。"""
    parts = [str(counters[lv]) for lv in range(min_level, level + 1) if lv in counters]
    if not parts:
        return ""
    if len(parts) == 1:
        return f"{parts[0]}. "
    return ".".join(parts) + " "


def entries_need_number_upgrade(
    entries: list[TocEntry],
    toc_body: str,
    *,
    min_level: int,
) -> bool:
    if not entries:
        return False
    counters: dict[int, int] = {}
    for entry in entries:
        update_toc_level_counters(counters, entry.level)
        prefix = format_toc_number_prefix(counters, entry.level, min_level)
        base = (
            strip_number_prefix(entry.title)
            if has_number_prefix(entry.title)
            else entry.title
        )
        if f"[{prefix}{base}](#{entry.anchor})" not in toc_body:
            return True
    return False


def entries_need_number_downgrade(
    entries: list[TocEntry],
    toc_body: str,
    *,
    min_level: int,
) -> bool:
    """目录正文仍含「仅目录加号」前缀，但当前为 --no-numbered（标题本身已有序号则跳过）。"""
    if not entries:
        return False
    counters: dict[int, int] = {}
    for entry in entries:
        if has_number_prefix(entry.title):
            continue
        update_toc_level_counters(counters, entry.level)
        prefix = format_toc_number_prefix(counters, entry.level, min_level)
        if prefix and f"[{prefix}{entry.title}]" in toc_body:
            return True
    return False


def entries_need_number_sync(
    entries: list[TocEntry],
    toc_body: str,
    *,
    min_level: int,
    numbered: bool,
) -> bool:
    if numbered:
        return entries_need_number_upgrade(entries, toc_body, min_level=min_level)
    return entries_need_number_downgrade(entries, toc_body, min_level=min_level)


def sync_entry_titles_from_headings(
    entries: list[TocEntry],
    doc_headings: list[tuple[int, str]],
    anchor_map: dict[str, str],
) -> None:
    """--no-numbered 时，目录链接文字与正文标题一致（避免剥号后只剩纯文本）。"""
    anchor_to_title = {anchor_map[title]: title for _, title in doc_headings}
    for entry in entries:
        if entry.anchor in anchor_to_title:
            entry.title = anchor_to_title[entry.anchor]


def toc_pos_anchor(section_anchor: str) -> str:
    return f"toc-pos-{section_anchor}"


def is_toc_heading_line(line: str, toc_title: str) -> bool:
    """匹配「## 目录」标题行（允许行尾索引/回链等 HTML）。"""
    return bool(re.match(rf"^##\s+{re.escape(toc_title)}\b", line))


def _toc_section_pattern(toc_title: str, *, with_separator: bool) -> re.Pattern[str]:
    title = re.escape(toc_title)
    if with_separator:
        body = rf"^##\s+{title}\b.*?\n.*?(?:^---\s*\n+)"
    else:
        body = rf"^##\s+{title}\b.*?\n.*?(?=\n##\s+|\Z)"
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
                    title=strip_number_prefix(title),
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
                title=strip_number_prefix(title),
                anchor=anchor,
                toc_pos_anchor=pos,
                raw_line=line,
            )
        )
        pending_pos = None

    return entries


def extract_h1_title(content: str) -> str | None:
    m = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
    if not m:
        return None
    return clean_heading_title(m.group(1))


def resolve_toc_section_title(content: str, toc_base: str) -> str:
    """知识库目录行：`目录 • <# 文档标题>`。"""
    h1 = extract_h1_title(content)
    if h1:
        return f"{toc_base}{TOC_DOC_TITLE_SEP}{h1}"
    return toc_base


def render_toc_entry_lines(
    entry: TocEntry,
    *,
    min_level: int,
    numbered: bool,
    number_prefix: str,
    back_links: bool = False,
) -> list[str]:
    """单行列表项；back_links 时在 li 内插入 toc-pos 锚点。"""
    indent = "  " * (entry.level - min_level)
    if numbered and number_prefix:
        base = (
            strip_number_prefix(entry.title)
            if has_number_prefix(entry.title)
            else entry.title
        )
        display = f"{number_prefix}{base}"
    else:
        display = entry.title
    if back_links:
        line = (
            f'{indent}- <a id="{entry.toc_pos_anchor}"></a>'
            f"[{display}](#{entry.anchor})"
        )
    else:
        line = f"{indent}- [{display}](#{entry.anchor})"
    return [line]


def render_toc_entries_lines(
    entries: list[TocEntry],
    *,
    min_level: int,
    numbered: bool,
    back_links: bool = False,
) -> list[str]:
    lines: list[str] = []
    counters: dict[int, int] = {}
    for entry in entries:
        prefix = ""
        if numbered:
            update_toc_level_counters(counters, entry.level)
            prefix = format_toc_number_prefix(counters, entry.level, min_level)
        lines.extend(
            render_toc_entry_lines(
                entry,
                min_level=min_level,
                numbered=numbered,
                number_prefix=prefix,
                back_links=back_links,
            )
        )
    return lines


def make_toc_entry(
    level: int,
    title: str,
    anchor: str,
    *,
    min_level: int,
    numbered: bool = True,
) -> TocEntry:
    pos = toc_pos_anchor(anchor)
    return TocEntry(
        level=level,
        title=title,
        anchor=anchor,
        toc_pos_anchor=pos,
        raw_line="",
    )


def entries_need_nav_upgrade(
    entries: list[TocEntry], toc_body: str, *, back_links: bool
) -> bool:
    if not entries:
        return False
    has_html_anchors = (
        TOC_ANCHOR_LINE_RE.search(toc_body) is not None
        or TOC_ITEM_INLINE_RE.search(toc_body) is not None
    )
    if not back_links:
        return has_html_anchors
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

        if is_toc_heading_line(line, toc_title):
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


def inject_heading_number_prefixes(
    content: str,
    *,
    min_depth: int,
    max_depth: int,
    toc_title: str,
) -> tuple[str, int]:
    """
    为缺少序号前缀的正文标题补上 ``1.`` / ``1.1`` 等，并刷新章节 ``<a id>``。
    返回 (新文本, 修改标题行数)。
    """
    if not content:
        return content, 0

    min_level = min_depth
    slugger = Slugger()
    counters: dict[int, int] = {}
    lines = content.splitlines()
    out: list[str] = []
    in_fence = False
    fence_marker = ""
    skipping_toc = False
    changed = 0

    for line in lines:
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
            continue

        if in_fence:
            out.append(line)
            continue

        if is_toc_heading_line(line, toc_title):
            skipping_toc = True
            out.append(line)
            continue
        if skipping_toc:
            out.append(line)
            if line.strip() == "---":
                skipping_toc = False
            continue

        hm = HEADING_RE.match(line)
        if not hm:
            out.append(line)
            continue

        level = len(hm.group(1))
        if level < min_depth or level > max_depth:
            out.append(line)
            continue

        title = clean_heading_title(hm.group(2))
        if not title or title == toc_title:
            out.append(line)
            continue

        if has_number_prefix(title):
            apply_counters_from_numbered_title(counters, level, min_level, title)
            out.append(line)
            continue

        update_toc_level_counters(counters, level)
        prefix = format_toc_number_prefix(counters, level, min_level)
        new_title = f"{prefix}{title}"
        section_anchor = slugger.slug(new_title)
        hashes = hm.group(1)
        base = f"{hashes} {new_title}"
        base = strip_heading_section_id(strip_inline_back_link(base))
        new_line = f"{base} {heading_section_id_html(section_anchor)}"
        if new_line != line:
            changed += 1
        out.append(new_line)

    new_text = "\n".join(out)
    if content.endswith("\n"):
        new_text += "\n"
    return new_text, changed


def inline_back_link_svg() -> str:
    """弧形向上（corner-left-up），stroke 继承 color，尺寸固定为 ### 级别。"""
    size = BACK_LINK_ICON_SIZE
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:-0.15em" aria-hidden="true">'
        '<path d="M9 14 4 9l5-5"/>'
        '<path d="M20 20v-7a4 4 0 0 0-4-4H4"/>'
        "</svg>"
    )


def inline_back_link_html(pos_anchor: str) -> str:
    return (
        f'<a href="#{pos_anchor}" class="{BACK_LINK_CLASS}" '
        f'style="{BACK_LINK_STYLE}">{inline_back_link_svg()}</a>'
    )


def index_link_html(index_href: str = INDEX_FILE) -> str:
    """目录标题行右侧：指向知识库 _INDEX_.md。"""
    return (
        f'<a href="{index_href}" class="{INDEX_LINK_CLASS}" '
        f'style="{BACK_LINK_STYLE}" title="知识库索引">'
        f"{inline_back_link_svg()}</a>"
    )


def render_toc_heading_line(
    toc_title: str, *, link_to_index: bool, index_href: str
) -> str:
    line = f"## {toc_title}"
    if link_to_index:
        line += " " + index_link_html(index_href)
    return line


def toc_heading_has_any_index_link(content: str, toc_title: str) -> bool:
    m = re.search(
        rf"^##\s+{re.escape(toc_title)}\b.*$",
        content,
        re.MULTILINE,
    )
    return bool(m and INDEX_LINK_RE.search(m.group(0)))


def toc_heading_has_index_link(
    content: str, toc_title: str, index_href: str
) -> bool:
    m = re.search(
        rf"^##\s+{re.escape(toc_title)}\b.*$",
        content,
        re.MULTILINE,
    )
    if not m:
        return False
    line = m.group(0)
    return (
        f'href="{index_href}"' in line
        and f'class="{INDEX_LINK_CLASS}"' in line
        and f'width="{BACK_LINK_ICON_SIZE}"' in line
        and "<svg" in line
    )


def resolve_index_href(md_path: Path) -> str | None:
    """向上查找知识库根目录下的 _INDEX_.md，返回相对链接路径。"""
    for parent in (md_path.parent, *md_path.parents):
        if (parent / INDEX_FILE).is_file():
            rel = Path(os.path.relpath(parent / INDEX_FILE, md_path.parent))
            return rel.as_posix()
    return None


def upgrade_toc_heading_index_link(
    content: str,
    toc_title: str,
    index_href: str,
) -> tuple[str, bool]:
    pat = re.compile(
        rf"^##\s+{re.escape(toc_title)}\b.*$",
        re.MULTILINE,
    )
    m = pat.search(content)
    if not m:
        return content, False
    section_title = resolve_toc_section_title(content, toc_title)
    new_line = render_toc_heading_line(
        section_title, link_to_index=True, index_href=index_href
    )
    if m.group(0) == new_line:
        return content, False
    return content[: m.start()] + new_line + content[m.end() :], True


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
    return (
        f'href="#{pos_anchor}"' in line
        and f'class="{BACK_LINK_CLASS}"' in line
        and BACK_LINK_STYLE in line
        and f'width="{BACK_LINK_ICON_SIZE}"' in line
        and "<svg" in line
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
    toc_title: str,
    min_depth: int,
    max_depth: int,
) -> bool:
    if any(is_separate_back_link_line(line) for line in content.splitlines()):
        return True
    for line in content.splitlines():
        if is_toc_heading_line(line, toc_title):
            continue
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
    content: str,
    separator: bool,
    min_level: int,
    numbered: bool,
    nav_hint: bool = False,
    link_to_index: bool = False,
    index_href: str = INDEX_FILE,
    back_links: bool = False,
) -> str:
    if not entries:
        return ""
    section_title = resolve_toc_section_title(content, toc_title)
    lines = [
        render_toc_heading_line(
            section_title, link_to_index=link_to_index, index_href=index_href
        ),
        "",
    ]
    if nav_hint:
        lines.append("> 点击章节右侧 **↑** 回到目录对应条目。")
        lines.append("")
    lines.extend(
        render_toc_entries_lines(
            entries, min_level=min_level, numbered=numbered, back_links=back_links
        )
    )
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
    numbered: bool,
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
        entry = make_toc_entry(
            level, title, anchor, min_level=min_level, numbered=numbered
        )
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
    numbered: bool,
    nav_hint: bool,
    link_to_index: bool,
    index_href: str,
    back_links: bool = False,
) -> str:
    section = extract_toc_section(content, toc_title, with_separator=separator)
    if section is None:
        return content
    prefix, _, suffix = section
    block = render_toc_block(
        entries,
        toc_title=toc_title,
        content=content,
        separator=separator,
        min_level=min_level,
        numbered=numbered,
        nav_hint=nav_hint,
        link_to_index=link_to_index,
        index_href=index_href,
        back_links=back_links,
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

        if is_toc_heading_line(line, toc_title):
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

            if (
                min_depth <= level <= max_depth
                and title in title_to_pos
                and title != toc_title
            ):
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


def strip_nav_html_from_content(
    content: str,
    *,
    toc_title: str,
    min_depth: int,
    max_depth: int,
    strip_toc_index_link: bool,
) -> tuple[str, int]:
    """移除目录标题与章节标题中的 HTML 锚点/回链。返回 (新文本, 变更处数)。"""
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

        if is_toc_heading_line(line, toc_title):
            skipping_toc = True
            new_line = line
            if strip_toc_index_link:
                stripped = INDEX_LINK_RE.sub("", new_line).rstrip()
                if stripped != new_line:
                    changed += 1
                    new_line = stripped
            out.append(new_line)
            i += 1
            continue

        if skipping_toc:
            out.append(line)
            if line.strip() == "---":
                skipping_toc = False
            i += 1
            continue

        if is_separate_back_link_line(line) or BACK_LINK_BLOCK_RE.match(line):
            changed += 1
            i += 1
            continue

        hm = HEADING_RE.match(line)
        if hm:
            level = len(hm.group(1))
            stripped = strip_heading_section_id(
                strip_inline_back_link(line)
            ).rstrip()
            if stripped != line.rstrip():
                changed += 1
            out.append(stripped)
            i += 1
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
    index_href: str | None,
    numbered: bool,
) -> tuple[str, list[TocEntry], bool, int, bool, bool]:
    """
    返回 (新全文, 新增目录条目, 是否新建目录, 新增回链数, 是否升级了目录锚点)。
    """
    if not doc_headings:
        return content, [], False, 0, False, False

    link_to_index = index_href is not None
    min_level = min(level for level, _ in doc_headings)
    anchor_map = build_anchor_map(doc_headings)
    section = extract_toc_section(content, toc_title, with_separator=separator)
    toc_upgraded = False
    added: list[TocEntry] = []
    created = False

    if section is None:
        entries = [
            make_toc_entry(
                level, title, anchor_map[title], min_level=min_level, numbered=numbered
            )
            for level, title in doc_headings
        ]
        block = render_toc_block(
            entries,
            toc_title=toc_title,
            content=content,
            separator=separator,
            min_level=min_level,
            numbered=numbered,
            nav_hint=nav_hint,
            link_to_index=link_to_index,
            index_href=index_href or INDEX_FILE,
            back_links=back_links,
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
        number_downgrade = (
            not numbered
            and entries_need_number_downgrade(
                existing, body, min_level=min_level
            )
        )
        if number_downgrade:
            merged = [
                make_toc_entry(
                    level,
                    title,
                    anchor_map[title],
                    min_level=min_level,
                    numbered=numbered,
                )
                for level, title in doc_headings
            ]
            added = []
        else:
            merged, added = supplement_toc_entries(
                existing,
                doc_headings,
                anchor_map,
                min_level=min_level,
                numbered=numbered,
            )
        all_entries = merged

        need_rebuild = (
            added
            or number_downgrade
            or entries_need_nav_upgrade(merged, body, back_links=back_links)
            or entries_need_number_sync(
                merged, body, min_level=min_level, numbered=numbered
            )
            or (not nav_hint and toc_body_has_legacy_hint(body))
            or (
                not link_to_index
                and toc_heading_has_any_index_link(content, toc_title)
            )
        )
        if need_rebuild:
            if not numbered and not number_downgrade:
                sync_entry_titles_from_headings(merged, doc_headings, anchor_map)
            content = rebuild_toc_section(
                content,
                merged,
                toc_title=toc_title,
                separator=separator,
                min_level=min_level,
                numbered=numbered,
                nav_hint=nav_hint,
                link_to_index=link_to_index,
                index_href=index_href or INDEX_FILE,
                back_links=back_links,
            )
            toc_upgraded = True

    index_link_upgraded = False
    if link_to_index and not toc_heading_has_index_link(
        content, toc_title, index_href or INDEX_FILE
    ):
        content, index_link_upgraded = upgrade_toc_heading_index_link(
            content, toc_title, index_href or INDEX_FILE
        )

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
    else:
        content, stripped = strip_nav_html_from_content(
            content,
            toc_title=toc_title,
            min_depth=min_depth,
            max_depth=max_depth,
            strip_toc_index_link=not link_to_index,
        )
        if stripped:
            links_added = stripped

    return content, added, created, links_added, toc_upgraded, index_link_upgraded


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
    index_href: str | None,
    numbered: bool,
    inject_heading_numbers: bool,
) -> bool:
    if inject_heading_numbers and headings_need_number_injection(doc_headings):
        return True

    min_level = min(level for level, _ in doc_headings)
    section = extract_toc_section(content, toc_title, with_separator=separator)

    if section is None:
        return True

    if index_href and not toc_heading_has_index_link(
        content, toc_title, index_href
    ):
        return True

    if not index_href and toc_heading_has_any_index_link(content, toc_title):
        return True

    _, toc_part, _ = section
    header_end = toc_part.index("\n") + 1
    body = toc_part[header_end:]
    existing = parse_toc_entries(body, min_level=min_level)
    existing_titles = {e.title for e in existing}
    if any(title not in existing_titles for _, title in doc_headings):
        return True
    if entries_need_nav_upgrade(existing, body, back_links=back_links):
        return True
    if entries_need_number_sync(
        existing, body, min_level=min_level, numbered=numbered
    ):
        return True

    if back_links:
        title_to_pos = build_title_to_pos(existing)
        title_to_section = build_title_to_section(existing)
        if heading_back_links_need_update(
            content,
            doc_headings,
            title_to_pos,
            title_to_section,
            toc_title=toc_title,
            min_depth=min_depth,
            max_depth=max_depth,
        ):
            return True
        if not nav_hint and toc_body_has_legacy_hint(body):
            return True
    elif not back_links:
        _, stripped = strip_nav_html_from_content(
            content,
            toc_title=toc_title,
            min_depth=min_depth,
            max_depth=max_depth,
            strip_toc_index_link=not index_href,
        )
        if stripped:
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
    index_href: str | None,
    numbered: bool,
    inject_heading_numbers: bool,
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

    headings_injected = 0
    if inject_heading_numbers and headings_need_number_injection(headings):
        text, headings_injected = inject_heading_number_prefixes(
            text,
            min_depth=min_depth,
            max_depth=max_depth,
            toc_title=toc_title,
        )
        headings = extract_headings(
            text,
            min_depth=min_depth,
            max_depth=max_depth,
            toc_title=toc_title,
        )

    needs = document_needs_update(
        text,
        headings,
        toc_title=toc_title,
        separator=separator,
        min_depth=min_depth,
        max_depth=max_depth,
        back_links=back_links,
        nav_hint=nav_hint,
        index_href=index_href,
        numbered=numbered,
        inject_heading_numbers=False,
    )

    new_text, added, created, links_added, toc_upgraded, index_upgraded = (
        apply_document_toc(
            text,
            headings,
            toc_title=toc_title,
            separator=separator,
            min_depth=min_depth,
            max_depth=max_depth,
            back_links=back_links,
            nav_hint=nav_hint,
            index_href=index_href,
            numbered=numbered,
        )
    )

    changed = new_text != text or headings_injected > 0

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
            if headings_injected:
                print(f"（将为正文标题补序号 {headings_injected} 处）")
            if toc_upgraded:
                print("（将升级目录 toc-pos 锚点/序号）")
            if links_added:
                print(f"（将更新章节 ↑ 回链 {links_added} 处）")
            if index_upgraded:
                print("（将为「目录」添加指向 _INDEX_.md 的箭头）")
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
    if headings_injected:
        parts.append(f"正文标题补序号 {headings_injected} 处")
    if created:
        parts.append(f"新建目录 {len(headings)} 条")
    elif added:
        parts.append(f"补充 {len(added)} 条")
    if toc_upgraded and not created:
        parts.append("升级目录锚点/序号")
    if links_added:
        parts.append(
            f"↑ 回链 {links_added} 处"
            if back_links
            else f"移除 HTML 导航 {links_added} 处"
        )
    if index_upgraded:
        parts.append("目录→索引")
    print(f"{path}: 已更新（{', '.join(parts)}）")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="为 Markdown 插入/补充纯 Markdown 目录（默认无 HTML 锚点）"
    )
    parser.add_argument("files", nargs="+", type=Path, help="目标 .md 文件")
    parser.add_argument("--max-depth", type=int, default=3, metavar="N")
    parser.add_argument("--min-depth", type=int, default=2, metavar="N")
    parser.add_argument("--title", default="目录", help="目录小节标题")
    parser.add_argument("--no-separator", action="store_true")
    parser.add_argument(
        "--back-links",
        action="store_true",
        help="在目录/章节插入 HTML 锚点与 ↑ 回链（默认：纯 Markdown 目录）",
    )
    parser.add_argument(
        "--index-link",
        action="store_true",
        help="在「目录」标题添加指向 _INDEX_.md 的箭头（默认：不添加）",
    )
    parser.add_argument(
        "--no-back-links",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--no-index-link",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--nav-hint",
        action="store_true",
        help="在目录块顶部插入一行简短用法提示",
    )
    parser.add_argument(
        "--numbered",
        action="store_true",
        help="仅在目录中加层级序号，不修改正文标题（与默认「先补正文序号」相反）",
    )
    parser.add_argument(
        "--no-numbered",
        action="store_true",
        help="目录条目不另加序号（默认：序号写在正文标题中，目录与标题一致）",
    )
    parser.add_argument(
        "--no-heading-numbers",
        action="store_true",
        help="不为正文标题补序号（缺号时仅目录加号需配合 --numbered）",
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
        back_links = args.back_links and not args.no_back_links
        index_href = (
            resolve_index_href(f)
            if args.index_link and not args.no_index_link
            else None
        )
        if args.numbered and args.no_numbered:
            parser.error("--numbered 与 --no-numbered 不能同时使用")
        toc_numbered = args.numbered
        inject_heading_numbers = not args.numbered and not args.no_heading_numbers
        r = process_file(
            f,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
            toc_title=args.title,
            separator=not args.no_separator,
            back_links=back_links,
            nav_hint=args.nav_hint,
            index_href=index_href,
            numbered=toc_numbered,
            inject_heading_numbers=inject_heading_numbers,
            dry_run=args.dry_run,
            check=args.check,
            stdout_mode=args.stdout,
        )
        if r != 0:
            rc = r
    return rc


if __name__ == "__main__":
    sys.exit(main())
