#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PIPE = Path(__file__).resolve().parent / "pipeline.py"

FETCH = json.dumps(
    {
        "data": {
            "document": {
                "content": """
<h1>AMP 验证报告</h1>
<p>计划标准：验证过程。N=10000。</p>
<h2>方法</h2>
<table><tr><td>a</td></tr></table>
<h2>结果</h2>
<p>|p99|=3µs。通过。</p>
<image token="imgTok1"/>
<whiteboard token="wbTok1"/>
"""
            }
        }
    },
    ensure_ascii=False,
)


class TestExtract(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PIPE), *args],
            capture_output=True,
            text=True,
        )

    def test_fetch_json_outline(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src0.json"
            src.write_text(FETCH, encoding="utf-8")
            out = Path(td) / "out"
            r = self.run_cli(
                "extract",
                str(src),
                "-o",
                str(out),
                "--url",
                "https://example.feishu.cn/docx/ABC",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertTrue(man["ok"])
            self.assertIn("AMP 验证报告", man["headings"])
            self.assertGreaterEqual(man["whiteboards"], 1)
            self.assertGreaterEqual(man["images"], 1)
            self.assertTrue(any("10000" in n or "3µs" in n for n in man["numbers"]))
            self.assertEqual(man["urls"][0].endswith("ABC"), True)
            self.assertTrue((out / "outline.json").is_file())
            self.assertTrue((out / "source.txt").is_file())
            self.assertGreater(len(man["section_files"]), 0)
            body = (out / man["section_files"][0]).read_text(encoding="utf-8")
            self.assertIn("验证过程", body)

    def test_pretty_md(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "doc.md"
            src.write_text("# 背景\n\n问题。\n\n## 结果\n\n通过。\n", encoding="utf-8")
            r = self.run_cli("extract", str(src), "-o", str(Path(td) / "o"))
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertEqual(man["heading_count"], 2)


if __name__ == "__main__":
    unittest.main()
