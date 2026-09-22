---
name: lark-cli-skills-sync
description: >-
  After updating lark-cli, copies official lark-* Agent Skills from
  ~/.agents/skills to ~/.cursor/skills so Cursor actually loads them.
  Use when running lark-cli update, npx skills add larksuite/cli,
  npm/pnpm global install of @larksuite/cli, when _notice.skills appears,
  or when the user mentions 同步 lark skill、~/.agents/skills、~/.cursor/skills.
---

# lark-cli Skills 同步到 Cursor

Cursor 优先加载 `~/.cursor/skills/` 的同名 skill。`lark-cli update` 只更新 `~/.agents/skills/lark-*`，不同步则 Cursor 继续用旧副本。

真实源目录是 **`~/.agents/skills`**（复数 `agents`），不是 `~/.agent/skills`。

## 必须同步的时机

升级 CLI 或官方 Skills **成功之后**立刻跑脚本，不要只告诉用户去拷、也不要手写 `cp -r`：

```bash
bash ~/.cursor/skills/lark-cli-skills-sync/scripts/sync.sh
```

触发命令包括：

- `lark-cli update`（不要在仅 `--check` 时同步）
- `npx skills add larksuite/cli -y -g`
- `npm install -g @larksuite/cli` / `pnpm add -g @larksuite/cli`
- 输出里出现 `_notice.skills` 或用户明确要求同步 lark skill

`lark-cli update` 是 high-risk-write：先按 `lark-shared` 取得用户同意，升级成功后再同步。

## 脚本行为

- 只同步源侧名为 `lark*` 的**目录**到 `~/.cursor/skills/<同名>/`（`rsync -a --delete`）。
- **不删除** Cursor 独有目录（例如 `lark-whiteboard-cli`）。
- **不**整目录对拷 `~/.agents/skills`，以免冲掉个人 skill。

## 本机 Hook

用户级 `afterShellExecution` hook 会在匹配的升级命令成功后自动跑同一脚本。Agent 仍应在升级成功后主动执行脚本，避免 hook 未加载时漏同步。

向用户汇报时只说同步了多少个官方 `lark-*`、以及未改动的 Cursor 独有项。
