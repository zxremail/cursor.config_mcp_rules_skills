# md-toc — Markdown 目录补充工具



## 目录

<a id="toc-pos-安装路径"></a>
- [安装路径](#安装路径)
<a id="toc-pos-用法"></a>
- [用法](#用法)
<a id="toc-pos-行为"></a>
- [行为](#行为)
<a id="toc-pos-双向跳转"></a>
- [双向跳转（↑）](#双向跳转)
<a id="toc-pos-可选加入-path"></a>
- [可选：加入 PATH](#可选加入-path)

---

为 `.md` 文档插入或**仅补充**「## 目录」小节（GitHub / VS Code / Cursor 预览锚点兼容）。

## 安装路径 <a href="#toc-pos-安装路径" style="float:right;text-decoration:none">↑</a>

```
~/.cursor/tools/md-toc/
├── md-toc          # shell 入口（可加 PATH）
├── md-toc.py
├── md_toc_slug.py
└── github_slugger_regex.pattern
```

## 用法 <a href="#toc-pos-用法" style="float:right;text-decoration:none">↑</a>

```bash
~/.cursor/tools/md-toc/md-toc path/to/doc.md
python3 ~/.cursor/tools/md-toc/md-toc.py --dry-run doc.md
```

## 行为 <a href="#toc-pos-行为" style="float:right;text-decoration:none">↑</a>

| 情况 | 行为 |
|------|------|
| 无 `## 目录` | 在 `#` 标题后新建完整目录 |
| 已有目录 | **保留**现有条目与顺序，只追加正文中未列入的章节 |
| 目录已齐全 | 不写文件，退出 0 |

## 双向跳转（↑） <a href="#toc-pos-双向跳转" style="float:right;text-decoration:none">↑</a>

- 每条目录项前有 `<a id="toc-pos-..."></a>`，标记该链接在目录中的位置
- 章节标题**同一行右侧**浮动 ↑：`<a href="#toc-pos-..." style="float:right">↑</a>`
- 需要目录块顶部提示时：`--nav-hint`
- 不需要回链时：`--no-back-links`

## 可选：加入 PATH <a href="#toc-pos-可选加入-path" style="float:right;text-decoration:none">↑</a>

```bash
ln -sf ~/.cursor/tools/md-toc/md-toc ~/.local/bin/md-toc
```
