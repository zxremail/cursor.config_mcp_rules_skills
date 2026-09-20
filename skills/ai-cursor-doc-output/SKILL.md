---
name: ai-cursor-doc-output
description: >-
  Use when the workspace root contains an ai.cursor/ directory and the user
  asks to save, export, or generate explanatory Markdown or HTML (including
  md2html, sidecar .figures/, and HTML slides). Also use when choosing a
  default path for a new .md/.html, when tempted to write it to the repo root,
  docs/, or next to source for “方便打开”, or when moving an existing knowledge
  note so it sits beside a new HTML file. Triggers: 保存 markdown、导出 html、
  生成幻灯片、放到项目里、ai.cursor.
---

# ai.cursor 文档默认落点

工作区根存在目录 `ai.cursor/` 时，用户要求保存/导出的说明类 `.md` / `.html` 默认写入该知识库。

## 何时适用

- 工作区根下存在 **目录** `<workspace>/ai.cursor/`（只看根，不扫深层 `**/ai.cursor`）
- 用户要求保存、导出、生成说明文档、指南、架构说明、md2html、HTML 幻灯片

**不适用：** 项目 README、测试夹具、构建产物；用户未要求导出的源码旁文件；工作区路径本身叫 `ai.cursor` 但根下 **没有** `ai.cursor/` 子目录（例如本知识库仓库）。

## 优先级

1. 用户消息里的**显式路径**
2. 本规则
3. 「方便双击 / 赶时间以后再整理 / 和 html 放一起」**不能**把文件改写到仓库根

## 落点步骤

1. 知识库根 = `<workspace>/ai.cursor/`
2. **先 Read** `ai.cursor/_INDEX_.md`。没有则建最小三列表格（文档 | 说明 | 提要）
3. 索引里已有匹配分类 → 放入对应子目录
4. 没有匹配 → 按主题新建英文、小写、连字符子目录，并在索引**补一行**
5. basename 仍按 **`markdown-export`**（英文、小写、连字符）
6. HTML 与 sidecar `*.figures/` 与源 md **同目录**——同在知识库子目录内，不是同在仓库根
7. 落盘后走 **`markdown-knowledge-maintain`**（`md-toc` + 索引）

**例：** 索引已有 `software/`，用户要「LXI 调试指南」→ `ai.cursor/software/lxi-debugging.md`，html 为同目录 `lxi-debugging.html`，并给 `_INDEX_.md` 补行。

## 已有文件

原地更新。禁止为了和新 html/slides 放一起，把已有笔记搬出 `ai.cursor/`。

## 借口对照

| 借口 | 实际 |
|------|------|
| 根目录方便双击打开 | 浏览器能打开任意路径；默认仍是 `ai.cursor/<分类>/` |
| 赶时间，路径以后再整理 | 第一次就要写对；漏索引等于文档不可发现 |
| md 和 html 放同一文件夹更简单 | 对，但那一层是知识库子目录，不是仓库根 |
| 用户说「放到项目里」 | 项目里的默认位置是 `ai.cursor/` |

## 红旗 — 停下并改路径

- 准备写到 `<workspace>/foo.md`、`<workspace>/foo.html` 或 `docs/foo.md`
- 准备把已有 `ai.cursor/.../x.md` 移到仓库根
- 写了新说明文档但没改 `_INDEX_.md`
