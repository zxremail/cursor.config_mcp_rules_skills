---
name: unattended-build-loop
description: >-
  Runs the local unattended compile supervisor and the short-lived fix Agent
  protocol. Use when the user mentions 无人值守编译, unattended-build, Supervisor,
  ub start, q.build-rk3399-yocto.sh, or overnight Yocto/kernel builds that
  should auto-classify errors and only ping Feishu at human gates.
  Also use when adding a new platform task YAML (RK3588 Buildroot, another SDK).
---

# Unattended build loop

Compile is owned by the **Supervisor** at `~/loop.AI/unattended-build` (`./x.sh` / `./ub`).
This directory is a multi-repo hub. RK3399 Yocto is the current task set; RK3588
Buildroot is a new `tasks/*.yaml`, not a second Supervisor. The Agent is short-lived
and must not sit through the compile (`bitbake`, `make`, or the task `start` command).

## Supervisor commands

长期入口是 `./x.sh`。先 `cd ~/loop.AI/unattended-build`，再 `./x.sh`（中文菜单）。不必记完整 task id。

```bash
cd ~/loop.AI/unattended-build
./x.sh               # 长期入口：用法 + 菜单（按 tasks/*.yaml 生成）
./ub kernel          # 当前 YAML 简称：编 RK3399 内核
./ub all             # 当前 YAML 简称：编 RK3399 完整镜像
./status
./board              # http://127.0.0.1:8765/
./stop
./install-shortcuts  # 可选：链到 ~/.local/bin/x.sh
```

旧写法仍可用：`./ub start rk3399-yocto-kernel`、`./ub kernel`、`./ub all`。无参数的 `./ub` 与 `./x.sh` 相同。说明见仓库 `README.md`。

`ub start` / `ub serve` also bind a localhost board (port 8765) unless `--no-board`.
看板左侧列出 `runs/` 下全部历史，点选即可回顾该次日志与 Agent 分析；`?run=<id>` 可收藏。仅当前正在 `building`/`agent` 的 run 每 2 秒拉 `/api`。中间栏仍展示该次 `agent-history.jsonl`。无历史时回退 `decision.json` 的 summary。
While `status=building`, Feishu heartbeat uses `notify.heartbeat_minutes` (default 45).

Task YAML lives in `~/loop.AI/unattended-build/tasks/`. Runs live in
`~/loop.AI/unattended-build/runs/<id>/` (`state.json`, `build.log`, `extract/`, `notify.log`).

`rk3399-yocto-*` 默认 `agent_enabled: true`。`preclass=agent` 时 Supervisor 调用
Cursor SDK 本地 Agent（请求 `composer-2.5` 且 Fast=`false`；实际模型写入 `agent-model.json`，不因 Fast 停回路；`cwd` 为任务 YAML 的 `cwd`，超时 15 分钟）
写 `decision.json`。无 `CURSOR_API_KEY` 或未安装 `cursor-sdk` 时降级为
`wait_human` / `agent_unavailable`。自动 `patch`/`retry` **不发飞书**，只写
`notify.log`。Fill `notify.chat_id` (`oc_...`) 只在 success / wait_human / failed /
heartbeat。飞书正文附带尝试次数、错误指纹、Agent 摘要、改动文件、请求/实际模型。
`selftest-*` 保持 `agent_enabled: false`。

## When invoked as the fix Agent

Supervisor has already extracted the failure. Do not re-run the compile.

1. Read only `extract/` in the current run dir plus allowlisted source files.
2. Write `decision.json` in that run dir, then stop.

```json
{
  "action": "patch | retry | human | abort",
  "fingerprint": "kind|subject|normalized-error",
  "summary": "one sentence for Feishu",
  "files_changed": [],
  "human_options": ["继续重编", "中止"],
  "risk": "low | medium | high"
}
```

### Hard rules

- Do not Read or Grep `build.log` in full. Do not search build output trees
  (`yocto/build/tmp`, `sstate-cache`, `output`, `dl`).
- Do not patch files under those output trees or `.git`.
- If the error path is an unpack (`tmp/work/.../git/` or Buildroot `output/build/`),
  find the in-tree source. If you cannot, `action: human`.
- Do not run the task `start` / `restart` command, nor `agent.forbid_commands`.
- Do not `git commit` or `git push`.
- One fingerprint per run. Same fingerprint already auto-fixed 3 times → `abort`.
- `risk: high` must be `human` even if a patch is prepared.
- Empty `files_changed` with `action: patch` is invalid; use `human`.

Write allowlist and denylist come from the current task YAML. Empty `allow_write`
means do not patch (`action: human`).

See [references/decision.md](references/decision.md) for field semantics.
