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



def test_dark_swimlane_svg_lightened_for_feishu():
    md = """# 标题

## 图

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80" style="background:#0D1117;"><rect width="200" height="80" fill="#0D1117"/><rect width="200" height="40" fill="#0D2433"/><rect width="50" height="40" fill="#163A4D"/><text x="25" y="24" font-size="14" fill="#FFFFFF">业务进程</text><rect x="70" y="8" width="80" height="24" rx="6" fill="#2E86AB"/><text x="110" y="24" font-size="13" fill="#FFFFFF">crash_handler</text></svg>
"""
    xml, _, out = run_convert(md)
    svg = (out / "fig0.svg").read_text(encoding="utf-8")
    assert "#0D1117" not in svg.upper().replace("0D1117", "0D1117")
    assert "#0D1117" not in svg and "#0d1117" not in svg
    assert "#0D2433" not in svg and "#0d2433" not in svg
    assert "#F8FAFC" in svg or "#F3F4F6" in svg or "#DBEAFE" in svg
    assert 'fill="#2E86AB"' in svg or "fill='#2E86AB'" in svg or 'fill="#2e86ab"' in svg.lower()
    assert 'font-size="14"' in svg and "#1F2329" in svg
    assert "crash_handler" in svg


def test_dark_platform_stack_svg_lightened_for_feishu():
    md = """# 标题

## 图

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 640" style="background:#0D1117;"><title>深色平台栈：测试</title><rect width="1320" height="640" fill="#0D1117"/><rect x="16" y="16" width="152" height="608" rx="16" fill="#161B22" stroke="#F85149"/><text fill="#FFA198">Device Manager</text><rect x="248" y="20" width="300" height="44" rx="22" fill="#2E86AB" stroke="#58A6FF"/><text fill="#FFFFFF">A 类业务</text><polygon points="246,124 264,132 246,140" fill="#F59E0B"/></svg>
"""
    xml, _, out = run_convert(md)
    svg = (out / "fig0.svg").read_text(encoding="utf-8")
    assert "#0D1117" not in svg and "#0d1117" not in svg
    assert "#161B22" not in svg and "#161b22" not in svg
    assert "#2E86AB" not in svg and "#2e86ab" not in svg
    assert "#F7F7F6" in svg
    assert "#EDEDED" in svg
    assert "#F3F3F3" in svg
    assert "#3D3D3D" in svg
    assert "#D0D0D0" in svg
    assert 'viewBox="0 0 1320 640"' in svg
    assert "Device Manager" in svg


def test_dark_timeline_svg_lightened_for_feishu():
    md = """# 标题

## 图

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" role="img" aria-label="开机动画时间线暗色主题" style="background:#0D1117"><style>.dtl-when{font-size:12px;fill:#FFFFFF}.dtl-sub{fill:#E8EAED}</style><rect x="0" y="0" width="400" height="200" fill="#0D1117"/><line x1="20" y1="100" x2="380" y2="100" stroke="#555577" stroke-dasharray="6 6"/><rect x="20" y="10" width="200" height="148" rx="8" fill="#2E86AB" stroke="#1B4965"/><path d="M28,10 h184 q8,0 8,8 v20 h-200 v-20 q0,-8 8,-8 z" fill="#1B4965"/><text x="120" y="30" class="dtl-when">0 s ~ 3.8 s</text><circle cx="120" cy="100" r="8" fill="#0D1117" stroke="#2E86AB"/></svg>
"""
    xml, _, out = run_convert(md)
    svg = (out / "fig0.svg").read_text(encoding="utf-8")
    assert "#0D1117" not in svg and "#0d1117" not in svg
    assert 'fill="#FFFFFF"' in svg
    assert 'fill="#E3F2FD"' in svg
    assert "#2E86AB" not in svg and "#2e86ab" not in svg
    assert 'stroke="#1F2329"' in svg
    assert "fill:#1F2329" in svg
    assert "#555577" not in svg
    assert "#D0D3D6" in svg


def test_patch_board_lightens_swimlane_raw():
    raw = {
        "nodes": [
            {"type": "shape", "style": {"fill_color": "#0D2433"}},
            {"type": "shape", "style": {"fill_color": "#161B22"}},
            {"type": "shape", "style": {"fill_color": "#2E86AB"}},
            {
                "type": "text",
                "text": {"text": "业务进程", "font_size": 14, "text_color": "#FFFFFF"},
            },
            {
                "type": "text",
                "text": {"text": "crash_handler", "font_size": 13, "text_color": "#FFFFFF"},
            },
        ]
    }
    tmp = Path(tempfile.mkdtemp()) / "board.json"
    tmp.write_text(json.dumps(raw), encoding="utf-8")
    subprocess.check_call(
        [sys.executable, str(PIPELINE), "patch-board", str(tmp)],
        stdout=subprocess.DEVNULL,
    )
    d = json.loads(tmp.read_text(encoding="utf-8"))
    fills = [n["style"]["fill_color"].upper() for n in d["nodes"] if n.get("style")]
    assert "#0D2433" not in fills
    assert "#DBEAFE" in fills
    assert "#2E86AB" in fills
    texts = {n["text"]["text"]: n["text"] for n in d["nodes"] if n.get("type") == "text"}
    assert texts["业务进程"]["text_color"].upper() == "#1F2329"
    assert texts["crash_handler"]["text_color"].upper() == "#FFFFFF"




def test_patch_board_widens_clipped_text():
    raw = {
        "nodes": [
            {
                "type": "composite_shape",
                "x": 716,
                "y": 62,
                "width": 148,
                "height": 56,
                "style": {"fill_color": "#2E86AB"},
            },
            {
                "type": "text_shape",
                "x": 754,
                "y": 91,
                "width": 72,
                "height": 16,
                "text": {
                    "text": "（logcat libc）",
                    "font_size": 11,
                    "text_color": "#FFFFFF",
                },
            },
            {
                "type": "text_shape",
                "x": 666,
                "y": 67,
                "width": 55,
                "height": 16,
                "text": {
                    "text": "交给 bionic",
                    "font_size": 11,
                    "text_color": "#06B6D4",
                },
            },
        ]
    }
    tmp = Path(tempfile.mkdtemp()) / "board.json"
    tmp.write_text(json.dumps(raw), encoding="utf-8")
    subprocess.check_call(
        [sys.executable, str(PIPELINE), "patch-board", str(tmp)],
        stdout=subprocess.DEVNULL,
    )
    d = json.loads(tmp.read_text(encoding="utf-8"))
    by = {n["text"]["text"]: n for n in d["nodes"] if n.get("type") == "text_shape"}
    assert by["（logcat libc）"]["width"] >= 96, by["（logcat libc）"]["width"]
    assert by["交给 bionic"]["width"] >= 70, by["交给 bionic"]["width"]


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
        test_dark_swimlane_svg_lightened_for_feishu,
        test_dark_platform_stack_svg_lightened_for_feishu,
        test_dark_timeline_svg_lightened_for_feishu,
        test_patch_board_lightens_swimlane_raw,
        test_patch_board_widens_clipped_text,
    ]:
        try:
            fn()
            print("PASS", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, type(e).__name__, e)
    raise SystemExit(failed)
