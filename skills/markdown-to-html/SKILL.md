---
name: markdown-to-html
description: >-
  将 Markdown 文档转换为独立 HTML 页面。当 Mermaid 图表过于密集、节点过多导致
  auto-layout 混乱时，自动改用分层彩色卡片布局（HTML/CSS）替代 Mermaid。
  Use when the user asks to convert markdown to HTML, or mentions
  "md 转 html", "生成 html", "导出 html", "markdown to html".
---

# Markdown 转 HTML 规范

将 Markdown 文档转换为可在浏览器中独立打开的 HTML 页面，支持 Mermaid 渲染，并在 Mermaid 表达力不足时自动降级为分层彩色卡片布局。

---

## 1. 基本结构

生成的 HTML 必须是**单文件、零依赖**的独立页面（CDN 引用除外）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>文档标题</title>
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
  <style>/* 内嵌全部样式 */</style>
</head>
<body>
  <div id="layout">
    <nav id="sidebar"><!-- 自动生成目录 --></nav>
    <main><article id="content"></article></main>
  </div>
  <script>/* Markdown 解析 + Mermaid 初始化 + TOC 生成 */</script>
</body>
</html>
```

要求：
- 深色主题（GitHub Dark 风格），参考色板见下方"配色体系"
- 左侧固定侧边栏（自动从 h1/h2 生成目录）
- 响应式布局（`@media max-width:900px` 时侧边栏收起）
- Markdown 内容通过 `marked.js` 在客户端解析渲染

## 2. Mermaid 图表处理

### 正常情况

Markdown 中的 ` ```mermaid ` 代码块由 `mermaid.js` 在客户端渲染，无需特殊处理。

### 触发降级的条件（必须自动判断）

遇到以下任一情况时，**禁止使用 Mermaid**，必须改用分层彩色卡片布局：

| 信号 | 说明 |
|------|------|
| 节点 > 15 个 | 单个 Mermaid 代码块中节点数超过 15 |
| 层级 > 4 层 | 架构图存在 4 层以上的纵向分层 |
| 并列 subgraph > 3 | 同一层级有 3 个以上并列 subgraph |
| 节点含多行文本 | 节点内需要标题 + 描述 + 注释等多行信息 |
| 双向/复杂连接 | 层间存在大量双向箭头或交叉连接 |
| 表格/列表嵌套 | 节点内需要展示列表或表格形式的子项 |

**判断原则**：如果 Mermaid 渲染后可能出现节点重叠、文字截断、箭头交叉、需要横向滚动，就必须降级。

## 3. 分层彩色卡片布局规范

当 Mermaid 不适用时，使用纯 HTML/CSS 绘制分层架构图。

### 3.1 配色体系（深色主题）

```css
:root {
  --bg:#0d1117; --panel:#161b22; --panel2:#21262d; --border:#30363d;
  --text:#c9d1d9; --muted:#8b949e; --dim:#484f58;
  --blue:#58a6ff;    --bluebg:#0d2137;    --bluetxt:#79c0ff;
  --green:#3fb950;   --greenbg:#122117;   --greentxt:#7ee787;   --greenborder:#238636;
  --orange:#f0883e;  --orangebg:#1a150d;  --orangetxt:#ffcc80;
  --purple:#a371f7;  --purplebg:#1a1428;  --purpletxt:#d2a8ff;  --purpleborder:#6e40c9;
  --red:#f85149;     --redbg:#2d1215;     --redtxt:#ffa198;     --redborder:#da3633;
}
```

### 3.2 层级配色分配

每一层使用不同颜色主题，从上到下推荐：

| 层级 | 语义 | 颜色 | border | 背景 | 文字 |
|------|------|------|--------|------|------|
| 应用层 | 用户态进程 | 灰 | `--dim` | `--panel2` | `--muted` |
| 库/SDK 层 | 链接库 | 蓝 | `--blue` | `--bluebg` | `--bluetxt` |
| 服务层 | Daemon | 橙 | `--orange` | `--orangebg` | `--orangetxt` |
| 内核层 | 驱动/模块 | 紫 | `--purple` | `--purplebg` | `--purpletxt` |
| 硬件层 | FPGA/芯片 | 灰暗 | `--dim` | `--panel` | `--muted` |
| 固件层 | MCU/FW | 橙虚线 | `--orange` dashed | `--orangebg` | `--orangetxt` |
| 管理面 | 监控/告警 | 红 | `--red` | `--redbg` | `--redtxt` |
| 数据面 | 高速数据通路 | 绿 | `--green` | `--greenbg` | `--greentxt` |

如果实际层级语义与上表不匹配，可灵活选择颜色，但必须保持**相邻层颜色有明显区分**。

### 3.3 HTML 结构模板

每一层使用 `.layer` 容器：

```html
<div class="customfig">
  <!-- 一层 -->
  <div class="layer layer-xxx">
    <div class="layer-header">
      <span class="layer-label">层级名称</span>
      <span class="layer-sub">层级简要说明</span>
    </div>
    <div class="layer-body">
      <span class="node xxx">节点名称<br><span class="note">附注信息</span></span>
      <span class="node xxx">节点名称</span>
    </div>
  </div>

  <!-- 层间箭头 -->
  <div class="arrow">↓ 通信方式说明 ↓</div>

  <!-- 下一层 -->
  <div class="layer layer-yyy">
    ...
  </div>

  <!-- 图例（可选） -->
  <div class="legend">
    <div><span class="swatch" style="border-color:var(--blue);background:var(--bluebg)"></span> 库层</div>
    <div><span class="swatch" style="border-color:var(--orange);background:var(--orangebg)"></span> 服务层</div>
  </div>
</div>
```

### 3.4 CSS 基础类

```css
.customfig {
  background: #0d1117; border-radius: 12px; padding: 28px; margin: 18px 0;
  font-family: "SF Mono","Cascadia Code",monospace; font-size: 13px;
  line-height: 1.55; color: var(--text); border: 1px solid var(--border);
}
.layer {
  border: 2px solid var(--dim); border-radius: 8px;
  padding: 12px 14px; margin: 0 0 4px 0; background: #0d1117;
}
.layer-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 10px; gap: 10px;
}
.layer-label { font-weight: bold; font-size: 14px; }
.layer-sub   { color: var(--dim); font-size: 11px; }
.layer-body  { display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; }
.node {
  padding: 6px 12px; border-radius: 5px; font-size: 12px;
  display: inline-block; line-height: 1.4;
}
.node .note { font-size: 10px; opacity: .8; }
.arrow { text-align: center; color: var(--dim); margin: 2px 0; font-size: 11px; }
```

### 3.5 复杂布局扩展

当单层内有子分组（如"管理面 vs 数据面"并列）时，使用 flex 分栏：

```html
<div class="layer-split">
  <div class="subpanel panel-mgmt">
    <div class="panel-header">管理面</div>
    <div class="panel-tags"><span>功能项 A</span><span>功能项 B</span></div>
  </div>
  <div class="panel-bridge">
    <span class="bridge-arrow">◄──►</span>
    <span class="bridge-label">通信方式</span>
  </div>
  <div class="subpanel panel-data">
    <div class="panel-header">数据面</div>
    <div class="panel-tags"><span>功能项 C</span><span>功能项 D</span></div>
  </div>
</div>
```

当需要网格布局（如多列功能矩阵）时，使用 CSS Grid：

```css
.layer-body.grid-4 {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
}
```

## 4. `<template>` 注入机制

将自绘图放在 `<template>` 标签中，通过占位符注入 Markdown 渲染结果：

1. 在 Markdown 源文本中放置占位符：`<!-- FIGURE: fig-id -->`
2. 在 HTML 的 `<template id="fig-id">` 中定义图形
3. JS 渲染完成后，将占位符替换为 template 内容

```javascript
document.querySelectorAll('[data-figure]').forEach(el => {
  const tpl = document.getElementById(el.dataset.figure);
  if (tpl) el.replaceWith(tpl.content.cloneNode(true));
});
```

## 5. 文件命名

- 与源 Markdown 同名，扩展名改为 `.html`
- 放在与源文件相同的目录下
- 例：`architecture-design.md` → `architecture-design.html`

## 6. 不要做的事

- **不要**把所有图都降级为卡片——简单的 Mermaid 图保留 Mermaid
- **不要**使用外部 CSS 文件——所有样式内嵌
- **不要**使用外部图片——图表全部用 HTML/CSS 绘制
- **不要**生成后不检查——生成后应提醒用户在浏览器中预览确认
