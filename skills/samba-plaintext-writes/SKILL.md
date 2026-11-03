---
name: samba-plaintext-writes
description: >-
  Prevents TSD/corporate transparent encryption when creating or editing files
  on Samba, UNC, or NFS paths from Windows-hosted Cursor. Use when workspace or
  tool paths look like \\\\host\\share, //host/, mapped network drives, VMware
  guest homes (e.g. 192.168.52.137), or when Linux file(1) shows data or
  %TSD-Header-###% on saved files.
---

# Samba / UNC 明文写入（避免 TSD）

Windows 上 Cursor Agent 通过 **SMB/UNC** 直接 `Write` / `StrReplace` 保存到 Linux（Samba）时，公司终端安全软件可能写入 **TSD 透明加密**（`%TSD-Header-###%`）。Linux 上 `file` 显示 `data`，Python/脚本无法执行；Windows 读同一共享可能仍像明文。

**硬规则：Agent 不得通过 UNC/Samba 路径创建或修改应在 Linux 上保持明文的文件。**

## 路径识别（命中任一则适用本 skill）

- Windows UNC：`\\hostname\...`、`\\192.168.x.x\...`
- 已映射网络驱动器上的工程（如 `Z:\...` 对应 `\\192.168.52.137\adil\...`）
- 工具参数里出现 `//host/share/...` 且写入目标是远程 Linux 家目录/代码树
- 用户说明文件在 VMware 虚拟机、137、Samba 共享上

**只读**：用 Read/Grep 看 UNC 上现有内容通常可以；**禁止**对这类路径做 Write/StrReplace/Delete 写入。

## 推荐做法（按优先级）

### 1. Remote SSH（首选）

- 用 **Cursor Remote SSH** 打开 Linux 主机（如 `adil@192.168.52.137`）。
- 在 VM **本地路径**编辑（如 `~/loop.AI/...`），不要用 Windows 工作区指向 `\\192.168.52.137\...` 作为写入根目录。
- 改完后在 Linux 上验证：`file path` 应为 `Python script` / `UTF-8 text`，不是 `data`。

### 2. 必须从 Windows 推送文件时

**不要用 `scp`**（本环境可能仍上传 TSD 包）。

用 **SSH + base64 管道**（明文在 Linux 侧落盘）：

```powershell
# 示例：推送单个文件到 137
$py = "$env:LocalAppData\Programs\Python\Python313\python.exe"
& $py -c @"
import base64, pathlib, subprocess
p = pathlib.Path(r'LOCAL\path\to\file.py')
data = p.read_bytes()
subprocess.run(
    ['ssh', 'USER@HOST', 'base64 -d > ~/target/path/file.py'],
    input=base64.b64encode(data),
    check=True,
)
"@
```

或在 Linux 上：`git pull` / 在 VM 内直接编辑。

本 skill 目录下的 [`scripts/push_plaintext.ps1`](scripts/push_plaintext.ps1) 可封装上述逻辑（Agent 可调用）。

### 3. 仓库布局

- **源码真源**放在 Linux（如 `~/loop.AI/unattended-build`、`unattended-download`）。
- Windows 只跑必须本机的步骤（USB、`upgrade_tool`、本地 `server.py`），或通过 **只读 UNC** 读固件；不要长期用 Windows Cursor  workspace 绑定 UNC 源码树做 Agent 修改。

## 改后验证（Linux 上执行）

```bash
file ~/path/to/edited.py
head -c 20 ~/path/to/edited.py | xxd   # 应以 23 21 7f 等可见文本开头，而非 25 54 53 44 (%TSD)
grep -rl 'TSD-Header' ~/loop.AI/ 2>/dev/null && echo '仍有 TSD 文件' || echo OK
```

## Agent 决策表

| 任务 | Windows + UNC 路径 | SSH / Linux 本地 |
|------|--------------------|------------------|
| 读代码、搜关键字 | 允许 | 允许 |
| 新建/修改/删除源码 | **禁止** | **允许** |
| 批量迁移目录 | robocopy 到 UNC **有风险**；优先 VM 内 git/rsync 或 base64 推送 | 推荐 |
| 用户 insist 改 UNC | 说明 TSD 风险，改走 SSH 或 push 脚本 | — |

## 与用户沟通

若用户要在 `\\192.168.52.137\...` 上改文件：简短说明 **Explorer 锁/加密图标 + Linux 上 file=data** 同源问题，建议 **SSH 137** 或 **push_plaintext.ps1**，不要继续在 UNC 上 Agent 写入。
