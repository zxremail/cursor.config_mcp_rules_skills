#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "audit_html.py"
SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample.html"


MIN_OK = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<script>function mdGithubSlug(){}
mermaid.initialize({flowchart:{useMaxWidth:false}})</script>
<style>.mermaid svg{max-width:100%;width:auto}</style>
</head>
<body><div id="layout"><nav id="sidebar"></nav>
<main><article id="content"></article></main></div>
</body></html>
"""


def run(html: str, md: str | None = None) -> tuple[dict, int]:
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "t.html"
        hp.write_text(html, encoding="utf-8")
        cmd = [sys.executable, str(SCRIPT), str(hp)]
        if md is not None:
            mp = Path(td) / "t.md"
            mp.write_text(md, encoding="utf-8")
            cmd.extend(["--md", str(mp)])
        p = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(p.stdout), p.returncode


class AuditHtmlTests(unittest.TestCase):
    def test_min_ok(self):
        data, code = run(MIN_OK)
        self.assertTrue(data["ok"], data)
        self.assertEqual(code, 0)

    def test_missing_slug(self):
        bad = MIN_OK.replace("mdGithubSlug", "x")
        data, code = run(bad)
        self.assertFalse(data["ok"])
        self.assertIn("slug", {i["code"] for i in data["issues"]})
        self.assertEqual(code, 2)

    def test_downgrade_missing_sidecar(self):
        nodes = "\n".join(f'    N{i}["n{i}"] --> N{i+1}["n{i+1}"]' for i in range(20))
        md = f"```mermaid\nflowchart TB\n{nodes}\n```\n"
        data, _ = run(MIN_OK, md)
        self.assertFalse(data["ok"])
        self.assertTrue(any(i["code"] == "sidecar" for i in data["issues"]))

    def test_sample_html_if_present(self):
        if not SAMPLE.is_file():
            self.skipTest("no sample.html")
        p = subprocess.run(
            [sys.executable, str(SCRIPT), str(SAMPLE), "--md", str(SAMPLE.with_suffix(".md"))],
            capture_output=True,
            text=True,
        )
        data = json.loads(p.stdout)
        self.assertIsInstance(data["bytes"], int)


if __name__ == "__main__":
    unittest.main()
