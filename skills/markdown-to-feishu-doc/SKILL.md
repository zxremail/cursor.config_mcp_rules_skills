---
name: markdown-to-feishu-doc
description: >
  Use when converting a local Markdown/md file to a Feishu/Lark Docx or Wiki,
  or when the user says markdown 转飞书, md 转飞书文档, 把 md 导入飞书,
  代码块标题, caption, 画板标题, 画板斜体, 字面量 HTML, small 标签未渲染.
  Also use when a previous Markdown 导入 left default「代码块」captions, missing
  seq=auto headings, unstyled tables, or when tempted to docs +update overwrite
  a document that already has whiteboards.
---

# Markdown → 飞书文档（Mermaid → 画板）

**前置条件**：认证失败时才读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)。排版条见 [`../feishu-doc-format/SKILL.md`](../feishu-doc-format/SKILL.md)，本流程一次写对，不要先导入再整篇回写。

脚本（只向 stdout 打 JSON 摘要）：`scripts/pipeline.py`。

## 核心原则

1. **Mermaid 必须变成飞书画板**，不是代码块、不是图片。
2. **格式在本地 XML 里一次写齐**：`seq="auto"` 的 `<h1>`/`<h2>`、浅紫表头、浅蓝首列、`<pre caption>`。禁止 `docs +create --doc-format markdown` 再 fetch 全文补样式。
3. **带画板的文档禁止 `docs +update --command overwrite`**。overwrite 会克隆/打空白画板（常见 `Whiteboard clone failed` / `degrade_code=2105`），然后被迫把五张图再画一遍。漏改用 `block_replace` / `block_insert_after`。
4. **大文件不准进对话**：不要 `Read` 转换产物 `doc.xml`、`docs +fetch` 全文、画板 `raw` JSON。一律写到 cwd 相对路径，用 `pipeline.py audit-*` 看摘要。源 md 由脚本读取，模型最多 `Read` `manifest.json`。

## 禁止（上次烧 token 的写法）

| 禁止 | 改做 |
|------|------|
| `+create --doc-format markdown` 再 `+fetch` 整篇 XML 改表 | `pipeline.py convert` → `+create --doc-format xml` |
| `+update --command overwrite` 补 `seq`/表色 | 创建时 XML 已带；事后只 `block_replace` 单块 |
| `Read` 7 万字 fetch / 千行 board.json | `audit-xml` / `patch-board` / `audit-board` |
| Mermaid 带 `%%{init: theme dark}` | 脚本已剥掉；否则飞书报 `Unsupported color format: "2D3436"` |
| `whiteboard +update --yes`、`@/tmp/...` | 无 `--yes`；`@file` 必须是 cwd 相对路径 |
| 正则把 `<thead>` 当成 `<th` | 表样式只由脚本写，勿手写 `<th[^>]*>` |

## 执行流程

```
Step 1  pipeline.py convert → out/doc.xml + out/mermaid/ + manifest.json
Step 2  只读 manifest（标题、mermaid 张数、画板标题列表）
Step 3  docs +create --doc-format xml --content @./out/doc.xml --as user
Step 4  按 token 顺序 mermaid overwrite（用 mN.mmd，无 YAML / 无 init）
Step 4b export raw 落盘 → patch-board → raw overwrite（浅框 + 去 HTML）
Step 4c whiteboard-cli 标题 DSL → italic → raw 增量追加（不要 overwrite）
Step 5  fetch/export 只落盘 + audit-xml / audit-board；向用户给 doc url
```

### Step 1–2：本地转换

在**工作区 cwd**建短时目录（用完删除），不要用绝对 `/tmp` 当 `@file`：

```bash
python3 ~/.cursor/skills/markdown-to-feishu-doc/scripts/pipeline.py convert \
  ./path/to/src.md ./_feishu_out
```

stdout / `manifest.json` 含 `title`、`mermaid_count`、`titles`。缺少 YAML `title:` 时脚本用最近小节凑标题；不对就只改正文 `titleN.txt`，不要为改一个标题去 Read 整份 XML。

非 Mermaid 围栏会写成带实际含义 `caption` 的 `<pre>`（`{主题} {体裁}`：函数声明 / 调用示例 / 命令行示例 / 配置示例）。禁止 caption 为「代码块」「示例」「c」。

### Step 3：创建

```bash
lark-cli docs +create --as user --doc-format xml \
  --title "manifest.title" \
  --content "@./_feishu_out/doc.xml"
```

用户指定位置时加 `--parent-token`（文件夹或知识库节点）。返回里按出现顺序记下每张白板的 `block_token`，与 `m0.mmd`… 对齐。`new_blocks` 里 `block_type=whiteboard` 即画板。

长文（xml >50KB）仍可先 create 再 **`append`** 后半；**append 不是 overwrite**。每次记下新增 token。

无 Mermaid 时仍走本 XML 路径（表色和 caption 一次到位）。不要用 `drive +import` 当主路径。

### Step 4：填 Mermaid

对每个 token：

```bash
lark-cli whiteboard +update --as user \
  --whiteboard-token <token> \
  --input_format mermaid \
  --source "@./_feishu_out/mermaid/mN.mmd" \
  --overwrite
```

保留 `style` / `classDef`。不要把 `title:` frontmatter 送进飞书。失败且报 `2D3436`：确认 mmd 无 `%%{init` 后重试同一文件（偶发），不要改业务色。

### Step 4b：raw 去 HTML + 浅色层框

顺序固定：**先 4b overwrite，再 4c 加标题**。4b 的 `--overwrite` 会清掉已有标题节点。

```bash
lark-cli whiteboard +export --as user --whiteboard-token <token> \
  --output-type raw --output "./_feishu_out/boardN.json" --overwrite
python3 ~/.cursor/skills/markdown-to-feishu-doc/scripts/pipeline.py patch-board \
  ./_feishu_out/boardN.json
lark-cli whiteboard +update --as user --whiteboard-token <token> \
  --input_format raw --source "@./_feishu_out/boardN.json" --overwrite
```

`patch-board` 做：去掉 `<b>`/`<small>`/`<br/>` 且主题/注解仍两段（bold + 11px）；`section` `#F3F4F6`；深色 subgraph 改浅底（紫 `#EDE9FE`、蓝 `#DBEAFE`、橙 `#FFEDD5`、品红 `#FCE7F3`，内层可白）；叶子深彩色 + 白字 `text_color_type: 1`。不要手编 OpenAPI JSON。preview jpg 在 raw 写回后常是占位图，**不能**据此再 mermaid overwrite。

### Step 4c：画布斜体标题

标题在画板内顶部独立 `text_shape`：24px、`italic: true`、`font_weight: regular`、`#1F2329`、宽与图同宽、`y` 约在内容上方 48px。不要 `<whiteboard caption>`，不要在文档里画板上方再写加粗段。

用 **whiteboard-cli DSL `version: 2`**（缺 version 会校验失败）。脚本：

```bash
python3 ~/.cursor/skills/markdown-to-feishu-doc/scripts/pipeline.py title-dsl \
  "实际含义标题" <图宽> > ./_feishu_out/titleN.dsl.json
npx -y @larksuite/whiteboard-cli@^0.2.0 -i ./_feishu_out/titleN.dsl.json \
  -f dsl -t openapi -o ./_feishu_out/titleN.oa.json -F json
```

用一小段 Python **只改** oa.json 里 `text.italic=true`（不要把 oa 打印到对话），然后：

```bash
lark-cli whiteboard +update --as user --whiteboard-token <token> \
  --input_format raw --source "@./_feishu_out/titleN.src.json"
```

**不要** `--overwrite`。裁切见 `feishu-whiteboard-text-visibility`。

### Step 5：验收（摘要，不是全文）

```bash
lark-cli docs +fetch --as user --doc <id> --detail with-ids --doc-format xml \
  > ./_feishu_out/fetch.json
python3 ~/.cursor/skills/markdown-to-feishu-doc/scripts/pipeline.py audit-xml \
  ./_feishu_out/fetch.json
lark-cli whiteboard +export --as user --whiteboard-token <token> \
  --output-type raw --output ./_feishu_out/vN.json --overwrite
python3 ~/.cursor/skills/markdown-to-feishu-doc/scripts/pipeline.py audit-board \
  ./_feishu_out/vN.json
```

`audit-xml` 必须 `ok: true`：标题 `seq=auto`、无手写序号、无标题 `<code>`、表头/首列色、pre caption、白板数量 = mermaid 张数。`audit-board`：无 `<small>`/`<b>`/`<br`，有斜体标题。缺一张白板用 `block_insert_after` 插 `<whiteboard type="blank">`，再走 Step 4–4c，**不要 overwrite 整篇**。

通过后删 `_feishu_out`，把 `document.url` 给用户。

## 画板标题与 HTML（格式不降级）

- YAML `title:` 优先；禁止「画板」「如图」「流程图」。
- 源码 Mermaid 仍可写 `<b>` + `<br/>` + `<small>（注解）</small>` 给 HTML 预览；飞书不解析这些标签，必须 Step 4b。
- 非 Mermaid 图：思维导图/时序/类图/饼图走 mermaid；架构/泳道等走 [`../lark-whiteboard-cli/SKILL.md`](../lark-whiteboard-cli/SKILL.md)。

## 快速决策表

| 用户说 | 做什么 |
|-------|--------|
| 把这个 md 转成飞书文档 | Step 1–5 |
| 放到某文件夹/知识库 | Step 3 `--parent-token` |
| md 转飞书不用画板 | 仍 XML create（表色/caption）；Mermaid 若存在仍须画板 |
| 已有文档缺表色/序号 | `block_replace` 目标表或标题；禁止 overwrite |

## 格式验收（与 feishu-doc-format 相同，不打折）

- 章 `<h1 seq="auto">`、节 `<h2 seq="auto">`，正文标题不从 `<h2>` 起篇
- 表头 `rgb(236,226,254)` 居中加粗；首列 `rgb(225,234,255)` 加粗且无 `<code>`
- 每个 `<pre>` 有实际含义 caption
- 每个画板画布顶部斜体标题；节点无字面量 HTML；section 浅底、叶子深彩色白字
