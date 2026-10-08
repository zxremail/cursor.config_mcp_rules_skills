---
name: mermaid-to-drawio
description: >-
  Use when converting a Mermaid sequenceDiagram to Draw.io (.drawio),
  or the user says 时序图转 drawio、sequenceDiagram 转 drawio、生命线/角色栏转 drawio.
  Not for flowchart、分层卡片、胶囊图, or a generic 「转 drawio」 with no sequence diagram.
---

# Mermaid 时序图 → Draw.io

flowchart / 分层卡片 / 胶囊图不要走本转换；分诊见 `diagram-style-catalog`。分层卡片 HTML → drawio 走 `cards-to-drawio`。产出可被 `drawio-to-feishu-canvas` 导入。

**格式不准降级。** 箭头色、生命线、标签分离、矩形参与者以 [references/sequence-drawio.md](references/sequence-drawio.md) 为准。XML **禁止手写、禁止 `Read` 整份 `.drawio`**。转换用脚本：

```bash
python3 ~/.cursor/skills/mermaid-to-drawio/scripts/pipeline.py convert \
  ./doc.md -o . --stem i2c-init-sequence
python3 ~/.cursor/skills/mermaid-to-drawio/scripts/pipeline.py audit-drawio \
  ./i2c-init-sequence.drawio
```

`ok: true` 才交差。输入可以是 `.mmd` 或 Markdown 里的 ` ```mermaid ` 围栏（只处理 `sequenceDiagram`）。

## 执行顺序

1. 确认输入是 Mermaid **sequenceDiagram**。flowchart → `mermaid-flowchart-layout` / catalog；分层卡片 → `cards-to-drawio`。不是时序 → 停。
2. `--stem` = 主体+视角（英文小写连字符，如 `i2c-init-sequence`）。禁止 `YYYY-MM-DD-` 前缀。术语英文、说明中文：转换前把消息文案按此改好再喂脚本。
3. `convert` → `audit-drawio`。
4. 告诉用户打开方式：draw.io Desktop / VS Code Draw.io Integration / [app.diagrams.net](https://app.diagrams.net)。

可跳过 sequence-drawio.md 的条件：脚本已 convert 且 audit `ok`（色板/箭头/生命线由脚本执行）。要改自调用几何、Note/alt/loop、或色板时 **必须 Read** sequence-drawio.md。

| 借口 | 实际 |
|------|------|
| 「XML 不长，手写更快」 | 走 convert；漏虚线生命线/标签分离/自调用竖箭 |
| 「自调用画个小环好看」 | 禁止环形；垂直向下、落在生命线中心 |
| 「Read 一下 drawio 检查」 | audit-drawio 看摘要 |

## 格式（脚本已实现，不得改掉）

- 文件 `.drawio`；stem 英文小写连字符。
- 自调用：**垂直向下**实线 `#000000`，居中在生命线上；禁止环形 / `curved=1`。
- 向右调用 `#0000FF`；向左返回 `#00AA00`。
- 消息文字是独立 `mxCell`，`fillColor=none`，不写在箭头 `value` 上。
- 参与者 **矩形** `rounded=0`，白字；色板循环：`#2E86AB` / `#E63946` / `#2D936C` / `#F18F01` / `#A23B72` / `#6A4C93`（及对应描边，见 reference）。
- 生命线：参与者下方垂直 **虚线** `dashed=1`。
- 脚本暂不渲染 `Note` / `alt` / `loop` / `opt`（解析时跳过）。需要这些块时 Read sequence-drawio.md 后改脚本，不要手写 XML。

## 不要

flowchart/卡片当本 skill；环形自调用；箭头上带底色标签；圆角/圆形参与者；文件名加日期；生成后不说怎么打开；`Read` 整份 `.drawio`。
