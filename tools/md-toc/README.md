# md-toc — Markdown 目录补充工具



## 目录 • md-toc — Markdown 目录补充工具

- [1. 安装路径](#1-安装路径)
- [2. 用法](#2-用法)
- [3. 行为](#3-行为)
- [4. 可选 HTML 导航（默认关闭）](#4-可选-html-导航默认关闭)
- [5. 可选：加入 PATH](#5-可选加入-path)

---

为 `.md` 文档插入或**仅补充**「## 目录」小节（GitHub / VS Code / Cursor 预览锚点兼容）。**默认输出纯 Markdown 列表**，不插入 HTML 锚点或回链。

## 1. 安装路径

```
~/.cursor/tools/md-toc/
├── md-toc              # shell 入口（按 Python 版本自动选择实现，推荐）
├── md-toc.py           # 完整实现（需 Python >= 3.7）
├── md-toc-batch.py     # 兼容实现（Python 3.5/3.6）
├── md_toc_slug.py
└── github_slugger_regex.pattern
```

## 2. 用法

```bash
# 推荐：统一入口（Python >= 3.7 用 md-toc.py，否则用 md-toc-batch.py）
~/.cursor/tools/md-toc/md-toc path/to/doc.md
cd /path/to/knowledge-dir && ~/.cursor/tools/md-toc/md-toc    # 无参数：处理当前目录 *.md

# 直接调用（高级）
python3 ~/.cursor/tools/md-toc/md-toc.py --dry-run doc.md
python3 ~/.cursor/tools/md-toc/md-toc-batch.py doc.md

# 可选：HTML 双向跳转（默认关闭）
~/.cursor/tools/md-toc/md-toc --back-links doc.md
~/.cursor/tools/md-toc/md-toc --index-link doc.md
```

**版本选择**：`md-toc` 脚本检测 `python3` 版本；3.7 以下自动走 `md-toc-batch.py`，行为与默认参数下的 `md-toc.py` 对齐（h2–h3、目录补充、纯 Markdown 目录）。

## 3. 行为

| 情况 | 行为 |
|------|------|
| 无 `## 目录` | 在 `#` 标题后新建完整目录 |
| 已有目录 | **保留**现有条目与顺序，只追加正文中未列入的章节 |
| 目录已齐全 | 不写文件，退出 0 |
| 标题无 `1.` / `2.1` 编号 | **默认**：先给正文 h2–h3 补序号，再生成与标题一致的目录 |
| 标题已手写编号 | 默认不再叠号；仅目录加号用 `--numbered`；禁止改正文序号用 `--no-heading-numbers` |
| **目录标题格式** | 知识库场景下标题行写为 `## 目录 • <文档标题>`，`<文档标题>` 取自首行 `# …`；详见 **`markdown-knowledge-maintain`** skill |
| **HTML 导航** | **默认关闭**；对已有文档会自动**移除**旧版 `toc-pos-*` / `md-toc-back` / `md-toc-index` HTML |

## 4. 可选 HTML 导航（默认关闭）

仅在显式传参时启用：

| 参数 | 说明 |
|------|------|
| `--back-links` | 目录项加 `toc-pos-*` 锚点；章节标题同行右侧 ↑ 回链（`md-toc-back`） |
| `--index-link` | 目录标题行尾链到 `_INDEX_.md`（`md-toc-index` SVG 箭头） |
| `--nav-hint` | 目录块顶部插入一行简短用法提示 |

已废弃（默认行为已等价）：`--no-back-links`、`--no-index-link`（保留兼容，无效果）。

## 5. 可选：加入 PATH

```bash
ln -sf ~/.cursor/tools/md-toc/md-toc ~/.local/bin/md-toc
```
