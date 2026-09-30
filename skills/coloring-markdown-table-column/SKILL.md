---
name: coloring-markdown-table-column
description: >
  Use when the user asks to color or visually distinguish values in one column
  of a Markdown table (某一列上色、列着色、区分颜色、按取值着色、按语义着色),
  or when table cell text color did not change in preview, or when a Mermaid
  fence right after an HTML table shows as raw source / 乱码 / `{data-source-line=`.
  Not for Feishu tables, header-only styling, or when the user asks for cell backgrounds.
---

# 给 Markdown 表的某一列加区分字色

## Overview

只改**指定列**的**文字颜色**。颜色跟的是这一列的**语义类别**，不是「每个不同字符串一种色」。不要改底色。管道表单元格里的 `span style` 在 Cursor / MPE 预览里经常被剥掉，看起来像「没改」；这一列上色必须用 HTML `<table>` + `<font color>`。

「是/否」「共用/分叉」只是**某次列语义下的映射示例**，不是固定分类表。列义变了，类别和配色跟着变。

## When to Use

- 「给某某列用不同颜色区分」
- 「按这一列的取值上色」
- 预览里字色没变化、和改之前一样
- 给表上色后，紧挨着的 mermaid 变成源码 / 乱码 / `{data-source-line=`

**不要用本 Skill：** 飞书云文档 → `feishu-doc-format` / `feishu-table-format-choice`。只给**表头**上浅紫字 → `markdown-export` §9（继续管道表 + span）。用户明确要**底色/背景**时不要套本 Skill 的「禁止底色」。

## 步骤

1. 定位 `.md`、表格（邻近标题或表头）、列名。多表时只改用户点名的那张。
2. **先读列义，再上色。** 用列名、邻近小节、图例，判断这一列在区分什么（例如：是否共用源码、是否通过、平台）。把单元格归进这些语义桶，而不是按字面去重：
   - 同一语义、措辞不同 → **同色**（如「是」与「是（整份头文件）」）。
   - 对立语义 → **对比色**（如共用 vs 不共用）。
   - 一格含两类语义 → **拆成两个** `<font>`，不要涂成中间色。
   - 用户当场给了映射 → 用用户的。文中已有图例/同文档色义 → **复用**。
   - 语义桶 ≥3 且用户没给色 → 先问，不要按字符串数 mermaid 色板轮询。
   - 两类且无指定时，可用 `#5BE49B` / `#FFB020` 作对比色；哪边用绿哪边用橙仍跟**列义**（肯定/达成/共用偏绿，否定/分叉/失败偏橙），不要对调乱套。
3. 仅把**这一张表**改成 HTML（已是 HTML 则只改目标列）。其它列、其它表不动。表头字色仍用 `#C9A0FF`。
4. 目标列每个数据格：`<font color="#……"><b>原文</b></font>`。禁止 `background-color`、禁止给 `<td>` / `<th>` 铺底、禁止文档级 `<style>` 改背景。
5. 表上方一行图例写**语义桶 → 色**，不是「每种原文 → 色」。提醒用户刷新预览。
6. **`</table>` 后面必须空一行**，再写任何 Markdown（尤其 `` ```mermaid ``、标题、列表）。CommonMark 把 HTML 块吃到**空行**为止；`</table>` 紧挨围栏时，预览会把 mermaid **当原文吐出来**（一整行源码、`{data-source-line=`、看起来像乱码）。表改成 HTML 后必须看紧随其后的块，不能只改表本身。

反例：`</table>` 下一行直接 `` ```mermaid ``（只有换行、没有空行）→ 预览乱码。

正例：`</table>` 与 `` ```mermaid `` 之间空一行。

## 目标列单元格（示例：列义是「是否共用同一份源码」）

```html
<td><font color="#FFB020"><b>否</b></font></td>
<td><font color="#5BE49B"><b>是</b></font></td>
<td><font color="#5BE49B"><b>声明共用</b></font>、<font color="#FFB020"><b>实现不共用</b></font></td>
```

## 借口对照

| 借口 | 实际 |
|------|------|
| 管道表里写 `span style="color"` 就行 | 预览常剥掉，用户会说「文字颜色没有变化」 |
| 底色比字色更明显，先铺底 | 默认只要字色；未要求底色就禁止 `background` |
| markdown-export 说不要改成 HTML 表 | 那条只管**表头**浅紫字；**数据列区分色**必须 HTML |
| 整表、首列一起上色更好看 | 只改用户点名的列 |
| `td style="color"` 和 span 一样省事 | 用 `<font color>`；`style` 在部分预览里同样无效 |
| 列不是是/否就套不上本 Skill | 任意列都适用；先按该列语义分桶 |
| 有几个不同字符串就用几种色 | 按语义归类；同义不同词同色 |
| 表改完了，后面原来的 mermaid 不用动 | 管道表改成 HTML 后，`</table>` 会把无空行的后续 Markdown 吞进 HTML 块 |
| 表和围栏之间已经换行了 | 换行不够，必须是**空行**（中间不能只有 `</table>\n```） |

## 红旗

- 管道表数据格靠 `span` / `**` 冒充上色
- 出现 `background` / `background-color` / 色块 padding
- 为上色改了未点名的列或其它表
- 把一格里的两类语义涂成单一中间色
- 把「是/否、共用/分叉」当成唯一允许的分类
- 忽略列名、按单元格原文各涂一色
- `</table>` 下一行就是 `` ```mermaid ``（或其它围栏/标题），中间没有空行
- 预览里 mermaid 变成源码、`{data-source-line=`、或用户说「乱码」却只去改图语法
