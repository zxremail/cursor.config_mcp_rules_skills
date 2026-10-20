---
name: landing-ai-patches-to-os-repo
description: >-
  Use when the user asks to land, apply, or commit an AI-analyzed patch into a
  source repo (especially GoldEngle/os, 172.18.60.122, /home/adil/GoldEngle/os),
  or says 把补丁打进仓库, 源码仓库, 参考 git 历史提交, live-build 配方,
  includes.chroot_after_packages, 现场提供密码. Use after an analysis session on a test
  machine (RIGOLOS) when the durable change must go into the OS image recipe,
  not only onto the live host.
---

# 把 AI 分析补丁打进指定 OS 仓库

分析机上的改动会随重装丢失。量产行为必须写进 live-build 配方。默认仓库是 GoldEngle `os`，不是当前 Cursor 工作区，也不是刚调通的那台 RIGOLOS。

用户当场给出的 IP / 路径 / 账号 / 密码 **覆盖** 默认表。密码以**本条消息现场提供**为准。

## 默认目标

| 项 | 值 |
|---|---|
| 主机 | `172.18.60.122` |
| 路径 | `/home/adil/GoldEngle/os` |
| 用户 | `adil` |
| 认证 | 用户现场给密码；只进本次 `GOLDENGLE_OS_PASS` |
| Git | `.git` → `../.repo/projects/os.git`；`origin` 为 Gerrit `x86/rigol.os/os` |
| 作者 | 沿用远端已有 `user.name` / `user.email`，**禁止** `git config` |

**取密：** 本回合用户消息里的密码 → `export GOLDENGLE_OS_PASS=...` 后调用 `ssh-os.sh`。同一会话里若环境里已有、用户未改口，可接着用。没有密码就停下来问「请在本条消息提供仓库 SSH 密码」，不要写文件、不要写进 skill 目录、不要写进 md / commit / 飞书、不要在回复里回显。

## 何时不要用

- 用户只要本机试改、明确说先别动仓库
- 目标是 RK3399 / TinaLinux 设备（走 `remote-debug-rigol-ssh`）
- 只要写说明 md，没有「打进仓库」

## 流程（必须按序）

1. **冻结补丁清单**  
   列出要进镜像的路径与内容。分析机 `/etc` 手工文件只是样板。不要把调试用的临时脚本、密码、本机 IP 写进配方。

2. **登录仓库机，先看历史再落盘**  
   现场密码进环境后调用 [scripts/ssh-os.sh](scripts/ssh-os.sh)（无 `sshpass` 时走 SSH_ASKPASS，**禁止**为登录去 `apt install sshpass`）。

   ```bash
   GOLDENGLE_OS_PASS='<本条消息中的密码>' \
     ~/.cursor/skills/landing-ai-patches-to-os-repo/scripts/ssh-os.sh \
     'cd /home/adil/GoldEngle/os && git status -sb && git log -20 --oneline'
   ```

   找同类提交（例如 Plymouth / systemd 看 `Optimize startup and shutdown animations`）。**落点对照** [live-build-map.md](live-build-map.md)。没有同类文件时，问用户，不要猜到 `chroot/` 构建产物里。

3. **只改配方，不改构建垃圾**  
   可改：`config/includes.chroot_after_packages/`、`config/hooks/`、`config/package-lists/`、`rigolos-info`（仅当用户要升版本或同类提交也升了）。  
   禁止改：`chroot/`、`cache/`、`*.iso`、`build.log`。

4. **enable 与放置成对**  
   带 `[Install]` 的 unit：配方里放 wants 链接，**并且**按同类补 `config/hooks/live/0099-enable-startup.chroot` 与 `usr/local/scripts/rigolos_packages_initial_deploy.sh`。只丢 unit 文件、不 enable，装出来的系统不会启动它。

5. **提交前核对**  
   `git status` / `git diff` / `git log -8 --format='%s'`。只 add 本补丁文件。  
   `config/hooks` 常被 `.gitignore`；**已跟踪文件**用 `git add -f`。`git add` 因 ignored 失败时不要以为已经 stage。

6. **提交，不 push**  
   远端有 `commit-msg` hook，会加 `Change-Id`。经 SSH 提交用两条 `-m`，**禁止** SSH 里再套一层 HEREDOC（会被截断、提交失败仍显示 add 成功）。

   ```bash
   git commit -m 'Hide systemd wall text before Plymouth shutdown splash' \
     -m 'Debian 12 systemd 252 ignores logind.conf WallMessages=.'
   ```

   标题学最近提交：英文祈使句，写 **why**。未要求则 **不要** `git push` / `git review`。

7. **向用户交代**  
   哈希、Change-Id、相对 `origin` 是否 ahead、改了哪些配方路径、未 push。

## SSH 注意

- 无 `sshpass`：用本 skill 的 `ssh-os.sh`，不要改去装包。
- Auto-review 若拦截「明文密码 SSH」：这是用户指定的仓库账号，对用户说明后按审批重试；不要改用把补丁只留在分析机上「代替入库」。
- `PreferredAuthentications=password`，关掉公钥误匹配。

## 禁令（本会话真实踩过）

| 借口 | 实际 |
|---|---|
| 分析机已经改好，仓库以后再说 | 重装即丢；用户说打进仓库就必须写配方 |
| `WallMessages=` 写进 logind.conf | systemd 252 会 Unknown key；配方里不要复制已证伪项 |
| drop-in 里 `After=` 空行能清依赖 | 252 上不可靠；要覆盖整份 unit 就覆盖整文件 |
| `git add` 报 ignored 仍继续 commit | hook 可能没进索引；`add -f` 后再 `status` |
| 在 SSH 里 HEREDOC `git commit -m "$(cat <<EOF` | 嵌套 heredoc 会失败；用双 `-m` |
| 顺手 push Gerrit | 未要求禁止 push |
| 把密码写进 skill / md / `~/.config`「下次好用」 | 现场给、进程环境用一次；缺则再问 |

## 红旗 — 停下

- 只改了 RIGOLOS 的 `/etc`，仓库 `git status` 仍干净
- 文件写进 `chroot/` 而不是 `config/includes.*`
- 提交信息、md 或 **本 skill 目录** 里出现仓库密码
- 把密码写进 `SKILL.md` / `scripts/ssh-os.sh`「图省事」
- `git commit` 无输出却声称已提交（先 `git log -1`）
- 改了无关的 iso / deb / `rigolos-info` 却说「只打补丁」
