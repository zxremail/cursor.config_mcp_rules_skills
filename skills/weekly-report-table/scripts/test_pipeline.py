#!/usr/bin/env python3
"""weekly-report-table pipeline 单测。"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline  # noqa: E402

FETCH = {
    "data": {
        "document": {
            "content": """
<h1>驱动组周报</h1>
<p>朱兴瑞</p>
<p>本周任务</p>
<ul>
<li>草原雕上电分析：<cite type="doc" title="草原雕 COME 上电流程耗时梳理" doc-id="PiEEwMighiT9ZukDryMc646unug" file-type="wiki"/></li>
</ul>
<p>下周任务</p>
<ul>
<li>继续完善 LXI 立项：<cite type="doc" doc-id="VPYpwPv5riXWhYkcKE4c3oNBnWc" file-type="wiki"/></li>
</ul>
"""
        }
    }
}

REPORT = {
    "mmdd": "1008",
    "categories": [
        {
            "name": "重点项目开发",
            "this_week": [
                {
                    "project": "草原雕",
                    "items": [
                        {
                            "text": "上电链路及耗时分析",
                            "cite": {
                                "doc_id": "PiEEwMighiT9ZukDryMc646unug",
                                "file_type": "wiki",
                                "title": "草原雕 COME 上电流程耗时梳理",
                            },
                        }
                    ],
                }
            ],
            "next_week": [
                {
                    "project": "草原雕",
                    "items": [{"text": "继续补充上电流程耗时分析结论"}],
                }
            ],
        },
        {
            "name": "技术选项与优化",
            "this_week": [],
            "next_week": [
                {
                    "project": "LXI 1.6",
                    "items": [{"text": "继续完善认证项目立项材料"}],
                }
            ],
        },
        {"name": "问题定位与支持", "this_week": [], "next_week": []},
    ],
}


class ExtractTests(unittest.TestCase):
    def test_buckets_cites_and_strips_wrapper(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "fetch.json"
            src.write_text(json.dumps(FETCH, ensure_ascii=False), encoding="utf-8")
            out = td / "out"
            summary = pipeline.cmd_extract([src], out)
            self.assertTrue(summary["ok"])
            self.assertEqual(
                [c["doc_id"] for c in summary["cites"]["this_week"]],
                ["PiEEwMighiT9ZukDryMc646unug"],
            )
            self.assertEqual(
                [c["doc_id"] for c in summary["cites"]["next_week"]],
                ["VPYpwPv5riXWhYkcKE4c3oNBnWc"],
            )
            self.assertIn("朱兴瑞", summary["names_present"])
            text = (out / "source.txt").read_text(encoding="utf-8")
            self.assertIn("草原雕", text)
            self.assertNotIn('"document"', text)


class ConvertTests(unittest.TestCase):
    def test_xml_colors_cites_and_md_links(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            report = td / "report.json"
            report.write_text(json.dumps(REPORT, ensure_ascii=False), encoding="utf-8")
            out = td / "out"
            man = pipeline.cmd_convert(report, out)
            xml = (out / "doc.xml").read_text(encoding="utf-8")
            self.assertIn(pipeline.TH_BG, xml)
            self.assertIn(pipeline.TD0_BG, xml)
            self.assertIn('doc-id="PiEEwMighiT9ZukDryMc646unug"', xml)
            self.assertNotIn("VPYpwPv5riXWhYkcKE4c3oNBnWc", xml)
            self.assertIn("<p>-</p>", xml)
            self.assertEqual(xml.count("<tbody>"), 1)
            self.assertEqual(len(pipeline.table_cells(xml)), 3)
            md = (out / man["md"]).read_text(encoding="utf-8")
            self.assertIn(
                "https://rigolportal.feishu.cn/wiki/PiEEwMighiT9ZukDryMc646unug",
                md,
            )
            self.assertNotIn("feishu.cn/wiki/VPYp", md)
            self.assertTrue(man["ok"])
            self.assertEqual(man["this_week_cites"], 1)
            self.assertEqual(man["next_week_cites"], 0)

    def test_rejects_fourth_category(self):
        bad = json.loads(json.dumps(REPORT))
        bad["categories"].append(
            {"name": "调试测试文档", "this_week": [], "next_week": []}
        )
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p = td / "r.json"
            p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(SystemExit):
                pipeline.cmd_convert(p, td / "out")


class AuditTests(unittest.TestCase):
    def test_ok_and_expect_cites(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            report = td / "report.json"
            report.write_text(json.dumps(REPORT, ensure_ascii=False), encoding="utf-8")
            out = td / "out"
            pipeline.cmd_convert(report, out)
            extract = {
                "cites": {
                    "this_week": [
                        {
                            "doc_id": "PiEEwMighiT9ZukDryMc646unug",
                            "file_type": "wiki",
                        }
                    ]
                }
            }
            ep = td / "extract.json"
            ep.write_text(json.dumps(extract), encoding="utf-8")
            result = pipeline.audit_xml(out / "doc.xml", ep)
            self.assertTrue(result["ok"], result["issues"])

    def test_next_week_cite_fails(self):
        xml = f"""<table>
<thead><tr>
<th background-color="{pipeline.TH_BG}">h</th>
<th background-color="{pipeline.TH_BG}">h</th>
<th background-color="{pipeline.TH_BG}">h</th>
</tr></thead>
<tbody>
<tr>
<td background-color="{pipeline.TD0_BG}"><p><b>重点项目开发</b></p></td>
<td><p>-</p></td>
<td><cite type="doc" doc-id="ABC" file-type="wiki"/></td>
</tr>
<tr>
<td background-color="{pipeline.TD0_BG}"><p><b>技术选项与优化</b></p></td>
<td><p>-</p></td><td><p>-</p></td>
</tr>
<tr>
<td background-color="{pipeline.TD0_BG}"><p><b>问题定位与支持</b></p></td>
<td><p>-</p></td><td><p>-</p></td>
</tr>
</tbody></table>"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.xml"
            p.write_text(xml, encoding="utf-8")
            result = pipeline.audit_xml(p, None)
            self.assertFalse(result["ok"])
            self.assertTrue(any("下周" in i for i in result["issues"]))


if __name__ == "__main__":
    unittest.main()
