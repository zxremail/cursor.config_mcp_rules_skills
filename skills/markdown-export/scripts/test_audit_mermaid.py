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


def run_audit(text: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.md"
        p.write_text(text, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(p)],
            capture_output=True,
            text=True,
        )
        return json.loads(r.stdout), r.returncode


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

    def test_html_fence(self):
        text = "</table>\n```mermaid\n%%{init: {'theme':'dark'}}%%\nflowchart TB\nA-->B\nstyle A fill:#2E86AB,stroke:#1B4965,color:#FFFFFF\nstyle B fill:#2E86AB,stroke:#1B4965,color:#FFFFFF\n```\n"
        data, _ = run_audit("---\ntitle: 某调用关系\n---\n" + text)
        codes = {i["code"] for i in data["issues"]}
        self.assertIn("html-fence", codes)


if __name__ == "__main__":
    unittest.main()
