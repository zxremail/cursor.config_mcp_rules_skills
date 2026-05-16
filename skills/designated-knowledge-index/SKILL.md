---
name: designated-knowledge-index
description: >-
  Teaches agents to use a repository's **designated** Markdown knowledge directory
  (path from project rules, README, AGENTS.md, user message—not a fixed folder
  name): open that directory's index first (often `_INDEX_.md`), use 说明/提要
  columns to pick docs, then read linked notes. Use when the user names a notes
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
- 常见三列：**文档** | **说明** | **提要**（以该索引实际表头为准）。
- **说明**：短标签（几字到十来字），扫读分类；**提要**：较长说明，含侧重点与检索词；先据此选题，再读正文核对。

## 与仓库真源的关系

- 指定目录下多为人类整理笔记，**正误与领域依项目而异**；回答须与仓库内**源码、配置、脚本、日志**等可验证材料对照，冲突时以可验证真源为准。

## 维护索引（用户让你改笔记时）

- 在 `<根>` 下新增或重命名 `.md` 时，在索引的合适分类中补一行，**同时**维护 **说明**（短标签）与 **提要**（较长说明），两列分工明确。

## 阅读顺序

- **优先遵从该索引内**写明的总览文或「建议阅读顺序」；若无，则按任务关键词匹配 **说明** 列，再读 **提要** 与正文。
