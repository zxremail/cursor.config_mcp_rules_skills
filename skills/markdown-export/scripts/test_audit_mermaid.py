#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "audit_mermaid.py"

GOOD = """# t

| <span style="color:#C9A0FF">列</span> |
|------|
| a |

```mermaid
---
title: 业务进程到特权守护进程的调用关系
---
%%{init: {'theme': 'dark', 'flowchart': {'useMaxWidth': false}}}%%
flowchart TB
    A["开始"] --> B["结束"]
    style A fill:#2E86AB,stroke:#1B4965,color:#FFFFFF
    style B fill:#2D936C,stroke:#1E6B4E,color:#FFFFFF
```
"""

BAD = """# t

| 列 |
|------|
| a |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    A --- B
    A["x"] --> B["y"]
    ~~~
```
"""


def run_audit_named(text: str, name: str = "t.md") -> tuple[dict, int]:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(text, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(p)],
            capture_output=True,
            text=True,
        )
        return json.loads(r.stdout), r.returncode


def run_audit(text: str) -> tuple[dict, int]:
    return run_audit_named(text, "t.md")


class AuditTests(unittest.TestCase):
    def test_good(self):
        data, code = run_audit(GOOD)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_bad_flags(self):
        data, code = run_audit(BAD)
        self.assertFalse(data["ok"])
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("title", codes)
        self.assertIn("fill", codes)
        self.assertIn("ghost", codes)
        self.assertIn("th-color", codes)
        self.assertEqual(code, 2)

    def test_legend_bare_color_name(self):
        text = GOOD + "\n- **绿**：拓扑服务\n"
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-color-name", codes)
        self.assertEqual(code, 2)

    def test_legend_span_matches_fill(self):
        text = GOOD + '\n- **<span style="color:#2D936C">绿</span>**：拓扑服务\n'
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)
        self.assertNotIn("legend-hex", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_legend_hex_not_in_fills(self):
        text = GOOD + '\n- **<span style="color:#00A870">绿</span>**：拓扑服务\n'
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-hex", codes)

    def test_bare_chengse(self):
        text = GOOD + "\n橙色约束是不进作业队列。\n"
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-color-name", codes)
        self.assertEqual(code, 2)

    def test_bare_zikuang(self):
        text = GOOD + "\n左右两个紫框是同一条套接字。\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-color-name", codes)

    def test_bare_zuogui(self):
        text = GOOD + "\n左轨贴内容区左边下去。\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-color-name", codes)

    def test_shixian_xuxian_not_color_key(self):
        text = GOOD + "\n实线是下发，虚线是上报。\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)

    def test_ipc_kuang_not_color_key(self):
        text = GOOD + "\n左列上下两个 IPC 框共用一条套接字。\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)

    def test_baimingdan_not_color_key(self):
        text = GOOD + "\n驱动 VID/DID 白名单之外的卡不会绑上。\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)

    def test_chengse_span_hex_not_in_figures(self):
        text = GOOD + '\n<span style="color:#123456">橙色</span>约束是不进作业队列。\n'
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-hex", codes)

    def test_chengse_span_matches_svg_fill(self):
        text = (
            GOOD
            + '\n<span style="color:#F18F01">橙色</span>约束是不进作业队列。\n'
            + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">\n'
            + "<title>短句图意</title>\n"
            + '<rect x="0" y="0" width="10" height="10" fill="#F18F01"/>\n'
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)
        self.assertNotIn("legend-hex", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_zuogui_span_matches_svg_stroke(self):
        text = (
            GOOD
            + '\n<span style="color:#3370FF">左轨</span>贴内容区左边下去。\n'
            + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">\n'
            + "<title>短句图意</title>\n"
            + '<line x1="0" y1="0" x2="10" y2="10" stroke="#3370FF"/>\n'
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)
        self.assertNotIn("legend-hex", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_svg_text_zuogui_not_prose_key(self):
        text = (
            GOOD
            + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">\n'
            + "<title>短句图意</title>\n"
            + '<text fill="#3370FF">左轨 · Lite</text>\n'
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("legend-color-name", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_bare_hong_list(self):
        text = GOOD + "\n- **红**：FPGA 硬件\n"
        data, _ = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("legend-color-name", codes)

    def test_html_fence(self):
        text = "</table>\n```mermaid\n%%{init: {'theme':'dark'}}%%\nflowchart TB\nA-->B\nstyle A fill:#2E86AB,stroke:#1B4965,color:#FFFFFF\nstyle B fill:#2E86AB,stroke:#1B4965,color:#FFFFFF\n```\n"
        data, _ = run_audit("---\ntitle: 某调用关系\n---\n" + text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("html-fence", codes)

    def test_svg_blank_inside(self):
        text = (
            GOOD
            + "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 10 10\">\n"
            + "<title>短句图意</title>\n"
            + "\n"
            + "<rect x=\"0\" y=\"0\" width=\"10\" height=\"10\"/>\n"
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("svg-blank", codes)
        self.assertEqual(code, 2)

    def test_svg_no_blank_ok(self):
        text = (
            GOOD
            + "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 10 10\">\n"
            + "<title>短句图意</title>\n"
            + "<rect x=\"0\" y=\"0\" width=\"10\" height=\"10\"/>\n"
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("svg-blank", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_svg_open_split(self):
        text = (
            GOOD
            + "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 10 10\"\n"
            + "     style=\"width:100%\">\n"
            + "<title>短句图意</title>\n"
            + "<rect x=\"0\" y=\"0\" width=\"10\" height=\"10\"/>\n"
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("svg-open-split", codes)
        self.assertEqual(code, 2)

    def test_swimlane_png_forbidden(self):
        text = (
            "左栏是层，应用在上、硬件在下。\n\n"
            "![未劫持时 SIGSEGV 应进 debuggerd](foo.figures/unhijacked.png)\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("swimlane-png", codes)
        self.assertEqual(code, 2)

    def test_swimlane_inline_svg_ok(self):
        text = (
            GOOD
            + "\n左栏是层，应用在上、硬件在下。\n"
            + "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 10 10\">\n"
            + "<title>短句图意</title>\n"
            + "<rect x=\"0\" y=\"0\" width=\"10\" height=\"10\"/>\n"
            + "</svg>\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("swimlane-png", codes)
        self.assertNotIn("svg-open-split", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_md_filename_ascii_ok(self):
        data, code = run_audit(GOOD)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("md-filename", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_md_filename_non_ascii(self):
        data, code = run_audit_named(GOOD, "启动失败分析.md")
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("md-filename", codes)
        self.assertEqual(code, 2)

    def test_md_filename_space(self):
        data, code = run_audit_named(GOOD, "boot fail.md")
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("md-filename", codes)
        self.assertEqual(code, 2)

    def test_seq_live_classdef_forbidden(self):
        text = """# t

| <span style="color:#C9A0FF">列</span> |
|------|
| a |

```mermaid
---
title: AMS 拉起进程后被 verifier 拒绝
---
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant A as AMS
    A->>A: Start proc
    classDef act fill:#2E86AB,stroke:#1B4965,color:#FFFFFF
```
"""
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("seq-classdef", codes)
        self.assertEqual(code, 2)

    def test_seq_live_class_assign_forbidden(self):
        text = """# t

| <span style="color:#C9A0FF">列</span> |
|------|
| a |

```mermaid
---
title: AMS 拉起进程后被 verifier 拒绝
---
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    %% classDef n fill:#2E86AB,stroke:#1B4965,color:#FFFFFF
    participant A as AMS
    A->>A: Start proc
    class A n
```
"""
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("seq-classdef", codes)
        self.assertEqual(code, 2)

    def test_seq_comment_classdef_ok(self):
        text = """# t

| <span style="color:#C9A0FF">列</span> |
|------|
| a |

```mermaid
---
title: AMS 拉起进程后被 verifier 拒绝
---
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    %% classDef n fill:#2E86AB,stroke:#1B4965,color:#FFFFFF
    participant A as AMS
    A->>A: Start proc
```
"""
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("seq-classdef", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_seq_missing_comment_classdef(self):
        text = """# t

| <span style="color:#C9A0FF">列</span> |
|------|
| a |

```mermaid
---
title: AMS 拉起进程后被 verifier 拒绝
---
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant A as AMS
    A->>A: Start proc
```
"""
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("seq-classdef", codes)
        self.assertEqual(code, 2)

    def test_flowchart_live_classdef_not_seq_rule(self):
        data, code = run_audit(GOOD)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("seq-classdef", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_svg_blank_in_fence_ignored(self):
        text = (
            GOOD
            + "\n```svg\n<svg xmlns=\"http://www.w3.org/2000/svg\">\n\n<rect/>\n</svg>\n```\n"
        )
        data, code = run_audit(text)
        codes = {i["code"] for i in data["issues"]}
        self.assertNotIn("svg-blank", codes)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
