---
name: designated-knowledge-index
description: >-
  Teaches agents to use a repository's **designated** Markdown knowledge directory
  (path from project rules, README, AGENTS.md, user message—not a fixed folder
  name): open that directory's index first (often `_INDEX_.md`), use 说明/提要
  columns to pick docs, then read linked notes. Index: prefer a 3-column table
  (文档|说明|提要); split 提要 segments with HTML `<br>` inside cells. Use when the user names a notes
  path, asks to maintain a knowledge index, or project docs define a doc root.
---

# 仓库内「指定目录」笔记 / 知识库

## 如何确定目录

- **知识库根目录**须由本仓库或用户**明确指定**，没有全局固定路径名；可能是 `docs/notes/`、`internal/`、`ai.cursor/` 等任意约定目录。
- 来源优先级（从高到低）：**用户当前消息中的路径** → **仓库规则/说明**（如 `AGENTS.md`、README、`.cursor/rules` 等写明的路径）→ **在仓库内搜索**常见索引（如 `**/_INDEX_.md`）并结合上下文推断。仍无法确定时，**先向用户确认路径**，勿臆造目录名。

## 必须先做

1. 记知识库根为 **`<根>`**（即上述指定目录）。若 **`<根>/_INDEX_.md`** 存在（或项目约定的其它索引文件名）：**先 Read 该索引**，再按表内链接 Read 其它 `.md`；不要跳过索引、在 `<根>` 下凭猜打开文件。
2. 若 `<根>` 存在但无索引文件：列出该目录（及子目录）下 `.md`，优先读总览类文件名或用户点名的文档。

## 索引表怎么用（存在索引时）

- 索引路径以项目约定为准；常见为 `<根>/_INDEX_.md`。
- **展示形式（推荐）**：用 Markdown **三列表格** — **文档** | **说明** | **提要**（表头以项目约定为准，常见即此三列）。
- **说明**：短标签（几字到十来字），扫读分类。
- **提要**：较长说明，含侧重点与检索词；可拆成多条「一句一义」，以清晰扫读为目标。
- **提要如何在表格里换行**：标准 Markdown **表格单元格内不能直接插入换行**；若要把提要写成多段，在 **提要** 列内使用 **HTML `<br>`** 分段（常见预览器 / GitHub 均支持）。可在表上方用 **blockquote** 一行说明「提要多条时用 `<br>`」，方便后续维护者照抄格式。
- **与分块词条的取舍**：若用户明确要求「仍以表格展示」，则保留表格，**不要**为换行而改成分块标题 + 列表；提要清晰度用 **`<br>` 分段** 解决。
- 先据此选题，再读正文核对。

## 与仓库真源的关系

- 指定目录下多为人类整理笔记，**正误与领域依项目而异**；回答须与仓库内**源码、配置、脚本、日志**等可验证材料对照，冲突时以可验证真源为准。

## 维护索引（用户让你改笔记时）

- 在 `<根>` 下新增或重命名 `.md` 时，在索引表格中 **补一行**（或按项目约定插入到合适分类），**同时**维护 **说明**（短标签）与 **提要**（较长说明），两列分工明确。
- **提要** 若有多条并列信息：在表格中仍以 **一行一格** 呈现，格内用 **`<br>`** 连接各段，保持「一条 `<br>` 前为一条提要」的维护习惯，避免整格挤成一长句。

## 阅读顺序

- **优先遵从该索引内**写明的总览文或「建议阅读顺序」；若无，则按任务关键词匹配 **说明** 列，再读 **提要** 与正文。
