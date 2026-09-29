---
name: markdown-to-feishu-doc
description: >
  将本地 Markdown 文档转化为飞书云文档，自动将 Mermaid 代码块转为飞书画板，
  并把每个代码块标题、每个画板标题改成实际含义。
  Use when the user asks to convert markdown/md files to Feishu (飞书) documents,
  or mentions "markdown 转飞书", "md 转飞书文档", "把 md 导入飞书", "markdown 导入飞书",
  "把 markdown 文档转化为飞书文档", "md 文档转化为飞书文档",
  "代码块标题", "代码块描述", "caption", "代码块",
  "画板标题", "画板增加实际含义标题", "mermaid 实际含义标题".
---

# Markdown → 飞书文档（Mermaid → 画板）

**前置条件**：先读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 了解认证和权限处理。

## 🔴 核心原则

**Mermaid 代码块必须转为飞书画板**，不是普通代码块，也不是图片。画板可编辑、可协作，是飞书原生可视化组件。

## 执行流程

```
Step 1: 读取并解析 Markdown
Step 2: 提取 Mermaid → 生成转化后的 Markdown（非 Mermaid 代码块必须带实际含义 caption）
Step 3: 创建飞书文档（含空白画板占位）
Step 4: 填充画板内容（Mermaid → 画板），并为每个画板增加实际含义标题
Step 5: 验证完成（含代码块标题、画板内标题）
```

### Step 1: 读取并解析 Markdown

1. 使用 Read 工具读取本地 `.md` 文件全文
2. 识别所有 Mermaid 代码块：以 ` ```mermaid ` 开头、` ``` ` 结尾的围栏代码块
3. 按出现顺序记录每个 Mermaid 块的内容（含完整的 Mermaid 代码，**保留 style 指令**）。同时记下 YAML `title:`（实际含义标题）；没有则按最近小节 + 图意拟定，转换前不要丢下缺标题的源码。

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
- 非 Mermaid 的代码块**不得**原样丢进飞书围栏：必须写成带 `caption` 的 `<pre>`（见下节）
- 其余标准 Markdown 格式原样保留，飞书 `docs +create` 支持标准 Markdown

### 代码块标题必须是实际含义

每个「代码块」的标题都要全部改成实际含义。飞书 `<pre>` 没有 `caption`、或 caption 为空 / 仅换行时，界面统一显示「代码块」，转换后禁止留下这种默认标题。

Markdown 围栏通常只有语言标记（如 c、bash），没有标题。转换时根据**上一节标题 + 代码角色**为每一块单独拟定 caption，写入：

```xml
<pre lang="c" caption="priv_reboot 函数声明"><code>priv_result_t priv_reboot(void);</code></pre>
```

拟定规则（`{主题} {体裁}`，同一节内不重复）：

| 代码角色 | 体裁用词 | 示例 |
|---------|---------|------|
| 函数/类型声明、签名模板 | 函数声明 / 签名模板 | `priv_reboot 函数声明`、`超时版便捷 API 签名模板` |
| 调用、判断返回值 | 调用示例 | `priv_reboot 调用示例` |
| shell / CLI | 命令行示例 | `lcd-brightness 命令行示例` |
| 配置、JSON、单元片段 | 配置示例 / 报文示例 | `usbtmc.conf 配置示例` |

- 主题取最近的小节标题或代码里的主符号（函数名、命令、文件名），不要只用语言名。
- caption 短句、无句号；不要写成「如下」「示例」「代码」「c」「bash」。
- 代码正文放在 `<code>` 内；`<` `>` `&` 按 XML 转义；换行用 `<br/>`。
- Mermaid 走画板，不给 `<pre>` 加「代码块」标题。

若 `docs +create --markdown` 未能带上 caption：立刻 `docs +fetch --detail with-ids`，对每个 `<pre>` 做 `block_replace`，补上 `caption="实际含义"`。不要等用户再提。

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

### 每个画板增加实际含义标题

每个画板增加实际含义标题。标题必须写在**画板内部画布顶部**，作为独立 `text` / `text_shape` 节点，不要写在文档正文里，也不要当成代码块那样的 `<whiteboard caption>`（该属性会换掉整块画板）。

拟定规则：优先用源码 YAML `title:`；没有则取最近小节标题 + 图在讲什么。短句、无句号。例如 `业务进程到特权守护进程的调用关系`、`便捷 API 一次调用内部顺序`。禁止「画板」「如图」「流程图」。

向飞书画板写入 Mermaid 时，**不要**把 YAML `title:` / `---` 行送进 `whiteboard +update --input_format mermaid`（飞书渲染器常不认，标题也不会变成画布文字）。去掉 frontmatter 后再 overwrite，然后用上面的 YAML `title` 做画布内标题。

做法（Mermaid `+update --overwrite` 之后立刻做，否则标题会被冲掉）：

1. `whiteboard +export --output-type raw --output @相对路径`，按节点包围盒取图宽，标题 `x` 与图左对齐、`width` 等于图宽、`y` 在内容上方约 48px。
2. 用 whiteboard-cli 把一条 DSL `type: text`、`fontSize: 24`、`textAlign: center` 转成 OpenAPI；`font_weight` 改为 `bold`。
3. `whiteboard +update --input_format raw --source @文件` **不要加 `--overwrite`**（增量追加）。
4. `+export --output-type preview` 确认标题整行可见、未被裁切。文字露出规则见 `feishu-whiteboard-text-visibility`。

从 DSL 一次画成的图：标题作为文档第一个 text 子节点一起写入，不要事后再在文档里加一行加粗段落。

**非 Mermaid 可视化内容的路由**：如果 Markdown 中包含复杂图表描述（如文字描述的架构图、流程图），参考以下路由决策：
- 思维导图 / 时序图 / 类图 / 饼图 → Mermaid 格式（`--input_format mermaid`）
- 架构图 / 组织架构图 / 泳道图 / 鱼骨图等 → 使用 whiteboard-cli DSL，参见 [`../lark-whiteboard-cli/SKILL.md`](../lark-whiteboard-cli/SKILL.md)

### Step 5: 验证完成

- 确认所有 Mermaid 块都已转为画板并填充内容
- 确认没有遗漏任何 board_token
- **代码块标题**：`docs +fetch --detail with-ids` 后，每个 `<pre>` 的 `caption` 都是实际含义；不得为空、不得仅为换行、不得仍是「代码块」
- **画板标题**：每张画板预览顶部都有实际含义标题；文档里画板正上方不得再留重复加粗段落
- 按 [`../feishu-doc-format/SKILL.md`](../feishu-doc-format/SKILL.md) 检查标题是否 `seq="auto"`（无手写序号）、表格是否浅紫表头 + 浅蓝首列、表头与首列是否加粗、首列是否未使用代码格式、代码块 caption 与画板内标题是否为实际含义；Markdown 导入未带上时用 `docs +update` / `whiteboard +update` 补
- 向用户返回文档链接（`doc_url`）

## 快速决策表

| 用户说 | 做什么 |
|-------|-------|
| "把这个 md 转成飞书文档" | 完整执行 Step 1-5 |
| "markdown 导入飞书" | 完整执行 Step 1-5 |
| "md 转飞书，不用画板" | `drive +import` 后仍须给每个代码块补实际含义 caption |
| "md 转飞书，放到 XX 文件夹" | Step 3 添加 `--folder-token` |
| "md 转飞书，放到知识库" | Step 3 添加 `--wiki-node` 或 `--wiki-space` |

## 注意事项

- `drive +import` 只能原样导入 Markdown，**不会**将 Mermaid 转为画板。本 Skill 必须使用 `docs +create` + `whiteboard +update` 的组合流程
- 画板创建后不可逆。如果 Mermaid 语法有误导致画板更新失败，检查错误信息、修正语法后重试
- 如果原始 Markdown 不包含任何 Mermaid 代码块，可以用 `drive +import --file ./xxx.md --type docx` 简化创建，但**导入后仍必须**为每个代码块补上实际含义 caption（import 不会写 caption）
- 「代码块」是飞书缺省标题，不是可用文案。转换结束前必须改完，不能留给用户手工点选
- 「画板」是飞书缺省块名。每个画板增加实际含义标题，写在画布内，不能留给用户手工点选
