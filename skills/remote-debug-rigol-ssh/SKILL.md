---
name: remote-debug-rigol-ssh
description: >-
  Default SSH user and identity file for Rigol remote debugging. Use when the
  user mentions a host IP, hostname, remote debug, SSH, 3399 平台, 跳板, or 连设备.
  Chooses root vs rigol by whether the target is explicitly the 3399 platform;
  always uses ~/.ssh/id_rsa on the current machine unless overridden.
---

# 远程调试 SSH（默认用户与密钥）

## 何时生效

用户**给出或提到**用于远程访问/远程调试的 IP 或主机名，且**未另行说明**用户名、密钥路径或其他认证方式时，按本节处理。

## 身份文件（两台情况相同）

一律使用**当前机器环境**下的私钥：

`~/.ssh/id_rsa`

命令中写为：`-i ~/.ssh/id_rsa`（或 `IdentityFile ~/.ssh/id_rsa`）。

## 用户名（按是否 3399 平台分支）

| 条件 | SSH 用户 |
|------|----------|
| 用户**明确**说明远程主机是 **3399 平台**（如「3399 平台」「3399平台」、在上下文中明确指该平台设备） | `root` |
| 其他情况（默认） | `rigol` |

**3399 判定**：须为**明确**表述；仅出现数字「3399」但语义不清时，仍按默认 `rigol`，除非用户补充说明是 3399 平台。

## 代理行为

1. **SSH 命令模板**：`ssh -i ~/.ssh/id_rsa <用户>@<IP或主机名>`
2. **scp / rsync 等**：同样加上 `-i ~/.ssh/id_rsa`，用户按上表选取。
3. **用户覆盖**：若用户指定了其他用户、其他密钥或密码登录，以当次说明为准。
4. **勿默认密码**：本技能不再假定密码登录；若密钥失败，再请用户说明是否用密码或其他密钥。

## 示例

- 用户：`3399 平台上 192.168.1.10 远程调试` → `ssh -i ~/.ssh/id_rsa root@192.168.1.10`
- 用户：`连 10.0.0.5 看日志`（未提 3399 平台）→ `ssh -i ~/.ssh/id_rsa rigol@10.0.0.5`
- 用户已说 `用 ubuntu 登录` → 以 `ubuntu` 为准，不套用 root/rigol

## 环境说明

`~` 指当前执行 SSH 的环境（本机终端/Cursor 集成终端）下的用户主目录；Windows 下若用 Git Bash/WSL，路径仍按该环境的 `~/.ssh/id_rsa` 解析。
