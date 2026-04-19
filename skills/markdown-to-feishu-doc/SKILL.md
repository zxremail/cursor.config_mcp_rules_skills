---
name: markdown-to-feishu-doc
description: >
  将本地 Markdown 文档转化为飞书云文档，自动将 Mermaid 代码块转为飞书画板。
  Use when the user asks to convert markdown/md files to Feishu (飞书) documents,
  or mentions "markdown 转飞书", "md 转飞书文档", "把 md 导入飞书", "markdown 导入飞书",
  "把 markdown 文档转化为飞书文档", "md 文档转化为飞书文档".
---

# Markdown → 飞书文档（Mermaid → 画板）

**前置条件**：先读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 了解认证和权限处理。

## 🔴 核心原则

**Mermaid 代码块必须转为飞书画板**，不是普通代码块，也不是图片。画板可编辑、可协作，是飞书原生可视化组件。

## 执行流程

```
Step 1: 读取并解析 Markdown
Step 2: 提取 Mermaid → 生成转化后的 Markdown
Step 3: 创建飞书文档（含空白画板占位）
Step 4: 填充画板内容（Mermaid → 画板）
Step 5: 验证完成
```

### Step 1: 读取并解析 Markdown

1. 使用 Read 工具读取本地 `.md` 文件全文
2. 识别所有 Mermaid 代码块：以 ` ```mermaid ` 开头、` ``` ` 结尾的围栏代码块
3. 按出现顺序记录每个 Mermaid 块的内容（含完整的 Mermaid 代码，**保留 style 指令**）

### Step 2: 生成转化后的 Markdown

将原始 Markdown 中的每个 Mermaid 代码块替换为飞书空白画板标签：

```
原始：
  ```mermaid
  graph TD
      A --> B
      style A fill:#2E86AB
  ```

替换为：
  <whiteboard type="blank"></whiteboard>
```

**关键规则**：
- 每个 Mermaid 块对应一个 `<whiteboard type="blank"></whiteboard>`
- 保持 Mermaid 块在文档中的相对位置不变
- 非 Mermaid 的代码块（如 python、bash）保持原样
- 标准 Markdown 格式原样保留，飞书 `docs +create` 支持标准 Markdown

### Step 3: 创建飞书文档

使用 `docs +create` 创建文档：

```bash
lark-cli docs +create \
  --title "文档标题" \
  --markdown '转化后的 Markdown 内容' \
  --as user
```

**可选目标位置参数**（按用户指定选择其一）：
- `--folder-token <TOKEN>` — 放入指定文件夹
- `--wiki-node <TOKEN>` — 放入知识库节点下
- `--wiki-space <ID>` — 放入知识空间根目录

**长文档策略**：如果 Markdown 内容超长（>50KB），分段操作：
1. 先用 `docs +create` 创建文档的前半部分
2. 再用 `docs +update --mode append` 追加后续内容
3. 每次追加时记录返回的 `board_tokens`

**从返回值中记录 `board_tokens`**：
- `data.board_tokens` 是本次创建的所有空白画板 token 列表
- token 的顺序与 Markdown 中 `<whiteboard>` 标签的出现顺序一致
- 将每个 token 与 Step 1 中记录的 Mermaid 代码一一对应

### Step 4: 填充画板内容

对于每个 (board_token, mermaid_code) 配对：

1. 将 Mermaid 代码写入临时文件

```bash
cat > /tmp/mermaid_N.mmd << 'MERMAID_EOF'
graph TD
    A[开始] --> B{判断}
    B -->|是| C[处理]
    style A fill:#2E86AB,stroke:#1B4965,color:#FFFFFF
MERMAID_EOF
```

2. 使用 `whiteboard +update` 更新画板

```bash
lark-cli whiteboard +update \
  --whiteboard-token <board_token> \
  --input_format mermaid \
  --source @/tmp/mermaid_N.mmd \
  --overwrite --yes --as user
```

**Mermaid style 保留规则**：原始 Mermaid 中的 `style` 指令（fill、stroke、color 等）必须完整保留，不得丢弃。

**非 Mermaid 可视化内容的路由**：如果 Markdown 中包含复杂图表描述（如文字描述的架构图、流程图），参考以下路由决策：
- 思维导图 / 时序图 / 类图 / 饼图 → Mermaid 格式（`--input_format mermaid`）
- 架构图 / 组织架构图 / 泳道图 / 鱼骨图等 → 使用 whiteboard-cli DSL，参见 [`../lark-whiteboard-cli/SKILL.md`](../lark-whiteboard-cli/SKILL.md)

### Step 5: 验证完成

- 确认所有 Mermaid 块都已转为画板并填充内容
- 确认没有遗漏任何 board_token
- 向用户返回文档链接（`doc_url`）

## 快速决策表

| 用户说 | 做什么 |
|-------|-------|
| "把这个 md 转成飞书文档" | 完整执行 Step 1-5 |
| "markdown 导入飞书" | 完整执行 Step 1-5 |
| "md 转飞书，不用画板" | 直接 `drive +import --file ./xxx.md --type docx`（Mermaid 保留为代码块） |
| "md 转飞书，放到 XX 文件夹" | Step 3 添加 `--folder-token` |
| "md 转飞书，放到知识库" | Step 3 添加 `--wiki-node` 或 `--wiki-space` |

## 注意事项

- `drive +import` 只能原样导入 Markdown，**不会**将 Mermaid 转为画板。本 Skill 必须使用 `docs +create` + `whiteboard +update` 的组合流程
- 画板创建后不可逆。如果 Mermaid 语法有误导致画板更新失败，检查错误信息、修正语法后重试
- 如果原始 Markdown 不包含任何 Mermaid 代码块，可以直接使用 `drive +import --file ./xxx.md --type docx` 简化流程
