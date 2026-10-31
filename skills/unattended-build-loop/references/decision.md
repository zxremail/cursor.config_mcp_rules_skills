# decision.json

Supervisor never parses Agent chat prose. Only this file is an input.

| Field | Allowed | Notes |
|-------|---------|--------|
| `action` | `patch`, `retry`, `human`, `abort` | `patch` requires `files_changed` |
| `fingerprint` | string | Copy from `extract/meta` / state when present |
| `summary` | one sentence | Copied to Feishu / `notify.log` |
| `files_changed` | repo-relative paths | Must be inside the task allowlist |
| `human_options` | strings | Buttons; default 继续重编 / 中止 |
| `risk` | `low`, `medium`, `high` | `high` upgrades `patch` to `human` |

When `agent_enabled` is false, Supervisor maps `preclass=agent` to
`wait_human` / `agent_disabled`. When true, it launches a one-shot local Agent
that must write this file. Invalid JSON, empty patch, or `risk: high` become
`wait_human`. Auto `patch`/`retry` does not send Feishu.
