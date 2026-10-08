---
name: cards-to-drawio
description: >-
  Use when converting layered colored-card architecture HTML (.layer / .halbox / customfig)
  to Draw.io (.drawio), or the user says 分层卡片转 drawio、彩色卡片图转 drawio、卡片布局转 drawio.
  Not for Mermaid sequence、胶囊图, or a generic 「转 drawio」 with no layered cards.
  Also: 新增卡片 drawio 格式、写进 SKILL、改 audit。
---

# 分层彩色卡片图 → Draw.io

其它图种（胶囊图、时序、时间表）不要走本转换；分诊见 `diagram-style-catalog`。时序走 `mermaid-to-drawio`。产出可被 `drawio-to-feishu-canvas` 导入。

**格式不准降级。** 几何、色板、mxCell 模板以 [references/cards-drawio.md](references/cards-drawio.md) 为准。XML **禁止手写、禁止 `Read` 整份 `.drawio`**。转换用脚本：

```bash
python3 ~/.cursor/skills/cards-to-drawio/scripts/pipeline.py convert \
  ./doc.figures/mermaid-0.html -o . --stem rxie-shmc-service-internal
python3 ~/.cursor/skills/cards-to-drawio/scripts/pipeline.py audit-drawio \
  ./rxie-shmc-service-internal.drawio
```

`ok: true` 才交差。多张卡片图多次 convert（不同 `--stem`），**不要 `--merge`**。

用户要加/改本 skill 硬格式：**不要只改本页。** 可扫描的（画布宽、背景色、禁 `edge`、禁日期前缀、禁 `--merge`）→ `cards-drawio.md` 一条 + `scripts/pipeline.py` 的 `audit-drawio` + `test_pipeline.py`；`convert` 必须一起改，禁止只改规范仍手写 XML。尚未脚本化的（最右支柱加宽）→ reference，改 convert 或拒手改 XML。本页只加清单一行。

## 执行顺序

1. 确认输入是 `.customfig` / `.layer` / `.halbox` HTML（sidecar 或 `<template>`）。截图先做成 sidecar HTML 再转。无分层卡片 → 停，改走 catalog。
2. 一份源里有多图：每张一个 `.drawio`，stem = 主体+视角（英文小写连字符）。禁止 `-cards`/`-drawio` 后缀、禁止 `YYYY-MM-DD-` 前缀。只有用户**明确**说「合并为一份/多页签」才允许多 `<diagram>`（脚本默认拒绝 `--merge`）。
3. `convert` → `audit-drawio`。
4. 告诉用户打开方式：draw.io Desktop / VS Code Draw.io Integration / [app.diagrams.net](https://app.diagrams.net)。

可跳过 cards-drawio.md 的条件：脚本已 convert 且 audit `ok`（几何/色板由脚本执行）。输入不是标准 `.layer` 结构、或要改色板/骨架时 **必须 Read** cards-drawio.md。

| 借口 | 实际 |
|------|------|
| 「XML 不长，手写更快」 | 走 convert；漏背景/等宽/转义 |
| 「多图画在一个 mxfile 方便」 | 默认各写一份；插件只渲染首页 |
| 「Read 一下 drawio 检查」 | audit-drawio 看摘要 |

## 格式（脚本已实现，不得改掉）

- 画布宽 **1040**，背景 **`#0d1117`**，高 = 各层高 + 箭头 + 上下边距 30。
- 内容 x∈[25,1015]，W=990，gap=10；N 列等宽：2→490@25/525；3→323；4→240；5→190。
- 层外框 `fillColor=#0d1117`，`strokeWidth=2`，主色描边。层间用**纯文本** arrow，**禁止** `edge="1"`。
- 色板（边框/填充/文字）：I/O MCU 蓝 `#58a6ff/#0d2137/#79c0ff`；IPC 红 `#da3633/#2d1215/#ffa198`；CLI/内核紫 `#6e40c9/#1a1428/#d2a8ff`；中枢橙 `#f0883e/#1a150d/#ffcc80`；数据/业务绿 `#238636/#122117/#7ee787`；基础设施灰 `#30363d/#21262d/#8b949e`；支柱绿虚线 `#238636/#0a1e0a/#7ee787` `dashed=1`。找不到语义就近选，**不要发明色**。
- 入站箭头字橙 `#f0883e`，出站绿 `#3fb950`，命令回送蓝 `#79c0ff`。
- value 双重转义；只用 `<b>` `<br>` `<i>` + 内联 `style=`；禁止 `<div>` `<span>` `<table>`。
- 同一层卡片等宽（例外：关键支柱可最右更宽——当前脚本尚未做「最右加宽」，需要时 Read 原文 §5 后改该层 HTML 列数或提需求，不要手改 XML 破等宽）。
- 高度参考：层标题 30、I/O 卡 ~85、业务 70–115、扁卡 50、箭头 20–22。

## 不要

连线表达层间关系；自创配色；浅色背景；多图合一页签；文件名加日期或 `-cards`；生成后不说怎么打开；把时序/胶囊当本 skill。
