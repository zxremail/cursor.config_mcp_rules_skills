#!/usr/bin/env python3
"""Mermaid sequenceDiagram → .drawio。stdout 只打 JSON 摘要。"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

PART_COLORS = [
    ("#2E86AB", "#1B4965"),
    ("#E63946", "#B52D38"),
    ("#2D936C", "#1E6B4E"),
    ("#F18F01", "#C67500"),
    ("#A23B72", "#7B2D55"),
    ("#6A4C93", "#4A3566"),
]
ARROW_RIGHT = "#0000FF"
ARROW_LEFT = "#00AA00"
ARROW_SELF = "#000000"
BOX_W, BOX_H = 120, 40
COL_GAP = 200
ORIGIN_X, ORIGIN_Y = 40, 40
ROW_H = 52
SELF_LEN = 28

FENCE_RE = re.compile(r"```[ \t]*mermaid[^\n]*\n(.*?)```", re.S | re.I)
PART_RE = re.compile(
    r"^\s*(?:participant|actor)\s+(\S+)(?:\s+as\s+(.+))?\s*$", re.I
)
MSG_RE = re.compile(
    r"^\s*(\S+?)\s*(-(?:>>?|x|\)|-)?>>?|-->>?|->|-->|-x|--x)\s*(\S+?)\s*:\s*(.*)$"
)
SKIP_RE = re.compile(
    r"^\s*(?:sequenceDiagram|autonumber|activate|deactivate|Note\b|loop\b|alt\b|"
    r"else\b|opt\b|par\b|and\b|rect\b|critical\b|break\b|end\b|title\b|%%|---)",
    re.I,
)


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


def slug(s: str) -> str:
    s = s.lower().replace("_", "-")
    s = re.sub(r"[^a-z0-9-]+", "-", s).strip("-")
    return s or "sequence"


@dataclass
class Participant:
    pid: str
    label: str


@dataclass
class Message:
    src: str
    dst: str
    text: str
    arrow: str


@dataclass
class Seq:
    participants: list[Participant] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)


def strip_yaml(body: str) -> str:
    body = body.strip()
    if body.startswith("---"):
        m = re.match(r"^---\n.*?\n---\n?(.*)$", body, re.S)
        if m:
            body = m.group(1)
    body = re.sub(r"^%%\{init:.*?\}%%\n?", "", body, flags=re.M | re.S)
    return body.strip()


def parse_sequence(src: str) -> Seq:
    src = strip_yaml(src)
    if not re.search(r"^\s*sequenceDiagram\b", src, re.M | re.I):
        die("不是 sequenceDiagram（flowchart/卡片请走对应 skill）")
    seq = Seq()
    order: list[str] = []
    labels: dict[str, str] = {}

    def ensure(pid: str, label: str | None = None) -> None:
        pid = pid.strip()
        if pid not in labels:
            labels[pid] = (label or pid).strip()
            order.append(pid)
        elif label:
            labels[pid] = label.strip()

    for raw in src.splitlines():
        line = raw.strip()
        if not line or SKIP_RE.match(line) and not MSG_RE.match(line):
            if PART_RE.match(line):
                m = PART_RE.match(line)
                assert m
                ensure(m.group(1), m.group(2))
            continue
        m = PART_RE.match(line)
        if m:
            ensure(m.group(1), m.group(2))
            continue
        m = MSG_RE.match(line)
        if m:
            a, arr, b, text = m.group(1), m.group(2), m.group(3), m.group(4)
            a = re.sub(r"[+-]$", "", a)
            b = re.sub(r"^[+-]", "", b)
            ensure(a)
            ensure(b)
            seq.messages.append(Message(src=a, dst=b, text=text.strip(), arrow=arr))
            continue
    seq.participants = [Participant(p, labels[p]) for p in order]
    if not seq.participants:
        die("没有参与者或消息")
    return seq


def extract_sequences(text: str, path: Path) -> list[tuple[str, Seq]]:
    if path.suffix.lower() in {".mmd"} or (
        "sequenceDiagram" in text and "```" not in text[:80]
    ):
        return [(path.stem, parse_sequence(text))]
    out = []
    for i, m in enumerate(FENCE_RE.finditer(text)):
        body = m.group(1)
        if not re.search(r"^\s*sequenceDiagram\b", body, re.M | re.I):
            continue
        out.append((f"{path.stem}-seq-{i}" if i else path.stem, parse_sequence(body)))
    if not out:
        die("未找到 sequenceDiagram 围栏")
    return out


def cx(i: int) -> float:
    return ORIGIN_X + i * COL_GAP + BOX_W / 2


def emit(seq: Seq, name: str) -> str:
    idx = {p.pid: i for i, p in enumerate(seq.participants)}
    n = len(seq.participants)
    life_top = ORIGIN_Y + BOX_H
    life_bot = ORIGIN_Y + BOX_H + 24 + max(1, len(seq.messages)) * ROW_H
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for i, p in enumerate(seq.participants):
        fill, stroke = PART_COLORS[i % len(PART_COLORS)]
        x = ORIGIN_X + i * COL_GAP
        cells.append(
            f'<mxCell id="p{i}" value="{xml_esc(p.label)}" '
            f'style="shape=rectangle;rounded=0;fillColor={fill};strokeColor={stroke};'
            f'fontColor=#FFFFFF;fontStyle=1;whiteSpace=wrap;html=1;" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{ORIGIN_Y}" width="{BOX_W}" height="{BOX_H}" as="geometry"/>'
            f"</mxCell>"
        )
        cells.append(
            f'<mxCell id="life{i}" style="endArrow=none;dashed=1;strokeColor=#888888;" '
            f'edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{cx(i)}" y="{life_top}" as="sourcePoint"/>'
            f'<mxPoint x="{cx(i)}" y="{life_bot}" as="targetPoint"/>'
            f"</mxGeometry></mxCell>"
        )
    for k, msg in enumerate(seq.messages):
        si, di = idx[msg.src], idx[msg.dst]
        y = ORIGIN_Y + BOX_H + 36 + k * ROW_H
        if si == di:
            color = ARROW_SELF
            x0, x1 = cx(si), cx(si)
            y1 = y + SELF_LEN
            cells.append(
                f'<mxCell id="msg{k}" style="endArrow=block;endFill=1;strokeColor={color};" '
                f'edge="1" parent="1">'
                f'<mxGeometry relative="1" as="geometry">'
                f'<mxPoint x="{x0}" y="{y}" as="sourcePoint"/>'
                f'<mxPoint x="{x1}" y="{y1}" as="targetPoint"/>'
                f"</mxGeometry></mxCell>"
            )
            lx, ly, lw = x0 + 10, y, 160
        else:
            color = ARROW_RIGHT if si < di else ARROW_LEFT
            x0, x1 = cx(si), cx(di)
            cells.append(
                f'<mxCell id="msg{k}" style="endArrow=block;endFill=1;strokeColor={color};" '
                f'edge="1" parent="1">'
                f'<mxGeometry relative="1" as="geometry">'
                f'<mxPoint x="{x0}" y="{y}" as="sourcePoint"/>'
                f'<mxPoint x="{x1}" y="{y}" as="targetPoint"/>'
                f"</mxGeometry></mxCell>"
            )
            lx = min(x0, x1) + 12
            ly = y - 18
            lw = max(80, abs(x1 - x0) - 24)
        cells.append(
            f'<mxCell id="lab{k}" value="{xml_esc(msg.text)}" '
            f'style="text;html=1;align=left;verticalAlign=middle;fillColor=none;'
            f'strokeColor=none;fontSize=11;" vertex="1" parent="1">'
            f'<mxGeometry x="{lx}" y="{ly}" width="{lw}" height="20" as="geometry"/>'
            f"</mxCell>"
        )
    page_w = int(ORIGIN_X + n * COL_GAP + 40)
    page_h = int(life_bot + 40)
    did = uuid.uuid4().hex[:8]
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<mxfile host="app.diagrams.net" version="22.1.0">'
        f'<diagram name="{xml_esc(name)}" id="{did}">'
        f'<mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" page="1" '
        f'pageWidth="{page_w}" pageHeight="{page_h}">'
        f"<root>{''.join(cells)}</root></mxGraphModel></diagram></mxfile>\n"
    )


def cmd_convert(src: Path, out_dir: Path, stem: str | None) -> dict:
    text = src.read_text(encoding="utf-8")
    seqs = extract_sequences(text, src)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for i, (auto, seq) in enumerate(seqs):
        name = stem if (stem and i == 0 and len(seqs) == 1) else (stem + f"-{i}" if stem and len(seqs) > 1 else auto)
        name = slug(name)
        if re.match(r"^\d{4}-\d{2}-\d{2}-", name):
            die("文件名不要日期前缀")
        path = out_dir / f"{name}.drawio"
        path.write_text(emit(seq, name), encoding="utf-8")
        files.append(
            {
                "file": str(path),
                "participants": len(seq.participants),
                "messages": len(seq.messages),
                "bytes": path.stat().st_size,
            }
        )
    man = {"ok": True, "count": len(files), "files": files}
    print(json.dumps(man, ensure_ascii=False))
    return man


def audit_drawio(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if "<mxfile" not in raw:
        issues.append("不是 mxfile")
    if "shape=rectangle" not in raw and "rounded=0" not in raw:
        issues.append("参与者须矩形（非圆角）")
    if "fillColor=#2E86AB" not in raw:
        issues.append("缺少第 1 参与者色板 #2E86AB")
    if "dashed=1" not in raw:
        issues.append("缺少生命线虚线")
    if "fillColor=none" not in raw:
        issues.append("消息标签须 fillColor=none")
    if ARROW_RIGHT not in raw and ARROW_LEFT not in raw and ARROW_SELF not in raw:
        issues.append("缺少方向箭头色 #0000FF/#00AA00/#000000")
    if "shape=mxgraph.flowchart.loop" in raw or "curved=1" in raw:
        issues.append("自调用不要环形箭头")
    if re.search(r"\d{4}-\d{2}-\d{2}-", path.name):
        issues.append("文件名不要日期前缀")
    result = {
        "ok": not issues,
        "file": str(path),
        "cells": len(re.findall(r"<mxCell\b", raw)),
        "issues": issues,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="sequenceDiagram → drawio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("src", type=Path)
    c.add_argument("-o", "--out", type=Path, required=True)
    c.add_argument("--stem", default="")
    a = sub.add_parser("audit-drawio")
    a.add_argument("file", type=Path)
    args = ap.parse_args()
    if args.cmd == "convert":
        cmd_convert(args.src, args.out, args.stem or None)
    else:
        r = audit_drawio(args.file)
        raise SystemExit(0 if r["ok"] else 2)


if __name__ == "__main__":
    main()
