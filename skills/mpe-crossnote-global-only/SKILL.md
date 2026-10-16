---
name: mpe-crossnote-global-only
description: >-
  Restricts Markdown Preview Enhanced .crossnote edits to the global config
  only. Use when customizing MPE preview CSS/JS, style.less, head.html,
  parser.js, config.js, Open Preview 目录/侧栏, Customize CSS, or any .crossnote
  path. Never create or edit a workspace .crossnote.
---

# MPE 只改全局 .crossnote

修改.crossnote只修改全局.crossnote，永不生成工作区.crossnote，永不修改工作区的.crossnote

## 只许写这些文件

按平台选**全局**目录（本机 Customize CSS/Html Head (Global) 打开的就是这份）：

| 平台 | 路径 |
|------|------|
| Linux / *nix | `$XDG_CONFIG_HOME/.crossnote`，否则 `~/.local/state/crossnote`（本机即 `/home/adil/.local/state/crossnote/`） |
| Windows | `%USERPROFILE%/.crossnote/` |

不要把 Linux 的全局配置写到 `~/.crossnote/`：本机 MPE 不读那里。

| 文件 | 用途 |
|------|------|
| `style.less` | 预览 CSS。命令面板 **Markdown Preview Enhanced: Customize CSS (Global)** |
| `head.html` | 注入 `<head>`。**Customize Preview Html Head (Global)** |
| `toc-level1-open.js` 等同目录 `.js` | 仅当 `head.html` 用 `<script src="文件名.js">` 引用时 |

禁止：`<workspace>/.crossnote/**`、`mkdir` 工作区 `.crossnote`、把全局文件复制进仓库。

工作区若已有 `.crossnote`：不要改、不要删；只告诉用户它会盖过全局。用户未明确要求前不要动它。

## 保存后生效

1. 在编辑器里保存刚改的**全局** `style.less` 或 `head.html`（只存 `.md` 不会刷新外壳 CSS）。
2. 仍旧：关 MPE 预览再 **Open Preview**，或 `Developer: Reload Window`。

## 侧栏目录宽度

默认用 `--sidebar-toc-width`。不要给 `.md-sidebar-toc` 写 `width: … !important`，否则拖条失效。MPE 会把上次宽度记在 `localStorage` 的 `crossnote.sidebarTocWidth`。
