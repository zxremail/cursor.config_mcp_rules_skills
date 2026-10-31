---
name: unattended-build-loop
description: >-
  Runs the local unattended compile supervisor and the short-lived fix Agent
  protocol. Use when the user mentions 无人值守编译, unattended-build, Supervisor,
  ub start, q.build-rk3399-yocto.sh, or overnight Yocto/kernel builds that
  should auto-classify errors and only ping Feishu at human gates.
---

# Unattended build loop

Compile is owned by the **Supervisor** at `~/unattended-build` (`./ub`). The
Agent is short-lived and must not sit through bitbake.

## Supervisor commands

```bash
~/unattended-build/ub start selftest-fail
~/unattended-build/ub start rk3399-yocto-kernel
~/unattended-build/ub status
~/unattended-build/ub board          # http://127.0.0.1:8765/
~/unattended-build/ub stop
```

`ub start` / `ub serve` also bind a localhost board (port 8765) unless `--no-board`.
While `status=building`, Feishu heartbeat uses `notify.heartbeat_minutes` (default 45).

Task YAML lives in `~/unattended-build/tasks/`. Runs live in
`~/unattended-build/runs/<id>/` (`state.json`, `build.log`, `extract/`, `notify.log`).

Phase 1: `agent_enabled: false`. Failures that would be AUTO become `wait_human`
with reason `agent_disabled`. Fill `notify.chat_id` (`oc_...`) to send Feishu;
empty chat id only appends `notify.log`.

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

- Do not Read or Grep `build.log` in full. Do not search `yocto/build/tmp`.
- Do not patch files under `yocto/build/tmp`, `sstate-cache`, `output`, `.git`.
- If the error path is a tmp unpack (`tmp/work/.../git/`), find the recipe or
  in-tree source. If you cannot, `action: human`.
- Do not run `q.build-rk3399-yocto.sh`, `./build.sh`, `bitbake`, or `cleanall`.
- Do not `git commit` or `git push`.
- One fingerprint per run. Same fingerprint already auto-fixed 3 times → `abort`.
- `risk: high` must be `human` even if a patch is prepared.
- Empty `files_changed` with `action: patch` is invalid; use `human`.

Default write allowlist: `kernel/`, `u-boot/`, `yocto/meta*`, `device/rockchip/`,
`z.scripts/`. Task YAML may narrow this.

See [references/decision.md](references/decision.md) for field semantics.
