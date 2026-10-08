---
name: markdown-export
description: >-
  Use when generating, writing, saving, or exporting markdown documents;
  when drawing or editing Mermaid diagrams in .md; or when a chart looks
  light-themed, default-colored, washed-out, pale, or hard to read on a
  dark background. Triggers: 生成 markdown、写文档、导出 md、Mermaid 配色、
  深彩色、暗色主题、theme dark、浅色图、默认配色、文字被遮挡、显示不全、裁切、
  嵌套 subgraph 外框内框同色、套盒糊成一块、层框列框不易区分、
  时序图按向左/向右给箭头上色、实际含义标题、YAML title、
  表格表头、标题栏颜色、管道表、表头字体颜色、span color、
  断句、加逗号、加标点、语义更清晰、只改标点不改措辞、
  首次生成 markdown、增补章节、黏连长句、事后补标点、
  先结论、施事不明、不是 A 是 B、碰巧与绑定、一层定语、同一叫法、
  拆成多行、子行缩进、符号前缀、多层一句、分号硬挤、列表拆段、
  表格单元格、br 分行、主谓宾齐全、短标签列、是/否着色、括号补充、听 X 实际是 Y、对照表残句、
  语义清晰化、万能口语动词、打完成中断、打用户 Slave、打 TLAST、
  摸 BAR、直捅、一并改掉、专名标记、直角引号、通道完成中断。
---

# Markdown 文档导出规范

**格式不准降级。** 完整条文与示例：[references/export.md](references/export.md)（§1–§5、§7–§9）、[references/prose.md](references/prose.md)（§6）。SKILL 变短只去掉重复目录/长示例，**禁止**因此省略 YAML `title`、`theme: dark`、节点 `fill`、表头 `#C9A0FF`、断句、专名「」、格内列义。

验收（不要 `Read` 整份 md 自检配色）：

```bash
python3 ~/.cursor/skills/markdown-export/scripts/audit_mermaid.py ./path.md
```

`ok: true` 才算图和表头合格。排版/连线另遵 **`mermaid-flowchart-layout`**（细则 [layout.md](../mermaid-flowchart-layout/references/layout.md)）。有 `ai.cursor/` 时 **REQUIRED** **`ai-cursor-doc-output`**。

工作区根存在 `ai.cursor/` 时，目录由该 skill 决定；本文件约束 basename、正文格式、每一张 Mermaid 的深彩色。

## 1. 文件命名

英文、小写、连字符：`rk3588-device-tree-guide.md`。适用 `ai-cursor-doc-output` 时不要写到仓库根或 `docs/`。

## 2. 内容

详实、需要时用图，不要为凑类型硬画。尽量不要外部图片链接或 ASCII 艺术图。中文按 **§6**（细则 prose.md）。管道表表头按 **§9**，不要为此改成 HTML `<table>`。列数据着色走 `coloring-markdown-table-column`。

## 3. 图表语法（格式）

- 用 Mermaid。`</table>` 与 `` ```mermaid `` 之间必须空一行。
- 每个围栏开头 YAML `title`（最近小节 + 图意，短句无句号），然后 `%%{init}`。禁止「流程图」「如图」「示意图」。围栏外不要再写一行标题。`sequenceDiagram` 只用 YAML `title`，不要再写 `title xxx`。
- **每张图**同时：`%%{init: {'theme': 'dark'}}%%` **加上**每个可见节点 `style`/`classDef`（深彩色 `fill` + `color:#FFFFFF`）。只写 `theme: dark` = 未完成。对话里的图同样适用。
- 换行用 `<br>`，禁止 `\n`。文字必须完整露出；flowchart 排法见 layout skill。
- 转飞书时 YAML `title` 作画板标题，见 `markdown-to-feishu-doc`。

## 4. 密度

对比类禁止左右并列 subgraph 挤一块，拆成多个围栏。单链过长改 `TB` 或拆块。跨域架构优先单张 `TB` + 隐形占位线（禁止裸 `~~~`），见 layout §1.4、§3–§6。小图不加独立图例。

## 5. 深彩色（硬规则，先于排版）

适用范围：一切 `` ```mermaid ``（flowchart / sequence / class / er / state / gantt / pie / mindmap / block / C4 / 草稿）。

禁止：无 init dark；无 fill；`fill:#fff/#eee/#f8f8f8/#fafafa`；深底 `color:#000/#333`；嵌套 subgraph 外框内框同一 `fill`（外深内浅，layout §0.1）。

色板：主 `#2E86AB` / 次 `#A23B72` / 决策 `#F18F01` / 成功 `#2D936C` / 失败 `#E63946` / 信息 `#6A4C93`（stroke 用同色相更深，字 `#FFFFFF`）。节点多用 `classDef`。`linkStyle` 不能代替节点色。时序方向色：向右 `#3370FF`、向左 `#00A870`、暗底自调用 `#E8EAED`（layout §4.1）。

## 6. 中英文排版

撰写、首次生成、增补都要当场写清。细则与对照表 **必守** [prose.md](references/prose.md)，不得把本节当成「可以不读细则」。

- 中英文之间空格。
- **落笔即断句**：两套主语、并列路径、条件状语当场用逗号/顿号/分号；不要等用户说加标点。用户只要标点时只加标点、不改措辞。
- **语义**：先结论；写清谁对谁做什么；不是 A 是 B；对照用表、步骤用编号、结构用图。一层定语；同一概念同一叫法。多层一句改列表。不要用「打 / 摸 / 直捅」当万能动词（「打开」设备、「打印」日志、「打点」计数除外；「打 TLAST」写「置 TLAST」）。中文专名用「」，不用 “」。
- **表格格内**：先看列义。分类/是否/状态用短标签（可括号补细节）；解释/对照/提要列主谓宾 + `<br>` 分行，禁止分号硬挤。索引「说明」短标签、「提要」完整句。

## 7. 实时保存

边写边存。禁止把无配色 Mermaid 当占位写入。

## 8. 引脚颜色

Input `#E066FF`；Output `#00FF00`；Bidirectional `#FFD700`；Power `#FF0000`；Ground `#404040`。深色 fill 上字黑或白按对比度。示例见 export.md §8。

## 9. 管道表表头字色

每个表头单元格：`<span style="color:#C9A0FF">列名</span>`。只改字色。知识库默认给 Cursor 预览看，GitHub 会剥 `style` 也照写。例外：飞书走 `feishu-doc-format`；用户明确不要 HTML；冻结/sticky 走 `freezing-html-table-headers` 或 `freezing-mpe-table-headers`；数据列着色走 `coloring-markdown-table-column`。

## 交付

写完跑 `audit_mermaid.py`。`ok: false` 按 `issues[].code` 改，不要带着浅色图/无色表头结束。知识库维护走 `markdown-knowledge-maintain`。
