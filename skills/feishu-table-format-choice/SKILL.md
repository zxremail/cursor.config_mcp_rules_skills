---
name: feishu-table-format-choice
description: >
  Use when the user says 润色飞书表格, 修改飞书表格, 改飞书表格, 表格排版,
  polish/edit a Feishu/Lark Docx table, or asks to restyle a table without
  naming both a format skill and the target columns.
  Do not use for new-doc creation, whiteboard, or when format plus columns
  are already explicit.
---

# 飞书表格：先选格式和列

用户说「润色飞书表格」或「修改飞书表格」，且**尚未同时指定格式 Skill 与目标列**时：先列出候选、请用户选择，**选定前不要改表**。

底层读写仍走 **lark-doc**；表头/首列配色仍以 **feishu-doc-format** 为底。列级样式只在用户选中对应 Skill 后套用。

## 流程

1. **定位表**：有文档 URL 则 `docs +fetch` 读出表头列名。没有 URL 先问 URL。多表时列出表（用首列表头或邻近标题），请用户指定一张。
2. **列出候选 Skill**：扫描 `~/.cursor/skills/feishu-table-*/SKILL.md`，再加上 `feishu-doc-format`。对每个候选给出 **name + 一句话**（从该 Skill 的 overview / 首段压缩，不要贴全文）。当前已知：

   | Skill | 作用 |
   |---|---|
   | `feishu-doc-format` | 默认底：浅紫表头、浅蓝首列、单元格段落；不拆圆点列表 |
   | `feishu-table-cell-bullets` | 指定列：多条约束按 `；` 拆成单元格内圆点列表 |

   目录里新出现的 `feishu-table-*` 也要列入，不要只背上表。
3. **请用户选两次**（一次不要省）：
   - **格式**：选哪个 Skill（可多选：底 + 列级）。
   - **列**：按表头列名选，要改哪些列。`feishu-doc-format` 作用于整表底色/首列时，列可选「整表」。
4. **提问方式**：有 `AskQuestion` 就用它（两题：格式、列；列 `allow_multiple`）。否则用编号列表问，等回复。
5. **再动手**：读用户选中的 Skill 并只改选定列。未回复则停。

## 不要抢跑

| 借口 | 处理 |
|---|---|
| 「默认格式就行，先改了」 | 用户说润色/改表时必须先问 |
| 「硬约束列很明显」 | 仍要列出列名请用户选 |
| 「只有一个列级 Skill」 | 仍要列出，包含默认底 |

用户本轮已经点名 Skill **并且** 说出列名（或「整表」）→ 跳过提问，直接读该 Skill 执行。
