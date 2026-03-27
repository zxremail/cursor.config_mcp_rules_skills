---
name: remote-debug-rigol-ssh
description: >-
  Applies default SSH credentials for Rigol remote debugging targets. Use when
  the user mentions a host IP (or hostname) for remote access, remote debug,
  SSH, 跳板, 连设备, or similar; infer the connection is SSH as user rigol with
  the documented password unless the user states otherwise.
---

# 远程调试 SSH（Rigol 默认账号）

## 何时生效

用户只要**给出或提到用于远程访问/远程调试的 IP 或主机名**（未另行说明用户名或密码时），按本节默认值处理。

## 默认凭据（不可与仓库共享）

| 项 | 值 |
|----|-----|
| 用户 | `rigol` |
| 密码 | `123456` |

## 代理行为

1. **SSH 命令**：使用 `ssh rigol@<IP或主机名>`。若用户只写了 IP，补全为 `rigol@该 IP`。
2. **说明与文档**：在回复中如需写出连接方式，明确用户名 `rigol`；密码仅在用户需要手动输入或配置工具时说明（勿把密码写进会被提交的代码或公开文档，除非用户明确要求）。
3. **用户覆盖**：若用户指定了其他用户名、密钥路径或密码，以用户当次说明为准，不再套用本默认值。
4. **非交互场景**：若需在脚本中自动输入密码，可提示使用本机已安装的工具（如 `sshpass`）或改用 SSH 公钥；默认仍优先建议交互式 `ssh` 以减小凭据泄露面。

## 示例

- 用户：`调试 192.168.1.100` → 连接：`ssh rigol@192.168.1.100`，密码 `123456`。
- 用户：`ssh 到 10.0.0.5 抓日志` → 同上，用户 `rigol`。

## 安全提示（给用户）

密码保存在个人 Skill 中，仅本机 Cursor 生效；生产或共享环境建议改为 SSH 公钥并轮换密码。
