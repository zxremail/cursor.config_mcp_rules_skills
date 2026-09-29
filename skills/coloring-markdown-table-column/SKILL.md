---
name: coloring-markdown-table-column
description: >
  Use when the user asks to color or visually distinguish values in one column
  of a Markdown table (某一列上色、列着色、区分颜色、按取值着色),
  or when table cell text color did not change in preview. Not for Feishu
  tables, header-only styling, or when the user asks for cell backgrounds.
---

# 给 Markdown 表的某一列加区分字色

## Overview

只改**指定列**的**文字颜色**，按该列**实际出现的类别**上色。不要改底色。管道表单元格里的 `span style` 在 Cursor / MPE 预览里经常被剥掉，看起来像「没改」；这一列上色必须用 HTML `<table>` + `<font color>`。

「是/否」「共用/分叉」只是**映射示例**，不是本 Skill 的固定分类。下次列里是通过/失败、Linux/Windows、或任意枚举，同样按本流程，用用户指定或文中已有的色值。

## When to Use

- 「给某某列用不同颜色区分」
- 「按这一列的取值上色」
- 预览里字色没变化、和改之前一样

**不要用本 Skill：** 飞书云文档 → `feishu-doc-format` / `feishu-table-format-choice`。只给**表头**上浅紫字 → `markdown-export` §9（继续管道表 + span）。用户明确要**底色/背景**时不要套本 Skill 的「禁止底色」。

## 步骤

1. 定位 `.md`、表格（邻近标题或表头）、列名。多表时只改用户点名的那张。
2. 列出该列互异取值，做成字色映射：
   - 用户当场给了对应关系 → 用用户的。
   - 文中已有图例或同文档其它图的色义 → **复用那些色值**。
   - 都没有 → 再问一句，或对两类取值用下面的默认示例色（不是强制语义）：`#5BE49B` 与 `#FFB020`。三类及以上不要猜，先问。
   - 一格写了两类 → **拆成两个** `<font>`，不要混成第三种色。
3. 仅把**这一张表**改成 HTML（已是 HTML 则只改目标列）。其它列、其它表不动。表头字色仍用 `#C9A0FF`。
4. 目标列每个数据格：`<font color="#……"><b>原文</b></font>`。禁止 `background-color`、禁止给 `<td>` / `<th>` 铺底、禁止文档级 `<style>` 改背景。
5. 表上方一行图例（同样只用 `<font color>`，无底色）。提醒用户刷新预览。

## 目标列单元格（示例：两类取值）

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
| 列不是是/否就套不上本 Skill | 任意类别列都适用；是/否只是示例 |

## 红旗

- 管道表数据格靠 `span` / `**` 冒充上色
- 出现 `background` / `background-color` / 色块 padding
- 为上色改了未点名的列或其它表
- 把一格里的两类取值涂成单一中间色
- 把「是/否、共用/分叉」当成唯一允许的分类
