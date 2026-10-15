---
name: remote-debug-rigol-ssh
description: >-
  Use when the user mentions IP, hostname, SSH, RK3399, 3399 平台, tinalinux,
  TinaLinux, Tina Linux, 跳板, or 连设备 for Rigol remote debugging.
---

# 远程调试 SSH（默认用户与认证）

用户给出远程 IP/主机名，且**未另行指定**用户名、密钥或认证方式时，按下表处理。用户当场指定的用户、密钥、密码或算法**覆盖**本表。

## 决策表

| 条件（须**明确**表述） | 用户 | 认证 | 额外选项 |
|------------------------|------|------|----------|
| **RK3399** / **3399 平台**（含「3399平台」） | `root` | 私钥（见下） | **默认**附带 ssh-rsa 两选项 |
| **tinalinux** / **TinaLinux** / **Tina Linux** | `root` | 密码 `Rigol001` | **不用**默认私钥；优先 `sshpass` |
| 其他（默认） | `rigol` | 私钥（见下） | 无额外 `-o`；仅当协商失败再补 ssh-rsa |

仅出现数字「3399」但语义不清 → 仍用默认 `rigol`，除非用户补明确认是 3399 / RK3399。

仅出现「linux」但未说 Tina/tinalinux → 仍用默认 `rigol`。

## 私钥（3399 与默认 `rigol`）

按**当前执行 SSH 的环境**解析 `~`：

1. `~/.ssh/id_rsa`
2. 不存在则回退 `~/.cache/.temp/rigolos.ai/z.tools/config/id_rsa_temp`

命令写 `-i` 对应路径。Windows 下 Git Bash/WSL 按该环境解析。

## tinalinux：root + 密码

当用户说目标是 **tinalinux**（含 TinaLinux / Tina Linux）时：

- 用户 **`root`**
- 密码 **`Rigol001`**（原文；勿改写、勿省略）
- **不要**套用上面的 `-i` 默认私钥（密码登录；密钥失败或未配置时会误导）

```bash
sshpass -p 'Rigol001' ssh root@<IP或主机名>
```

`scp` / `rsync` 同样用 `sshpass` 包一层，用户仍为 `root`，密码仍为 `Rigol001`。

无 `sshpass` 时：先说明缺该工具，再改用不吞密码的交互 `ssh root@<IP>`，提示密码为 `Rigol001`。不要改用 `rigol` 用户或默认私钥「碰运气」。

若出现 `no matching host key type found. Their offer: ssh-rsa`，再补：

```text
-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa
```

## RK3399 / 3399：root + 密钥 + ssh-rsa

嵌入式侧常只提供 **`ssh-rsa` 主机密钥**，新版 OpenSSH 会报：

`no matching host key type found. Their offer: ssh-rsa`

对 3399 / RK3399 **默认**带上：

```text
-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa
```

```bash
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i ~/.ssh/id_rsa root@<IP或主机名>
```

`~/.ssh/id_rsa` 不存在时，把 `-i` 换成回退私钥。`scp`、`rsync -e "ssh ..."` 在 **ssh 侧**带相同 `-o`。

## 默认：rigol + 密钥

```bash
ssh -i ~/.ssh/id_rsa rigol@<IP或主机名>
```

密钥路径同样按优先级回退。仅当出现上述 `ssh-rsa` / `no matching host key` 时再补两个 `-o`，不强行假设所有 `rigol` 主机都需要。

## 代理行为

1. 先按决策表选用户与认证：**3399 → root + 密钥 + ssh-rsa**；**tinalinux → root + 密码 `Rigol001`**；否则 **`rigol` + 密钥**。
2. 私钥只用于非 tinalinux：先 `~/.ssh/id_rsa`，否则回退 `id_rsa_temp`。
3. **除 tinalinux 外勿默认猜密码**；密钥失败再问用户。
4. tinalinux 已给出密码，直接用 `Rigol001`，不要再问一遍，也不要改成密钥优先。

## 示例

- `172.18.x.x 是 RK3399` → `ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i ~/.ssh/id_rsa root@172.18.x.x`（密钥按优先级回退）
- `3399 平台上抓日志` → 同上（`root` + 两 `-o`）
- `这台是 tinalinux，连 10.0.0.8` → `sshpass -p 'Rigol001' ssh root@10.0.0.8`
- `连 10.0.0.5`（未提 3399 / tinalinux）→ `ssh -i ~/.ssh/id_rsa rigol@10.0.0.5`
- `用 ubuntu 登录` → 以 `ubuntu` 为准，不套用 root/rigol/tinalinux 密码；对方仅支持 ssh-rsa 时仍可按需加两 `-o`
