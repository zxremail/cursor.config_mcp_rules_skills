---
name: samba-no-tsd-writes
description: >-
  Auto-enforces plain (non-TSD) writes on Samba, UNC, and mapped network paths
  (\\\\host\\share, e.g. 192.168.52.137). Use whenever workspace or edits target
  network paths, VMware guest shares, or Linux homes via SMB. For Windows local
  disks (C:\, D:\), apply no-TSD verify/fix only when the user explicitly asks
  (no tsd, 避免 TSD, transparent encryption, @samba-no-tsd-writes local).
disable-model-invocation: false
---

# Samba 自动 no-TSD；Windows 本地按需

TSD 头：`%TSD-Header-###%`。Skill **不能**关闭公司策略。

脚本：`$S = "$env:USERPROFILE\.cursor\skills\samba-plaintext-writes\scripts"`

## A. 始终自动（Samba / UNC / 映射盘）

**禁止**对下列路径 `Write` / `StrReplace` / `Delete`（Read/Grep 只读可以）：

- `\\hostname\...`、`\\192.168.x.x\...`
- 映射盘（实质 UNC，如 `Z:\` → `\\192.168.52.137\...`）
- 工具参数里的 `//host/share/...` 且目标在 Linux 源码树

**必须**改用：

1. **Cursor Remote SSH** 编辑 VM 本地路径（如 `~/loop.AI/...`），或  
2. `push_plaintext.ps1`（**禁止 scp**）、**禁止 robocopy** 写 UNC 源码。

涉及 137 时，改完后可在 Linux **一行**检查：`grep -rl TSD-Header ~/loop.AI 2>/dev/null || echo OK`（勿贴文件内容）。

## B. 仅当用户明确要求（Windows 本地 C:\ / D:\ …）

用户说出 **no tsd / 避免 TSD / 不要 TSD 加密** 等，或点名 **Windows 本地也要 no tsd** 时，才：

1. 任务结束前对**本次改过的本地文件**跑一次：  
   `& "$S\verify_paths.ps1" -Path ...` 或 `-Root ...`
2. 失败：用内存中的正确 UTF-8 → Shell `write_bytes` 覆盖；勿把 TSD 文件读进对话。  
3. 对话里 **只报一行**校验结果。

**未明确要求时**：Windows 本地路径 **不要**自动 verify、不要自动 `write_bytes` 修复。

细节见 [reference.md](reference.md)（B 节失败时再读）。

## 推送 Linux（UNC 禁止写时的替代）

```powershell
& "$S\push_plaintext.ps1" -UserHost USER@HOST -RemoteDir ~/dir  D:\local\file.py
```

## Token

- A 节：不写 UNC，一般不产生大段文件内容。  
- B 节：仅用户点名时跑 verify；禁止 xxd/全文进 chat。
