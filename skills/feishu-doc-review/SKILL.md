---
name: feishu-doc-review
description: >-
  Use when reviewing another author's Feishu/Lark Docx or Wiki (技术方案、排查记录、实验记录、方案草稿、需求/设计文档),
  or when the user says 飞书文档review、评审意见、审一下这份飞书、帮我review这篇文档、文档评审,
  or pastes a feishu.cn / larksuite.com /docx/ or /wiki/ URL to review.
  Not for code PR/Bugbot/security review, dual-doc FAQ, or AI成果说明填报.
  Also: fetch 落盘、extract 大纲、写进 SKILL、改 extract。
---

# 飞书文档 Review

审**别人写的**飞书云文档。默认产出独立「评审意见」，不改源文档、不发飞书评论。

**未 extract 不评审。** 禁止凭标题、记忆或对话摘要下结论。表、次数、截图、版本、外链以切片为准；读不到写「未见 / 无法复核」。**评文档，不重写文档。** 回复用简体中文。

**大文件不准进对话。** `+fetch` 重定向落盘；不要 `Read` fetch JSON / markdown 全文 / `source.txt`。只读 extract 的 JSON；核对主张时再 `Read` `sections/*.txt`。评审正文和 P0/P1 判断**仍由模型写**。认证失败才 Read `lark-doc` / `lark-shared`。

```bash
lark-cli docs +fetch --doc "<URL>" --as user --doc-format markdown \
  > ./_review_out/src0.json
python3 ~/.cursor/skills/feishu-doc-review/scripts/pipeline.py extract \
  ./_review_out/src0.json -o ./_review_out --url "<同一条原始 URL>"
```

stdout：`title`、`revision_id`、`headings`、`empty_or_short_headings`、`priority_section_files`（结论/风险/附录/变更/WIP）、表/图/画板计数。配套 FRS 同样落盘再 extract，不要把第二份全文灌进对话。工作目录 `_review_out`，用完删除。

用户要加/改本 skill 硬格式：**不要只改本页。** 可扫描的（unwrap、空章节、优先节名）→ `scripts/pipeline.py extract` + 单测。书脊/分级/类型重点 → `template.md` 与 [references/review.md](references/review.md)，extract 不能代替评审。

## 执行顺序

1. 用户给 `/docx/` 或 `/wiki/` URL（含 `doubao.com`）。无链接则先问，不要审本地臆造稿冒充飞书评审。
2. `+fetch` **必须 `>` 落盘**（可另存一份 `--scope outline` 到 `outline-cli.json`，同样不打进对话）。截断则分页再 extract。
3. 看 extract JSON。优先 Read `priority_section_files` 切片，再按主张补读其它节。画板/图只有 token 时：结论若依赖图，标「证据不可复核」并降级主张；需要核对再 `+media-preview`，预览也不要把 raw 读进对话。
4. 写评审前 **Read** [template.md](template.md)。类型重点、P0/P1/P2 定义、回写步骤 → [references/review.md](references/review.md)。领域专节可插在总体评价之后，**书脊 1～7 不能缺**。
5. 评审 md 存工作区：`{英文短名}-review.md`（kebab-case）。图表默认不加；仅成熟度分叉/选型/会后顺序才用 Mermaid（走 `markdown-export`）。
6. 聊天只给：**总体判断 + P0 列表 + 优先三件事 + 短摘要** + 本地路径。全文不必再贴，除非用户要粘贴。

默认只读：不 `docs +update`、不 `drive +add-comment`。用户明确说「写回原文 / 发评论 / 贴到文档」才按 review.md §3 回写。

| 借口 | 实际 |
|------|------|
| 「短文档直接看 fetch stdout」 | 一律落盘 + extract |
| 「先总结再挑刺」 | 先总体判断和 P0 |
| 「作者更熟不宜质疑」 | 评的就是主张是否被证据撑住 |
| 「没图就算了」 | 结论依赖它则标不可复核 |
| 「帮忙把文档改好」 | 未要求回写则只出意见 |
| 「问题都是建议」 | 必须有 P0/P1/P2；确无 P0 写「未见 P0」及依据 |

红旗：fetch 没重定向；或开始写评审却还没打开 template.md。

## 硬规则（不得降级）

1. 不编造；先找打架（结论 vs 附录、表 vs 正文、图 vs 图注、主张 vs 证据）。
2. P0：内部矛盾、图文证伪、安全/不可上仪器、数字自洽失败、未完成却当基线。P1 证据弱。P2 结构/空节。
3. 「优先改三件事」必须能独立执行。短摘要无表、无 Mermaid。
4. 不要把作者的下一步计划当成已经完成的验证；空标题/WIP 不得当结论依据。
