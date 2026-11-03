---
name: windows-no-tsd-writes
description: >-
  Avoid TSD (%TSD-Header) on Windows Cursor writes. Use when editing UNC/Samba
  (\\\\host\\share, 192.168.52.137), mapped drives, Windows local project files,
  or user mentions TSD, transparent encryption, Samba, or Explorer lock icons.
disable-model-invocation: true
---

# 避免 TSD 明文写入

TSD 头：`%TSD-Header-###%` → Linux 上 `file: data`，`scp` 到 VM 也可能带密文。**Skill 不能关公司策略，只约束 Agent 写法。**

脚本根目录：`$S = "$env:USERPROFILE\.cursor\skills\samba-plaintext-writes\scripts"`

## 规则

| 路径 | Write/StrReplace |
|------|------------------|
| `\\*`、映射盘、`//host/` | **禁止** → Remote SSH 改 Linux，或 `push_plaintext.ps1` |
| `C:\` / `D:\` 等本地盘 | 允许；**任务结束前**校验 |
| `~/…`（Remote SSH 会话） | 允许；Linux 上 `grep TSD-Header` 或 `file` |

- UNC **只读**（Read/Grep）可。
- **禁止** `scp`、**robocopy** 写 UNC 源码树。

## 校验（少占 tokens）

仅对**本次改过的路径**，任务结束前跑 **一次**：

```powershell
& "$S\verify_paths.ps1" -Path 'D:\a.py','D:\b.md'
# 或目录：& "$S\verify_paths.ps1" -Root 'D:\proj\src' -Include *.py,*.md,*.json,*.yaml,*.ps1,*.cmd
```

- 退出码 0：对话里 **只写一行**「TSD 校验通过（N 个文件）」。
- 退出码 1：**只列失败路径**，勿贴 `xxd`/文件全文。

## 失败时

1. 用 Agent 内存中的**正确 UTF-8 内容** → Shell 里 `Path.write_bytes(...)`，勿从磁盘 `read_text` 已 TSD 的文件。
2. 仍失败 → 改 **SSH 137** 存盘，或 `push_plaintext.ps1`。
3. 细节见 [reference.md](reference.md)（仅失败时再读）。

## 推送 Linux

```powershell
& "$S\push_plaintext.ps1" -UserHost USER@HOST -RemoteDir ~/target/dir  D:\local\file.py
```

## Token 纪律

- 不自动加载本 Skill；用户提 TSD/UNC/137 或 @windows-no-tsd-writes 时用。
- verify 输出不进入长解释；Linux 检查只用 `grep -rl TSD-Header DIR || echo OK` 一行。
