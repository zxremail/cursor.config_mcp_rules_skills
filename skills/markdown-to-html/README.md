# md2html — Markdown 转独立 HTML



## 目录 • md2html — Markdown 转独立 HTML

- <a id="toc-pos-1-安装"></a>[1. 安装](#1-安装)
- <a id="toc-pos-2-用法"></a>[2. 用法](#2-用法)
- <a id="toc-pos-3-sidecar-约定customfig"></a>[3. Sidecar 约定（customfig）](#3-sidecar-约定customfig)
- <a id="toc-pos-4-frontmatter可选"></a>[4. Frontmatter（可选）](#4-frontmatter可选)
- <a id="toc-pos-5-示例"></a>[5. 示例](#5-示例)
- <a id="toc-pos-6-与-agent-工作流"></a>[6. 与 Agent 工作流](#6-与-agent-工作流)
  - <a id="toc-pos-61-阶段-a--基本-sidecar默认"></a>[6.1 阶段 A — 基本 sidecar（默认）](#61-阶段-a--基本-sidecar默认)
  - <a id="toc-pos-62-阶段-b--按需打磨用户点名时"></a>[6.2 阶段 B — 按需打磨（用户点名时）](#62-阶段-b--按需打磨用户点名时)

---

将 Markdown 转为可在浏览器中独立打开的深色主题 HTML 页面，实现 [SKILL.md](./SKILL.md) 中的规范。

**技术选型：Python**（CLI 与文件处理）；页面内仍使用 CDN 的 `marked.js` + `mermaid.js` 做客户端渲染。

## 1. 安装 <a id="1-安装"></a> <a href="#toc-pos-1-安装" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

**方式 A（有 pip）**

```bash
pip install -e ~/.cursor/skills/markdown-to-html
md2html build examples/sample.md
```

**方式 B（无 pip）**

```bash
~/.cursor/skills/markdown-to-html/bin/md2html build examples/sample.md
# 或
PYTHONPATH=~/.cursor/skills/markdown-to-html python3 -m md2html build examples/sample.md
```

## 2. 用法 <a id="2-用法"></a> <a href="#toc-pos-2-用法" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```bash
# 构建（输出与源文件同目录、同名 .html）
md2html build docs/architecture.md

# 指定 customfig sidecar 目录（默认：<stem>.figures/）
md2html build docs/architecture.md --figures docs/architecture.figures/

# 严格模式：应降级但缺少 sidecar、或引用了不存在的 fig-id 时失败
md2html build docs/architecture.md --strict-figures

# 构建后用浏览器打开
md2html build docs/architecture.md --open

# 仅分析 Mermaid 块是否建议降级
md2html analyze docs/architecture.md
```

## 3. Sidecar 约定（customfig） <a id="3-sidecar-约定customfig"></a> <a href="#toc-pos-3-sidecar-约定customfig" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

与 `architecture.md` 同级目录 `architecture.figures/`：

| 文件 | 作用 |
|------|------|
| `fig-id.html` | 生成 `<template id="fig-id">…</template>` |
| `mermaid-0.html` | 替换第 0 个应降级的 mermaid 块为 `customfig:mermaid-0` |
| `extra.css` | 追加到页面内嵌样式 |

Markdown 中引用方式：

```markdown
<!-- FIGURE: fig-id -->

或

```customfig:fig-id
```
```

## 4. Frontmatter（可选） <a id="4-frontmatter可选"></a> <a href="#toc-pos-4-frontmatter可选" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```yaml
---
title: 浏览器标题
sidebar_title: 侧栏主标题
sidebar_subtitle: 侧栏副标题（显示为橙色小字）
version: v1.0 · 2026-05-23
---
```

## 5. 示例 <a id="5-示例"></a> <a href="#toc-pos-5-示例" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```bash
md2html build examples/sample.md --open
```

## 6. 与 Agent 工作流 <a id="6-与-agent-工作流"></a> <a href="#toc-pos-6-与-agent-工作流" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

完整规范见 [SKILL.md](./SKILL.md) §7.5。摘要：

### 6.1 阶段 A — 基本 sidecar（默认） <a id="61-阶段-a--基本-sidecar默认"></a> <a href="#toc-pos-61-阶段-a--基本-sidecar默认" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

1. `md2html analyze doc.md` → 列出需降级的 `mermaid-N`
2. 为每个 N 写**可读即可**的 `doc.figures/mermaid-N.html`（不必一次打磨完美）
3. `md2html build doc.md` → 浏览器通读
4. 无降级块的文档直接 build，保留 Mermaid

### 6.2 阶段 B — 按需打磨（用户点名时） <a id="62-阶段-b--按需打磨用户点名时"></a> <a href="#toc-pos-62-阶段-b--按需打磨用户点名时" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

1. **只改** `doc.figures/mermaid-N.html` 一个文件
2. 对照原 Mermaid 源码与同节正文
3. `md2html build doc.md` → 只复查该图

**不要**在未要求时把全库 sidecar 都做到出版级。
