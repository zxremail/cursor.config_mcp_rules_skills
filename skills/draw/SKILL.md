---
name: draw
description: >-
  Use when the user types /draw to pick a diagram visual language from the
  catalog, then draw. Slash menu for 画图 / 架构图 / 胶囊图 / 路线图 / 时序图.
disable-model-invocation: true
---

# /draw

**REQUIRED SUB-SKILL:** Read `diagram-style-catalog` 后按下面做。未选定前禁止画 Mermaid、禁止上画板。

已点名 Skill 或贴了对照图：跳过菜单，直接走对应 Skill；媒介按目录 §2 默认表，多出口的才问。

## 一轮菜单（只调用一次 AskQuestion）

两道题放进**同一次** AskQuestion，不要拆成两轮。

**Q1 `kind`**（必选）：

| id | 标签 |
|----|------|
| capsule | 新画：分层行动胶囊图 |
| tinted-cards | 新画：浅色分层卡片墙 |
| mermaid-flow | 新画：Mermaid 分层/连线架构 |
| dark-cards | 新画：深色分层彩色卡片墙 |
| seq-html | 新画：HTML 贴顶角色时序 |
| roadmap | 新画：项目阶段路线图 |
| assign | 新画：人员分工时间表 |
| cards-drawio | 转换：分层卡片 HTML → draw.io |
| seq-drawio | 转换：Mermaid 时序图 → draw.io |
| internalize | 其它：把对照图内化成 Skill |

选定后 `kind` → Skill：`capsule`→`layer-action-capsule-diagram`，`tinted-cards`→`fig-tinted-layer-cards`，`mermaid-flow`→`mermaid-flowchart-layout`，`dark-cards`→`markdown-to-html`，`seq-html`→`html-sequence-swimlane`，`roadmap`→`task-roadmap-timeline`，`assign`→`task-assignment-timeline`，`cards-drawio`→`cards-to-drawio`，`seq-drawio`→`mermaid-to-drawio`。

**Q2 `medium`**：飞书画板 / MD→飞书文档 / 独立 HTML / HTML 幻灯片 / 本图种默认。

选定后：

1. 目录 §2「固定出口」的图种 **忽略 Q2**，用表里的默认。
2. `capsule` / `mermaid-flow` 才采用 Q2；选了「本图种默认」时：胶囊→飞书画板，Mermaid 架构→本地 `.md`。
3. `internalize` → 目录 §3，不出填空构图大纲。
4. Read 对应样式 Skill。
5. 把目录 **§5 对应填空大纲**贴给用户，**等用户填完再画**。
