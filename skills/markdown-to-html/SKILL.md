---
name: markdown-to-html
description: >-
  将 Markdown 文档转换为独立 HTML 页面。复杂 Mermaid 用 sidecar（.figures/）
  分层卡片替代；推荐两阶段：先基本 sidecar + md2html build，再按需打磨单张图。
  Use when the user asks to convert markdown to HTML, md2html, sidecar,
  customfig, or mentions "md 转 html", "生成 html", "导出 html", "markdown to html".
  时序图向右箭头 #3370FF、向左虚线 #00A870、
  新增 HTML 格式、写进 SKILL、改 audit。
---

# Markdown 转 HTML 规范

选 sidecar 布局前先读 `diagram-style-catalog`。本 skill 管 HTML 交卷与深色分层卡片（§3 / §7.6）；浅色行动胶囊走 `layer-action-capsule-diagram`；贴顶泳道时序走 `html-sequence-swimlane`。

**格式不准降级。** 完整条文、卡片 HTML/CSS 模板、命令说明以 [references/html.md](references/html.md) 为准。转换用已有 **md2html**，不要手写整页、不要 `Read` 生成的 `.html` 全文。

用户要加/改本 skill 硬格式：**不要只改本页。** 可扫描的（深色主题类名、slug 双 id、sidecar 约定、禁读特征）→ `html.md` 一条 + `scripts/audit_html.py` + 其单测；骨架/卡片 HTML 仍由 **md2html** 生成，改模板不改「手写整页」。不能扫的（卡片分层怎么排）→ `html.md` §3/§7.6，写 sidecar 前 Read。本页只加清单一行。改完跑 audit 单测。

源 `.md` 的 Mermaid 深彩色走 **`markdown-export`** + `audit_mermaid.py`。有 `ai.cursor/` 时 **REQUIRED** **`ai-cursor-doc-output`**（html / sidecar 与源 md 同知识库子目录）。

## 执行顺序（先命令，再按需 Read）

1. `md2html analyze doc.md`（stdout 已是块清单，不要 Read 源里每张图的围栏全文来「再判断一遍」，以 analyze 为准）。
2. **仅当** analyze 标了「建议降级」：先 `Read` [references/html.md](references/html.md) §3 与 §7.6，再写 `doc.figures/mermaid-N.html`。  
   `sequenceDiagram` 降级 → `html-sequence-swimlane`，不要改成蓝/绿卡片墙。源 `.md` 长图阶段带须原样进 sidecar（`阶段 N：因果`），细则 `html-sequence-swimlane` 与 layout.md §4.2。
3. `md2html build doc.md`（可 `--strict-figures`）。本机有桌面时可再加 `--open`；无显示器、远程 SSH、或 Agent 会话里不要 `--open`（会抢焦点或失败）。
4. `python3 ~/.cursor/skills/markdown-to-html/scripts/audit_html.py doc.html --md doc.md`  
   `ok: true` 才交差。禁止 `Read` `doc.html`。
5. 提醒用户浏览器预览。阶段 B（打磨单张）只改那一个 sidecar 再 build + audit。

可跳过 html.md 的唯一条件：analyze **零**「建议降级」，且不写任何 sidecar。

| 借口 | 实际 |
|------|------|
| 「先看一眼生成页再改」 | audit 看摘要；不要把 HTML 灌进对话 |
| 「卡片结构我记得」 | 未 Read §3 不得写 `.layer` / `.customfig` |
| 「简单图也做成卡片」 | 未触发降级则保留 Mermaid |

红旗：将写 `mermaid-N.html` 却还没打开 html.md §3。停下来先 Read。

```bash
~/.cursor/skills/markdown-to-html/bin/md2html analyze doc.md
~/.cursor/skills/markdown-to-html/bin/md2html build doc.md
# 仅本机桌面预览：md2html build doc.md --open
python3 ~/.cursor/skills/markdown-to-html/scripts/audit_html.py doc.html --md doc.md
```

有 pip：`pip install -e ~/.cursor/skills/markdown-to-html` 后直接 `md2html …`。

## 1. 基本结构（格式）

单文件、零依赖（CDN 除外）：深色 GitHub Dark、`#layout` + 左栏 `#sidebar`、`marked.js` + `mermaid.js`、`@media max-width:900px` 收起侧栏。骨架见 html.md §1。

### 1.1 GitHub slug

正文目录锚点是 **github-slugger**（`#1-怎么验证`）。标题必须两套 id：`id="h-1"` **加上** `<span id="github-slug">`。实现：`md2html/templates/anchor.js` 拼在 `runtime.js` 前。**不要改回去、不要从 builder.py 拿掉拼接。** 改这三处后跑 `node ~/.cursor/skills/markdown-to-html/tests/test_anchor.js`。正文 `#` 找不到目标时不要 `preventDefault`。

## 2. Mermaid

源图必须已是深彩色；页面 `theme:'dark'` 不能代替节点 `fill`。时序：`->>` / `-->>`；页面把实线描成 `#3370FF`、虚线 `#00A870`（`base.css`）。自调用浅色 → 泳道 `.seq-self`。流程图步骤箭头不用这组色。

### 2.2 必须降级（analyze 已实现）

任一：节点 >15；层级 >4；并列 subgraph >3；节点多行标题+描述；大量双向/交叉；节点内列表/表。渲染会重叠、截断、交叉、横滑 → 降级。

### 2.3 小图不要拉满栏宽

模板已是 `.mermaid svg { max-width:100%; width:auto }` 且 `useMaxWidth:false`。**禁止** `max-width:none`。源里小图 fence 仍写 `useMaxWidth:false`。宽图用横向滚动，不要撑满放大。

## 3. 分层卡片（写 sidecar 前 Read html.md §3）

`.customfig` > `.layer` > `.layer-header`（`.layer-label` + `.layer-sub`）> `.layer-body` > `.node` / `.note`；层间 `.arrow`；可选 `.legend`。相邻层颜色必须明显区分。

色板：`--bg:#0d1117`；应用/硬件灰 `--dim`/`--panel`；库蓝 `--blue/#58a6ff`；服务/固件橙 `--orange/#f0883e`；内核紫 `--purple/#a371f7`；管理红 `--red/#f85149`；数据绿 `--green/#3fb950`。结构模板、CSS、`.layer-split` / grid 只在 html.md §3.3–3.5。

## 4. template 注入

Markdown：`<!-- FIGURE: fig-id -->` 或 `customfig:mermaid-N`。sidecar 片段根元素 `.customfig`，build 打进 `<template>`。

## 5. 文件名

与源同目录、同 stem、`.html`。sidecar：`doc.figures/mermaid-N.html`（N 与 analyze 编号一致，从 0）。自定义 `fig-id.html`。`extra.css` 可追加；长表冻结走 `freezing-html-table-headers`（页面 sticky，禁止 overflow+max-height 内框）。

## 6. 不要

全部降级；改回 `useMaxWidth:true` / `max-width:none`；外链 CSS（CDN 除外）；外链图片当图；不预览；丢掉 GitHub slug / 拿掉 `anchor.js`；`Read` 整页生成 HTML。

## 7. 两阶段 + 布局速查

- **A（默认）**：analyze → 建议降级则基本 sidecar（覆盖节点与层次即可，复杂连线用 `.deps` 文字）→ build → audit。  
- **B**：用户点名某图才精修那一个 `mermaid-N.html`，不要全库重绘。

| 模式 | 场景 |
|------|------|
| platform-stack | 软件分层纵叠 `.layer` + `.arrow` |
| phys-map | 物理 \| 映射 \| 软件 三列 |
| cfg-data-flow | 配置/数据/同步三列 `.lane` |
| multi-stack | 双列+分布式 |
| link-legend | 仅线型图例 |
| seq-flow | 水平步骤条 |
| seq-swimlane | 贴顶角色栏 → `html-sequence-swimlane` |

`--strict-figures`：缺 sidecar 即失败。更多命令见 html.md §7.7 与 [README.md](README.md)。
