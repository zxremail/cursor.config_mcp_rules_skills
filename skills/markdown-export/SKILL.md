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
  表格表头、标题栏颜色、管道表、表头字体颜色、span color、图例色名、蓝绿紫橙上色、类似处理、模块底色、
  断句、加逗号、加标点、语义更清晰、只改标点不改措辞、
  首次生成 markdown、增补章节、黏连长句、事后补标点、
  先结论、施事不明、不是 A 是 B、碰巧与绑定、一层定语、同一叫法、
  拆成多行、子行缩进、符号前缀、多层一句、分号硬挤、列表拆段、
  表格单元格、br 分行、主谓宾齐全、短标签列、是/否着色、括号补充、听 X 实际是 Y、对照表残句、
  语义清晰化、万能口语动词、打完成中断、打用户 Slave、打 TLAST、
  摸 BAR、直捅、一并改掉、专名标记、直角引号、通道完成中断、
  新增格式要求、写进 SKILL、改 audit、自优化、格式写进 skill。
---

# Markdown 文档导出规范

**格式不准降级。** 完整条文与示例：[references/export.md](references/export.md)（§1–§5、§7–§10）、[references/prose.md](references/prose.md)（§6）。SKILL 变短只去掉重复目录/长示例，**禁止**因此省略 YAML `title`、`theme: dark`、节点 `fill`、表头 `#C9A0FF`、图例色名对齐 fill、断句、专名「」、格内列义。

## 执行顺序（先 Read，再落笔）

本页是清单，**对照表在 references**。未 Read 就写 = 未遵守本 skill。

1. **要写或改中文句子 / 列表 / 表格**（含格内）：先 `Read` [references/prose.md](references/prose.md)，再 Write。  
   可跳过的唯一可观察条件：本次交付**零**中文句子（纯英文或纯代码）。
2. **流程图排版**走 `mermaid-flowchart-layout`（其 Step 0 决定是否 Read layout.md）。
3. 落盘后跑 `audit_mermaid.py`（验收图、表头、图例色名，**代替不了** prose.md）。
4. 图下用「蓝 / 绿 / 紫 / 橙」指节点底色时，色名字色必须等于该图 `classDef` `fill`（[export.md](references/export.md) **§10**）。同类图例自动套。

| 借口 | 实际 |
|------|------|
| 「§6 摘要已经够用」 | 摘要没有对照表；未 Read prose.md 不得写中文 |
| 「赶时间，写完再读」 | 读是落笔前的步骤，不是验收 |
| 「只改一句 / 和上次一样」 | 仍要 Read；凭记忆会漏格内列义、「」和动词表 |
| 「audit 过了就行」 | 脚本不检查断句和专名 |

红旗：还没打开 `prose.md` 就开始 Write `.md` 正文。出现则停下来先 Read，不要接着写。

验收（不要 `Read` 整份业务 md 自检配色）：

```bash
python3 ~/.cursor/skills/markdown-export/scripts/audit_mermaid.py ./path.md
```

`ok: true` 才算图、表头、图例色名合格。排版/连线另遵 **`mermaid-flowchart-layout`**（细则 [layout.md](../mermaid-flowchart-layout/references/layout.md)）。有 `ai.cursor/` 时 **REQUIRED** **`ai-cursor-doc-output`**。

工作区根存在 `ai.cursor/` 时，目录由该 skill 决定；本文件约束 basename、正文格式、每一张 Mermaid 的深彩色。

## 0. 维护新政（用户改「生成 md」格式时）

用户说「写进 Skill / 新增格式要求 / 以后生成 md 都要…」，**不要只改本页散文**。先分类，再落盘。未分类就改 SKILL = 未完成。

| 类型 | 落哪里 | 还要做什么 |
|------|--------|------------|
| **可扫描**（色值、围栏字段、`theme`、表头字色、禁止某字面量、`useMaxWidth`、`</table>` 后空行） | `references/export.md` 一条硬规则 | `scripts/audit_mermaid.py` 加 `issues[].code` + `scripts/test_audit_mermaid.py` 正反例。`SKILL.md` **只加清单一行**，禁止把长示例贴回本页 |
| **每次写中文都要用**（断句、专名「」、格内列义、动词表） | `references/prose.md` | 本页 §6 最多补半行指针。脚本**不要**假装能验 |
| **偶发 / 某类图才用**（复杂 subgraph、图例方案 D、名+注） | 对应 reference（export 或 `mermaid-flowchart-layout` 的 layout.md） | 本页只写「出现 X 时 Read」。排版细则仍以 layout skill 为准 |
| **用户当场只要这一篇、以后不守** | 不改 Skill | 只改那份业务 md |

禁止：

- 只改 `SKILL.md`、不改脚本，导致 audit 仍按旧规则放行或误拦。
- 把可扫描规则写成「模型自己 Read 全文检查」。
- 把 `prose.md` 类规则塞进 audit（脚本代替不了断句）。
- 新政导致本页明显变长：长对照表进 references，本页保持编排。

改完脚本必须跑 `python3 ~/.cursor/skills/markdown-export/scripts/test_audit_mermaid.py`。向用户交代：这条进了 audit / prose / 按需 Read 哪一层。

| 借口 | 实际 |
|------|------|
| 「用户只说写进 Skill」 | 写进 Skill 包含分流；可扫描的必须改 audit |
| 「先改规范，脚本下次再说」 | 同一次交付改完；否则下次生成会被旧 audit 拽回去 |
| 「10 条新政都写进本页才不会忘」 | 本页只留分类后的一行；忘了靠 audit 和 Read 门，不靠把手册堆回来 |

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
- 图例色名对齐节点 fill：见 export.md **§10**。

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

写完跑 `audit_mermaid.py`。`ok: false` 按 `issues[].code` 改，不要带着浅色图/无色表头/未上色的图例色名结束。知识库维护走 `markdown-knowledge-maintain`。用户在改本 skill 的格式要求时走 **§0**，不要只改散文。
