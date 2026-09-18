---
name: html-sequence-swimlane
description: >-
  用 HTML/CSS 绘制贴近 Mermaid sequenceDiagram 的多泳道时序图：贴顶彩色角色栏、
  生命线、橙色 Note、自消息回弯箭头、标签在箭头上方、alt/opt 虚线框。
  配合 markdown-to-html 的 sidecar customfig 使用。
  Use when HTML sequence diagram, 泳道时序, sequenceDiagram 降级,
  贴顶角色栏, sticky actors, seq-e2e, or md2html customfig 时序图.
---

# HTML 泳道时序图（seq-e2e）

Markdown 预览继续用 Mermaid `sequenceDiagram`。生成的独立 HTML 里，复杂时序用本格式替换 sidecar，不要改成蓝/绿卡片墙。

## 何时用

- `md2html` 把 `sequenceDiagram` 降级为 `doc.figures/mermaid-N.html`
- 用户要求下滑时顶部模块保持可见
- 对照 Markdown 预览，HTML 时序必须「长得像 Mermaid」

分层架构卡、数据流卡仍走 `markdown-to-html` §3 / §7.6 其它模式。

## 工作流

1. 保留 `.md` 里的 Mermaid 块（预览用）。
2. 把 [templates/seq-e2e.css](templates/seq-e2e.css) 合并进 `doc.figures/extra.css`（或整文件拷入）。
3. 按下方结构写 `doc.figures/mermaid-N.html`，根元素 `.customfig.seq-e2e`。
4. `N` 必须等于 `md2html analyze` 对该块的编号；改块数量会错位。
5. `--seq-cols` 的列数 = 角色数；生命线 `<span>` 个数相同。
6. `md2html build` 后在浏览器核对：角色栏 sticky、自消息有回弯箭头、箭头标签在线上方、同行不重叠。

Windows：`PYTHONIOENCODING=utf-8 py -3 -m md2html build doc.md`

## 视觉规则（对照 Markdown 预览）

| 元素 | 做法 | 禁止 |
|------|------|------|
| 角色栏 | 每列一色圆角条，`white-space:nowrap`，`position:sticky;top:0` | 角色名折成两行 |
| 生命线 | 列中心竖线 `#8AA0B4` | 无线 |
| 阶段 / Note | 橙色底 `#F18F01`、黑字，只覆盖相关列 | 通栏橙条（除非 Note 真覆盖全部角色） |
| 自消息 `A->>A` | 生命线右侧 **回弯箭头** + 右侧白字 | 纯文字无箭头；蓝/绿卡片 |
| 跨角色消息 | 线连两列中心，**标签在线上方** | 黑底胶囊切断线条 |
| alt / opt | 左上色块 + 虚线框；分支名 `[实体键]` 叠在该箭头正中上方 | 紫底大卡片、else 写成左对齐长标题抢泳道 |
| 时间推进 | **一行一事**（一个 `.seq-row` 只放一条消息或一张 Note） | grid 自动把多条事件挤进同一行 |

文案尽量用 Mermaid 原文，不要为「塞进一列」过度缩写。

## 列坐标

角色从左到右 1-indexed。`grid-column: start / end` 的 **end 为开区间**。`--span` = 跨越的列数 = `end - start`。

```
User=1  DMCU=2  Gate=3  PSU=4  PMCU=5  COMe=6  FPGA=7  EP=8
User -> COMe     grid-column:1/7; --span:6
COMe -> Gate     grid-column:3/7; --span:4   （left 箭头，标签仍居中）
DMCU 自消息      grid-column:2/6; --span:4   （从生命线向右留出写字宽度）
Note over Gate   grid-column:3
Note over PMCU,COMe  grid-column:5/7
```

箭头线用 `left/right: calc(50% / var(--span))` 收到首尾列中心。自消息 `padding-left: calc(50% / var(--span))` 对齐该角色生命线。

## HTML 骨架

最小结构见 [templates/skeleton.html](templates/skeleton.html)。完整样式见 CSS 模板。要点：

```html
<div class="customfig seq-e2e">
  <div class="seq-e2e-head"> … 角色 … </div>
  <div class="seq-e2e-body">
    <div class="seq-lifelines" aria-hidden="true"><!-- N 个 span --></div>

    <div class="seq-row"><div class="seq-note" style="grid-column:2/6">阶段 0：…</div></div>
    <div class="seq-row"><div class="seq-self" style="grid-column:2/6;--span:4">自调用文案</div></div>

    <div class="seq-frame">
      <div class="seq-frame-tab">alt</div>
      <div class="seq-row">
        <div class="seq-call" style="grid-column:1/7;--span:6">
          <div class="seq-branch">[实体键]</div>
          <div class="seq-msg right"><span>面板键（与 PE3 或）</span></div>
        </div>
      </div>
      <div class="seq-else"></div>
      <!-- 下一条分支同样包在 seq-call 里 -->
    </div>

    <div class="seq-row"><div class="seq-msg left" style="grid-column:3/7;--span:4"><span>S3 有效</span></div></div>
  </div>
  <div class="seq-e2e-foot">可选脚注</div>
</div>
```

- 自消息：`.seq-self` 的 `::before/::after` 画回弯箭头，**不要**再套卡片。
- 跨列消息：`.seq-msg.right` / `.seq-msg.left`。
- opt：`.seq-frame.opt` + `seq-frame-tab` 文案 `opt`。
- 分支名必须放在 **同一条箭头的 `.seq-call` 里**，不要单独全宽居中（会落到错误列上）。

## 角色色

每列一种，相邻列要能分开。默认八色（可少可多）：

| 类 | 底 | 边 |
|----|----|----|
| `.c-user` | `#3d4a5c` | `#64748b` |
| `.c-dmcu` | `#2E86AB` | `#1B4965` |
| `.c-gate` | `#C67500` | `#F18F01` |
| `.c-psu` | `#b52d38` | `#E63946` |
| `.c-pmcu` | `#1E6B4E` | `#2D936C` |
| `.c-come` | `#4A3566` | `#6A4C93` |
| `.c-fpga` | `#0e7490` | `#22d3ee` |
| `.c-ep` | `#334155` | `#94A3B8` |

信号线 `#B0BEC5`，标签 `#E8EAED`，Note `#F18F01` / 字 `#1A1A1A`，alt `#6A4C93`，opt `#2D936C`。与 Mermaid `themeVariables` 对齐。

## 打磨清单

- [ ] 下滑时 `.seq-e2e-head` 贴在视口顶（祖先不要 `overflow:hidden` / `overflow-x:auto`，否则 sticky 失效）
- [ ] 自消息每条都有回弯箭头，箭头落在对应生命线上
- [ ] 跨列箭头从源列中心到目标列中心
- [ ] Note / 阶段条只盖 `Note over A,B` 的列范围
- [ ] 无卡片化自消息、无切断线条的标签胶囊、无同行重叠
- [ ] 角色栏单行；过长用短名 + `title` 全称

## 参考实现

`digitalboard_for_SteppleEagle/ai.cursor/come_x86_complete_power_on_sequence.figures/`  
`mermaid-10.html` + `extra.css`（8 泳道冷启动时序）。
