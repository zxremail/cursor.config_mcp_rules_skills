# md-toc — Markdown 目录补充工具

为 `.md` 文档插入或**仅补充**「## 目录」小节（GitHub / VS Code / Cursor 预览锚点兼容）。

## 安装路径

```
~/.cursor/tools/md-toc/
├── md-toc          # shell 入口（可加 PATH）
├── md-toc.py
├── md_toc_slug.py
└── github_slugger_regex.pattern
```

## 用法

```bash
~/.cursor/tools/md-toc/md-toc path/to/doc.md
python3 ~/.cursor/tools/md-toc/md-toc.py --dry-run doc.md
```

## 行为

| 情况 | 行为 |
|------|------|
| 无 `## 目录` | 在 `#` 标题后新建完整目录 |
| 已有目录 | **保留**现有条目与顺序，只追加正文中未列入的章节 |
| 目录已齐全 | 不写文件，退出 0 |

## 可选：加入 PATH

```bash
ln -sf ~/.cursor/tools/md-toc/md-toc ~/.local/bin/md-toc
```
