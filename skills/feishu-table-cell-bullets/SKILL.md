---
name: feishu-table-cell-bullets
description: >
  Use when the user explicitly asks to format a Feishu/Lark Docx table column
  as bullet lists: 圆点列表, 单元格列表, 硬约束拆条, ul/li, 按截图那种列表,
  服务端硬约束列, 或点名本 skill。
  Do not use for ordinary Feishu table create/edit, docs +create/+update,
  or markdown-to-Feishu conversion; those keep paragraph cells from feishu-doc-format.
---

# 飞书表格：约束列圆点列表

把某一列里「一条格子挤多条规则」改成单元格内 `<ul>`。表头浅紫、首列浅蓝等仍遵守 **feishu-doc-format**。本格式**不是**默认表格样式。

## 何时用 / 何时不用

**用：** 用户当场点名本 skill，或明确说把某列改成圆点列表 / 硬约束拆条。

**不用：** 只是写飞书表、改表、导入 Markdown。默认单元格继续用 `<p>`，不要主动拆成列表。

未点名时不要「顺便」套用。用户指定了列才改那一列；没指定则只改语义为多条约束的列（如「服务端硬约束」），其它列不动。

## 规则

1. **拆条**：按中文分号 `；` 拆成 `<li>`。一项一条；不要把无关句子硬拆。
2. **末项不分号**：除最后一项外，每条 `<li>` 末尾保留 `；`。
3. **单条保持段落**：整格只有一句（如「无」「同上，…」）用 `<p>`，不要包 `<ul>`。
4. **标识用 code**：路径、正则、枚举值、设备名用 `<code>`。首列仍禁止 `<code>`（feishu-doc-format）。
5. **不改语义**：只改结构。不要润色、合并或删约束。
6. **写入**：`lark-cli docs +update`，XML；单元格内写 `<ul><li>…</li></ul>`，不要用纯文本 `•`。

## 示例

原文一段：

```xml
<td vertical-align="top"><p>仅 <code>/dev/rtc</code> + 数字；<code>NULL</code> 则用 <code>/dev/rtc1</code></p></td>
```

改为：

```xml
<td vertical-align="top"><ul>
  <li>仅 <code>/dev/rtc</code> + 数字；</li>
  <li><code>NULL</code> 则用 <code>/dev/rtc1</code></li>
</ul></td>
```

单条不要改成列表：

```xml
<td vertical-align="top"><p>无</p></td>
```
