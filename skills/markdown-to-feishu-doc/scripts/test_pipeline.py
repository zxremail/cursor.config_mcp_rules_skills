#!/usr/bin/env python3
"""HTML 表 / 内嵌 SVG / 嵌套反引号：convert 不得把标签转义成源码。"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "pipeline.py"


def run_convert(md: str) -> tuple[str, dict, Path]:
    tmp = Path(tempfile.mkdtemp(prefix="feishu_md_"))
    src = tmp / "src.md"
    src.write_text(md, encoding="utf-8")
    out = tmp / "out"
    subprocess.check_call(
        [sys.executable, str(PIPELINE), "convert", str(src), str(out)],
        stdout=subprocess.DEVNULL,
    )
    xml = (out / "doc.xml").read_text(encoding="utf-8")
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    return xml, man, out


def run_audit(xml: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="feishu_audit_"))
    p = tmp / "doc.xml"
    p.write_text(xml, encoding="utf-8")
    out = subprocess.check_output(
        [sys.executable, str(PIPELINE), "audit-xml", str(p)],
        text=True,
    )
    return json.loads(out)


def test_html_table_becomes_feishu_table():
    md = """# 标题

## 排除项

假说是否成立：<font color="#5BE49B"><b>是</b></font>　<font color="#FFB020"><b>否</b></font>

<table>
<thead>
<tr>
<th><font color="#C9A0FF">假说</font></th>
<th><font color="#C9A0FF">是否</font></th>
<th><font color="#C9A0FF">依据</font></th>
</tr>
</thead>
<tbody>
<tr>
<td>LMK / OOM 杀进程</td>
<td><font color="#FFB020"><b>否</b></font></td>
<td>LMK 走信号 9。</td>
</tr>
<tr>
<td><code>kill -9</code></td>
<td><font color="#FFB020"><b>否</b></font></td>
<td>那也是信号 9。</td>
</tr>
</tbody>
</table>
"""
    xml, _, _ = run_convert(md)
    assert "&lt;table" not in xml, xml[:400]
    assert "&lt;thead" not in xml
    assert "&lt;td" not in xml
    assert xml.count("<table") == 1
    assert "rgb(236,226,254)" in xml
    assert "rgb(225,234,255)" in xml
    assert "LMK / OOM 杀进程" in xml
    assert "text-color=\"orange\"" in xml
    assert "text-color=\"green\"" in xml
    assert "<font" not in xml


def test_pipe_table_still_works():
    md = """# 标题

## 现场结论

| 项 | 结论 |
|------|------|
| 进程为何退出 | SIGSEGV |
"""
    xml, _, _ = run_convert(md)
    assert xml.count("<table") == 1
    assert "进程为何退出" in xml


def test_inline_svg_becomes_whiteboard():
    md = """# 标题

## 图

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>示例图</title><rect width="10" height="10"/></svg>

后面还有字。
"""
    xml, man, out = run_convert(md)
    assert "&lt;svg" not in xml
    assert "<whiteboard type=\"svg\"" in xml
    figs = list(out.glob("fig*.svg"))
    assert len(figs) == 1
    assert "<svg" in figs[0].read_text(encoding="utf-8")


def test_nested_backticks_in_link_no_nul():
    md = """# 标题

## 目录

- [4.1 `SIG_DFL` + `raise` 不会再进 debuggerd](#41-sig_dfl)
"""
    xml, _, _ = run_convert(md)
    assert "\x00" not in xml
    assert "SIG_DFL" in xml
    assert "raise" in xml


def test_audit_flags_escaped_html_table():
    bad = '<title>x</title><h1 seq="auto">排除项</h1><p>&lt;table&gt;</p><p>&lt;thead&gt;</p>'
    r = run_audit(bad)
    assert r["ok"] is False
    assert any("源码" in i or "table" in i.lower() or "HTML" in i for i in r["issues"])


def test_audit_ok_on_real_table():
    good = (
        '<title>x</title><h1 seq="auto">排除项</h1>'
        '<table><thead><tr>'
        '<th background-color="rgb(236,226,254)"><p align="center"><b>假说</b></p></th>'
        '<th background-color="rgb(236,226,254)"><p align="center"><b>是否</b></p></th>'
        "</tr></thead><tbody><tr>"
        '<td background-color="rgb(225,234,255)"><p><b>LMK</b></p></td>'
        "<td><p>否</p></td></tr></tbody></table>"
    )
    r = run_audit(good)
    assert r["ok"] is True
    assert r["tables"] == 1


if __name__ == "__main__":
    failed = 0
    for fn in [
        test_html_table_becomes_feishu_table,
        test_pipe_table_still_works,
        test_inline_svg_becomes_whiteboard,
        test_nested_backticks_in_link_no_nul,
        test_audit_flags_escaped_html_table,
        test_audit_ok_on_real_table,
    ]:
        try:
            fn()
            print("PASS", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, type(e).__name__, e)
    raise SystemExit(failed)
