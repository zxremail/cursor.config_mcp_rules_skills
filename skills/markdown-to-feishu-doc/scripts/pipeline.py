#!/usr/bin/env python3
"""Markdown → 飞书 XML / 画板 raw 修补 / 验收摘要。只向 stdout 打短摘要，禁止把全文 XML/JSON 印进对话。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TH_BG = "rgb(236,226,254)"
TD0_BG = "rgb(225,234,255)"
LAYER_FILL = {
    "#0d2433": ("#DBEAFE", "#1B4965"),
    "#1a1230": ("#EDE9FE", "#4A3566"),
    "#2a1020": ("#FCE7F3", "#7B2D55"),
    "#3d2a10": ("#FFEDD5", "#C67500"),
    "#1b4965": ("#FFFFFF", "#1B4965"),
    "#163044": ("#FFFFFF", "#1B4965"),
    "#0d1117": ("#F8FAFC", "#1F2329"),
    "#161b22": ("#E2E8F0", "#1F2329"),
    "#163a4d": ("#93C5FD", "#1F2329"),
    "#0d241c": ("#D1FAE5", "#1F2329"),
    "#16382c": ("#86EFAC", "#1F2329"),
    "#1e1530": ("#EDE9FE", "#1F2329"),
    "#2a1f40": ("#DDD6FE", "#1F2329"),
    "#3d2a00": ("#FFEDD5", "#1F2329"),
    "#5a3d00": ("#FDBA74", "#1F2329"),
    "#30363d": ("#94A3B8", "#1F2329"),
}
LEAF_FILL = {
    "#6a4c93",
    "#2e86ab",
    "#f18f01",
    "#a23b72",
    "#2d936c",
    "#e63946",
}
LANG_ROLE = {
    "c": "代码示例",
    "h": "头文件示例",
    "cpp": "代码示例",
    "bash": "命令行示例",
    "sh": "命令行示例",
    "shell": "命令行示例",
    "json": "配置示例",
    "yaml": "配置示例",
    "yml": "配置示例",
    "xml": "配置示例",
    "text": "文本示例",
}


def xml_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def strip_heading_num(text: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text).strip()


FONT_TEXT_COLOR = {
    "#5BE49B": "green",
    "#FFB020": "orange",
}
FONT_UNWRAP = {"#C9A0FF"}
PH_L, PH_R = "\uFFF0", "\uFFF1"


def restore_ph(text: str, placeholders: list[str]) -> str:
    pat = re.compile(re.escape(PH_L) + r"(\d+)" + re.escape(PH_R))
    prev = None
    while prev != text:
        prev = text
        text = pat.sub(lambda m: placeholders[int(m.group(1))], text)
    return text


def inline_md(text: str) -> str:
    placeholders: list[str] = []

    def hold(s: str) -> str:
        placeholders.append(s)
        return f"{PH_L}{len(placeholders) - 1}{PH_R}"

    def font_repl(m: re.Match) -> str:
        named = FONT_TEXT_COLOR.get(m.group(1).strip().upper())
        inner = inline_md(m.group(2))
        if m.group(1).strip().upper() in FONT_UNWRAP or named is None:
            return inner
        return hold(f'<span text-color="{named}">{inner}</span>')

    text = re.sub(r'<span\s+style="[^"]*">(.*?)</span>', r"\1", text, flags=re.S)
    text = re.sub(
        r"""<font\s+color=["']([^"']+)["']>(.*?)</font>""",
        font_repl,
        text,
        flags=re.S | re.I,
    )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(
        r"<code>(.*?)</code>",
        lambda m: hold(f"<code>{xml_esc(m.group(1))}</code>"),
        text,
        flags=re.S | re.I,
    )
    text = re.sub(
        r"<b>(.*?)</b>",
        lambda m: hold(f"<b>{xml_esc(m.group(1))}</b>"),
        text,
        flags=re.S | re.I,
    )
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: hold(f"<b>{xml_esc(m.group(1))}</b>"), text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: hold(
            f'<a href="{xml_esc(m.group(2))}">{inline_md(strip_heading_num(m.group(1)))}</a>'
        ),
        text,
    )
    text = re.sub(r"`([^`]+)`", lambda m: hold(f"<code>{xml_esc(m.group(1))}</code>"), text)
    text = xml_esc(text)
    text = restore_ph(text, placeholders)
    return text.replace("\n", "<br/>")


def cell_xml(text: str, header: bool, first_col: bool) -> str:
    body = inline_md(text.strip())
    if header:
        return f'<p align="center"><b>{body}</b></p>'
    if first_col:
        # 首列不加 code：剥掉 code 标签但留文字
        body = re.sub(r"</?code>", "", body)
        return f"<p><b>{body}</b></p>"
    return f"<p>{body}</p>"


def table_xml(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    ths = "".join(
        f'<th background-color="{TH_BG}" vertical-align="middle">{cell_xml(c, True, False)}</th>'
        for c in head
    )
    trs = []
    for row in body:
        tds = []
        for i, c in enumerate(row):
            if i == 0:
                tds.append(
                    f'<td background-color="{TD0_BG}" vertical-align="top">{cell_xml(c, False, True)}</td>'
                )
            else:
                tds.append(f'<td vertical-align="top">{cell_xml(c, False, False)}</td>')
        trs.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{ths}</tr></thead><tbody>{''.join(trs)}</tbody></table>"


def parse_table(lines: list[str], i: int) -> tuple[str, int]:
    rows = []
    while i < len(lines) and lines[i].startswith("|"):
        raw = lines[i].strip()
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if re.match(r"^:?-+:?$", cells[0].replace(" ", "")) or all(
            re.match(r"^:?-+:?$", c.replace(" ", "") or "-") for c in cells
        ):
            i += 1
            continue
        rows.append(cells)
        i += 1
    return table_xml(rows), i


def take_until(lines: list[str], i: int, end_re: str) -> tuple[str, int]:
    buf = [lines[i]]
    i += 1
    while i < len(lines) and not re.search(end_re, buf[-1], re.I):
        buf.append(lines[i])
        i += 1
    if i < len(lines) and not re.search(end_re, buf[-1], re.I):
        buf.append(lines[i])
        i += 1
    return "\n".join(buf), i


def parse_html_table(lines: list[str], i: int) -> tuple[str, int]:
    html, i = take_until(lines, i, r"</table>")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.S | re.I):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)
        rows.append([re.sub(r"\s+", " ", c).strip() for c in cells])
    return table_xml(rows), i


# fig-alternating-timeline 深彩色卡 → 飞书白底浅彩色（白卡 + 浅顶栏 + 深字）
TL_LEAF_TO_TINT = {
    "6a4c93": "#EDE7F6",
    "2e86ab": "#E3F2FD",
    "2d936c": "#E8F5E9",
    "f18f01": "#FFF8E1",
    "3d5a80": "#ECEFF1",
    "a23b72": "#FCE4EC",
    "c67500": "#FFF3E0",
    "3370ff": "#E0F7FA",
    "e63946": "#FCE4EC",
}
TL_STROKE_TO_TINT = {
    "4a3566": "#EDE7F6",
    "1b4965": "#E3F2FD",
    "1e6b4e": "#E8F5E9",
    "c67500": "#FFF8E1",
    "2b3f5c": "#ECEFF1",
    "6e284e": "#FCE4EC",
    "8a5100": "#FFF3E0",
}


def _hex_key(col: str) -> str:
    key = col.lstrip("#")
    if len(key) == 3:
        key = "".join(ch * 2 for ch in key)
    return key.lower()


def is_alternating_timeline_svg(svg: str) -> bool:
    if re.search(r"\b(?:dtl-|dbr-)", svg):
        return True
    if "暗色主题" in svg and ("时间线" in svg or "墙钟" in svg):
        return True
    if re.search(r"#0[Dd]1117", svg) and re.search(r'height="(?:148|132)"', svg):
        return True
    return False


def lighten_alternating_timeline_for_feishu(svg: str) -> str:
    """深底整卡时间线 / 比例条 → 白底浅顶栏白卡（或浅段），字改深色。Markdown 源图不动。"""

    def card_rect(m: re.Match) -> str:
        tag, fill = m.group(0), m.group(1)
        if _hex_key(fill) not in TL_LEAF_TO_TINT:
            return tag
        tag = re.sub(r"""\bfill=(["'])#[0-9A-Fa-f]{3,8}\1""", 'fill="#FFFFFF"', tag)
        if re.search(r"\bstroke=", tag):
            tag = re.sub(
                r"""\bstroke=(["'])#[0-9A-Fa-f]{3,8}\1""",
                'stroke="#1F2329"',
                tag,
            )
        return tag

    # 交错卡片身（约 148/132 高）改白底深边
    svg = re.sub(
        r"""<rect\b[^>]*\bheight="(?:148|132)"[^>]*\bfill="(#[0-9A-Fa-f]{3,8})"[^>]*>""",
        card_rect,
        svg,
    )
    svg = re.sub(
        r"""<rect\b[^>]*\bfill="(#[0-9A-Fa-f]{3,8})"[^>]*\bheight="(?:148|132)"[^>]*>""",
        card_rect,
        svg,
    )

    def mapped_color(col: str, table: dict[str, str]) -> str | None:
        return table.get(_hex_key(col))

    def attr_map(m: re.Match) -> str:
        attr, q, col = m.group(1), m.group(2), m.group(3)
        tint = mapped_color(col, TL_LEAF_TO_TINT) or mapped_color(col, TL_STROKE_TO_TINT)
        if tint and attr.lower() in {"fill", "stroke"}:
            # 卡身已改白，剩下的叶色是顶栏 path / 比例条 / 圆点
            return f"{attr}={q}{tint}{q}"
        if _hex_key(col) == "0d1117":
            return f"{attr}={q}#FFFFFF{q}"
        if _hex_key(col) == "555577":
            return f"{attr}={q}#D0D3D6{q}"
        if _hex_key(col) in {"ffffff"} and attr.lower() == "fill":
            return m.group(0)
        if _hex_key(col) == "e8eaed":
            return f"{attr}={q}#646A73{q}"
        if _hex_key(col) == "c9d1d9":
            return f"{attr}={q}#8F959E{q}"
        return m.group(0)

    svg = re.sub(
        r"""\b(fill|stroke|stop-color)=(["'])(#[0-9A-Fa-f]{3,8})\2""",
        attr_map,
        svg,
    )
    svg = re.sub(r"background:\s*#0[Dd]1117", "background:#FFFFFF", svg)
    svg = svg.replace("fill:#FFFFFF", "fill:#1F2329")
    svg = svg.replace("fill:#E8EAED", "fill:#646A73")
    svg = svg.replace("fill:#C9D1D9", "fill:#8F959E")
    svg = svg.replace("fill:#e8eaed", "fill:#646A73")
    svg = svg.replace("fill:#c9d1d9", "fill:#8F959E")
    # 卡身 fill="#FFFFFF" 被上一行 CSS 替换误伤时，rect 已是属性不是 style
    return svg


def lighten_svg_for_feishu(svg: str) -> str:
    """暗色水平泳道（fig-horizontal-swimlane）→ 白底画板可读的浅色。节点饱和填色保持，白字保留。
    fig-alternating-timeline 深彩色时间线改走浅彩色白卡，见 lighten_alternating_timeline_for_feishu。"""
    if is_alternating_timeline_svg(svg):
        return lighten_alternating_timeline_for_feishu(svg)
    fill_map = {k.lstrip("#"): v for k, (v, _) in LAYER_FILL.items()}

    def color_repl(m: re.Match) -> str:
        attr, q, col = m.group(1), m.group(2), m.group(3)
        key = col.lstrip("#")
        if len(key) == 3:
            key = "".join(ch * 2 for ch in key)
        mapped = fill_map.get(key.lower())
        return f"{attr}={q}{mapped}{q}" if mapped else m.group(0)

    svg = re.sub(
        r"""\b(fill|stroke|stop-color)=(["'])(#[0-9A-Fa-f]{3,8})\2""",
        color_repl,
        svg,
    )
    svg = re.sub(r"background:\s*#0[Dd]1117", "background:#F8FAFC", svg)

    def text_open(m: re.Match) -> str:
        tag = m.group(0)
        if re.search(r'font-size="(14|16)"', tag) and re.search(
            r'fill="#(?:FFFFFF|fff)"', tag, re.I
        ):
            return re.sub(r'fill="#(?:FFFFFF|fff)"', 'fill="#1F2329"', tag, flags=re.I)
        return tag

    return re.sub(r"<text\b[^>]*>", text_open, svg)


def parse_svg(lines: list[str], i: int, out_dir: Path, svg_n: list[int]) -> tuple[str, int]:
    html, i = take_until(lines, i, r"</svg>")
    html = lighten_svg_for_feishu(html)
    n = svg_n[0]
    (out_dir / f"fig{n}.svg").write_text(html, encoding="utf-8")
    svg_n[0] += 1
    rel = f"@./{out_dir.name}/fig{n}.svg"
    return f'<whiteboard type="svg" path="{xml_esc(rel)}"></whiteboard>', i


def fence_caption(lang: str, heading: str, code: str) -> str:
    theme = strip_heading_num(heading) or ""
    first = ""
    for line in code.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("//"):
            first = s
            break
    m = re.search(r"\b([A-Za-z_][\w.]*)\s*\(", first)
    ident = m.group(1) if m else ""
    role = LANG_ROLE.get(lang.lower(), "代码示例") if lang else "代码示例"
    if ident and ("(" in first) and lang.lower() in {"c", "h", "cpp", "go"}:
        if first.endswith(";") or re.match(r".*\w+\s+\w+\s*\(", first):
            role = "函数声明"
        else:
            role = "调用示例"
        theme = ident
    cap = f"{theme} {role}".strip()
    cap = re.sub(r"\s+", " ", cap)
    if cap in {"代码示例", "示例", "代码", lang}:
        cap = f"{theme or '本节'} {role}".strip()
    return cap[:80]


def mermaid_for_feishu(src: str) -> tuple[str, str]:
    title = ""
    m = re.search(r"^title:\s*(.+)$", src, re.M)
    if m:
        title = m.group(1).strip()
    body = re.sub(r"^---\n.*?---\n", "", src, count=1, flags=re.S)
    body = re.sub(r"^%%\{init:.*?\}%%\n?", "", body, flags=re.M)
    return body.strip() + "\n", title


def convert(md_path: Path, out_dir: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    mermaid_dir = out_dir / "mermaid"
    mermaid_dir.mkdir(exist_ok=True)
    titles = []
    mermaid_n = [0]
    svg_n = [0]
    heading = "文档"

    def take_mermaid(m):
        body, title = mermaid_for_feishu(m.group(1))
        if not title:
            title = f"{strip_heading_num(heading)} 关系"
        i = mermaid_n[0]
        (mermaid_dir / f"m{i}.mmd").write_text(body, encoding="utf-8")
        titles.append(title)
        mermaid_n[0] += 1
        return "\n<whiteboard type=\"blank\"></whiteboard>\n"

    text = re.sub(r"```mermaid\n(.*?)```", take_mermaid, text, flags=re.S)

    lines = text.splitlines()
    title_doc = md_path.stem
    chunks = []
    i = 0
    list_buf = []
    list_tag = None

    def flush_list():
        nonlocal list_buf, list_tag
        if not list_buf:
            return
        items = "".join(f"<li>{inline_md(x)}</li>" for x in list_buf)
        chunks.append(f"<{list_tag}>{items}</{list_tag}>")
        list_buf, list_tag = [], None

    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not chunks:
            title_doc = strip_heading_num(line[2:].strip())
            i += 1
            continue
        if re.match(r"^#{2,6}\s", line):
            flush_list()
            hashes, rest = re.match(r"^(#{2,6})\s+(.*)$", line).groups()
            heading = rest
            text_h = strip_heading_num(rest)
            level = min(len(hashes) - 1, 6)  # ## → h1, ### → h2
            chunks.append(f'<h{level} seq="auto">{xml_esc(text_h)}</h{level}>')
            i += 1
            continue
        if re.match(r"^\s*<table\b", line, re.I):
            flush_list()
            tbl, i = parse_html_table(lines, i)
            chunks.append(tbl)
            continue
        if re.match(r"^\s*<svg\b", line, re.I):
            flush_list()
            wb, i = parse_svg(lines, i, out_dir, svg_n)
            chunks.append(wb)
            continue
        if re.match(r"^\s*</?p\b[^>]*>\s*$", line, re.I):
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-+:?", lines[i + 1]):
            flush_list()
            tbl, i = parse_table(lines, i)
            chunks.append(tbl)
            continue
        if line.startswith("```") and not line.startswith("```mermaid"):
            flush_list()
            lang = line.strip("`").strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code = "\n".join(buf)
            cap = fence_caption(lang, heading, code)
            inner = xml_esc(code).replace("\n", "<br/>")
            lang_attr = f' lang="{xml_esc(lang)}"' if lang else ""
            chunks.append(f'<pre{lang_attr} caption="{xml_esc(cap)}"><code>{inner}</code></pre>')
            continue
        m_ul = re.match(r"^\s*[-*]\s+(.*)$", line)
        m_ol = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m_ul or m_ol:
            tag = "ul" if m_ul else "ol"
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            list_buf.append((m_ul or m_ol).group(1))
            i += 1
            continue
        flush_list()
        if line.strip() in {"---", "***"}:
            chunks.append("<hr/>")
            i += 1
            continue
        if line.strip() == "<whiteboard type=\"blank\"></whiteboard>":
            chunks.append('<whiteboard type="blank"></whiteboard>')
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        chunks.append(f"<p>{inline_md(line.strip())}</p>")
        i += 1
    flush_list()

    xml = f"<title>{xml_esc(title_doc)}</title>" + "".join(chunks)
    xml_path = out_dir / "doc.xml"
    xml_path.write_text(xml, encoding="utf-8")
    manifest = {
        "title": title_doc,
        "xml": str(xml_path),
        "mermaid_count": mermaid_n[0],
        "titles": titles,
        "bytes": xml_path.stat().st_size,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for i, t in enumerate(titles):
        (mermaid_dir / f"title{i}.txt").write_text(t, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "title": title_doc,
                "xml": "doc.xml",
                "bytes": manifest["bytes"],
                "mermaid_count": mermaid_n[0],
                "titles": titles,
            },
            ensure_ascii=False,
        )
    )
    return manifest


def audit_xml(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    if raw.lstrip().startswith("{"):
        data = json.loads(raw)
        content = (
            data.get("data", {}).get("document", {}).get("content")
            or data.get("document", {}).get("content")
            or ""
        )
    else:
        content = raw
    issues = []
    h = re.findall(r"<h([1-6])([^>]*)>(.*?)</h\1>", content)
    if h and h[0][0] != "1":
        issues.append(f"首个标题是 h{h[0][0]}，应从 h1 起篇")
    for lv, attrs, text in h:
        if 'seq="auto"' not in attrs:
            issues.append(f"h{lv} 缺 seq=auto: {re.sub('<[^>]+>', '', text)[:40]}")
        plain = re.sub(r"<[^>]+>", "", text)
        if re.match(r"^\d+(\.\d+)*\.\s", plain):
            issues.append(f"标题仍手写序号: {plain[:40]}")
        if "<code>" in text:
            issues.append(f"标题含 code: {plain[:40]}")
    pres = re.findall(r"<pre([^>]*)>", content)
    for attrs in pres:
        cap = re.search(r'caption="([^"]*)"', attrs)
        if not cap or not cap.group(1).strip() or cap.group(1).strip() in {"代码块", "示例", "代码"}:
            issues.append("存在缺实际含义 caption 的 pre")
    tables = re.findall(r"<table[\s\S]*?</table>", content)
    unstyled = 0
    for t in tables:
        if TH_BG not in t or TD0_BG not in t:
            unstyled += 1
    if unstyled:
        issues.append(f"{unstyled}/{len(tables)} 张表缺浅紫表头或浅蓝首列")
    if "&lt;table" in content or "&lt;thead" in content or "&lt;svg" in content:
        issues.append("HTML 表或 SVG 被转义成源码，应分别为 table / whiteboard")
    if "\x00" in content:
        issues.append("XML 含 NUL，飞书会截断正文")
    wbs = re.findall(r"<whiteboard[^>]*>", content)
    tokens = re.findall(r'token="([^"]+)"', "".join(wbs))
    print(
        json.dumps(
            {
                "headings": len(h),
                "h1": sum(1 for x in h if x[0] == "1"),
                "tables": len(tables),
                "pre": len(pres),
                "whiteboards": len(wbs),
                "whiteboard_tokens": tokens,
                "issues": issues,
                "ok": not issues,
            },
            ensure_ascii=False,
        )
    )


def walk_text(tobj: dict) -> None:
    if not isinstance(tobj, dict):
        return
    rt = tobj.get("rich_text") or {}
    paras = rt.get("paragraphs") or []

    def strip_tags(s: str) -> str:
        s = re.sub(r"</?b>", "", s)
        s = re.sub(r"</?small>", "", s)
        return s.replace("<br/>", "").replace("<br>", "")

    for p in paras:
        for el in p.get("elements") or []:
            te = el.get("text_element") or {}
            if "text" in te:
                te["text"] = strip_tags(te["text"])
    if paras:
        for el in paras[0].get("elements") or []:
            te = el.setdefault("text_element", {})
            ts = te.setdefault("text_style", {})
            ts["font_weight"] = "bold"
        if len(paras) >= 2:
            for el in paras[1].get("elements") or []:
                te = el.setdefault("text_element", {})
                ts = te.setdefault("text_style", {})
                ts["font_size"] = 11
                ts["font_weight"] = "regular"
        lines = []
        for p in paras:
            parts = []
            for el in p.get("elements") or []:
                parts.append((el.get("text_element") or {}).get("text") or "")
            lines.append("".join(parts))
        tobj["text"] = "\n".join(lines)
    elif isinstance(tobj.get("text"), str):
        t = tobj["text"]
        t = re.sub(r"</?b>", "", t)
        t = re.sub(r"</?small>", "", t)
        t = t.replace("<br/>", "\n").replace("<br>", "\n")
        tobj["text"] = t


def set_text_color(tobj: dict, color: str) -> None:
    if not isinstance(tobj, dict):
        return
    tobj["text_color"] = color
    tobj["text_color_type"] = 1
    for p in (tobj.get("rich_text") or {}).get("paragraphs") or []:
        for el in p.get("elements") or []:
            te = el.setdefault("text_element", {})
            ts = te.setdefault("text_style", {})
            ts["text_color"] = color
            ts["text_color_type"] = 1


def estimate_text_px(s: str, font_size: float) -> float:
    w = 0.0
    for ch in s:
        if ch.isspace():
            w += 0.4 * font_size
        elif "\u4e00" <= ch <= "\u9fff" or ch in "（）·，、：；《》":
            w += 1.12 * font_size
        else:
            w += 0.78 * font_size
    return w


def fit_overlay_text(nodes: list) -> None:
    """加宽被裁切的 text_shape：框内注释放到节点宽，边标按字宽扩，不缩小字号。"""
    boxes = [
        n
        for n in nodes
        if n.get("type") == "composite_shape"
        and 40 <= (n.get("height") or 0) <= 80
        and (n.get("width") or 0) >= 80
        and (n.get("style") or {}).get("fill_color", "").lower() in LEAF_FILL
    ]
    canvas = max(
        (n.get("x", 0) + n.get("width", 0) for n in nodes if (n.get("width") or 0) > 400),
        default=920,
    )
    for n in nodes:
        if n.get("type") not in {"text_shape", "text"}:
            continue
        tobj = n.get("text") if isinstance(n.get("text"), dict) else {}
        s = (tobj or {}).get("text") or ""
        fs = float((tobj or {}).get("font_size") or 11)
        if not s or fs >= 20:
            continue
        need = estimate_text_px(s, fs) + 22
        x, y, w, h = n.get("x") or 0, n.get("y") or 0, n.get("width") or 0, n.get("height") or 0
        cx, cy = x + w / 2, y + h / 2
        parent = next(
            (
                b
                for b in boxes
                if b["x"] <= cx <= b["x"] + b["width"] and b["y"] <= cy <= b["y"] + b["height"]
            ),
            None,
        )
        if parent:
            pw = parent["width"]
            if need > pw - 4:
                extra = need + 8 - pw
                parent["x"] = parent["x"] - extra / 2
                parent["width"] = pw + extra
                pw = parent["width"]
            new_w = min(max(need, w), pw - 4)
            n["width"] = new_w
            n["x"] = parent["x"] + (pw - new_w) / 2
        else:
            n["width"] = max(need, w)
            n["x"] = cx - n["width"] / 2
            if n["x"] + n["width"] > canvas:
                n["x"] = canvas - n["width"]
            if n["x"] < 0:
                n["x"] = 0
            # 同道水平边标不要塞进 44px 节点缝，抬到框顶上方
            if fs <= 12 and x > 120 and 60 <= y <= 100:
                n["y"] = 44
        n["height"] = max(h, fs * 1.5)


def patch_board(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes") or []
    for n in nodes:
        if n.get("type") == "group":
            n.pop("style", None)
            continue
        st = n.setdefault("style", {})
        if n.get("type") == "section":
            st["fill_color"] = "#F3F4F6"
            st["fill_color_type"] = 1
        walk_text(n.get("text") if isinstance(n.get("text"), dict) else None)
        if isinstance(n.get("text"), dict):
            walk_text(n["text"])
        fc = (st.get("fill_color") or "").lower()
        if fc in LAYER_FILL:
            nf, tc = LAYER_FILL[fc]
            st["fill_color"] = nf
            st["fill_color_type"] = 1
            if isinstance(n.get("text"), dict):
                set_text_color(n["text"], tc)
        elif fc in LEAF_FILL and isinstance(n.get("text"), dict):
            set_text_color(n["text"], "#FFFFFF")
        bc = (st.get("border_color") or "").lower()
        if bc in LAYER_FILL:
            st["border_color"] = LAYER_FILL[bc][0]
            st["border_color_type"] = 1
        t = n.get("text")
        if isinstance(t, dict):
            fs = t.get("font_size")
            tc = (t.get("text_color") or "").lower()
            if fs in (14, 16) and tc in {"#ffffff", "#fff"}:
                set_text_color(t, "#1F2329")

    def rec(o):
        if isinstance(o, dict):
            if isinstance(o.get("code"), str):
                o["code"] = re.sub(r"</?b>|</?small>|<br\s*/?>", lambda m: "\\n" if "br" in m.group(0) else "", o["code"])
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for x in o:
                rec(x)

    fit_overlay_text(nodes)
    rec(data)
    blob = json.dumps(data, ensure_ascii=False)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": "<small>" not in blob and "<b>" not in blob,
                "nodes": len(nodes),
                "has_small": "<small>" in blob,
                "has_b": "<b>" in blob,
                "section_fill_ok": "#F3F4F6" in blob or "#f3f4f6" in blob,
            }
        )
    )


def audit_board(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    titles = []
    for n in data.get("nodes") or []:
        if n.get("type") in {"text", "text_shape"}:
            t = n.get("text") or {}
            titles.append(
                {
                    "text": t.get("text"),
                    "italic": t.get("italic"),
                    "font_weight": t.get("font_weight"),
                    "font_size": t.get("font_size"),
                }
            )
    issues = []
    if "<small>" in blob or "<b>" in blob or "<br" in blob:
        issues.append("raw 仍有字面量 HTML")
    if not any(t.get("italic") is True for t in titles):
        issues.append("缺少斜体画布标题")
    print(
        json.dumps(
            {"titles": titles, "issues": issues, "ok": not issues},
            ensure_ascii=False,
        )
    )


def make_title_dsl(title: str, width: float, x: float = 0, y: float = -48) -> None:
    dsl = {
        "version": 2,
        "nodes": [
            {
                "type": "text",
                "id": "title1",
                "x": x,
                "y": y,
                "width": width,
                "height": 36,
                "text": title,
                "fontSize": 24,
                "textAlign": "center",
                "textColor": "#1F2329",
            }
        ],
    }
    json.dump(dsl, sys.stdout, ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("md")
    c.add_argument("out_dir")
    a = sub.add_parser("audit-xml")
    a.add_argument("path")
    b = sub.add_parser("patch-board")
    b.add_argument("path")
    d = sub.add_parser("audit-board")
    d.add_argument("path")
    t = sub.add_parser("title-dsl")
    t.add_argument("title")
    t.add_argument("width", type=float)
    args = p.parse_args()
    if args.cmd == "convert":
        convert(Path(args.md), Path(args.out_dir))
    elif args.cmd == "audit-xml":
        audit_xml(Path(args.path))
    elif args.cmd == "patch-board":
        patch_board(Path(args.path))
    elif args.cmd == "audit-board":
        audit_board(Path(args.path))
    elif args.cmd == "title-dsl":
        make_title_dsl(args.title, args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
