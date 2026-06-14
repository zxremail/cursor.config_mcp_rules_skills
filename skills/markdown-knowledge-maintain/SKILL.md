---
name: markdown-knowledge-maintain
description: >-
  Maintains Markdown knowledge-base notes after edits: supplements in-document TOC
  via md-toc CLI (never regenerates existing 目录), formats TOC heading as
  「目录 • <文档标题>」, and syncs <root>/_INDEX_.md per designated-knowledge-index.
  Use when creating or editing .md notes in a knowledge directory, adding/renaming
  sections, or when the user mentions 目录、TOC、索引、_INDEX_.
---

# Markdown 知识库文档维护

## 目录 • Markdown 知识库文档维护

- [1. 补充文档内目录（CLI，优先于手写）](#1-补充文档内目录cli优先于手写)
  - [1.1 目录 • 文档标题](#11-目录--文档标题)
- [2. 同步 `_INDEX_.md`](#2-同步-_index_md)
- [3. 推荐执行顺序](#3-推荐执行顺序)
- [4. 自动 Hook（用户级）](#4-自动-hook用户级)
- [5. 何时可跳过](#5-何时可跳过)
- [6. 工具位置](#6-工具位置)

---

在**指定知识库目录**内创建或修改任意 `.md` 后，除完成用户任务外，**必须**执行下列维护（无需用户再次提醒）。

## 1. 补充文档内目录（CLI，优先于手写）

```bash
~/.cursor/tools/md-toc/md-toc -- "<改动的.md绝对或相对路径>"
# 默认：正文标题无 1./2.1 时先补序号再生成目录；标题已有编号则不叠号
# 仅目录加号、不改正文：加 --numbered；禁止补正文序号：加 --no-heading-numbers
# 入口按 python3 版本自动选择：>=3.7 用 md-toc.py，否则用 md-toc-batch.py
# 亦可：python3 ~/.cursor/tools/md-toc/md-toc.py -- "<path>"
```

| 规则 | 说明 |
|------|------|
| 已有 `## 目录` | **只追加**正文中未列入的章节；禁止整段重写、禁止打乱已有条目顺序 |
| 无目录 | CLI 在 `#` 文档标题后新建目录 |
| 无新增标题 | 命令输出「无变化」即可，勿用 Agent 重复生成目录 |
| **目录标题格式** | 见下节「目录 • 文档标题」 |
| **纯 Markdown** | **禁止**在目录/章节中插入 HTML 锚点、↑ 回链或 `_INDEX_.md` SVG 箭头；默认 CLI 已满足，勿手写 `<a id=…>` / `md-toc-back` |

可选检查：`--dry-run` 预览将补充的条目；`--check` 用于 CI。

**禁止**：为省事先读全文手写目录块；与 `github-slugger` 不一致的锚点；向 `.md` 写入 md-toc 旧版 HTML 导航（`toc-pos-*`、`md-toc-back`、`md-toc-index`）。

若用户**明确要求** HTML 双向跳转（罕见），才加 `--back-links`；要求目录行链到索引才加 `--index-link`。

### 1.1 目录 • 文档标题

知识库 `.md` 的目录小节标题行须写为：

```markdown
## 目录 • <文档标题>
```

| 要点 | 说明 |
|------|------|
| `<文档标题>` | 取自正文首行 `# …` 的 H1 标题，与文档主标题**完全一致** |
| 分隔符 | 半角空格 + `•` + 半角空格（` • `） |
| 索引入口 | 通过 `_INDEX_.md` 表格导航即可；**不要**在目录标题行追加 HTML/SVG 链到索引 |
| 标题变更 | 修改 `#` 文档标题后，**同步更新**目录行中的 `<文档标题>` 部分 |
| 示例 | `## 目录 • 专题 T1：NI PXIe 是否采用 AMP / OpenAMP 架构` |

新建或维护目录时：先跑 `md-toc`，再检查目录标题是否为 `目录 • <当前 # 标题>`；若 CLI 尚未写入标题后缀，由 Agent **补全**，勿改回纯 `## 目录`。

## 2. 同步 `_INDEX_.md`

同一知识库根目录 `<根>` 下若存在 `_INDEX_.md`（或其它项目约定索引名），按 **`designated-knowledge-index`** skill：

- 新增 / 重命名 `.md` → 在索引表补一行，维护 **说明** 与 **提要**
- 仅改正文、未改文档定位 → 视情况更新 **提要** 列
- 先 Read 索引再改，避免漏项或重复行

## 3. 推荐执行顺序

1. 完成用户对正文的修改  
2. 运行 `md-toc` 补充目录，并确认目录标题为 `目录 • <# 标题>`（无 HTML 导航）  
3. 更新 `<根>/_INDEX_.md`（若适用）  
4. 若目录或索引有变，在回复中**一句话**说明（例如「已补充目录 2 条、已更新索引」）

## 4. 自动 Hook（用户级）

若存在 `~/.cursor/hooks.json` 并在 `afterFileEdit` 注册 `supplement-md-toc.sh`，直接调用默认入口即可（会自动补正文序号并生成纯 Markdown 目录）：

```bash
~/.cursor/tools/md-toc/md-toc -- "$FILE"
```

**索引表仍需 Agent 维护**（Hook 不修改 `_INDEX_.md`）。

## 5. 何时可跳过

- 仅修改代码块 / 表格数据 / 错别字，且**未增删改** `##`～`###` 标题
- 用户明确说「不要动目录/索引」
- 文件不在知识库场景（普通 README 等）：仅当用户要求时再跑 md-toc

## 6. 工具位置

| 组件 | 路径 |
|------|------|
| CLI（推荐入口） | `~/.cursor/tools/md-toc/md-toc`（自动选择实现） |
| 完整实现 | `~/.cursor/tools/md-toc/md-toc.py`（Python >= 3.7） |
| 兼容实现 | `~/.cursor/tools/md-toc/md-toc-batch.py`（Python 3.5/3.6） |
| 说明 | `~/.cursor/tools/md-toc/README.md` |
