---
name: feishu-doc-format
description: >
  个人默认飞书云文档排版：标题 seq=auto 自动编号（不手写 1. / 1.1），
  表格浅紫表头 rgb(236,226,254) + 浅蓝首列 rgb(225,234,255)。
  Use when creating or editing Feishu/Lark Docx or Wiki, 飞书文档,
  docs +create / +update, or converting markdown to Feishu documents.
---

# 飞书文档个人默认格式

写或改飞书云文档时默认采用下列格式。用户当场指定其他样式时以当场为准。
本 Skill 覆盖 `lark-doc` XML 里「表头用 light-gray / medium-gray」的建议。

## 标题

- 每一个正文标题写 `seq="auto"`。
- 标题文本不手写 `1.`、`1.1`、`一、` 等前置序号。
- 层级连续、从章开始：`<h1>` 章、`<h2>` 节，不要从 `<h2>` 起篇（否则自动编号对不齐 `1` / `1.1`）。
- 插入或删除同级标题后，飞书会自动重排（例如原 `1` 变为 `2`，`1.1` 变为 `2.1`）。
- 仅当用户明确要求公文手写序号（`一、` / `（一）`）时才不用 `seq="auto"`。

```xml
<h1 seq="auto">读前须知</h1>
<h2 seq="auto">你实际在用的是什么</h2>
```

## 表格

- **表头行**所有 `<th>`：`background-color="rgb(236,226,254)"`（飞书浅紫），文字 `<p align="center">`。
- **首列**（表头以下的 `<td>`）：`background-color="rgb(225,234,255)"`（飞书浅蓝）。
- 其余数据格默认白底，不铺色。
- 必须写上述 rgb 字符串。不要用基础色 `purple`（过深）；不要写 `medium-purple`（表格里会被映射成浅紫，语义不准）。

```xml
<table>
  <thead>
    <tr>
      <th background-color="rgb(236,226,254)" vertical-align="middle"><p align="center">产物</p></th>
      <th background-color="rgb(236,226,254)" vertical-align="middle"><p align="center">作用</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td background-color="rgb(225,234,255)" vertical-align="top"><p>首列内容</p></td>
      <td vertical-align="top"><p>说明</p></td>
    </tr>
  </tbody>
</table>
```

Markdown 导入飞书后若表头/首列无色、或标题仍手写序号，用 `docs +update` 按上表补色，标题改为 `seq="auto"` 并去掉手写前缀。
