---
name: ai-cursor-knowledge-index
description: >-
  Teaches agents to use a repository's `ai.cursor/` Markdown knowledge base
  when present: open `_INDEX_.md` first, use the 说明/提要 columns to pick docs,
  then read linked notes before inventing paths. Use when the workspace contains
  `ai.cursor/` or `ai.cursor/_INDEX_.md`, or the user mentions project notes,
  ai.cursor docs, or maintaining the index.
---

# 任意仓库中的 `ai.cursor/` 笔记库

## 必须先做

1. 若仓库中存在 **`ai.cursor/_INDEX_.md`**：**先 Read 该文件**，再按需 Read 索引中指向的其它 `.md`；不要跳过索引、凭猜测打开 `ai.cursor/` 下的文件名。
2. 若仅有 **`ai.cursor/`** 而无 `_INDEX_.md`：列出目录内 `.md`，优先阅读文件名或用户点名的文档；仍避免假设未读过的内容。

## 索引表怎么用（存在 `_INDEX_.md` 时）

- 常见表头三列：**文档** | **说明** | **提要**（具体措辞以该仓库索引为准）。
- **说明**：短标签（几字到十来字），用于扫读分类。
- **提要**：较长说明，含侧重点与检索词；回答用户时先据此选题，再打开正文核对细节。

## 与仓库真源的关系

- `ai.cursor/` 多为人类整理的笔记，**领域与对错因项目而异**；回答须与当前仓库内的**源码、配置、脚本、日志**等可验证材料对照，冲突时以可验证真源为准，笔记作入口与语境。

## 维护（用户让你改笔记或索引时）

- 在 `ai.cursor/` 新增或重命名 `.md`（通常排除 `_INDEX_.md` 自指）时，在 `_INDEX_.md` 的合适分类中补一行，**同时**维护 **说明**（短标签）与 **提要**（较长说明），两列分工明确、勿把长文塞进短标签列。

## 阅读顺序

- **优先遵从本仓库 `_INDEX_.md` 内写明的总览文或「建议阅读顺序」**；若索引未写，则按用户任务关键词在 **说明** 列中匹配标签，再读对应 **提要** 与正文。
