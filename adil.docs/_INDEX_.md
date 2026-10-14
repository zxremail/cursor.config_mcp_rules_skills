# adil.docs 索引

本目录记录本机 Cursor 配置与工具约定。提要有多条时用 `<br>` 分行。

| <span style="color:#C9A0FF">文档</span> | <span style="color:#C9A0FF">说明</span> | <span style="color:#C9A0FF">提要</span> |
|------|------|------|
| [cursor-config-github-sync.md](cursor-config-github-sync.md) | 定时拉取 | Windows 计划任务 `CursorConfigGitSync` 每天 7:00 到 23:00 每小时快进拉取 `~/.cursor`。<br>远程是 `github` 的 `master`。脚本不自动提交、不自动推送。<br>工作区有未提交改动时跳过拉取。分叉或网络失败时本轮结束，不立即重试，等到下一个整点。<br>日志在 `ai-tracking/github-sync.log`。 |
