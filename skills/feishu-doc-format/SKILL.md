---
name: feishu-doc-format
description: >
  个人默认飞书云文档排版：标题 seq=auto 自动编号（不手写 1. / 1.1）、标题不用代码格式，
  表格浅紫表头 rgb(236,226,254) + 浅蓝首列 rgb(225,234,255)，
  表头与首列加粗、首列不用代码格式。
  Use when creating or editing Feishu/Lark Docx or Wiki, 飞书文档,
  docs +create / +update, or converting markdown to Feishu documents.
  Takes precedence over lark-doc default table/heading styles; do not patch lark-doc.
---

# 飞书文档个人默认格式

写或改飞书云文档时默认采用下列格式。用户当场指定其他样式时以当场为准。
本 Skill 覆盖官方 `lark-doc` 里「表头用 light-gray / medium-gray」的建议。

**不要把本格式写进 `lark-doc/`。** `lark-cli update` 会同步覆盖官方 AI Skills；个人偏好只放本 Skill 和 `~/.cursor/rules/feishu-doc-format.mdc`。

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

- **表头行**所有 `<th>`：`background-color="rgb(236,226,254)"`（飞书浅紫），文字 `<p align="center"><b>…</b></p>`。
- **首列**（表头以下的 `<td>`）：`background-color="rgb(225,234,255)"`（飞书浅蓝），文字 `<p><b>…</b></p>`。
- 其余数据格默认白底、常规字重，不铺色。
- 必须写上述 rgb 字符串。不要用基础色 `purple`（过深）；不要写 `medium-purple`（表格里会被映射成浅紫，语义不准）。

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

Markdown 导入飞书后若表头/首列无色、未加粗、首列被包成代码，或标题仍手写序号、标题被包成 `<code>`，用 `docs +update` 按上表补齐：标题改为 `seq="auto"`、去掉手写前缀，并去掉标题上的 `<code>`。
