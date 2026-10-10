#!/usr/bin/env python3
"""扫描 .md / .mmd：Mermaid 硬格式 + 管道表表头字色 + 内联 SVG 空行。stdout 只打 JSON。"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BAD_TITLES = {"流程图", "如图", "示意图", "画板", "时序图", "架构图", "如图所示"}
LIGHT_FILLS = {
    "#fff",
    "#ffffff",
    "#eee",
    "#eeeeee",
    "#f8f8f8",
    "#fafafa",
    "#f5f5f5",
    "#ffffff00",
}
HEADER_COLOR = "#C9A0FF"
FENCE_RE = re.compile(r"^```mermaid[^\n]*\n(.*?)```", re.M | re.S)
ANY_FENCE_RE = re.compile(r"^```[^\n]*\n.*?^```", re.M | re.S)
SVG_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.I | re.S)
LEGEND_BARE_RE = re.compile(
    r"^\s*[-*]\s+\*\*(蓝|绿|紫|橙|青)\*\*[：:]"
)
LEGEND_SPAN_RE = re.compile(
    r'^\s*[-*]\s+\*\*<span\s+style="color:\s*(#[0-9A-Fa-f]{3,8})"\s*>'
    r"\s*(蓝|绿|紫|橙|青)\s*</span>\*\*[：:]",
    re.I,
)
SUBGRAPH_RE = re.compile(r"^\s*subgraph\s+([^\s\[]+)")
STYLE_FILL_RE = re.compile(
    r"style\s+(\w+)\s+[^;\n]*fill:\s*(#[0-9A-Fa-f]{3,8})", re.I
)
FILL_ANY_RE = re.compile(r"fill:\s*(#[0-9A-Fa-f]{3,8})", re.I)
INIT_DARK_RE = re.compile(
    r"%%\{init:.*?theme['\"]?\s*[:=]\s*['\"]?dark", re.I | re.S
)
TITLE_RE = re.compile(r"^title:\s*(.+)$", re.M)
PIPE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
SEP_CELL_RE = re.compile(r"^:?-+:?$")


def issue(file: str, line: int, diagram: int | None, code: str, msg: str) -> dict:
    d: dict = {"file": file, "line": line, "code": code, "msg": msg}
    if diagram is not None:
        d["diagram"] = diagram
    return d


def iter_fences(text: str):
    for i, m in enumerate(FENCE_RE.finditer(text)):
        start = text[: m.start()].count("\n") + 1
        yield i, start, m.group(1)


def split_yaml(body: str) -> tuple[str | None, str]:
    if not body.lstrip().startswith("---"):
        return None, body
    m = re.match(r"^\s*---\n(.*?)\n---\n?(.*)$", body, re.S)
    if not m:
        return None, body
    return m.group(1), m.group(2)


def subgraph_nesting(src: str) -> list[tuple[str, str]]:
    stack: list[str] = []
    pairs: list[tuple[str, str]] = []
    for line in src.splitlines():
        sm = SUBGRAPH_RE.match(line)
        if sm:
            sid = sm.group(1)
            if stack:
                pairs.append((stack[-1], sid))
            stack.append(sid)
            continue
        if re.match(r"^\s*end\s*$", line) and stack:
            stack.pop()
    return pairs


def style_fills(src: str) -> dict[str, str]:
    return {i: f.lower() for i, f in STYLE_FILL_RE.findall(src)}


def audit_diagram(file: str, diag: int, line: int, body: str, in_md: bool) -> list[dict]:
    issues: list[dict] = []
    yaml, src = split_yaml(body)
    if in_md:
        title = None
        if yaml:
            tm = TITLE_RE.search(yaml)
            title = tm.group(1).strip() if tm else None
        if not title:
            issues.append(issue(file, line, diag, "title", "缺 YAML title（实际含义标题）"))
        elif title in BAD_TITLES or title.rstrip("。.") in BAD_TITLES:
            issues.append(issue(file, line, diag, "title", f"标题禁止用类型名：{title}"))
    head = src[:800]
    if not INIT_DARK_RE.search(head) and not re.search(
        r"theme:\s*dark", head, re.I
    ):
        issues.append(issue(file, line, diag, "theme", "缺 theme dark"))
    fills = [f.lower() for f in FILL_ANY_RE.findall(src)]
    if "classDef" not in src and "style " not in src and not fills:
        issues.append(
            issue(file, line, diag, "fill", "无 style/classDef fill，节点仍是默认浅底")
        )
    for f in fills:
        if f in LIGHT_FILLS:
            issues.append(issue(file, line, diag, "light-fill", f"浅色 fill:{f}"))
    if r"\n" in src:
        issues.append(issue(file, line, diag, "newline", r"节点换行用 <br>，禁止 \n"))
    if "~~~" in src:
        issues.append(issue(file, line, diag, "ghost", "禁止裸 ~~~（幽灵线涂不掉）"))
    if re.search(r"(^|\n)\s*\S.*---.*\S", src) and "opacity:0" not in src.replace(
        " ", ""
    ):
        if "---" in src and "opacity:0" not in src.replace(" ", "").replace("\n", ""):
            compact = re.sub(r"\s+", "", src)
            if "opacity:0" not in compact:
                issues.append(
                    issue(
                        file,
                        line,
                        diag,
                        "placeholder",
                        "占位边 --- 必须 linkStyle opacity:0,stroke-width:0px",
                    )
                )
    fills_map = style_fills(src)
    for outer, inner in subgraph_nesting(src):
        a, b = fills_map.get(outer), fills_map.get(inner)
        if a and b and a == b:
            issues.append(
                issue(
                    file,
                    line,
                    diag,
                    "nest-fill",
                    f"嵌套 subgraph {outer}/{inner} 同 fill {a}",
                )
            )
    is_flow = bool(re.search(r"^\s*flowchart\b", src, re.M))
    node_ids = re.findall(
        r"^\s*([A-Za-z][\w-]*)(?:\[|\(|\{|>)", src, re.M
    )
    if is_flow and len(set(node_ids)) <= 7 and "useMaxWidth" not in src:
        issues.append(
            issue(
                file,
                line,
                diag,
                "maxwidth",
                "小 flowchart 须 useMaxWidth:false",
            )
        )
    if re.search(
        r'\["[^"]+\s+[^"]+"\]', src
    ) and "<b>" not in src and "<small>" not in src:
        # 主题+注解糊一行的弱信号，不误杀纯短标签
        pass
    if re.search(r"\[[^\]]+<br/>(?!.*<small>)", src):
        issues.append(
            issue(file, line, diag, "annot", "主题/注解须 <b>主题</b><br/><small>（注解）</small>")
        )
    return issues


def strip_fences(text: str) -> str:
    return FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def strip_any_fences(text: str) -> str:
    return ANY_FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def audit_svg_blanks(file: str, text: str) -> list[dict]:
    """`.md` 内联 SVG 禁止空行：CommonMark 在空行截断 HTML 块。"""
    issues: list[dict] = []
    masked = strip_any_fences(text)
    for m in SVG_RE.finditer(masked):
        block = m.group(0)
        lines = block.splitlines()
        for j, line in enumerate(lines):
            if line.strip() == "":
                issues.append(
                    issue(
                        file,
                        text[: m.start()].count("\n") + j + 1,
                        None,
                        "svg-blank",
                        ".md 内联 SVG 禁止空行（Markdown 会截断 HTML）",
                    )
                )
                break
    return issues


def audit_tables(file: str, text: str) -> list[dict]:
    issues: list[dict] = []
    raw_lines = text.splitlines()
    for i, line in enumerate(raw_lines[:-1]):
        if "</table>" in line.lower() and raw_lines[i + 1].strip().startswith("```"):
            issues.append(
                issue(
                    file,
                    i + 1,
                    None,
                    "html-fence",
                    "</table> 与围栏之间必须空一行",
                )
            )
    masked = strip_fences(text)
    lines = masked.splitlines()
    i = 0
    while i < len(lines) - 1:
        m = PIPE_ROW_RE.match(lines[i])
        sep = PIPE_ROW_RE.match(lines[i + 1]) if i + 1 < len(lines) else None
        if m and sep:
            sep_cells = [c.strip() for c in sep.group(1).split("|")]
            if sep_cells and all(SEP_CELL_RE.match(c.replace(" ", "") or "-") for c in sep_cells):
                header = lines[i]
                if HEADER_COLOR.lower() not in header.lower() and "<span" not in header.lower():
                    issues.append(
                        issue(
                            file,
                            i + 1,
                            None,
                            "th-color",
                            f"管道表表头须 <span style=\"color:{HEADER_COLOR}\">",
                        )
                    )
                i += 2
                continue
        i += 1
    return issues


def mermaid_fills(text: str) -> set[str]:
    found: set[str] = set()
    for _, _, body in iter_fences(text):
        _, src = split_yaml(body)
        found.update(f.lower() for f in FILL_ANY_RE.findall(src))
    return found


def audit_legend_color_names(file: str, text: str) -> list[dict]:
    issues: list[dict] = []
    fills = mermaid_fills(text)
    if not fills:
        return issues
    masked = strip_fences(text)
    for i, line in enumerate(masked.splitlines(), 1):
        if LEGEND_BARE_RE.match(line):
            issues.append(
                issue(
                    file,
                    i,
                    None,
                    "legend-color-name",
                    "图例色名须 span 且字色等于节点 fill",
                )
            )
            continue
        sm = LEGEND_SPAN_RE.match(line)
        if sm and sm.group(1).lower() not in fills:
            issues.append(
                issue(
                    file,
                    i,
                    None,
                    "legend-hex",
                    f"图例色名 {sm.group(1)} 未出现在本文 mermaid fill",
                )
            )
    return issues


def audit_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    in_md = path.suffix.lower() in {".md", ".markdown"}
    issues: list[dict] = []
    if path.suffix.lower() in {".mmd"}:
        issues.extend(audit_diagram(str(path), 0, 1, text, in_md=False))
        return issues
    if in_md:
        issues.extend(audit_svg_blanks(str(path), text))
    if not FENCE_RE.search(text) and in_md:
        issues.extend(audit_tables(str(path), text))
        return issues
    for i, line, body in iter_fences(text):
        issues.extend(audit_diagram(str(path), i, line, body, in_md))
    if in_md:
        issues.extend(audit_tables(str(path), text))
        issues.extend(audit_legend_color_names(str(path), text))
    return issues


def main() -> None:
    ap = argparse.ArgumentParser(description="Mermaid / 管道表格式验收")
    ap.add_argument("files", nargs="+", type=Path)
    args = ap.parse_args()
    all_issues: list[dict] = []
    diagrams = 0
    for f in args.files:
        t = f.read_text(encoding="utf-8")
        diagrams += len(list(FENCE_RE.finditer(t))) or (1 if f.suffix == ".mmd" else 0)
        all_issues.extend(audit_file(f))
    result = {
        "ok": not all_issues,
        "files": [str(p) for p in args.files],
        "diagrams": diagrams,
        "issues": all_issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
