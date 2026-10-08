---
name: weekly-report-table
description: >
  Use when 用户提供驱动小组周报（朱兴瑞、王霆、朱日芃）并要求汇总为小组总结表格、
  分类表格、weekly summary，或给出飞书周报文档链接要求生成飞书文档；
  以及tempted to docs +fetch 全文进对话、手写 DocxXML、或再输出「调试测试文档」第四行.
---

# 驱动小组周报总结表格

脚本（stdout 只打 JSON 摘要）：`scripts/pipeline.py`。分类/合并仍由模型做；**XML/MD/cite 验收禁止手写**。

## 核心原则

1. **小组视角、不写姓名**；同一项目合并到同一 `**项目名称**` 下。
2. **只有三行**：重点项目开发、技术选项与优化、问题定位与支持。文档并入所属项目，禁止第四行（含「调试测试文档」等同义）。
3. **本周**保留源 `cite`（`doc-id` / `file-type`）；**下周**只用自然语言，禁止 `<cite>` 和 URL。
4. **大文件不准进对话**：`docs +fetch` 只重定向落盘；不要 `Read` fetch JSON、`doc.xml`、飞书全文。只读 `extract` 摘要和 `source.txt`。

## 禁止

| 禁止 | 改做 |
|------|------|
| `+fetch` 打进对话 / `Read` fetch JSON | 重定向到 `_weekly_out/srcN.json` → `extract` |
| 手写 DocxXML / `--doc-format markdown` | `convert` → `+create --doc-format xml` |
| 抽查时再 `Read` fetch 全文 | `audit-xml --expect-cites extract.json` |
| 输出成员姓名、第四类行 | `convert` 会拒绝；分类见下表 |

## 执行流程

```
Step 1  各源周报 +fetch 落盘（或用户给的 md/截图转写为 txt）
Step 2  pipeline.py extract → source.txt + extract.json（只读摘要）
Step 3  按分类规则写 report.json（勿把 XML 写进对话）
Step 4  pipeline.py convert → doc.xml + 驱动小组周报表格_MMDD.md
Step 5  docs +create/--update xml @doc.xml
Step 6  fetch 落盘 + audit-xml；把文档 url 给用户
```

工作区 cwd 建 `_weekly_out`，用完删除。

### Step 1–2：抽取

```bash
lark-cli docs +fetch --doc "<URL>" --as user --doc-format xml \
  > ./_weekly_out/src0.json
python3 ~/.cursor/skills/weekly-report-table/scripts/pipeline.py extract \
  ./_weekly_out/src0.json -o ./_weekly_out
```

多份源把路径都传给 `extract`。stdout：`this_week_ids`、`names_present`、`chars_txt`。分类时 **Read `source.txt`**（纯文本 + `[cite wiki:TOKEN 标题]`），对照 `this_week_ids` 逐条勾掉。

### Step 3：`report.json`

```json
{
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
                "title": "草原雕 COME 上电流程耗时梳理"
              }
            }
          ]
        }
      ],
      "next_week": [
        {"project": "草原雕", "items": [{"text": "继续补充上电流程耗时分析结论"}]}
      ]
    },
    {"name": "技术选项与优化", "this_week": [], "next_week": []},
    {"name": "问题定位与支持", "this_week": [], "next_week": []}
  ]
}
```

`categories` 必须恰好上述三名、按序。无任务用空数组。下周 `items` 不要 `cite`。本周 `file-type` 与源一致（wiki/docx）。`title` 给本地 Markdown 链接用。

### Step 4–6：生成与验收

```bash
python3 ~/.cursor/skills/weekly-report-table/scripts/pipeline.py convert \
  ./_weekly_out/report.json -o ./_weekly_out
lark-cli docs +create --as user --doc-format xml \
  --title "驱动小组周报表格_MMDD" \
  --content "@./_weekly_out/doc.xml"
# 已有文档：+update --command overwrite --doc-format xml --content @doc.xml
# simple 会丢掉单元格 background-color，audit 会误报缺浅紫/浅蓝
lark-cli docs +fetch --doc <id> --as user --doc-format xml --detail full \
  > ./_weekly_out/fetch.json
python3 ~/.cursor/skills/weekly-report-table/scripts/pipeline.py audit-xml \
  ./_weekly_out/fetch.json --expect-cites ./_weekly_out/extract.json
```

`audit-xml` 必须 `ok: true`：三行三列、浅紫表头/浅蓝首列、本周含源 cite、下周无 cite/URL、无姓名、无第四类。把 `驱动小组周报表格_MMDD.md` 拷到用户指定处。通过后删 `_weekly_out`，给飞书 url。

表样式（浅紫/浅蓝/`<ul>/<li>`）由脚本写；不要按 `feishu-doc-format`「数据格不要自动改列表」把周报改成纯 `<p>`。

## 分类

| 类 | 放什么 |
|----|--------|
| 重点项目开发 | 产品/驱动/MCU/移植；产品测试、上电适配、上线介绍、HAL/操作教程 |
| 技术选项与优化 | 调研、立项、方案、认证材料；MCU 模板/HAL 库优化与重构 |
| 问题定位与支持 | 客户问题、硬件定位、跨项目支持；定位报告、联调记录、支持手册 |

立项/调研/方案 → 技术选项；产品测试/教程 → 重点项目；定位报告 → 问题支持。同一 `cite` 只出现一次。空单元格脚本会写成 `-`。

## 借口

| 借口 | 实际 |
|------|------|
| 「先 fetch 看看再分类」 | extract 已够；Read `source.txt` |
| 「XML 就几行，手写更快」 | 漏色/漏 cite；走 convert |
| 「下周也挂文档方便点开」 | 下周禁止链接 |
| 「文档单独成行更清楚」 | 并入三行里对应项目 |
| 「默认 fetch 就能 audit」 | 必须 `--detail full`；simple 无底色 |
