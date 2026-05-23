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



## 目录

- <a id="toc-pos-1-补充文档内目录cli优先于手写"></a>[1. 补充文档内目录（CLI，优先于手写）](#1-补充文档内目录cli优先于手写)
- <a id="toc-pos-1-补充文档内目录cli优先于手写"></a>[2. 1. 补充文档内目录（CLI，优先于手写）](#1-补充文档内目录cli优先于手写)
  - <a id="toc-pos-目录--文档标题"></a>[2.1. 目录 • 文档标题](#目录--文档标题)
- <a id="toc-pos-2-同步-_index_md"></a>[3. 2. 同步 `_INDEX_.md`](#2-同步-_index_md)
- <a id="toc-pos-3-推荐执行顺序"></a>[4. 3. 推荐执行顺序](#3-推荐执行顺序)
- <a id="toc-pos-4-自动-hook用户级"></a>[5. 4. 自动 Hook（用户级）](#4-自动-hook用户级)
- <a id="toc-pos-5-何时可跳过"></a>[6. 5. 何时可跳过](#5-何时可跳过)
- <a id="toc-pos-2-同步-_index_md"></a>[7. 同步 `_INDEX_.md`](#2-同步-_index_md)
- <a id="toc-pos-3-推荐执行顺序"></a>[8. 推荐执行顺序](#3-推荐执行顺序)
- <a id="toc-pos-4-自动-hook用户级"></a>[9. 自动 Hook（用户级）](#4-自动-hook用户级)
- <a id="toc-pos-5-何时可跳过"></a>[10. 何时可跳过](#5-何时可跳过)
- <a id="toc-pos-工具位置"></a>[11. 工具位置](#工具位置)

---

在**指定知识库目录**内创建或修改任意 `.md` 后，除完成用户任务外，**必须**执行下列维护（无需用户再次提醒）。

## 1. 补充文档内目录（CLI，优先于手写） <a id="1-补充文档内目录cli优先于手写"></a> <a href="#toc-pos-1-补充文档内目录cli优先于手写" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

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

可选检查：`--dry-run` 预览将补充的条目；`--check` 用于 CI。

**双向跳转**：CLI 为每条目录加 `toc-pos-*` 锚点；章节标题**同行右侧** **↑**（`float:right`），回到目录**对应条目**。

**禁止**：为省事先读全文手写目录块；与 `github-slugger` 不一致的锚点。

### 目录 • 文档标题 <a id="目录--文档标题"></a> <a href="#toc-pos-目录--文档标题" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

知识库 `.md` 的目录小节标题行须写为：

```markdown
## 目录 • <文档标题> <a href="…/_INDEX_.md" class="md-toc-index" …>…</a>
```

| 要点 | 说明 |
|------|------|
| `<文档标题>` | 取自正文首行 `# …` 的 H1 标题，与文档主标题**完全一致** |
| 分隔符 | 半角空格 + `•` + 半角空格（` • `） |
| 索引箭头 | 行尾保留指向 `_INDEX_.md` 的 SVG 箭头（`class="md-toc-index"`）；相对路径按文件深度计算（如 `docs/` 下为 `../_INDEX_.md`） |
| 标题变更 | 修改 `#` 文档标题后，**同步更新**目录行中的 `<文档标题>` 部分 |
| 示例 | `## 目录 • 专题 T1：NI PXIe 是否采用 AMP / OpenAMP 架构 <a href="../_INDEX_.md" …>` |

新建或维护目录时：先跑 `md-toc`，再检查目录标题是否为 `目录 • <当前 # 标题>`；若 CLI 尚未写入标题后缀，由 Agent **补全**，勿改回纯 `## 目录`。

## 2. 同步 `_INDEX_.md` <a id="2-同步-_index_md"></a> <a href="#toc-pos-2-同步-_index_md" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

同一知识库根目录 `<根>` 下若存在 `_INDEX_.md`（或其它项目约定索引名），按 **`designated-knowledge-index`** skill：

- 新增 / 重命名 `.md` → 在索引表补一行，维护 **说明** 与 **提要**
- 仅改正文、未改文档定位 → 视情况更新 **提要** 列
- 先 Read 索引再改，避免漏项或重复行

## 3. 推荐执行顺序 <a id="3-推荐执行顺序"></a> <a href="#toc-pos-3-推荐执行顺序" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

1. 完成用户对正文的修改  
2. 运行 `md-toc.py` 补充目录，并确认目录标题为 `目录 • <# 标题>`  
3. 更新 `<根>/_INDEX_.md`（若适用）  
4. 若目录或索引有变，在回复中**一句话**说明（例如「已补充目录 2 条、已更新索引」）

## 4. 自动 Hook（用户级） <a id="4-自动-hook用户级"></a> <a href="#toc-pos-4-自动-hook用户级" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

若存在 `~/.cursor/hooks.json` 并在 `afterFileEdit` 注册 `supplement-md-toc.sh`，直接调用默认入口即可（会自动补正文序号并生成目录）：

```bash
~/.cursor/tools/md-toc/md-toc -- "$FILE"
```

**索引表仍需 Agent 维护**（Hook 不修改 `_INDEX_.md`）。

## 5. 何时可跳过 <a id="5-何时可跳过"></a> <a href="#toc-pos-5-何时可跳过" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

- 仅修改代码块 / 表格数据 / 错别字，且**未增删改** `##`～`###` 标题
- 用户明确说「不要动目录/索引」
- 文件不在知识库场景（普通 README 等）：仅当用户要求时再跑 md-toc

## 工具位置 <a id="工具位置"></a> <a href="#toc-pos-工具位置" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

| 组件 | 路径 |
|------|------|
| CLI（推荐入口） | `~/.cursor/tools/md-toc/md-toc`（自动选择实现） |
| 完整实现 | `~/.cursor/tools/md-toc/md-toc.py`（Python >= 3.7） |
| 兼容实现 | `~/.cursor/tools/md-toc/md-toc-batch.py`（Python 3.5/3.6） |
| 说明 | `~/.cursor/tools/md-toc/README.md` |
