#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPE = ROOT / "pipeline.py"
SAMPLE = """\
```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: request
    Server-->>Client: response
    Server->>Server: self work
```
"""


class TestPipeline(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PIPE), *args],
            capture_output=True,
            text=True,
        )

    def test_convert_and_audit(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "login.md"
            src.write_text(SAMPLE, encoding="utf-8")
            out = Path(td) / "out"
            r = self.run_cli("convert", str(src), "-o", str(out), "--stem", "login-flow")
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertTrue(man["ok"])
            self.assertEqual(man["count"], 1)
            p = Path(man["files"][0]["file"])
            self.assertEqual(p.name, "login-flow.drawio")
            xml = p.read_text(encoding="utf-8")
            self.assertIn("shape=rectangle", xml)
            self.assertIn("dashed=1", xml)
            self.assertIn("fillColor=#2E86AB", xml)
            self.assertIn("#0000FF", xml)
            self.assertIn("#00AA00", xml)
            self.assertIn("#000000", xml)
            self.assertIn("fillColor=none", xml)
            self.assertNotIn("curved=1", xml)
            self.assertEqual(man["files"][0]["participants"], 2)
            self.assertEqual(man["files"][0]["messages"], 3)
            a = self.run_cli("audit-drawio", str(p))
            self.assertEqual(a.returncode, 0, a.stdout)
            self.assertTrue(json.loads(a.stdout)["ok"])

    def test_mmd_infer_participants(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "x.mmd"
            src.write_text(
                "sequenceDiagram\n    A->>B: hi\n    B->>A: ok\n",
                encoding="utf-8",
            )
            r = self.run_cli("convert", str(src), "-o", str(Path(td) / "o"))
            self.assertEqual(r.returncode, 0, r.stderr)
            man = json.loads(r.stdout)
            self.assertEqual(man["files"][0]["participants"], 2)

    def test_date_stem_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "x.mmd"
            src.write_text("sequenceDiagram\n    A->>B: hi\n", encoding="utf-8")
            r = self.run_cli(
                "convert",
                str(src),
                "-o",
                str(Path(td) / "o"),
                "--stem",
                "2026-10-08-foo",
            )
            self.assertNotEqual(r.returncode, 0)

    def test_flowchart_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "x.mmd"
            src.write_text("flowchart TD\n    A-->B\n", encoding="utf-8")
            r = self.run_cli("convert", str(src), "-o", str(Path(td) / "o"))
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
