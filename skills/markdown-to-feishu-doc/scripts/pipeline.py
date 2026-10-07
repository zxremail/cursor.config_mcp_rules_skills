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
    "#0d1117": ("#F3F4F6", "#1F2329"),
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


def inline_md(text: str) -> str:
    text = re.sub(r'<span\s+style="[^"]*">(.*?)</span>', r"\1", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    placeholders = []

    def hold(s: str) -> str:
        placeholders.append(s)
        return f"\x00{len(placeholders) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: hold(f"<code>{xml_esc(m.group(1))}</code>"), text)
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: hold(f"<b>{xml_esc(m.group(1))}</b>"), text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: hold(
            f'<a href="{xml_esc(m.group(2))}">{xml_esc(strip_heading_num(m.group(1)))}</a>'
        ),
        text,
    )
    text = xml_esc(text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: placeholders[int(m.group(1))], text)
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


def patch_board(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes") or []
    for n in nodes:
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

    def rec(o):
        if isinstance(o, dict):
            if isinstance(o.get("code"), str):
                o["code"] = re.sub(r"</?b>|</?small>|<br\s*/?>", lambda m: "\\n" if "br" in m.group(0) else "", o["code"])
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for x in o:
                rec(x)

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
