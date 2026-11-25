---
name: git-commit
description: >-
  Use when the user asks to commit, amend, write a commit message, 提交, 帮忙 commit,
  git commit, or before creating any local git commit on their behalf. Covers message
  language (English by default), safety (no push unless asked), and Gerrit-style hooks.
---

# Git 提交（Agent 代为 commit）

与 Cursor 用户规则 `committing-changes-with-git` 一并遵守；**本 Skill 补充语言与仓库惯例**。

## Commit message 语言（强制）

| 条件 | 语言 |
|------|------|
| 用户**未**明确要求中文提交说明 | **英文**（标题 + 正文） |
| 用户**显式**要求中文（如「commit 用中文」「提交说明用中文」「commit message 中文」） | **简体中文** |

- 「帮忙 commit」「提交一下」**不**算要求中文；仍用英文写 message。
- 与用户对话仍遵守 `chinese-response`（简体中文）；**仅** `git commit -m` 内容用英文。
- 技术标识符、Conventional 前缀（`feat:` / `fix:`）、Rigol 标题行里的英文名保持英文，不翻译成中文。

## 正文要求

1. 先看 `git status`、`git diff`、`git log -8`（并行）。
2. 标题 1 行：说明 **why**；可用 `feat:` / `fix:` / `refactor:` 等，与仓库近期风格对齐。
3. 需要时第二段 `-m` 写简短正文（仍英文，除非用户要中文）。
4. **默认不 push**；用户当场说 push / 推送 / 上传 Gerrit 才推。
5. 遵守 git 安全协议：不改 `git config`；hook 失败则修问题后 **新 commit**（不要误 amend 失败提交）。

## Rigol / Gerrit 仓库标题行（用户给出格式时）

用户若指定形如：

`YYYY-MM-DD : author #   feat: …`

则日期与 `feat:` 行用英文描述；不要擅自改回中文，除非用户当轮要求中文 commit。

## 示例（默认英文）

```text
feat: integrate vsftpd with FTP root at /data/UserData

Install and enable vsftpd during rootfs build; overlay config defers
service start until userdata bind completes.
```

## 示例（用户说「commit 用中文」时）

```text
feat: 镜像集成 vsftpd，FTP 根目录为 /data/UserData

构建阶段安装并 enable vsftpd，overlay 配置在 userdata 绑定后启动 FTP。
```

## 关联 Skill

- 补丁打进 GoldEngle `os` 等配方仓：`landing-ai-patches-to-os-repo`（远端 commit 已默认英文祈使句；仍须遵守本 Skill 语言表）。
- REA 还原分批 commit：`rea-decompile-to-git-source`（语义化标题；默认英文，除非用户要中文）。