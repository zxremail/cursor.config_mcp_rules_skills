---
name: feishu-doc-format
description: >
  个人默认飞书云文档排版：标题 seq=auto 自动编号（不手写 1. / 1.1）、标题不用代码格式，
  表格浅紫表头 rgb(236,226,254) + 浅蓝首列 rgb(225,234,255)，
  表头与首列加粗、首列不用代码格式。
  飞书文档画板中的时序图，参与者标题栏字体必须加粗；箭头按方向着色：向右实线 #3370FF、向左虚线 #00A870、自调用实线 #1F2329。
  代码块标题用实际含义，禁止停留在默认「代码块」。
  每个画板增加实际含义标题（画布顶部独立文字，斜体），写在画板内部画布顶部，不要写在文档正文里。
  Use when creating or editing Feishu/Lark Docx or Wiki, 飞书文档, 画板时序图,
  docs +create / +update, whiteboard +update, converting markdown to Feishu documents,
  代码块标题, 代码块描述, caption, 画板标题.
  Takes precedence over lark-doc default table/heading styles; do not patch lark-doc or lark-whiteboard.
---

# 飞书文档个人默认格式

写或改飞书云文档时默认采用下列格式。用户当场指定其他样式时以当场为准。
本 Skill 覆盖官方 `lark-doc` 里「表头用 light-gray / medium-gray」的建议。

**不要把本格式写进 `lark-doc/` 或 `lark-whiteboard/`。** `lark-cli update` 会同步覆盖官方 AI Skills；个人偏好只放本 Skill 和 `~/.cursor/rules/feishu-doc-format.mdc`。

## 标题

- 每一个正文标题写 `seq="auto"`。
- 标题文本不手写 `1.`、`1.1`、`一、` 等前置序号。
- 层级连续、从章开始：`<h1>` 章、`<h2>` 节，不要从 `<h2>` 起篇（否则自动编号对不齐 `1` / `1.1`）。
- 插入或删除同级标题后，飞书会自动重排（例如原 `1` 变为 `2`，`1.1` 变为 `2.1`）。
- 仅当用户明确要求公文手写序号（`一、` / `（一）`）时才不用 `seq="auto"`。

### 标题不用代码格式

- 标题文本一律普通正文，禁止 `<code>` / `inline_code` / 等宽字体。
- 类型名、函数名、头文件、库名写在标题里时也走普通文字，不要包成行内代码。
- 标题下正文、以及表格非首列，需要突出命令或标识时仍可用 `<code>`。

```xml
<h1 seq="auto">读前须知</h1>
<h2 seq="auto">你实际在用的是什么</h2>
<h2 seq="auto">priv_result_t</h2>
```

不要写成 `<h2 seq="auto"><code>priv_result_t</code></h2>`。

## 表格

用户说「润色飞书表格」或「修改飞书表格」，且未同时给出格式 Skill 与目标列时：先读并执行 **feishu-table-format-choice**（列出候选、请选格式和列），选定前不要改表。从零建文档里的表仍直接用本节默认底。

- **表头行**所有 `<th>`：`background-color="rgb(236,226,254)"`（飞书浅紫），文字 `<p align="center"><b>…</b></p>`。
- **首列**（表头以下的 `<td>`）：`background-color="rgb(225,234,255)"`（飞书浅蓝），文字 `<p><b>…</b></p>`。
- 其余数据格默认白底、常规字重，不铺色；内容用 `<p>`，不要自动改成圆点列表。
- 必须写上述 rgb 字符串。不要用基础色 `purple`（过深）；不要写 `medium-purple`（表格里会被映射成浅紫，语义不准）。
- 仅当用户（或经 `feishu-table-format-choice` 选定后）要「硬约束圆点列表 / 单元格 ul」时，才读 `feishu-table-cell-bullets` 拆指定列。

### 首列不用代码格式

- 首列（含表头「产物」这类标签）一律普通正文 + `<b>`，禁止 `<code>` / `inline_code` / 等宽字体。
- 库名、头文件、`.so` / `.h` 等标识写在首列时也走普通加粗正文，不要当成行内代码。
- 其它列需要突出命令、头文件名时，仍可用 `<code>`（例如 `-lrigolos_priv`、`priv_protocol.h`）。

```xml
<table>
  <thead>
    <tr>
      <th background-color="rgb(236,226,254)" vertical-align="middle"><p align="center"><b>产物</b></p></th>
      <th background-color="rgb(236,226,254)" vertical-align="middle"><p align="center"><b>作用</b></p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td background-color="rgb(225,234,255)" vertical-align="top"><p><b>librigolos_priv.so</b></p></td>
      <td vertical-align="top"><p>业务程序 <code>-lrigolos_priv</code> 链接它</p></td>
    </tr>
  </tbody>
</table>
```

从 Markdown **新建**飞书文档时走 `markdown-to-feishu-doc`：本地生成已带本表样式与 `seq="auto"` 的 XML，一次 `docs +create --doc-format xml`。不要 Markdown 导入后再 `+fetch` 全文、不要对已有画板的文档 `overwrite`。已有文档缺色或手写序号时，用 `block_replace` 改那一张表或那一条标题。

## 代码块标题

每个「代码块」的标题都要全部改成实际含义。

飞书 `<pre>` 缺 `caption`（或为空 / 仅换行）时，界面一律显示「代码块」。创建、从 Markdown 转换、或事后编辑，都必须写成：

```xml
<pre lang="c" caption="priv_reboot 函数声明"><code>...</code></pre>
```

用 `{主题} {体裁}`：函数声明、签名模板、调用示例、命令行示例、配置示例。禁止 caption 为「代码块」「示例」「如下」或仅语言名。转换流程见 `markdown-to-feishu-doc`。

## 画板标题

每个画板增加实际含义标题。

标题放在**画板内部**画布顶部：独立 `text` / `text_shape` 节点，24px、斜体、常规字重、居中，宽度与图同宽。`text.italic` 必须为 `true`，`font_weight` 用 `regular`，不要加粗。不要用文档里画板上方的加粗段落代替；不要给 `<whiteboard>` 写 `caption`（会换成空画板）；不要用 section / frame 的 `title`。

Mermaid 整板 `--overwrite` 之后必须再增量追加标题节点。转换步骤见 `markdown-to-feishu-doc`。预览里标题被裁切时遵守 `feishu-whiteboard-text-visibility`。

源码节点里的 `<b>` / `<small>` / `<br/>` 写入飞书 Mermaid 后会变成字面量。必须按 `markdown-to-feishu-doc` Step 4b 改 raw 富文本：主题加粗、注解 11px 换行带括号，画板上不得出现 `<small>`。

## 画板时序图标题栏

飞书文档画板中的时序图，参与者标题栏字体必须加粗。

- 参与者标题栏（`life_line` 的 `text.font_weight`）设为 `bold`。箭头、消息、自调用说明保持 `regular`。
- 加粗后字形变宽。预览里若换行或被裁切，只加宽该标题框，不缩小字号。时序图加宽时保持标题框中心不动，避免生命线和箭头错位。
- 改已有画板时改 raw 节点后写回。不要用 Mermaid 整板重画，否则字重会回到常规。写回后导出预览，确认标题加粗且整行可见。文字被裁切时同时遵守 `feishu-whiteboard-text-visibility`。

## 画板时序图箭头方向

飞书文档画板中的时序图，线条按方向区分颜色。同一约定也用于 Markdown 与 HTML 里的时序图；暗色底上的自调用改用 `#E8EAED`，见 `mermaid-flowchart-layout` §4.1 与 `html-sequence-swimlane`。流程图的步骤箭头不用这张表。

| 方向 | 含义 | 线型 | 颜色 |
|---|---|---|---|
| 向右 | 请求、调用 | 实线 | `#3370FF` |
| 向左 | 返回、结果 | 虚线 | `#00A870` |
| 自调用 | 进程内部动作 | 实线 | `#1F2329` |

- 只改连线的 `style.border_color`，并把 `border_color_type` 设为 `1`。留在 `0` 时飞书按系统色绘制，自定义色会被忽略，线仍是黑色。
- 说明文字保持 `#1f2329`、常规字重。
- 小图不加图例。分层架构图的路径色不套这张表。
