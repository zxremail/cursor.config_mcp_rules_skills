---
name: freezing-html-table-headers
description: >-
  Use when 用户要求表格下拉时标题行保持显示、冻结/钉住表头、sticky header，
  或抱怨生成的表格像内嵌滚动框、小窗口、iframe、太丑。
  适用于 Markdown 内嵌 HTML 表、md2html 独立 HTML、doc.figures/extra.css。
  Triggers: 冻结表头, 标题行始终显示, sticky thead, 内嵌表格, overflow max-height.
---

# HTML 表格冻结标题行

## Overview

长表在**整页滚动**时钉住 `<th>`，不要再包一层内部滚动框。

**REQUIRED BACKGROUND:** 由 md2html 生成独立 HTML 时，用 markdown-to-html 的 sidecar `extra.css`。

## When to Use

- 文档里有一张很长的表，下拉时希望列名一直可见
- 用户说「标题行保持显示 / 冻结表头 / sticky」
- 用户说现有效果「像内嵌表格、小窗口、太丑」

**不要用本模式**（仅当用户明确要求「表格自己有滚动条、固定高度」时才用 `overflow` + `max-height`）：

- 仪表盘卡片、预览窗、必须限制高度的控件

## 默认做法（页面级 sticky）

1. 给 `<table>` 加 class（如 `sticky-head`），**不要**外包 `overflow` 容器。
2. 样式写在 `doc.figures/extra.css`（md2html 会打进页面）；Markdown 预览可在每个 `<th>` 上再写同等内联样式。
3. 钉 `th`，不要钉 `thead` / `tr`（Safari 才稳）。
4. `border-collapse: separate`；`th` 用不透明背景。
5. 改完后 `md2html build doc.md`。

```html
<table class="sticky-head">
<thead>
<tr>
  <th>列 A</th>
  <th>列 B</th>
</tr>
</thead>
<tbody><!-- 原有行，不要包 overflow 容器 --></tbody>
</table>
```

```css
article table.sticky-head {
  border-collapse: separate !important;
  border-spacing: 0;
  width: 100%;
}
article table.sticky-head thead th {
  position: sticky;
  top: 0;
  z-index: 3;
  background: var(--panel, #161b22) !important;
  box-shadow: 0 1px 0 var(--border, #30363d);
}
```

表头背景必须盖得住正文行。黑底色字表用该表自己的底色（例如 `#000`），不要改成半透明。

页面已有顶栏时，把 `top: 0` 改成顶栏高度。md2html 默认无顶栏，用 `0`。

## 禁止：内嵌滚动框

```html
<!-- 错误：像 iframe，双滚动条 -->
<div style="overflow:auto;max-height:75vh">
  <table>...</table>
</div>
```

祖先上的 `overflow: auto | scroll | hidden`（含只有 `overflow-x: auto`）会把 sticky 锁在盒子里，或看起来像内嵌表。横向溢出让单元格换行，或接受整页横向滚动，不要用外包 `overflow-x: auto` 来「顺便」冻结表头。

## 常见错误

| 做法 | 结果 |
|------|------|
| `overflow` + `max-height` 包一层 | 内嵌小窗口，丑 |
| 祖先 `overflow-x: auto` | 页面级 sticky 失效 |
| `border-collapse: collapse` | 部分浏览器 sticky 失效或边框错乱 |
| `th` 背景透明 | 正文行从标题下透出来 |
| `position: sticky` 写在 `thead`/`tr` | Safari 不钉 |

## 检查清单

- [ ] 无 `max-height` + `overflow` 包裹层
- [ ] sticky 在 `th` 上，`top` 对齐视口（或顶栏）
- [ ] `border-collapse: separate; border-spacing: 0`
- [ ] `th` 不透明背景 + 底部分隔
- [ ] md2html 页面已重建
