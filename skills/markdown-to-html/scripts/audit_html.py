#!/usr/bin/env python3
"""验收 md2html 产物：只打 JSON 摘要，禁止把整页 HTML 印进对话。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from md2html.figures import default_figures_dir  # noqa: E402
from md2html.mermaid_analyze import analyze_markdown  # noqa: E402

CDN_OK = ("cdn.jsdelivr.net",)
EXT_CSS_RE = re.compile(
    r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', re.I
)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)


def audit(html_path: Path, md_path: Path | None) -> dict:
    html = html_path.read_text(encoding="utf-8")
    issues: list[dict] = []

    def add(code: str, msg: str) -> None:
        issues.append({"code": code, "msg": msg})

    if not re.search(r"<!DOCTYPE\s+html>", html, re.I):
        add("doctype", "缺 <!DOCTYPE html>")
    if 'id="layout"' not in html or 'id="sidebar"' not in html:
        add("layout", "缺 #layout / #sidebar")
    if "mdGithubSlug" not in html and "mdHeadingHtml" not in html:
        add("slug", "缺 GitHub slug 运行时（不要拿掉 anchor.js）")
    if re.search(r"\.mermaid\s+svg\s*\{[^}]*max-width\s*:\s*none", html, re.I | re.S):
        add("maxwidth-css", "禁止 .mermaid svg { max-width:none }")
    if "useMaxWidth" in html and re.search(
        r"useMaxWidth\s*:\s*true", html
    ):
        add("maxwidth-js", "页面 flowchart 须 useMaxWidth:false")
    for tag in EXT_CSS_RE.findall(html):
        hm = HREF_RE.search(tag)
        href = hm.group(1) if hm else ""
        if href and not href.startswith("data:") and "cdn.jsdelivr.net" not in href:
            add("ext-css", f"外部样式表: {href}")
    if "<img " in html.lower() and re.search(
        r'<img[^>]+src=["\']https?://', html, re.I
    ):
        add("ext-img", "图表不要用外部 <img> URL")

    sidecar_missing: list[str] = []
    downgrade_n = 0
    mermaid_n = 0
    if md_path and md_path.is_file():
        md = md_path.read_text(encoding="utf-8")
        fig_dir = default_figures_dir(md_path)
        blocks = analyze_markdown(md)
        mermaid_n = len(blocks)
        for b in blocks:
            if not b.should_downgrade:
                continue
            downgrade_n += 1
            name = f"mermaid-{b.index}.html"
            side = fig_dir / name
            if not side.is_file():
                sidecar_missing.append(name)
                add("sidecar", f"应降级块 #{b.index} 缺 {name}")
            elif f"mermaid-{b.index}" not in html:
                add("template", f"HTML 未嵌入 mermaid-{b.index} 模板")
        if "sequenceDiagram" in md and "#3370FF" not in html:
            add("seq-color", "源含 sequenceDiagram，页面应含向右色 #3370FF")

    result = {
        "ok": not issues,
        "html": str(html_path),
        "bytes": html_path.stat().st_size,
        "mermaid_blocks": mermaid_n,
        "downgrade": downgrade_n,
        "sidecar_missing": sidecar_missing,
        "issues": issues,
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="md2html 产物验收")
    ap.add_argument("html", type=Path)
    ap.add_argument("--md", type=Path, default=None)
    args = ap.parse_args()
    md = args.md
    if md is None:
        cand = args.html.with_suffix(".md")
        if cand.is_file():
            md = cand
    r = audit(args.html, md)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    raise SystemExit(0 if r["ok"] else 2)


if __name__ == "__main__":
    main()
