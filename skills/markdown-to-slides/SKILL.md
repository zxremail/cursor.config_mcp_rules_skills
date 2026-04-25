---
name: markdown-to-slides
description: >-
  将 Markdown 内容或用户描述转换为全屏深色主题 HTML 幻灯片演示文稿（单文件、零依赖）。
  支持封面页、内容页、对比页、数据页、总结页等多种布局，内置卡片、KPI、
  芯片列表、药丸标签、表格、维度网格等组件。支持 Mermaid 图表、键盘翻页、进度条。
  Use when the user asks to create slides, presentations, or mentions
  "生成幻灯片", "做 PPT", "做演示", "转幻灯片", "slides", "presentation",
  "HTML 幻灯片", "全屏演示", "slide deck".
---

# Markdown 转 HTML 幻灯片

将内容转换为可在浏览器中全屏展示的深色科技风 HTML 幻灯片。单文件、零依赖（CDN 引用 Mermaid 除外）。

---

## 1. 工作流

```text
Step 1: 需求澄清
  - 主题、受众、页数（推荐 8–15 页）
  - 是否需要 Mermaid 图表
  - 是否有品牌标识（logo 文字 / 颜色）

Step 2: 生成大纲 → 用户确认
  - 每页：标题 + 要点 + 布局类型
  - 确认后开始生成 HTML

Step 3: 生成 HTML
  - 读取模板参考：references/slide-template.html
  - 按大纲逐页填充 <section class="slide">
  - 更新页码和进度条宽度

Step 4: 交付
  - 保存到与内容相关的路径，扩展名 .html
  - 提醒用户在浏览器中打开预览
```

## 2. HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>演示标题</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>/* 内嵌全部样式 — 见配色体系 + 组件样式 */</style>
</head>
<body>
  <div class="stage" id="stage">
    <section class="slide active"><!-- 第 1 页 --></section>
    <section class="slide"><!-- 第 2 页 --></section>
    <!-- ... -->
  </div>
  <div class="nav">
    <button id="prev" title="上一页 ←">‹</button>
    <button id="next" title="下一页 →">›</button>
  </div>
  <script>/* 翻页 + Mermaid 初始化 */</script>
</body>
</html>
```

## 3. 配色体系（深色科技风）

```css
:root {
  --bg0: #0a0e1a;        /* 主背景 */
  --bg1: #101529;        /* 渐变终点 */
  --bg2: #1a2140;        /* 次级背景 */
  --fg:  #e6edf7;        /* 主文字 */
  --muted: #8aa0c8;      /* 次级文字 */
  --accent: #35d3ff;     /* 主强调色 · 蓝 */
  --accent2: #7b5cff;    /* 副强调色 · 紫 */
  --warn: #ffb454;       /* 警告 · 橙 */
  --ok:   #5af0a8;       /* 正面 · 绿 */
  --danger: #ff5f7a;     /* 危险 · 红 */
  --line: rgba(255,255,255,0.08);
  --card: rgba(255,255,255,0.04);
}
```

每页 `.slide` 背景使用双层 radial-gradient + linear-gradient 营造光晕效果。

## 4. 页面类型与布局

### 4.1 封面页（Cover）

居中大标题 + 副标题 + 标签胶囊。用 `.cover` 容器 + `h1` 渐变文字。

```html
<section class="slide active">
  <div class="hdr"><!-- 品牌 + 页码 --></div>
  <div class="cover">
    <div>
      <div class="tag">副标题文字</div>
      <h1>主标题</h1>
      <div class="meta">
        <span>标签 1</span><span>标签 2</span>
      </div>
    </div>
  </div>
  <div class="footer"><span>脚注</span><span>01 / N</span></div>
  <div class="pbar"><i style="width:10%"></i></div>
</section>
```

### 4.2 内容页（双栏）

左右两栏，每栏内放 `.card` 卡片，用于对比、并列、图文。

```html
<div class="content">
  <div class="col">
    <div class="card"><h3>标题</h3><ul class="chips">...</ul></div>
  </div>
  <div class="col">
    <div class="card"><h3>标题</h3><ul class="chips">...</ul></div>
  </div>
</div>
```

### 4.3 数据页（KPI + 表格）

上方 KPI 指标行，下方数据表格。

```html
<div class="grid3">
  <div class="card kpi"><div class="v">42</div><div class="l">指标名</div></div>
  <!-- 更多 KPI -->
</div>
<div class="card"><table class="m">...</table></div>
```

### 4.4 维度网格页

`.dims` 容器 + `.dim` 卡片，每个维度显示编号 + 名称 + 描述。

### 4.5 总结/收束页

`.stack` 三栏百分比拆分 + 底部总结框。

## 5. 组件库

### 5.1 卡片（.card）

基础容器。`.card.tight` 减少内边距。可添加彩色背景和边框：

```html
<div class="card" style="background: rgba(90,240,168,0.06); border-color: rgba(90,240,168,0.3);">
  <div class="label">标签</div>
  <h3 style="color: var(--ok);">卡片标题</h3>
  <!-- 内容 -->
</div>
```

### 5.2 芯片列表（ul.chips）

带发光圆点的列表项。通过 class 切换颜色：

| class | 颜色 | 语义 |
|-------|------|------|
| (默认) | `--accent` 蓝 | 中性信息 |
| `.ok` | `--ok` 绿 | 正面 / 新增 |
| `.warn` | `--warn` 橙 | 现状 / 警告 |
| `.danger` | `--danger` 红 | 风险 / 问题 |
| `.purple` | `#b9a8ff` 紫 | 特殊 / AI |

```html
<ul class="chips">
  <li class="ok">正面要点</li>
  <li class="warn">现状描述</li>
  <li class="danger">风险项</li>
</ul>
```

### 5.3 药丸标签（.pill）

行内胶囊。颜色变体同 chips。

```html
<div class="pill-row">
  <span class="pill ok">标签 A</span>
  <span class="pill warn">标签 B</span>
</div>
```

### 5.4 KPI 指标（.kpi）

大号渐变数字 + 下方说明文字。

### 5.5 表格（table.m）

紧凑暗色表格。`th` 大写字母间距，`td` 可用 `.sf` / `.ok` / `.warn` / `.purple` 着色。

### 5.6 维度卡片（.dim）

带编号的特性卡片。`.dim.ai` 变体使用紫色主题。

### 5.7 演进行（.evo-row）

多列网格行，用于对照表。`.evo-row.head` 作表头，`.mag` 列右对齐。

### 5.8 栈式百分比（.stack > .col-stack）

三等分百分比展示。`.col-stack.a` 绿 / `.b` 蓝 / `.c` 紫。

## 6. 页面通用结构

每页 `<section class="slide">` 内：

```text
┌─ .hdr ─────────────────────────────────────┐
│  .brand (logo + name)         .page (标签)  │
├─────────────────────────────────────────────┤
│  h2 标题                                    │
│  .subtitle 副标题                            │
├─ .content ──────────────────────────────────┤
│  .col          .col                         │
│   .card         .card                       │
│   .card         .card                       │
├─ .footer ───────────────────────────────────┤
│  脚注                           页码         │
├─ .pbar ─────────────────────────────────────┤
│  <i style="width:XX%">                      │
└─────────────────────────────────────────────┘
```

## 7. 翻页 JS

```javascript
const slides = document.querySelectorAll('.slide');
let cur = 0;
function go(i) {
  cur = (i + slides.length) % slides.length;
  slides.forEach((s, k) => s.classList.toggle('active', k === cur));
}
document.getElementById('next').onclick = () => go(cur + 1);
document.getElementById('prev').onclick = () => go(cur - 1);
window.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') go(cur + 1);
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') go(cur - 1);
  else if (e.key === 'Home') go(0);
  else if (e.key === 'End') go(slides.length - 1);
});
```

## 8. Mermaid 集成

有 Mermaid 图表时在 `<head>` 引入 CDN，并在 `<script>` 中初始化：

```javascript
mermaid.initialize({
  startOnLoad: false, securityLevel: 'loose', theme: 'base',
  themeVariables: {
    background: '#0a0e1a', primaryColor: '#1a2140',
    primaryTextColor: '#e6edf7', primaryBorderColor: '#35d3ff',
    lineColor: '#8aa0c8', secondaryColor: '#101529',
    tertiaryColor: '#101529', fontSize: '12px', fontFamily: 'inherit'
  },
  flowchart: { curve: 'basis', padding: 12, htmlLabels: true, useMaxWidth: false }
});
```

没有 Mermaid 图表时省略 CDN 引用和初始化代码。

## 9. 品牌栏（.hdr）

每页顶部统一放置品牌标识：

```html
<div class="hdr">
  <div class="brand">
    <div class="logo">R</div>
    <div class="name"><b>项目名</b> · 章节</div>
  </div>
  <div class="page">右侧标签</div>
</div>
```

logo 内放单个大写字母，渐变背景自动生成。

## 10. 进度条

每页底部 `.pbar > i` 的 `width` 按 `页码 / 总页数 * 100%` 设置。

## 11. 文件命名

- 与内容主题相关，英文小写，连字符分隔，`.html` 扩展名
- 例：`rxie-evolution-from-axie.html`、`product-roadmap-2026.html`

## 12. 不要做的事

- **不要**使用外部 CSS / JS 文件（CDN 除外）
- **不要**使用外部图片 — 图表用 HTML/CSS/Mermaid 绘制
- **不要**在幻灯片中放过多文字 — 每页信息密度要低，留白充分
- **不要**超过 15 页 — 建议 8–12 页
- **不要**漏掉翻页导航 JS 和进度条

## 13. 完整模板参考

生成前**必须**先读取完整模板以获取精确的 CSS：

- [slide-template.html](references/slide-template.html) — 包含全部 CSS 类和 JS 的可运行空白模板
