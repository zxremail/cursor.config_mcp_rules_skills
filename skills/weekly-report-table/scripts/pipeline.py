#!/usr/bin/env python3
"""驱动小组周报：抽取 cite 摘要、JSON→飞书 XML/本地 MD、验收。stdout 只打短 JSON。"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

TH_BG = "rgb(236,226,254)"
TD0_BG = "rgb(225,234,255)"
PORTAL = "https://rigolportal.feishu.cn"
CATEGORIES = ("重点项目开发", "技术选项与优化", "问题定位与支持")
FORBIDDEN_CATS = ("调试测试文档", "文档输出", "测试文档", "交付物")
NAMES = ("朱兴瑞", "王霆", "朱日芃")
CITE_RE = re.compile(r"<cite\b([^>]*)/?>", re.I)
MD_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https://[^)]*?(?:/wiki/|/docx/)([A-Za-z0-9]+))\)"
)


def xml_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def die(msg: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(code)


def parse_cite_attrs(attr_str: str) -> dict[str, str]:
    attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', attr_str))
    return {
        "doc_id": attrs.get("doc-id") or attrs.get("doc_id") or "",
        "file_type": attrs.get("file-type") or attrs.get("file_type") or "wiki",
        "title": attrs.get("title") or "",
        "type": attrs.get("type") or "doc",
    }


def unwrap_fetch(raw: str) -> str:
    text = raw.strip()
    if text.startswith("{"):
        data = json.loads(text)
        return (
            data.get("data", {}).get("document", {}).get("content")
            or data.get("document", {}).get("content")
            or data.get("content")
            or ""
        )
    return raw


def bucket_cites(content: str) -> dict[str, list[dict[str, str]]]:
    parts = re.split(r"(本周|下周|<cite\b[^>]*/?>)", content)
    bucket = "unknown"
    out: dict[str, list[dict[str, str]]] = {
        "this_week": [],
        "next_week": [],
        "unknown": [],
    }
    for p in parts:
        if p == "本周":
            bucket = "this_week"
        elif p == "下周":
            bucket = "next_week"
        elif p.lower().startswith("<cite"):
            m = CITE_RE.match(p)
            cite = parse_cite_attrs(m.group(1) if m else "")
            if cite["doc_id"]:
                out[bucket].append(cite)
    return out


def md_feishu_links(content: str) -> list[dict[str, str]]:
    found = []
    for title, url, token in MD_LINK_RE.findall(content):
        kind = "wiki" if "/wiki/" in url else "docx"
        found.append({"title": title, "url": url, "doc_id": token, "file_type": kind})
    return found


def to_source_txt(content: str) -> str:
    def repl(m: re.Match[str]) -> str:
        c = parse_cite_attrs(m.group(1))
        title = c["title"] or c["doc_id"]
        return f"[cite {c['file_type']}:{c['doc_id']} {title}]"

    text = CITE_RE.sub(repl, content)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</(p|h[1-6]|li|tr|div)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def headings_of(content: str) -> list[str]:
    hs = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", content, flags=re.I | re.S)
    md = re.findall(r"^#{1,6}\s+(.+)$", content, flags=re.M)
    plain = [re.sub(r"<[^>]+>", "", h).strip() for h in hs] + [h.strip() for h in md]
    return [h for h in plain if h][:40]


def cmd_extract(paths: list[Path], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    merged = {"this_week": [], "next_week": [], "unknown": []}
    chunks: list[str] = []
    names: list[str] = []
    heads: list[str] = []
    md_links: list[dict[str, str]] = []
    total = 0
    for i, p in enumerate(paths):
        raw = p.read_text(encoding="utf-8")
        total += len(raw)
        content = unwrap_fetch(raw) or raw
        b = bucket_cites(content)
        for k in merged:
            merged[k].extend(b[k])
        md_links.extend(md_feishu_links(content))
        heads.extend(headings_of(content))
        for n in NAMES:
            if n in content and n not in names:
                names.append(n)
        chunks.append(f"----- source {i}: {p.name} -----\n{to_source_txt(content)}")
    source_txt = out_dir / "source.txt"
    source_txt.write_text("\n".join(chunks), encoding="utf-8")
    extract = {
        "ok": True,
        "source_txt": "source.txt",
        "bytes_in": total,
        "chars_txt": source_txt.stat().st_size,
        "cites": merged,
        "this_week_ids": [c["doc_id"] for c in merged["this_week"]],
        "next_week_ids": [c["doc_id"] for c in merged["next_week"]],
        "names_present": names,
        "headings": heads[:40],
        "feishu_md_links": md_links,
    }
    (out_dir / "extract.json").write_text(
        json.dumps(extract, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "ok": True,
                "source_txt": "source.txt",
                "chars_txt": extract["chars_txt"],
                "this_week_cites": len(merged["this_week"]),
                "next_week_cites": len(merged["next_week"]),
                "unknown_cites": len(merged["unknown"]),
                "this_week_ids": extract["this_week_ids"],
                "names_present": names,
                "headings": heads[:20],
            },
            ensure_ascii=False,
        )
    )
    return extract


def cite_xml(cite: dict[str, str]) -> str:
    doc_id = xml_esc(cite.get("doc_id") or cite.get("doc-id") or "")
    ft = xml_esc(cite.get("file_type") or cite.get("file-type") or "wiki")
    return f'<cite type="doc" doc-id="{doc_id}" file-type="{ft}"/>'


def cite_md_url(cite: dict[str, str]) -> str:
    token = cite.get("doc_id") or cite.get("doc-id") or ""
    ft = cite.get("file_type") or cite.get("file-type") or "wiki"
    path = "wiki" if ft != "docx" else "docx"
    return f"{PORTAL}/{path}/{token}"


def item_xml(item: dict[str, Any]) -> str:
    text = xml_esc((item.get("text") or "").strip())
    cite = item.get("cite")
    if cite and (cite.get("doc_id") or cite.get("doc-id")):
        inner = f"{text}：{cite_xml(cite)}" if text else cite_xml(cite)
    else:
        inner = text
    return f"<li>{inner}</li>"


def projects_xml(projects: list[dict[str, Any]]) -> str:
    if not projects:
        return "<p>-</p>"
    bits = []
    for proj in projects:
        name = xml_esc((proj.get("project") or "").strip())
        items = proj.get("items") or []
        lis = "".join(item_xml(it) for it in items) or "<li>-</li>"
        bits.append(f"<li><b>{name}</b>：<ul>{lis}</ul></li>")
    return f"<ul>{''.join(bits)}</ul>"


def item_md(item: dict[str, Any], allow_link: bool) -> str:
    text = (item.get("text") or "").strip()
    cite = item.get("cite") if allow_link else None
    if not (cite and (cite.get("doc_id") or cite.get("doc-id"))):
        return text
    title = (cite.get("title") or text or cite.get("doc_id") or "").strip()
    link = f"[{title}]({cite_md_url(cite)})"
    if text and title != text:
        return f"{text}：{link}"
    if text and not cite.get("title"):
        return link
    return link if not text else f"{text}：{link}" if title != text else link


def projects_md(projects: list[dict[str, Any]], allow_link: bool) -> str:
    if not projects:
        return "-"
    blocks = []
    for proj in projects:
        name = (proj.get("project") or "").strip()
        items = proj.get("items") or []
        lines = [f"• **{name}**："]
        for it in items:
            lines.append(f"<br>&nbsp;&nbsp;- {item_md(it, allow_link)}")
        blocks.append("".join(lines))
    return "<br><br>".join(blocks)


def validate_report(data: dict[str, Any]) -> None:
    cats = data.get("categories")
    if not isinstance(cats, list) or len(cats) != 3:
        die("categories 必须恰好 3 项（重点项目开发 / 技术选项与优化 / 问题定位与支持）")
    names = [c.get("name") for c in cats]
    if tuple(names) != CATEGORIES:
        die(f"categories.name 必须按序为 {list(CATEGORIES)}，实际 {names}")
    blob = json.dumps(data, ensure_ascii=False)
    for c in cats:
        n = c.get("name") or ""
        if n not in CATEGORIES or any(bad == n for bad in FORBIDDEN_CATS):
            die(f"禁止第四类/非法分类名：{n}")
    for name in NAMES:
        if name in blob:
            die(f"输出禁止出现成员姓名：{name}")
    for cat in cats:
        for proj in cat.get("next_week") or []:
            for it in proj.get("items") or []:
                cite = it.get("cite") or {}
                text = it.get("text") or ""
                if cite.get("doc_id") or cite.get("doc-id"):
                    die("下周条目禁止 cite")
                if "http://" in text or "https://" in text or "<cite" in text:
                    die("下周条目禁止 URL / cite 文本")


def cmd_convert(report_path: Path, out_dir: Path) -> dict[str, Any]:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    validate_report(data)
    mmdd = str(data.get("mmdd") or "").strip()
    if not re.fullmatch(r"\d{4}", mmdd):
        die("mmdd 必须是四位日期，如 1008")
    title = data.get("title") or f"驱动小组周报表格_{mmdd}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows_xml = []
    this_n = next_n = 0
    for cat in data["categories"]:
        tw = cat.get("this_week") or []
        nw = cat.get("next_week") or []
        for proj in tw:
            for it in proj.get("items") or []:
                c = it.get("cite") or {}
                if c.get("doc_id") or c.get("doc-id"):
                    this_n += 1
        for proj in nw:
            for it in proj.get("items") or []:
                c = it.get("cite") or {}
                if c.get("doc_id") or c.get("doc-id"):
                    next_n += 1
        name = xml_esc(cat["name"])
        rows_xml.append(
            "<tr>"
            f'<td background-color="{TD0_BG}" vertical-align="top"><p><b>{name}</b></p></td>'
            f'<td vertical-align="top">{projects_xml(tw)}</td>'
            f'<td vertical-align="top">{projects_xml(nw)}</td>'
            "</tr>"
        )

    th = (
        f'<th background-color="{TH_BG}" vertical-align="middle">'
        f'<p align="center"><b>{{}}</b></p></th>'
    )
    table = (
        "<table><thead><tr>"
        + th.format("任务分类")
        + th.format("本周任务汇总")
        + th.format("下周任务安排")
        + "</tr></thead><tbody>"
        + "".join(rows_xml)
        + "</tbody></table>"
    )
    xml = f"<title>{xml_esc(title)}</title><h1 seq=\"auto\">{xml_esc(title)}</h1>{table}"
    xml_path = out_dir / "doc.xml"
    xml_path.write_text(xml, encoding="utf-8")

    md_name = f"驱动小组周报表格_{mmdd}.md"
    md_rows = [
        "| **任务分类** | **本周任务汇总** | **下周任务安排** |",
        "|---|---|---|",
    ]
    for cat in data["categories"]:
        md_rows.append(
            f"| **{cat['name']}** | {projects_md(cat.get('this_week') or [], True)} "
            f"| {projects_md(cat.get('next_week') or [], False)} |"
        )
    md = f"# {title}\n\n" + "\n".join(md_rows) + "\n"
    (out_dir / md_name).write_text(md, encoding="utf-8")

    manifest = {
        "ok": True,
        "title": title,
        "xml": "doc.xml",
        "md": md_name,
        "bytes": xml_path.stat().st_size,
        "this_week_cites": this_n,
        "next_week_cites": next_n,
        "rows": 3,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))
    return manifest


def table_cells(table: str) -> list[list[str]]:
    body = re.search(r"<tbody>([\s\S]*)</tbody>", table)
    if not body:
        return []
    rows = []
    for tr in re.findall(r"<tr>([\s\S]*?)</tr>", body.group(1)):
        tds = re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr)
        rows.append(tds)
    return rows


def audit_xml(path: Path, expect_cites: Path | None) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    content = unwrap_fetch(raw) if raw.lstrip().startswith("{") else raw
    issues: list[str] = []
    tables = re.findall(r"<table[\s\S]*?</table>", content)
    if len(tables) != 1:
        issues.append(f"期望 1 张表，实际 {len(tables)}")
    table = tables[0] if tables else content
    if TH_BG not in table or TD0_BG not in table:
        issues.append("缺浅紫表头或浅蓝首列")
    rows = table_cells(table)
    if len(rows) != 3:
        issues.append(f"数据行必须为 3，实际 {len(rows)}")
    got_names = []
    for row in rows:
        if len(row) != 3:
            issues.append(f"列数必须为 3，实际 {len(row)}")
            continue
        plain0 = re.sub(r"<[^>]+>", "", row[0]).strip()
        got_names.append(plain0)
    if tuple(got_names) != CATEGORIES and len(got_names) == 3:
        issues.append(f"首列分类须为 {list(CATEGORIES)}，实际 {got_names}")
    for bad in FORBIDDEN_CATS:
        if any(bad == n for n in got_names):
            issues.append(f"出现禁止分类：{bad}")
    for name in NAMES:
        if name in content:
            issues.append(f"出现成员姓名：{name}")
    this_ids: list[str] = []
    next_ids: list[str] = []
    for row in rows:
        if len(row) < 3:
            continue
        this_ids.extend(re.findall(r'doc-id="([^"]+)"', row[1]))
        next_ids.extend(re.findall(r'doc-id="([^"]+)"', row[2]))
        if re.search(r"https?://", row[2], re.I) or "<cite" in row[2].lower():
            issues.append("下周列含链接或 cite")
    if next_ids:
        issues.append(f"下周列出现 cite: {next_ids}")
    if expect_cites and expect_cites.exists():
        exp = json.loads(expect_cites.read_text(encoding="utf-8"))
        want = exp.get("this_week_ids") or [
            c.get("doc_id") for c in (exp.get("cites") or {}).get("this_week") or []
        ]
        missing = [i for i in want if i and i not in this_ids]
        if missing:
            issues.append(f"本周漏 cite: {missing}")
    result = {
        "ok": not issues,
        "tables": len(tables),
        "rows": len(rows),
        "this_week_cites": this_ids,
        "next_week_cites": next_ids,
        "issues": issues,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="驱动小组周报表格 pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ex = sub.add_parser("extract", help="fetch/xml/md → source.txt + extract.json")
    p_ex.add_argument("files", nargs="+", type=Path)
    p_ex.add_argument("-o", "--out", type=Path, required=True)

    p_cv = sub.add_parser("convert", help="report.json → doc.xml + md")
    p_cv.add_argument("report", type=Path)
    p_cv.add_argument("-o", "--out", type=Path, required=True)

    p_au = sub.add_parser("audit-xml", help="验收飞书 fetch 或本地 xml")
    p_au.add_argument("file", type=Path)
    p_au.add_argument("--expect-cites", type=Path, default=None)

    args = ap.parse_args()
    if args.cmd == "extract":
        cmd_extract(args.files, args.out)
    elif args.cmd == "convert":
        cmd_convert(args.report, args.out)
    elif args.cmd == "audit-xml":
        r = audit_xml(args.file, args.expect_cites)
        raise SystemExit(0 if r["ok"] else 2)


if __name__ == "__main__":
    main()
