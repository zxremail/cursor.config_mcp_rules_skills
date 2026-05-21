#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md-toc 的 Python 3.5/3.6 兼容实现（与 md-toc.py 默认行为对齐）。

通常由 ~/.cursor/tools/md-toc/md-toc 按版本自动调用，也可直接运行：
  python3 md-toc-batch.py doc.md
  python3 md-toc-batch.py          # 无参数：处理当前目录 *.md
"""
from __future__ import print_function

import argparse
import glob
import os
import re
import sys
from collections import namedtuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SLUG_PATTERN = os.path.join(SCRIPT_DIR, "github_slugger_regex.pattern")
if not os.path.isfile(_SLUG_PATTERN):
    print("错误: 未找到 {0}".format(_SLUG_PATTERN), file=sys.stderr)
    sys.exit(1)

_SLUG_RE = re.compile(open(_SLUG_PATTERN, encoding="utf-8").read())

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^(```+|~~~+)")
TOC_LINE_RE = re.compile(r"^(\s*)-\s+\[([^\]]+)\]\(#([^)]+)\)\s*$")
TOC_ITEM_INLINE_RE = re.compile(
    r'^(\s*)- <a id="(toc-pos-[^"]+)"></a>\[([^\]]+)\]\(#([^)]+)\)\s*$'
)
TOC_ANCHOR_LINE_RE = re.compile(
    r'^(\s*)<a id="(toc-pos-[^"]+)"></a>\s*$'
)
INLINE_BACK_LINK_RE = re.compile(r'\s*<a href="#toc-pos-[^"]+"[^>]*>.*?</a>\s*')
HEADING_SECTION_ID_RE = re.compile(r'\s*<a id="(?!toc-pos-)[^"]+"></a>\s*')
CUSTOM_ID_RE = re.compile(r"\s*\{#[^}]+\}\s*$")
INLINE_MD_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BACK_LINK_CLASS = "md-toc-back"
INDEX_LINK_CLASS = "md-toc-index"
INDEX_FILE = "_INDEX_.md"
BACK_LINK_ICON_SIZE = "10.5pt"
BACK_LINK_STYLE = "float:right;text-decoration:none;color:#5c6370"
TOC_TITLE = "目录"
MIN_DEPTH = 2
MAX_DEPTH = 3

TocEntry = namedtuple(
    "TocEntry", ["level", "title", "anchor", "toc_pos_anchor", "raw_line"]
)


def slug(value):
    if not isinstance(value, str):
        return ""
    value = value.lower()
    return _SLUG_RE.sub("", value).replace(" ", "-")


class Slugger(object):
    def __init__(self):
        self._occurrences = {}

    def slug(self, value):
        result = slug(value)
        original = result
        while result in self._occurrences:
            self._occurrences[original] = self._occurrences.get(original, 0) + 1
            result = "{0}-{1}".format(original, self._occurrences[original])
        self._occurrences[result] = 0
        return result


def clean_heading_title(raw):
    title = INLINE_BACK_LINK_RE.sub("", raw)
    title = HEADING_SECTION_ID_RE.sub("", title)
    title = CUSTOM_ID_RE.sub("", title.strip())
    title = INLINE_MD_RE.sub(r"\1", title)
    return title.strip()


def toc_pos_anchor(section_anchor):
    return "toc-pos-{0}".format(section_anchor)


def is_toc_heading_line(line, toc_title):
    return bool(re.match(r"^##\s+" + re.escape(toc_title) + r"\b", line))


def inline_back_link_svg():
    size = BACK_LINK_ICON_SIZE
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{0}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:-0.15em" aria-hidden="true">'
        '<path d="M9 14 4 9l5-5"/>'
        '<path d="M20 20v-7a4 4 0 0 0-4-4H4"/>'
        "</svg>"
    ).format(size)


def inline_back_link_html(pos_anchor):
    return (
        '<a href="#{0}" class="{1}" '
        'style="{2}">{3}</a>'
    ).format(pos_anchor, BACK_LINK_CLASS, BACK_LINK_STYLE, inline_back_link_svg())


def index_link_html(index_href=INDEX_FILE):
    return (
        '<a href="{0}" class="{1}" '
        'style="{2}" title="知识库索引">'
        "{3}</a>"
    ).format(index_href, INDEX_LINK_CLASS, BACK_LINK_STYLE, inline_back_link_svg())


def render_toc_heading_line(toc_title, link_to_index, index_href):
    line = "## {0}".format(toc_title)
    if link_to_index:
        line += " " + index_link_html(index_href)
    return line


def extract_headings(text, min_depth, max_depth, toc_title):
    headings = []
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
        if title:
            headings.append((level, title))
    return headings


def build_anchor_map(headings):
    slugger = Slugger()
    return {title: slugger.slug(title) for _, title in headings}


def parse_toc_entries(toc_body, min_level):
    entries = []
    pending_pos = None
    for line in toc_body.splitlines():
        inline = TOC_ITEM_INLINE_RE.match(line)
        if inline:
            spaces = inline.group(1)
            pos = inline.group(2)
            title = inline.group(3)
            anchor = inline.group(4)
            level = min_level + len(spaces) // 2
            entries.append(TocEntry(level, title, anchor, pos, line))
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
        entries.append(TocEntry(level, title, anchor, pos, line))
        pending_pos = None
    return entries


def render_toc_entry_lines(entry, min_level):
    indent = "  " * (entry.level - min_level)
    return [
        '{0}- <a id="{1}"></a>[{2}](#{3})'.format(
            indent, entry.toc_pos_anchor, entry.title, entry.anchor
        )
    ]


def make_toc_entry(level, title, anchor, min_level):
    pos = toc_pos_anchor(anchor)
    e = TocEntry(level, title, anchor, pos, "")
    lines = render_toc_entry_lines(e, min_level)
    return TocEntry(level, title, anchor, pos, lines[0])


def render_toc_block(entries, toc_title, min_level, link_to_index, index_href):
    lines = [
        render_toc_heading_line(toc_title, link_to_index, index_href),
        "",
    ]
    for entry in entries:
        lines.extend(render_toc_entry_lines(entry, min_level))
    lines.extend(["", "---", ""])
    return "\n".join(lines) + "\n\n"


def extract_toc_section(content, toc_title):
    title = re.escape(toc_title)
    pat = re.compile(
        r"^##\s+" + title + r"\b.*?\n.*?(?:^---\s*\n+)",
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(content)
    if not m:
        return None
    start, end = m.start(), m.end()
    block = m.group(0)
    blines = block.splitlines()
    body_lines = []
    for line in blines[1:]:
        if line.strip() == "---":
            break
        body_lines.append(line)
    header = blines[0] + "\n"
    body = "\n".join(body_lines)
    if body:
        body += "\n"
    return content[:start], header + body, content[end:]


def find_insert_index(result, doc_headings, doc_idx, existing_titles):
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


def supplement_toc_entries(existing, doc_headings, anchor_map, min_level):
    existing_titles = {e.title for e in existing}
    missing = [
        idx for idx, (_, title) in enumerate(doc_headings)
        if title not in existing_titles
    ]
    if not missing:
        return existing, []
    result = list(existing)
    added = []
    for doc_idx in missing:
        level, title = doc_headings[doc_idx]
        anchor = anchor_map[title]
        entry = make_toc_entry(level, title, anchor, min_level)
        pos = find_insert_index(result, doc_headings, doc_idx, existing_titles)
        result.insert(pos, entry)
        existing_titles.add(title)
        added.append(entry)
    return result, added


def heading_section_id_html(section_anchor):
    return '<a id="{0}"></a>'.format(section_anchor)


def heading_has_section_id(line, section_anchor):
    return 'id="{0}"'.format(section_anchor) in line


def heading_has_inline_back_link(line, pos_anchor):
    return (
        'href="#{0}"'.format(pos_anchor) in line
        and 'class="{0}"'.format(BACK_LINK_CLASS) in line
        and BACK_LINK_STYLE in line
        and 'width="{0}"'.format(BACK_LINK_ICON_SIZE) in line
        and "<svg" in line
    )


def append_back_link_to_heading(line, pos_anchor, section_anchor):
    need_id = not heading_has_section_id(line, section_anchor)
    need_back = not heading_has_inline_back_link(line, pos_anchor)
    if not need_id and not need_back:
        return line
    base = HEADING_SECTION_ID_RE.sub("", INLINE_BACK_LINK_RE.sub("", line))
    parts = [
        base,
        heading_section_id_html(section_anchor),
        inline_back_link_html(pos_anchor),
    ]
    return " ".join(parts)


def inject_back_links(content, title_to_pos, title_to_section, min_depth, max_depth, toc_title):
    if not title_to_pos:
        return content, 0
    lines = content.splitlines()
    out = []
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
        if hm:
            level = len(hm.group(1))
            if min_depth <= level <= max_depth:
                title = clean_heading_title(hm.group(2))
                if title in title_to_pos:
                    new_line = append_back_link_to_heading(
                        line, title_to_pos[title], title_to_section[title]
                    )
                    if new_line != line:
                        changed += 1
                    out.append(new_line)
                    continue
        out.append(line)
    return "\n".join(out) + ("\n" if content.endswith("\n") else ""), changed


def build_title_maps(entries):
    title_to_pos = {e.title: e.toc_pos_anchor for e in entries}
    title_to_section = {e.title: e.anchor for e in entries}
    return title_to_pos, title_to_section


def resolve_index_href(md_path):
    """同目录存在 _INDEX_.md 时返回相对链接（索引文件自身除外）。"""
    abspath = os.path.abspath(md_path)
    parent = os.path.dirname(abspath)
    if os.path.isfile(os.path.join(parent, INDEX_FILE)):
        if os.path.basename(abspath) != INDEX_FILE:
            return INDEX_FILE
    return None


def process(content, index_href):
    headings = extract_headings(content, MIN_DEPTH, MAX_DEPTH, TOC_TITLE)
    if not headings:
        return content, False, "无 h2-h3 标题"
    anchor_map = build_anchor_map(headings)
    min_level = min(l for l, _ in headings)
    link_to_index = index_href is not None
    entries = [
        make_toc_entry(l, t, anchor_map[t], min_level) for l, t in headings
    ]
    section = extract_toc_section(content, TOC_TITLE)
    created = False
    if section is None:
        block = render_toc_block(
            entries, TOC_TITLE, min_level, link_to_index, index_href or INDEX_FILE
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
        existing = parse_toc_entries(body, min_level)
        merged, added = supplement_toc_entries(
            existing, headings, anchor_map, min_level
        )
        all_entries = merged
        if added or not TOC_ITEM_INLINE_RE.search(body):
            block = render_toc_block(
                merged, TOC_TITLE, min_level, link_to_index, index_href or INDEX_FILE
            )
            content = prefix + block + suffix
        else:
            content = prefix + toc_part + suffix
    title_to_pos, title_to_section = build_title_maps(all_entries)
    content, links = inject_back_links(
        content, title_to_pos, title_to_section,
        MIN_DEPTH, MAX_DEPTH, TOC_TITLE
    )
    msg = "新建" if created else "更新"
    if links:
        msg += ", ↑{0}处".format(links)
    return content, True, msg


def process_file(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        print("{0}: 文件不存在".format(path), file=sys.stderr)
        return 1
    index_href = resolve_index_href(path)
    with open(path, "r", encoding="utf-8") as f:
        old = f.read()
    new, ok, msg = process(old, index_href)
    name = os.path.basename(path)
    if not ok:
        print("{0}: 跳过 ({1})".format(name, msg))
        return 0
    if new != old:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print("{0}: {1}".format(name, msg))
    else:
        print("{0}: 无变化 ({1})".format(name, msg))
    return 0


def collect_paths(file_args):
    if file_args:
        return file_args
    return sorted(glob.glob(os.path.join(os.getcwd(), "*.md")))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="为 Markdown 插入/补充「## 目录」（Python 3.5+ 兼容实现）"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="目标 .md；省略则处理当前目录下所有 *.md",
    )
    args = parser.parse_args(argv)
    paths = collect_paths(args.files)
    if not paths:
        print("未找到 .md 文件", file=sys.stderr)
        return 1
    rc = 0
    for path in paths:
        if process_file(path) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
