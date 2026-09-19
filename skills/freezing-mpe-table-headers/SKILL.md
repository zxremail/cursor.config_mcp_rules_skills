---
name: freezing-mpe-table-headers
description: >-
  Use when 用户在 Markdown Preview Enhanced (MPE) 里要求表格下拉时标题行保持显示、
  冻结/钉住表头，或抱怨 MPE 预览表头跟着滚走、导出 HTML 能钉预览不能钉、
  整页无法下滑、刷新预览无效、Customize CSS 不生效。
  Triggers: MPE, Markdown Preview Enhanced, .crossnote, style.less, head.html,
  crossnote[data-for=preview], Customize CSS, 预览无法下滑, 表头跟着表格滚。
---

# MPE 预览冻结表头

## Overview

Markdown Preview Enhanced 实时预览里，用**页面级** `th { position: sticky }`，不要内嵌滚动框。滚动必须留给预览视口；只解开内容容器的 `overflow`。

**REQUIRED BACKGROUND:** 钉 `th`、禁止 `overflow`+`max-height` 包一层，见 freezing-html-table-headers。本技能只管 MPE 预览壳。

## When to Use

- 用户明确用 MPE / Markdown Preview Enhanced
- 导出或独立 HTML 已能钉表头，MPE 预览不能
- 改完 CSS 后刷新预览仍无效
- 表头钉住后整页无法下滑

**不要用本技能：** 内置 Markdown 预览、md2html 独立 HTML（走 freezing-html-table-headers）。

## 必改文件（工作区优先，全局兜底）

| 路径 | 作用 |
|------|------|
| `<workspace>/.crossnote/style.less` | MPE 注入预览的主样式 |
| `<workspace>/.crossnote/head.html` | 写入 `<head>`，不被正文 DOMPurify 丢掉 |
| `~/.local/state/crossnote/style.less` | 命令面板 **Customize CSS (Global)** 写这里 |
| `~/.local/state/crossnote/head.html` | 全局 head 兜底 |

工作区文件优先于全局。两边都写同一套规则，避免「工作区改了、已打开的壳仍读全局」。

## 落地配方

把下面这段 **扁平 CSS**（不要 LESS 嵌套）写入 `style.less`；`head.html` 用同一段，外包 `<style id="mpe-sticky-table-header">`。表格 class 按文档替换（如 `capsule-table` / `sticky-head`）。

```css
/* 只解开内容容器。禁止 html/body overflow:hidden。 */
.preview-container .crossnote[data-for='preview'] {
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}
table.sticky-head {
  display: table !important;
  overflow: visible !important;
  border-collapse: separate !important;
  border-spacing: 0;
  width: 100%;
}
table.sticky-head thead th {
  position: sticky !important;
  top: 0 !important;
  z-index: 20;
  background: var(--panel, #161b22) !important;
  box-shadow: 0 1px 0 var(--border, #30363d);
}
```

`th` 背景必须不透明，盖住滚上来的正文。黑底表用该表自己的底色（例如 `#000`）。

## 三条硬规则

1. **禁止** `html, body { overflow: hidden }`（以及任何把整页锁死的 `overflow: hidden`）。sticky 仍失效时，去查预览内容容器，不要锁页面。这会让整个预览无法下滑。
2. **禁止**给表格外包 `overflow` + `max-height`。GitHub 主题的 `table { display:block; overflow:auto }` 必须用 `display:table; overflow:visible` 盖掉。
3. **改完必须关掉 MPE 预览标签再重新打开。** 不要只点刷新 / Reload Preview：`style.less` / `head.html` 写进预览壳，已打开的 webview **不重载外壳**。

## 为什么 `.md` 里的 `<style>` 不够

MPE 用 DOMPurify 丢掉正文里的 `<style>` 标签（`style=""` 属性会留）。即便留下，sticky 仍会挂在 `.preview-container .crossnote[data-for=preview]` 上——该节点默认 `overflow: auto` 且 `height: auto`，是一个**永不滚动的滚动祖先**，表头跟着表格一起走。只改表格、不解开这层 `overflow`，预览永远钉不住。

## 检查清单

- [ ] 写入工作区 `.crossnote/style.less` **和** `head.html`
- [ ] 需要时同步 `~/.local/state/crossnote/` 两份文件
- [ ] 只改 `.preview-container .crossnote[data-for=preview]`，没有 `html/body overflow:hidden`
- [ ] 表格 `display:table; overflow:visible`；sticky 在 `th` 上；不透明背景
- [ ] 无 `max-height` + `overflow` 包裹层
- [ ] 已关掉预览标签再打开（不是只刷新）
- [ ] 验证：整页仍能滚到底，表头钉在预览窗口顶部
