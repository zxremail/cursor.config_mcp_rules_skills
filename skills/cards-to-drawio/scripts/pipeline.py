#!/usr/bin/env python3
"""分层卡片 HTML → 独立 .drawio。stdout 只打 JSON 摘要。"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

PAGE_W = 1040
BG = "#0d1117"
BOX_X, BOX_W = 15, 1010
CONTENT_X0, CONTENT_W, GAP = 25, 990, 10
TITLE_H, ARROW_H, TOP = 30, 21, 15
LAYER_GAP = 28

PALETTES = [
    {"stroke": "#58a6ff", "fill": "#0d2137", "font": "#79c0ff", "keys": ("blue", "58a6ff", "mcu", "外设", "i/o", "io-")},
    {"stroke": "#da3633", "fill": "#2d1215", "font": "#ffa198", "keys": ("red", "da3633", "ipc", "cli" )},
    {"stroke": "#6e40c9", "fill": "#1a1428", "font": "#d2a8ff", "keys": ("purple", "6e40c9", "内核", "kernel", "运维")},
    {"stroke": "#f0883e", "fill": "#1a150d", "font": "#ffcc80", "keys": ("orange", "f0883e", "中枢", "调度", "事件")},
    {"stroke": "#238636", "fill": "#122117", "font": "#7ee787", "keys": ("green", "238636", "3fb950", "数据", "业务")},
    {"stroke": "#30363d", "fill": "#21262d", "font": "#8b949e", "keys": ("gray", "grey", "dim", "30363d", "基础", "infra")},
]
DASHED = {"stroke": "#238636", "fill": "#0a1e0a", "font": "#7ee787"}
DEFAULT = PALETTES[-1]


def die(msg: str) -> None:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)


def xml_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def html_txt(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr_html(html: str) -> str:
    return xml_esc(html)


def pick_palette(blob: str) -> dict[str, str]:
    b = blob.lower()
    if any(k in b for k in ("dashed", "支柱", "highlight", "0a1e0a")):
        return DASHED
    for p in PALETTES:
        if any(k in b for k in p["keys"]):
            return p
    m = re.search(r"#([0-9a-f]{6})", b)
    if m:
        hex6 = "#" + m.group(1)
        for p in PALETTES:
            if hex6 in (p["stroke"], p["fill"], p["font"]):
                return p
    return DEFAULT


@dataclass
class El:
    tag: str
    attrs: dict[str, str]
    children: list[El] = field(default_factory=list)
    text: str = ""

    @property
    def classes(self) -> str:
        return self.attrs.get("class", "")

    def has(self, *names: str) -> bool:
        cs = set(self.classes.split())
        return any(n in cs or n in self.classes for n in names)

    def style(self) -> str:
        return self.attrs.get("style", "")


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = El("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        node = El(tag.lower(), ad)
        self.stack[-1].children.append(node)
        if tag.lower() not in {"br", "img", "hr", "meta", "input"}:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].text += data


def parse_html(src: str) -> El:
    p = TreeBuilder()
    p.feed(src)
    p.close()
    return p.root


def walk(el: El):
    yield el
    for c in el.children:
        yield from walk(c)


def text_of(el: El) -> str:
    bits = [el.text]
    for c in el.children:
        if c.tag == "br":
            bits.append("\n")
        bits.append(text_of(c))
    return re.sub(r"[ \t]+", " ", "".join(bits)).strip()


def find_all(el: El, pred) -> list[El]:
    return [n for n in walk(el) if pred(n)]


@dataclass
class Card:
    title: str
    lines: list[str]
    blob: str
    dashed: bool = False


@dataclass
class Layer:
    label: str
    sub: str
    cards: list[Card]
    blob: str


@dataclass
class Figure:
    layers: list[Layer]
    arrows: list[str]  # after layer i: arrows[i] (len = len(layers) or +)
    fig_id: str


def extract_card(el: El) -> Card:
    notes = find_all(el, lambda n: n.has("note"))
    note_txt = "\n".join(text_of(n) for n in notes if text_of(n))
    full = text_of(el)
    if note_txt and full.endswith(note_txt):
        title = full[: -len(note_txt)].strip(" \n")
        lines = [ln.strip() for ln in note_txt.splitlines() if ln.strip()]
    else:
        parts = [ln.strip() for ln in full.splitlines() if ln.strip()]
        title = parts[0] if parts else ""
        lines = parts[1:]
    blob = el.classes + el.style() + title
    dashed = el.has("dashed") or "dashed" in el.style() or "支柱" in title
    return Card(title=title, lines=lines, blob=blob, dashed=dashed)


def extract_figure(root: El, fig_id: str) -> Figure:
    layers: list[Layer] = []
    arrows: list[str] = []
    pending_arrow = ""
    for child in root.children:
        if child.has("arrow"):
            pending_arrow = text_of(child)
            if layers:
                arrows.append(pending_arrow)
            continue
        if child.has("layer") or "layer" in child.classes:
            hdr = next((c for c in walk(child) if c.has("layer-header")), None)
            label_el = next((c for c in walk(child) if c.has("layer-label")), None)
            sub_el = next((c for c in walk(child) if c.has("layer-sub")), None)
            body = next((c for c in walk(child) if c.has("layer-body")), None)
            label = text_of(label_el) if label_el else (text_of(hdr) if hdr else "")
            sub = text_of(sub_el) if sub_el else ""
            cards_el = []
            scope = body or child
            for n in scope.children:
                if n.has("node", "halbox") or "node" in n.classes or "halbox" in n.classes:
                    cards_el.append(n)
                if n.has("subpanel"):
                    cards_el.append(n)
            if not cards_el:
                cards_el = find_all(scope, lambda n: n.has("node", "halbox"))
            cards = [extract_card(n) for n in cards_el]
            blob = child.classes + child.style() + label + sub
            layers.append(Layer(label=label, sub=sub, cards=cards, blob=blob))
            continue
        if child.has("legend"):
            continue
        # nested customfig wrapper
        if child.has("customfig") or child.tag == "div":
            inner = extract_figure(child, fig_id)
            if inner.layers:
                return inner
    while len(arrows) < max(0, len(layers) - 1):
        arrows.append("")
    return Figure(layers=layers, arrows=arrows, fig_id=fig_id)


def find_figures(tree: El) -> list[Figure]:
    figs = find_all(tree, lambda n: n.has("customfig"))
    if not figs:
        figs = find_all(tree, lambda n: n.tag == "template")
    out: list[Figure] = []
    if not figs:
        f = extract_figure(tree, "fig")
        if f.layers:
            out.append(f)
        return out
    for i, el in enumerate(figs):
        fid = el.attrs.get("id") or f"fig{i}"
        root = el
        if el.tag == "template":
            inner = next((c for c in walk(el) if c.has("customfig")), None)
            root = inner or el
        f = extract_figure(root, fid)
        if f.layers:
            out.append(f)
    return out


def col_widths(n: int) -> list[tuple[float, float]]:
    n = max(1, n)
    w = (CONTENT_W - (n - 1) * GAP) / n
    return [(CONTENT_X0 + i * (w + GAP), w) for i in range(n)]


def card_h(card: Card) -> int:
    lines = 1 + (2 if card.lines else 0) + max(0, len(card.lines) - 1)
    if len(card.lines) >= 3:
        return min(115, 70 + 12 * len(card.lines))
    if not card.lines:
        return 50
    return 85 if len(card.title) > 20 or len(card.lines) <= 2 else 70


def value_card(card: Card) -> str:
    html = f'<b style="font-size:13px">{html_txt(card.title)}</b>'
    if card.lines:
        html += "<br><br>" + "<br>".join(html_txt(x) for x in card.lines)
    return attr_html(html)


def emit_mxfile(fig: Figure, name: str) -> str:
    cells: list[str] = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    y = TOP
    for i, layer in enumerate(fig.layers):
        pal = pick_palette(layer.blob)
        n = max(1, len(layer.cards))
        hs = [card_h(c) for c in layer.cards] or [50]
        ch = max(hs)
        layer_h = 7 + TITLE_H + 8 + ch + 10
        title = layer.label
        if layer.sub:
            title = f"{layer.label}（{layer.sub}）" if layer.label else layer.sub
        cells.append(
            f'<mxCell id="L{i}box" value="" '
            f'style="rounded=1;arcSize=2;fillColor={BG};strokeColor={pal["stroke"]};strokeWidth=2;" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="{BOX_X}" y="{y}" width="{BOX_W}" height="{layer_h}" as="geometry"/>'
            f"</mxCell>"
        )
        cells.append(
            f'<mxCell id="L{i}title" value="{xml_esc(title)}" '
            f'style="text;html=1;align=center;verticalAlign=middle;fontColor={pal["stroke"]};fontSize=14;fontStyle=1;" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="20" y="{y + 7}" width="1000" height="{TITLE_H}" as="geometry"/>'
            f"</mxCell>"
        )
        cols = col_widths(n)
        for j, card in enumerate(layer.cards):
            cp = DASHED if card.dashed else pick_palette(card.blob + layer.blob)
            x, w = cols[j]
            cells.append(
                f'<mxCell id="L{i}c{j}" value="{value_card(card)}" '
                f'style="rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor={cp["fill"]};'
                f'strokeColor={cp["stroke"]};fontColor={cp["font"]};fontSize=11;align=left;'
                f'verticalAlign=middle;spacingLeft=10;spacingRight=8'
                f'{";dashed=1;strokeStyle=dashed" if card.dashed else ""}" '
                f'vertex="1" parent="1">'
                f'<mxGeometry x="{x:.0f}" y="{y + 45}" width="{w:.0f}" height="{ch}" as="geometry"/>'
                f"</mxCell>"
            )
        y += layer_h
        if i < len(fig.layers) - 1:
            arrow = fig.arrows[i] if i < len(fig.arrows) else ""
            if not arrow:
                arrow = "↓"
            acolor = "#f0883e"
            if "出" in arrow or "↑" in arrow and "入" not in arrow:
                acolor = "#3fb950"
            if "命令" in arrow or "回送" in arrow:
                acolor = "#79c0ff"
            cells.append(
                f'<mxCell id="arrow{i}" value="{xml_esc(arrow).replace(" ", "&amp;nbsp;")}" '
                f'style="text;html=1;align=center;verticalAlign=middle;fontColor={acolor};fontSize=11;" '
                f'vertex="1" parent="1">'
                f'<mxGeometry x="{BOX_X}" y="{y + 4}" width="{BOX_W}" height="{ARROW_H}" as="geometry"/>'
                f"</mxCell>"
            )
            y += LAYER_GAP
    page_h = int(y + TOP)
    did = uuid.uuid4().hex[:8]
    inner = "".join(cells)
    return (
        f'<mxfile host="app.diagrams.net" version="22.1.0" type="device">'
        f'<diagram name="{xml_esc(name)}" id="{did}">'
        f'<mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{PAGE_W}" pageHeight="{page_h}" math="0" shadow="0" '
        f'background="{BG}">'
        f"<root>{inner}</root></mxGraphModel></diagram></mxfile>\n"
    )


def cmd_convert(html_path: Path, out_dir: Path, stems: list[str], merge: bool) -> dict:
    tree = parse_html(html_path.read_text(encoding="utf-8"))
    figs = find_figures(tree)
    if not figs:
        die("未找到 .customfig / .layer")
    out_dir.mkdir(parents=True, exist_ok=True)
    if merge and len(figs) > 1:
        die("不要把多张图塞进一个 mxfile 的多个 diagram。请去掉 --merge，让脚本按图各写一份 .drawio")
    if stems and len(stems) != len(figs):
        die(f"stem 数量 {len(stems)} 与图数量 {len(figs)} 不一致")
    written = []
    for i, fig in enumerate(figs):
        stem = stems[i] if stems else (fig.fig_id if len(figs) > 1 else html_path.stem)
        stem = re.sub(r"[^a-z0-9-]+", "-", stem.lower()).strip("-") or f"fig-{i}"
        for bad in ("-cards", "-drawio"):
            if stem.endswith(bad):
                stem = stem[: -len(bad)]
        if re.match(r"^\d{4}-\d{2}-\d{2}-", stem):
            die(f"文件名不要日期前缀: {stem}")
        path = out_dir / f"{stem}.drawio"
        xml = emit_mxfile(fig, stem)
        path.write_text(xml, encoding="utf-8")
        written.append(
            {
                "file": str(path),
                "layers": len(fig.layers),
                "cards": sum(len(l.cards) for l in fig.layers),
                "bytes": path.stat().st_size,
            }
        )
    man = {"ok": True, "count": len(written), "files": written}
    print(json.dumps(man, ensure_ascii=False))
    return man


def audit_drawio(path: Path, allow_multi: bool) -> dict:
    raw = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if "<mxfile" not in raw:
        issues.append("不是 mxfile")
    if f'background="{BG}"' not in raw and f"background='{BG}'" not in raw:
        issues.append(f"背景必须 {BG}")
    if f'pageWidth="{PAGE_W}"' not in raw:
        issues.append(f"pageWidth 必须 {PAGE_W}")
    n_diag = len(re.findall(r"<diagram\b", raw))
    if n_diag != 1 and not allow_multi:
        issues.append(f"默认只能 1 个 <diagram>，实际 {n_diag}")
    if re.search(r'\bedge="1"', raw):
        issues.append("不要用 edge 连线表达层间关系")
    vals = re.findall(r'value="([^"]*)"', raw)
    for v in vals:
        low = v.lower()
        if any(x in low for x in ("&lt;div", "&lt;span", "&lt;table", "<div", "<span", "<table")):
            issues.append("value 禁用 div/span/table")
            break
    if re.search(r"2026-\d{2}-\d{2}-", path.name) or re.search(r"\d{4}-\d{2}-\d{2}-", path.name):
        issues.append("文件名不要日期前缀")
    if path.stem.endswith("-cards") or path.stem.endswith("-drawio"):
        issues.append("文件名不要 -cards/-drawio 后缀")
    result = {
        "ok": not issues,
        "file": str(path),
        "diagrams": n_diag,
        "cells": len(re.findall(r"<mxCell\b", raw)),
        "issues": issues,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="分层卡片 HTML → drawio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("convert")
    p.add_argument("html", type=Path)
    p.add_argument("-o", "--out", type=Path, required=True)
    p.add_argument("--stem", default="", help="逗号分隔，与图一一对应")
    p.add_argument("--merge", action="store_true")
    a = sub.add_parser("audit-drawio")
    a.add_argument("file", type=Path)
    a.add_argument("--allow-multi", action="store_true")
    args = ap.parse_args()
    if args.cmd == "convert":
        stems = [s.strip() for s in args.stem.split(",") if s.strip()]
        cmd_convert(args.html, args.out, stems, args.merge)
    else:
        r = audit_drawio(args.file, args.allow_multi)
        raise SystemExit(0 if r["ok"] else 2)


if __name__ == "__main__":
    main()
