# md-toc — Markdown 目录补充工具



## 目录

- <a id="toc-pos-安装路径"></a>[安装路径](#安装路径)
- <a id="toc-pos-用法"></a>[用法](#用法)
- <a id="toc-pos-行为"></a>[行为](#行为)
- <a id="toc-pos-双向跳转"></a>[双向跳转（↑）](#双向跳转)
- <a id="toc-pos-可选加入-path"></a>[可选：加入 PATH](#可选加入-path)

---

为 `.md` 文档插入或**仅补充**「## 目录」小节（GitHub / VS Code / Cursor 预览锚点兼容）。

## 安装路径 <a id="安装路径"></a> <a href="#toc-pos-安装路径" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```
~/.cursor/tools/md-toc/
├── md-toc              # shell 入口（按 Python 版本自动选择实现，推荐）
├── md-toc.py           # 完整实现（需 Python >= 3.7）
├── md-toc-batch.py     # 兼容实现（Python 3.5/3.6）
├── md_toc_slug.py
└── github_slugger_regex.pattern
```

## 用法 <a id="用法"></a> <a href="#toc-pos-用法" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```bash
# 推荐：统一入口（Python >= 3.7 用 md-toc.py，否则用 md-toc-batch.py）
~/.cursor/tools/md-toc/md-toc path/to/doc.md
cd /path/to/knowledge-dir && ~/.cursor/tools/md-toc/md-toc    # 无参数：处理当前目录 *.md

# 直接调用（高级）
python3 ~/.cursor/tools/md-toc/md-toc.py --dry-run doc.md
python3 ~/.cursor/tools/md-toc/md-toc-batch.py doc.md
```

**版本选择**：`md-toc` 脚本检测 `python3` 版本；3.7 以下自动走 `md-toc-batch.py`，行为与默认参数下的 `md-toc.py` 对齐（h2–h3、目录补充、↑ 回链、`_INDEX_.md` 链接）。

## 行为 <a id="行为"></a> <a href="#toc-pos-行为" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

| 情况 | 行为 |
|------|------|
| 无 `## 目录` | 在 `#` 标题后新建完整目录 |
| 已有目录 | **保留**现有条目与顺序，只追加正文中未列入的章节 |
| 目录已齐全 | 不写文件，退出 0 |

## 双向跳转（↑） <a id="双向跳转"></a> <a href="#toc-pos-双向跳转" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

- 每条目录项前有 `<a id="toc-pos-..."></a>`，标记该链接在目录中的位置
- 章节标题**同一行右侧**浮动弧形向上箭头（SVG，`md-toc-back`）
- **`## 目录` 标题行右侧**：同风格箭头指向同目录下的 `_INDEX_.md`（仅当该文件存在；`--no-index-link` 可关闭）
- 需要目录块顶部提示时：`--nav-hint`
- 不需要回链时：`--no-back-links`

## 可选：加入 PATH <a id="可选加入-path"></a> <a href="#toc-pos-可选加入-path" class="md-toc-back" style="float:right;text-decoration:none;color:#5c6370"><svg xmlns="http://www.w3.org/2000/svg" width="10.5pt" height="10.5pt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-0.15em" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></a>

```bash
ln -sf ~/.cursor/tools/md-toc/md-toc ~/.local/bin/md-toc
```
