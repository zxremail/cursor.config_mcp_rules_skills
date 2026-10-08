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
                "title": "NVMe 掉盘实验",
                "revision_id": "rev-9",
                "content": """
<h1>NVMe 掉盘实验</h1>
<p>主张：概率下降。</p>
<h2>结论</h2>
<p>已测通。max=12ms。</p>
<h2>风险</h2>
<p>单机。</p>
<h2>附录 WIP</h2>
<p></p>
<table><tr><td>1</td></tr></table>
<whiteboard token="wb1"/>
""",
            }
        }
    },
    ensure_ascii=False,
)


class TestExtract(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PIPE), *args], capture_output=True, text=True
        )

    def test_meta_and_priority(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src0.json"
            src.write_text(FETCH, encoding="utf-8")
            r = self.run_cli(
                "extract",
                str(src),
                "-o",
                str(Path(td) / "o"),
                "--url",
                "https://example.feishu.cn/docx/TOK",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertTrue(man["ok"])
            self.assertEqual(man["title"], "NVMe 掉盘实验")
            self.assertEqual(man["revision_id"], "rev-9")
            self.assertTrue(any("结论" in h for h in man["headings"]))
            self.assertTrue(man["priority_section_files"])
            self.assertGreaterEqual(man["whiteboards"], 1)
            self.assertTrue(any("WIP" in x or "附录" in x for x in man["empty_or_short_headings"]))

    def test_md(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "a.md"
            src.write_text("# 方案\n\n正文。\n\n## 变更日志\n\n无。\n", encoding="utf-8")
            r = self.run_cli("extract", str(src), "-o", str(Path(td) / "o"))
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertEqual(man["heading_count"], 2)
            self.assertTrue(man["priority_section_files"])


if __name__ == "__main__":
    unittest.main()
