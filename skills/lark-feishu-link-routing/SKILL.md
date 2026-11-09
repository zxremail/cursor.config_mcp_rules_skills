---
name: lark-feishu-link-routing
version: 1.0.0
description: >-
  用户消息中出现飞书 / Lark 链接或 token 时 MUST 启用（无需用户再提醒）。
  匹配 feishu.cn、larksuite.com、rigolportal.feishu.cn、doubao.com 的
  /wiki/、/docx/、/sheets/、/base/、/slides/、/mindnotes/、/file/ 等路径，
  或「飞书文档」「飞书链接」「解读这份文档」「读 wiki」等意图。
  强制用 lark-cli 读取正文，禁止先用 WebFetch、WebSearch 或浏览器打开飞书登录页代替 API。
  认证失败时生成 verification_url 与二维码让用户点击授权，禁止让用户手动执行 auth 命令。
metadata:
  requires:
    bins: ["lark-cli"]
    skills: ["lark-shared", "lark-doc", "lark-wiki"]
---

# 飞书链接 → lark-cli（自动优先）

**CRITICAL — 命中本 skill 后，第一步 MUST 用 Shell 执行 `lark-cli`，禁止用 WebFetch / 浏览器 MCP 读正文。**

## 触发（任一即启用）

- URL 含 `feishu.cn`、`larksuite.com`、`larkoffice.com`，或企业域名如 `rigolportal.feishu.cn`
- URL 路径含 `/wiki/`、`/docx/`、`/sheets/`、`/base/`、`/app/`、`/slides/`、`/minutes/`、`/doc/`、`/file/`
- 用户给 wiki/docx token，或要求解读 / 总结 / 评审飞书上的材料

## 访问前自检（≤2 条命令）

```bash
command -v lark-cli
lark-cli whoami
```

未安装：告知用户 `npm i -g @larksuite/cli` 或已有路径，不要改用浏览器凑合。

## URL → 命令路由

| 用户意图 | 首选命令 | 说明 |
|----------|----------|------|
| 读 Wiki / 知识库节点正文 | `lark-cli docs +fetch --as user --doc '<url>'` | `+fetch` 的 `--doc` **支持** `/wiki/` URL |
| 只要节点元数据（类型、obj_token、标题） | `lark-cli wiki +node-get --as user --node-token '<url>'` | 再按需 `docs +fetch --doc <obj_token>` |
| 电子表格 | `lark-sheets` + `lark-cli sheets …` | 勿 WebFetch |
| 多维表格 / Base | `lark-base` | 勿 WebFetch |
| 幻灯片 | `lark-slides` | 勿 WebFetch |
| 画板 | `lark-whiteboard` + `whiteboard +export` | 勿 WebFetch |
| 云盘文件 | `lark-drive` | 勿 WebFetch |

**默认身份**：读用户可见的正文时 **显式 `--as user`**。仅当 `whoami` 只有 bot 且用户明确要求应用视角时用 `--as bot`。

**大文档**：`docs +fetch` 若提示重定向到文件，按 hint **落盘相对路径**再读，不要把整篇 JSON/XML 塞进对话。

## 禁止行为

1. **禁止**对用户给的飞书 URL 优先 `WebFetch` 或「打开链接看看」——会得到登录页或空正文。
2. **禁止**在 `lark-cli` 未尝试前，用「无法访问」结论搪塞；至少跑一次 `docs +fetch` 或 `wiki +node-get`。
3. **禁止**在未获用户明确要求时，用 `drive +add-comment` 写文档评论（评审见 `feishu-doc-review` 规则）。
4. **禁止**让用户自己去终端敲 `auth login`；由 Agent 发起授权并把 **可点击链接 + 二维码** 交给用户。

## 认证 / 权限不足（Split-Flow）

先 Read [`../lark-shared/references/lark-shared-identity-and-permissions.md`](../lark-shared/references/lark-shared-identity-and-permissions.md)。

**User 缺 scope 或 token 过期时（当前轮）**：

```bash
lark-cli auth login --domain docs,drive,wiki --no-wait --json
# 或按错误 JSON 里的 missing_scopes 用 --scope "..." --no-wait --json
```

1. 从 JSON 提取 **`verification_url`**（原样输出，勿改 query）。
2. 生成二维码：`lark-cli auth qrcode <verification_url> --output ./lark-auth-qr.png`（cwd 相对路径）。
3. 回复用户：**先贴完整 URL，再附二维码**；说明「点链接完成飞书授权后，回复已授权」。
4. **同一轮不要**立刻跑 `--device-code` 阻塞，否则用户可能看不到链接。

**用户回复已授权后（下一轮）**：

```bash
lark-cli auth login --device-code <device_code>
```

由 **Agent 执行** `--device-code`，不要甩给用户。

**Bot 缺 scope**：把错误里的 `console_url` 给用户，**不要**对 bot 跑 `auth login`。

## 下游 Skill

- 正文读写细节 → [`lark-doc`](../lark-doc/SKILL.md)
- 知识库节点/空间 → [`lark-wiki`](../lark-wiki/SKILL.md)
- 认证与输出契约 → [`lark-shared`](../lark-shared/SKILL.md)
