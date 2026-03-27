---
name: remote-debug-rigol-ssh
description: >-
  Default SSH user, identity file, and legacy algorithm flags for Rigol remote
  debugging. Use when the user mentions IP, hostname, SSH, RK3399, 3399 平台,
  跳板, or 连设备. Uses root + ssh-rsa compatibility options for RK3399/3399
  platform; rigol + ~/.ssh/id_rsa otherwise; retry with ssh-rsa options if
  negotiation fails.
---

# 远程调试 SSH（默认用户与密钥）

## 何时生效

用户**给出或提到**用于远程访问/远程调试的 IP 或主机名，且**未另行说明**用户名、密钥路径或其他认证方式时，按本节处理。

## 身份文件（两种情况相同）

一律使用**当前机器环境**下的私钥：

`~/.ssh/id_rsa`

命令中写为：`-i ~/.ssh/id_rsa`（或 `IdentityFile ~/.ssh/id_rsa`）。

## 用户名（按是否 RK3399 / 3399 平台）

| 条件 | SSH 用户 |
|------|----------|
| 用户**明确**说明远程主机是 **RK3399** 或 **3399 平台**（如「RK3399」「3399 平台」「3399平台」、上下文明确指该平台设备） | `root` |
| 其他情况（默认） | `rigol` |

**判定**：须为**明确**表述；仅出现数字「3399」但语义不清时，仍按默认 `rigol`，除非用户补充说明是 3399 / RK3399 平台。

## RK3399 / 3399 平台：旧版 ssh-rsa（默认附带）

嵌入式侧常仅提供 **`ssh-rsa` 主机密钥**，新版 OpenSSH 默认会拒绝协商，报错类似：

`no matching host key type found. Their offer: ssh-rsa`

对 **RK3399 / 3399 平台**（即使用 **`root`** 的这类目标），生成 `ssh` / `scp` / `sftp` 命令时**默认附带**下列选项（与 `-i` 一并放在命令前部即可）：

```text
-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa
```

**完整模板（3399 / RK3399）：**

```bash
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i ~/.ssh/id_rsa root@<IP或主机名>
```

`scp`、`rsync -e "ssh ..."` 等需在 **ssh 侧**带上相同 `-o`（`scp` 可用 `-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa`）。

## 非 3399（默认 rigol）

**模板：**

```bash
ssh -i ~/.ssh/id_rsa rigol@<IP或主机名>
```

**若仍出现**上述 `ssh-rsa` / `no matching host key` 类错误，再**补加**与 3399 相同的两个 `-o`，不强行假设所有 rigol 主机都需要（多数新主机用 ed25519 等即可直连）。

## 代理行为小结

1. 先按平台选对用户；**3399 / RK3399 → root + 默认附带 ssh-rsa 两选项**；否则 `rigol`、无额外 `-o`。
2. **用户覆盖**：若用户指定其他用户、密钥、或要求不用 `ssh-rsa`，以当次说明为准。
3. **勿默认密码**：密钥失败时再请用户说明密码或其他密钥。

## 示例

- 用户：`172.18.x.x 是 RK3399` →  
  `ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i ~/.ssh/id_rsa root@172.18.x.x`
- 用户：`3399 平台上抓日志` → 同上（用户 `root`，带两 `-o`）。
- 用户：`连 10.0.0.5`（未提 3399 / RK3399）→ `ssh -i ~/.ssh/id_rsa rigol@10.0.0.5`
- 用户：`用 ubuntu 登录` → 以 `ubuntu` 为准，不套用 root/rigol；若对方仅支持 ssh-rsa，仍可按需加两 `-o`。

## 环境说明

`~` 指当前执行 SSH 的环境（本机终端/Cursor 集成终端）下的用户主目录；Windows 下若用 Git Bash/WSL，路径仍按该环境的 `~/.ssh/id_rsa` 解析。
