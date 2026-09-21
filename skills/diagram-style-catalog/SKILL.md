---
name: diagram-style-catalog
description: >-
  Use when 用户要画架构图、分层图、流程图、时序图、路线图、胶囊图、
  泳道图、分工时间表，或说内化图样式、对照这张图画、这张图做成 skill、
  图的样式目录、不确定该用哪种图；以及画成了错的那一种、
  新图该新建 skill 还是改旧 skill。不是具体画法。
---

# 图样式目录（路由）

先选**视觉语言**，再选**媒介**。本 skill 只做分诊：命中后 **Read 对应 SKILL.md** 再画。
禁止用 Mermaid `flowchart` / `gantt` 硬凑另一种语言。

落点：个人 `~/.cursor/skills/<name>/SKILL.md`（平级，不要 `skills/diagrams/` 子目录）。

## 1. 选视觉语言

按用户口头 / 截图指纹命中即停。对不上 → 问用户或走 §3 内化，不要猜。

| 指纹 | Skill |
|------|--------|
| 左栏 L0–L7 / 硬件；浅色色带 + 双白卡片；关/改/加/留/决策胶囊；平台角标嵌胶囊内 | `layer-action-capsule-diagram` |
| Mermaid `flowchart`、多 subgraph、跨层连线、暗色节点 | `mermaid-flowchart-layout` |
| 深色分层彩色卡片墙（`.layer` / `.halbox` / `customfig`） | `markdown-to-html` §3 / §7.6 |
| HTML 时序：贴顶彩色角色栏、生命线、橙色 Note | `html-sequence-swimlane` |
| 左栏阶段 × 顶栏季度；里程碑横条、菱形节点 | `task-roadmap-timeline` |
| 人员泳道、人力胶囊、Git 式分支合入、底栏星星 | `task-assignment-timeline` |
| 已有分层卡片 HTML → `.drawio` | `cards-to-drawio` |
| Mermaid **时序图** → `.drawio` | `mermaid-to-drawio` |

易混：

| 别当成 | 实际 |
|--------|------|
| 「架构图」一律 Mermaid | 先对本表；胶囊 / 深色卡片 / 时间表都不是 flowchart |
| 胶囊图 = 深色卡片墙 | 胶囊是浅色色带+白卡片；卡片墙是 `markdown-to-html` §3 |
| roadmap = 人员分工表 | 阶段×时间 → `task-roadmap-timeline`；谁做哪块 → `task-assignment-timeline` |
| 时序 HTML = 分层卡片 | 贴顶角色栏 → `html-sequence-swimlane` |

## 2. 选媒介（交卷）

样式 Skill 规定长什么样；媒介 Skill 负责写到哪。可组合。

| 交到 | Skill / 规则 |
|------|----------------|
| 飞书画板（编辑/覆盖） | `lark-whiteboard`；DSL 细节 `lark-whiteboard-cli` |
| 本地 MD → 飞书文档（Mermaid 变画板） | `markdown-to-feishu-doc` |
| 飞书画板保留 Mermaid 颜色 | 规则 `mermaid-to-feishu-whiteboard` |
| 独立 HTML / sidecar | `markdown-to-html` |
| HTML 幻灯片 | `markdown-to-slides` |

有样式 Skill 时：**先样式后媒介**。例如 3.1 胶囊图 → `layer-action-capsule-diagram` 再 `lark-whiteboard`，不要只走 whiteboard-cli 默认色板。

## 3. 内化新图（用户要把样子做成 Skill）

1. **查本表**。同一种样子 → 改那份 Skill（补色板/禁止项），不新建。
2. **只换业务内容**（同一胶囊换条文）→ 不建 Skill。
3. **新视觉语言** → 新建 `~/.cursor/skills/<name>/SKILL.md`：
   - 新 Skill 名可用 `fig-` 前缀（如 `fig-c4-container`）。**已有名字不要为整齐而改。**
   - `description` 只写触发指纹与反例症状，不写步骤摘要。
   - 正文：色板、几何、何时用/不用（互指兄弟）、禁止项。业务条文留在文档。
4. **在本表 §1 补一行**，并在新 Skill 的「何时用 / 不用」指回本目录与易混项。
5. 只换媒介（飞书 / HTML / draw.io）→ 不新建样式 Skill，走 §2。

**REQUIRED：** 新建或大改图类 Skill 时用 `create-skill` 的 frontmatter 规则。

## 4. 用户怎么点名

- 「按分层行动胶囊图画」「走 `layer-action-capsule-diagram`」
- 「像 3.1 那样，不要深色卡片墙」
- 「对照这张图内化成 Skill，先查目录有没有同类」
- 只说「画个架构图」→ 先对本表，对不上再问，不要直接画 Mermaid
