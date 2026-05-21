---
name: markdown-knowledge-maintain
description: >-
  Maintains Markdown knowledge-base notes after edits: supplements in-document TOC
  via md-toc CLI (never regenerates existing 目录), and syncs <root>/_INDEX_.md per
  designated-knowledge-index. Use when creating or editing .md notes in a knowledge
  directory, adding/renaming sections, or when the user mentions 目录、TOC、索引、_INDEX_.
---

# Markdown 知识库文档维护



## 目录

<a id="toc-pos-1-补充文档内目录cli优先于手写"></a>
- [1. 补充文档内目录（CLI，优先于手写）](#1-补充文档内目录cli优先于手写)
<a id="toc-pos-2-同步-_index_md"></a>
- [2. 同步 `_INDEX_.md`](#2-同步-_index_md)
<a id="toc-pos-3-推荐执行顺序"></a>
- [3. 推荐执行顺序](#3-推荐执行顺序)
<a id="toc-pos-4-自动-hook用户级"></a>
- [4. 自动 Hook（用户级）](#4-自动-hook用户级)
<a id="toc-pos-5-何时可跳过"></a>
- [5. 何时可跳过](#5-何时可跳过)
<a id="toc-pos-工具位置"></a>
- [工具位置](#工具位置)

---

在**指定知识库目录**内创建或修改任意 `.md` 后，除完成用户任务外，**必须**执行下列维护（无需用户再次提醒）。

## 1. 补充文档内目录（CLI，优先于手写） <a href="#toc-pos-1-补充文档内目录cli优先于手写" style="float:right;text-decoration:none">↑</a>

```bash
~/.cursor/tools/md-toc/md-toc -- "<改动的.md绝对或相对路径>"
# 入口按 python3 版本自动选择：>=3.7 用 md-toc.py，否则用 md-toc-batch.py
# 亦可：python3 ~/.cursor/tools/md-toc/md-toc.py -- "<path>"
```

| 规则 | 说明 |
|------|------|
| 已有 `## 目录` | **只追加**正文中未列入的章节；禁止整段重写、禁止打乱已有条目顺序 |
| 无目录 | CLI 在 `#` 文档标题后新建目录 |
| 无新增标题 | 命令输出「无变化」即可，勿用 Agent 重复生成目录 |

可选检查：`--dry-run` 预览将补充的条目；`--check` 用于 CI。

**双向跳转**：CLI 为每条目录加 `toc-pos-*` 锚点；章节标题**同行右侧** **↑**（`float:right`），回到目录**对应条目**。

**禁止**：为省事先读全文手写目录块；与 `github-slugger` 不一致的锚点。

## 2. 同步 `_INDEX_.md` <a href="#toc-pos-2-同步-_index_md" style="float:right;text-decoration:none">↑</a>

同一知识库根目录 `<根>` 下若存在 `_INDEX_.md`（或其它项目约定索引名），按 **`designated-knowledge-index`** skill：

- 新增 / 重命名 `.md` → 在索引表补一行，维护 **说明** 与 **提要**
- 仅改正文、未改文档定位 → 视情况更新 **提要** 列
- 先 Read 索引再改，避免漏项或重复行

## 3. 推荐执行顺序 <a href="#toc-pos-3-推荐执行顺序" style="float:right;text-decoration:none">↑</a>

1. 完成用户对正文的修改  
2. 运行 `md-toc.py` 补充目录  
3. 更新 `<根>/_INDEX_.md`（若适用）  
4. 若目录或索引有变，在回复中**一句话**说明（例如「已补充目录 2 条、已更新索引」）

## 4. 自动 Hook（用户级） <a href="#toc-pos-4-自动-hook用户级" style="float:right;text-decoration:none">↑</a>

`~/.cursor/hooks.json` 已在 `afterFileEdit` 注册 `supplement-md-toc.sh`，Agent 写入 `.md` 后会尝试自动跑目录补充。  
**索引表仍需 Agent 维护**（Hook 不修改 `_INDEX_.md`）。

## 5. 何时可跳过 <a href="#toc-pos-5-何时可跳过" style="float:right;text-decoration:none">↑</a>

- 仅修改代码块 / 表格数据 / 错别字，且**未增删改** `##`～`###` 标题
- 用户明确说「不要动目录/索引」
- 文件不在知识库场景（普通 README 等）：仅当用户要求时再跑 md-toc

## 工具位置 <a href="#toc-pos-工具位置" style="float:right;text-decoration:none">↑</a>

| 组件 | 路径 |
|------|------|
| CLI（推荐入口） | `~/.cursor/tools/md-toc/md-toc`（自动选择实现） |
| 完整实现 | `~/.cursor/tools/md-toc/md-toc.py`（Python >= 3.7） |
| 兼容实现 | `~/.cursor/tools/md-toc/md-toc-batch.py`（Python 3.5/3.6） |
| 说明 | `~/.cursor/tools/md-toc/README.md` |
