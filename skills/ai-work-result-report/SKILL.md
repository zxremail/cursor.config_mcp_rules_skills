---
name: ai-work-result-report
description: >-
  按公司 AI 工作成果抽检要求，从用户提供的飞书文档（lark-cli docs +fetch 读取）生成可过审、可直接复制粘贴的成果说明四段：
  使用场景、如何使用、输出成果、成果证明链接。Use when the user provides a Feishu docx/wiki link,
  成果说明、AI工作成果、工作成果报告、抽检、成果证明链接、采取的动作、ROI自评、飞书文档、复制粘贴填报、
  fetch 落盘、extract 大纲、写进 SKILL、改 extract。
---

# AI 工作成果说明（抽检过审框架）

从飞书证明文档生成可粘贴的四段说明。**禁止凭记忆编造**文档中不存在的表、数据、截图或结论。画板/图片在 fetch 里往往只是占位：只按大纲里的章节名与计数写「输出成果」，**不要** fetch 画板 raw、**不要**虚构画板内容。

**大文件不准进对话。** `+fetch` 重定向落盘；不要 `Read` fetch JSON / pretty 全文。只读 extract 的 JSON 摘要；写某一节时再 `Read` `sections/*.txt`。四段正文和 checklist **仍由模型写/判断**，脚本只抽大纲。

```bash
lark-cli docs +fetch --doc "<URL>" --as user --format pretty \
  > ./_result_out/src0.json
python3 ~/.cursor/skills/ai-work-result-report/scripts/pipeline.py extract \
  ./_result_out/src0.json -o ./_result_out \
  --url "<同一条原始飞书 URL>"
```

stdout 只有 `headings`、表/图/画板计数、`numbers`、`section_files`。工作区 cwd 建 `_result_out`，用完删除。

用户要加/改本 skill 硬格式：**不要只改本页。** 可扫描的（unwrap fetch、标题/表/图计数）→ `scripts/pipeline.py extract` + `test_pipeline.py`。四段措辞、checklist、ROI 相称 → `template.md` / `checklist.md` / `references/process.md`，不要假装 extract 能过审。本页只加清单一行。

## 执行顺序

1. 每条用户链接：`+fetch` **重定向**到 `_result_out/srcN.json`（`/docx/`、`/wiki/` 均可；wiki 类型不明时按 `lark-doc` 先 `get_node`）。输出被截断则 `--offset` / `--limit` 再 fetch 成 `srcN-p1.json`，一并交给 extract。**认证失败**才 Read `lark-shared` / `lark-doc`；成功路径不要先读那两份 SKILL。
2. `extract` → 看 stdout JSON。需要某章证据再 Read 对应 `sections/` 切片，禁止 Read `source.txt` 全文当「再确认一遍」。
3. 写四段前 **Read** [template.md](template.md)。用户给了计划完成标准、fail.txt 或说「被驳回」→ 再 Read [anti-patterns.md](anti-patterns.md)。卡写法时才 Read [examples.md](examples.md)。留痕/ROI 档位/证明文档结构 → [references/process.md](references/process.md)。
4. **只向用户输出一段纯文本**（标题与 template 四节一致），供复制。不用复杂 Markdown 表。第 4 节必须含用户**原始飞书链接**；多份时主报告在前并写清「审核优先点开哪条」。
5. 回复末尾附 checklist 自检 3～5 条（对照 [checklist.md](checklist.md)），**不要**把 checklist 放进粘贴正文。可选：用户要 ROI 时另给 1～2 句档位理由（与规模相称，细则 process.md）。

无飞书链接、只有本地 md：对 md 跑 `extract`，缺证明链接则提醒补飞书后再写第 4 节。

| 借口 | 实际 |
|------|------|
| 「pretty 不大，直接看 stdout」 | 重定向；漏一页就编造风险 |
| 「Read 一下 fetch 核对」 | extract 摘要 + 单节切片 |
| 「先读 lark-doc 再 fetch」 | 认证失败再读 |
| 「extract 已经算过审核」 | 脚本不算过审；checklist 仍要人判 |

红旗：fetch 没 `>` 落盘；或开始写四段却还没打开 template.md。停下来补步骤。

## 硬性要求（写四段时不得降级）

| 字段 | 必须做到 | 禁止 |
|------|----------|------|
| 使用场景 | 业务背景 + 问题 + 为何用 AI；对齐**计划完成标准** | 一句话、与动作重复、只写搭环境/写方案 |
| 如何使用 | 步骤 = 动作 + 工具 + 产出（形态+数量） | 「已完成」「已优化」 |
| 输出成果 | 形态+数量 + 执行结果/数据/结论 | 只有过程、没有实测 |
| 成果证明链接 | 组织内可点开即见证据 | 仅本地路径；描述与文档不符 |
| ROI | 与交付规模相称 | 小任务写 8h+ 无依据 |

数量用「N 份/张/组」，不用「若干」。计划原文里的标准短语原样保留。本地截图无链接时：先做成飞书「背景→方法→结果」再填第 4 节。

粘贴骨架：

```text
成果说明

1. 使用场景
…

2. 如何使用
…

3. 输出成果
…

4. 成果证明链接
…
```
