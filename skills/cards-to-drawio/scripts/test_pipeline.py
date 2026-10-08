#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pipeline.py"

HTML = """
<div class="customfig">
  <div class="layer layer-blue">
    <div class="layer-header">
      <span class="layer-label">L1 · I/O 边界</span>
      <span class="layer-sub">外部接口</span>
    </div>
    <div class="layer-body">
      <span class="node">① 入站<br><span class="note">TCP 长连接</span></span>
      <span class="node">② 出站<br><span class="note">Unix Socket</span></span>
    </div>
  </div>
  <div class="arrow">↓ 入站事件 ↑ 命令回送</div>
  <div class="layer layer-green">
    <div class="layer-header"><span class="layer-label">L2 · 数据面</span></div>
    <div class="layer-body">
      <span class="node">核心业务<br><span class="note">epoll</span></span>
      <span class="node">共享支撑</span>
    </div>
  </div>
</div>
"""


def run(cmd: list[str]) -> tuple[dict, int]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        data = {"_raw": p.stdout, "_err": p.stderr}
    return data, p.returncode


class ConvertTests(unittest.TestCase):
    def test_convert_and_audit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "fig.html"
            src.write_text(HTML, encoding="utf-8")
            data, code = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "convert",
                    str(src),
                    "-o",
                    str(td),
                    "--stem",
                    "rxie-shmc-service-internal",
                ]
            )
            self.assertTrue(data.get("ok"), data)
            self.assertEqual(code, 0)
            path = td / "rxie-shmc-service-internal.drawio"
            xml = path.read_text(encoding="utf-8")
            self.assertIn('pageWidth="1040"', xml)
            self.assertIn('background="#0d1117"', xml)
            self.assertIn('strokeColor=#58a6ff', xml)
            self.assertNotIn('edge="1"', xml)
            aud, ac = run([sys.executable, str(SCRIPT), "audit-drawio", str(path)])
            self.assertTrue(aud.get("ok"), aud)
            self.assertEqual(ac, 0)

    def test_date_prefix_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "fig.html"
            src.write_text(HTML, encoding="utf-8")
            data, code = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "convert",
                    str(src),
                    "-o",
                    str(td),
                    "--stem",
                    "2026-04-21-foo",
                ]
            )
            self.assertFalse(data.get("ok", True) and code == 0)


if __name__ == "__main__":
    unittest.main()
