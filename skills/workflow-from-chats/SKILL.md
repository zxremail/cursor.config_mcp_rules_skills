---
name: workflow-from-chats
description: >-
  Extract durable working preferences from recent Cursor chats and convert them
  into skills, rules, subagents, or commands. Use when asked to learn
  preferences, mine feedback, personalize workflows, generate team/person-specific
  agent guidance, or when the user mentions 从聊天提炼、沉淀工作流、内化成 skill/agent/command、
  回顾对话偏好、workflow-from-chats.
---

# Workflow From Chats

从近期 Cursor 对话中推断**可复用的工作偏好**。不要写聊天摘要；只抽取对未来任务有用的流程指导。

参考来源：[cursor-team-kit / workflow-from-chats](https://github.com/cursor/plugins/blob/1f84288b2c047b6d39952da23f51cf486f3b2f7a/cursor-team-kit/skills/workflow-from-chats/SKILL.md)。本技能是个人副本，不依赖该插件。

## Scope

- 默认扫描最近 **7 天**；用户指定窗口时以用户为准。
- 读父对话 transcript，以及相关子代理 transcript。子代理内容只作证据，**对外引用只引父对话**。
- **禁止**向用户暴露本地 transcript 路径、密钥、客户数据、私聊原文、凭据。
- **默认只展示建议，不写文件。** 用户明确确认后，才创建或修改 skill / rule / agent / command。证据互相矛盾时，先提问，再考虑落盘。

## 如何取证（Agent 内部）

Cursor 父对话在 `~/.cursor/projects/<project-slug>/agent-transcripts/`，文件名为 `<uuid>.jsonl`。先列出候选，再按需 Read，不要整目录灌进上下文。

对用户引用父对话时用：`[不超过六字的标题](uuid不含.jsonl)`。不要写出文件系统路径。

当前对话若已包含足够偏好/流程证据，可直接纳入语料，不必为了「走流程」再扫一遍无关历史。

## Workflow

1. 用一段话说明本次要提炼的工作流或偏好面。
2. 内部建立 transcript 清单：标题/主题、父对话 ID、大致日期、是否完成、相关子代理、为何可能含偏好证据。
3. 扫描显式偏好、纠正、流程标记，例如：`I prefer`、`always`、`never`、`not what I asked`、`stop`、`review`、`PR`、`CI`、`logs`、`skill`，以及中文「我希望」「不要」「每次都」「以后」「做成 skill」。
4. 抽出偏好原子：触发条件、流程步骤、决策规则、质量标准、停止条件、证据、置信度。
5. 标定置信度：strong / medium / weak / contradicted。
6. 按**工作流形态**聚类，不要按单次对话聚类。形态包括：shipping、review、simplification、debugging、capture、communication、delegation、validation。
7. 选择产物：new skill、skill edit、rule、subagent、command、workflow doc、或 no artifact。
8. 只起草可复用指导。过滤对未来任务无帮助的轶事。

## Confidence

- **Strong**：用户明确偏好、会改变流程的纠正、父对话中的重复模式、或直接要求把行为写进配置。
- **Medium**：已被接受的工作流、重复出现的工具/模型/验证偏好、或父代理成功采用的子代理共识。
- **Weak**：Agent 自作主张且无用户反馈、只有一份含糊 transcript、或更像本次任务特有的纠正。
- **Contradicted**：证据方向冲突；落盘前先问用户。

只把 **strong**（以及用户点头的 **medium**）做成产物建议。weak 放进 dismissed，不要据此写文件。

## Artifact Choice

先问「要不要独立上下文 / 要不要用户手动触发」，再选类型：

| 产物 | 何时选 | 落盘位置（确认后） |
|------|--------|-------------------|
| **Skill** | 反复出现、步骤清楚、有触发条件的多步流程；仍在主对话执行 | 个人 `~/.cursor/skills/<name>/SKILL.md`；项目 `.cursor/skills/<name>/SKILL.md` |
| **Skill edit** | 已有 skill 覆盖同一触发面，只需补规则/步骤 | 改现有 `SKILL.md`，不要平行新建 |
| **Subagent** | 需要隔离上下文、并行、或客观第三方视角（审查、长搜索） | 个人 `~/.cursor/agents/<name>.md`；项目 `.cursor/agents/<name>.md` |
| **Command** | 用户经常自己敲 `/命令名`，且不应被模型自动调用 | 个人 `~/.cursor/commands/<name>.md`；项目 `.cursor/commands/<name>.md`。更推荐写成 skill 并设 `disable-model-invocation: true` |
| **Rule** | 应广泛遵守的短偏好，不是长流程 | 个人 `~/.cursor/rules/`；项目 `.cursor/rules/`。仅当它是短约束时用 rule；长流程用 skill |
| **Workflow doc** | 有用但不好做成可靠触发 | 仅当用户要求保存文档时再写 |
| **No artifact** | 一次性、过时、证据弱 | 明确说不做 |

跨多个项目重复出现 → 默认个人级。只在单一仓库出现 → 问用户是否放项目级。

确认落盘后：创建 skill 走 `create-skill`；创建子代理走 `create-subagent`；创建 rule 走 `create-rule`。不要绕过这些技能自行发明格式。

## Output

先给简洁综合，再问是否落盘。结构固定为：

1. **Target workflow**：一段话。
2. **Evidence corpus**：只引用父对话（标题 + id）。
3. **Preference profile**：触发 / 步骤 / 决策 / 质量线 / 停止条件。
4. **Adopt / consider / dismissed**：采纳、可考虑、放弃。
5. **Proposed artifacts**：类型、建议名称、个人还是项目、为何选这个而不是另外两个。
6. **Open questions**：仅当问题会挡住落盘时才问。

提议产物时给一份**可直接确认的草稿提纲**（名称、description/触发词、主要步骤），不要先写成文件。用户说「写进去」「确认」「落盘」之后再创建。
