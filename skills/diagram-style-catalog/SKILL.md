---
name: diagram-style-catalog
description: >-
  Use when 用户要画架构图、分层图、流程图、时序图、路线图、胶囊图、
  泳道图、分工时间表，或说内化图样式、对照这张图画、这张图做成 skill、
  图的样式目录、不确定该用哪种图、/draw；以及画成了错的那一种、
  新图该新建 skill 还是改旧 skill。不是具体画法。
---

# 图样式目录（路由）

先选**视觉语言**，再选**媒介**。本 skill 只做分诊：命中后 **Read 对应 SKILL.md** 再画。
禁止用 Mermaid `flowchart` / `gantt` 硬凑另一种语言。

落点：个人 `~/.cursor/skills/<name>/SKILL.md`（平级，不要 `skills/diagrams/` 子目录）。
`/draw` 的菜单元数据以 `draw` Skill 为准；本目录提供指纹、默认出口、填空大纲。

## 0. 未点名必须出菜单

用户只说「画图 / 架构图 / /draw」、没有 Skill 名、也没有对照截图时：

1. **一次** AskQuestion：Q1 新画/转换/内化（见 `draw`），Q2 媒介。禁止拆成两轮。
2. 固定出口图种忽略 Q2。选定后贴 §5 大纲，**等用户填完再 Read 样式 Skill 并开画**。
3. **未选就画 = 违规**（尤其禁止直接画 Mermaid flowchart）。

已点名或已有对照图：跳过菜单，命中即停。

## 1. 选视觉语言

按用户口头 / 截图指纹命中即停。对不上 → 问用户或走 §3 内化，不要猜。

### 新画

| 指纹 | Skill |
|------|--------|
| 左栏 L0–L7 / 硬件；浅色色带 + 双白卡片；关/改/加/留/决策胶囊；平台角标嵌胶囊内 | `layer-action-capsule-diagram` |
| Mermaid `flowchart`、多 subgraph、跨层连线、暗色节点 | `mermaid-flowchart-layout` |
| 深色分层彩色卡片墙（`.layer` / `.halbox` / `customfig`） | `markdown-to-html` §3 / §7.6 |
| HTML 时序：贴顶彩色角色栏、生命线、橙色 Note | `html-sequence-swimlane` |
| 左栏阶段 × 顶栏季度；里程碑横条、菱形节点 | `task-roadmap-timeline` |
| 人员泳道、人力胶囊、Git 式分支合入、底栏星星 | `task-assignment-timeline` |

### 转换（已有图改格式，不是新构图）

| 指纹 | Skill |
|------|--------|
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

样式 Skill 规定长什么样；媒介 Skill 负责写到哪。

| 交到 | Skill / 规则 |
|------|----------------|
| 飞书画板（编辑/覆盖） | `lark-whiteboard`；DSL 细节 `lark-whiteboard-cli` |
| 本地 MD → 飞书文档（Mermaid 变画板） | `markdown-to-feishu-doc` |
| 飞书画板保留 Mermaid 颜色 | 规则 `mermaid-to-feishu-whiteboard` |
| 独立 HTML / sidecar | `markdown-to-html` |
| HTML 幻灯片 | `markdown-to-slides` |

**固定出口（不问媒介，用户选了也忽略）：**

| 图种 | 出口 |
|------|------|
| 深色分层卡片 / HTML 时序 / 阶段路线图 / 人员分工表 | `markdown-to-html` sidecar |
| 分层卡片 → draw.io / 时序 → draw.io | 本地 `.drawio` |
| 内化成 Skill | §3，不构图 |

**多出口（才采用 Q2）：** 胶囊图、Mermaid 分层架构。有样式 Skill 时先样式后媒介，不要只走 whiteboard-cli 默认色板。

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

- 聊天框输入 **`/draw`**：在 Skill 列表里搜 `draw` 并选中（`~/.cursor/skills/draw/`）。
- 也可以 `/` 后搜具体 Skill 名，如 `layer-action-capsule-diagram`
- 「按分层行动胶囊图画」「走 `layer-action-capsule-diagram`」
- 「对照这张图内化成 Skill，先查目录有没有同类」
- 只说「画个架构图」→ 先出一轮菜单 + §5 大纲，不要直接画 Mermaid

## 5. 选定后的填空大纲

把对应块原样贴出，等用户填。有现成文档/截图时可让用户改贴，不要再拆成五轮追问。

**胶囊图**
```
标题：
层（上→下）：
  - 层名：
    左模块：副标题
      - [共|A|R] 关|改|加|留|决策：短句
    右模块：
层间政策：
飞书链接或画板 token：
```

**Mermaid 分层架构**
```
标题：
subgraph / 层（上→下）：
节点与边：
.md 路径或飞书链接：
```

**深色分层卡片**
```
标题：
层（上→下）及每层卡片：
.md 路径：
```

**HTML 贴顶角色时序**
```
角色（左→右）：
消息（谁 → 谁：内容）：
.md 路径：
```

**项目阶段路线图**
```
时间轴 ticks：
阶段泳道与卡片：
里程碑：
输出路径：
```

**人员分工时间表**
```
顶栏阶段：
人员：
任务胶囊（谁 / 何时 / 分支）：
输出路径：
```

**分层卡片 → draw.io**
```
源 HTML 或 sidecar 路径：
输出 .drawio 路径：
```

**Mermaid 时序 → draw.io**
```
Mermaid sequence 源（文件或代码块）：
输出 .drawio 路径：
```

**内化成 Skill**
```
对照图（截图或链接）：
更像现有哪一种 / 要新建 fig-…：
```
