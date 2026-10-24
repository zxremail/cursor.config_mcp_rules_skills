# adil.docs 索引

本目录记录本机 Cursor 配置与工具约定。提要有多条时用 `<br>` 分行。

| <span style="color:#C9A0FF">文档</span> | <span style="color:#C9A0FF">说明</span> | <span style="color:#C9A0FF">提要</span> |
|------|------|------|
| [cursor-config-github-sync.md](cursor-config-github-sync.md) | 定时拉取 | Windows 计划任务 `CursorConfigGitSync` 每天 7:00 到 23:00 每小时快进拉取 `~/.cursor`。<br>远程是 `github` 的 `master`。脚本不自动提交、不自动推送。<br>工作区有未提交改动时跳过拉取。分叉、网络失败或卡住超过 1 分钟时本轮结束，不立即重试，等到下一个整点。<br>日志在 `ai-tracking/github-sync.log`。 |
| [mpe-crossnote-load-priority.md](mpe-crossnote-load-priority.md) | MPE 配置路径 | Windows 全局目录是 `%USERPROFILE%\.crossnote\`。<br>Linux 未设 `XDG_CONFIG_HOME` 时用 `~/.local/state/crossnote`；设了则用 `$XDG_CONFIG_HOME/crossnote`。Linux 的 `~/.crossnote/` 默认不读。<br>工作区 `.crossnote` 多数键盖过全局；`style.less` 是拼接。本机只改全局，不要新建工作区目录。 |
| [cursor-html-live-preview.md](cursor-html-live-preview.md) | HTML 预览 | SSH 远程里用 Live Preview 预览 HTML，快捷键是 `Ctrl+Shift+V`。<br>预览在当前编辑组整页打开，不左右分屏。<br>远程 `keybindings.json` 不生效，按键由本地扩展 `html-preview-keybinding` 贡献。<br>改过 Live Preview 的 `ViewColumn`；升级扩展后要再改一次。 |
