#!/usr/bin/env python3
"""飞书 fetch 落盘后抽大纲。stdout 只打 JSON；正文/章节留在磁盘。"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

NUM_RE = re.compile(
    r"(?<![A-Za-z_])(\d+(?:\.\d+)?\s*(?:µs|us|ms|s|%|次|组|张|份|个|人日)?|\d{1,3}(?:,\d{3})+)(?![A-Za-z_])"
)
H_XML_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.I | re.S)
H_MD_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.M)
TABLE_XML_RE = re.compile(r"<table\b", re.I)
IMG_RE = re.compile(r"<image\b[^>]*>", re.I)
WB_RE = re.compile(r"<whiteboard\b[^>]*>", re.I)
TOKEN_RE = re.compile(r'\btoken="([^"]+)"', re.I)
PREVIEW = 240


def die(msg: str) -> None:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)


def unwrap_fetch(raw: str) -> str:
    text = raw.strip()
    if text.startswith("{"):
        data = json.loads(text)
        return (
            data.get("data", {}).get("document", {}).get("content")
            or data.get("document", {}).get("content")
            or data.get("content")
            or data.get("pretty")
            or ""
        )
    return raw


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|h[1-6]|li|tr|div)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def slug_heading(s: str, i: int) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", s).strip("-")
    return f"{i:02d}-{(s[:40] or 'section')}"


def split_sections(content: str) -> list[dict[str, str]]:
    marks: list[tuple[int, int, str]] = []
    for m in H_XML_RE.finditer(content):
        title = strip_tags(m.group(2))
        if title:
            marks.append((m.start(), int(m.group(1)), title))
    if not marks:
        for m in H_MD_RE.finditer(content):
            marks.append((m.start(), len(m.group(1)), m.group(2).strip()))
    if not marks:
        body = strip_tags(content)
        return [{"level": 0, "title": "(全文无标题)", "text": body}]
    marks.sort(key=lambda x: x[0])
    out = []
    for i, (pos, level, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(content)
        chunk = content[pos:end]
        out.append({"level": level, "title": title, "text": strip_tags(chunk)})
    return out


def collect_numbers(text: str) -> list[str]:
    seen: list[str] = []
    for m in NUM_RE.finditer(text):
        v = re.sub(r"\s+", "", m.group(1))
        if v not in seen:
            seen.append(v)
        if len(seen) >= 40:
            break
    return seen


def cmd_extract(paths: list[Path], out_dir: Path, urls: list[str]) -> dict[str, Any]:
    if not paths:
        die("需要至少一个 fetch/md 文件")
    out_dir.mkdir(parents=True, exist_ok=True)
    sec_dir = out_dir / "sections"
    sec_dir.mkdir(exist_ok=True)
    all_sec: list[dict[str, Any]] = []
    heads: list[str] = []
    n_table = n_img = n_wb = 0
    img_tok: list[str] = []
    wb_tok: list[str] = []
    numbers: list[str] = []
    bytes_in = 0
    plains: list[str] = []

    for si, p in enumerate(paths):
        raw = p.read_text(encoding="utf-8")
        bytes_in += len(raw.encode("utf-8"))
        content = unwrap_fetch(raw) or raw
        n_table += len(TABLE_XML_RE.findall(content))
        n_table += len(re.findall(r"^\s*\|.+\|\s*$", content, flags=re.M)) // 8
        for m in IMG_RE.finditer(content):
            n_img += 1
            tm = TOKEN_RE.search(m.group(0))
            if tm:
                img_tok.append(tm.group(1))
        for m in WB_RE.finditer(content):
            n_wb += 1
            tm = TOKEN_RE.search(m.group(0))
            if tm:
                wb_tok.append(tm.group(1))
        plains.append(f"----- source {si}: {p.name} -----\n{strip_tags(content)}")
        for j, sec in enumerate(split_sections(content)):
            name = slug_heading(sec["title"], len(all_sec))
            rel = f"sections/{name}.txt"
            (out_dir / rel).write_text(sec["text"] + "\n", encoding="utf-8")
            rec = {
                "file": rel,
                "level": sec["level"],
                "title": sec["title"],
                "chars": len(sec["text"]),
                "preview": sec["text"][:PREVIEW],
                "source": p.name,
            }
            all_sec.append(rec)
            heads.append(sec["title"])
            for n in collect_numbers(sec["text"]):
                if n not in numbers:
                    numbers.append(n)

    source_txt = out_dir / "source.txt"
    source_txt.write_text("\n\n".join(plains) + "\n", encoding="utf-8")
    outline = {
        "ok": True,
        "bytes_in": bytes_in,
        "chars_txt": source_txt.stat().st_size,
        "urls": urls,
        "headings": heads,
        "sections": all_sec,
        "tables_est": n_table,
        "images": n_img,
        "image_tokens": img_tok[:30],
        "whiteboards": n_wb,
        "whiteboard_tokens": wb_tok[:30],
        "numbers": numbers[:40],
        "source_txt": "source.txt",
        "note": "勿虚构画板/图片内容；只按章节与计数写「输出成果」",
    }
    (out_dir / "outline.json").write_text(
        json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = {
        "ok": True,
        "outline": str(out_dir / "outline.json"),
        "source_txt": str(source_txt),
        "chars_txt": outline["chars_txt"],
        "heading_count": len(heads),
        "headings": heads[:40],
        "tables_est": n_table,
        "images": n_img,
        "whiteboards": n_wb,
        "numbers": numbers[:20],
        "section_files": [s["file"] for s in all_sec],
        "urls": urls,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="成果说明：extract 大纲")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("src", nargs="+", type=Path)
    e.add_argument("-o", "--out", type=Path, required=True)
    e.add_argument("--url", action="append", default=[], help="用户原始飞书链接，写入大纲")
    args = ap.parse_args()
    if args.cmd == "extract":
        cmd_extract(args.src, args.out, args.url)


if __name__ == "__main__":
    main()
