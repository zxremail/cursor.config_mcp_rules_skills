---
name: html-sequence-swimlane
description: >-
  Use when HTML sequence diagram, 泳道时序, sequenceDiagram, 贴顶角色栏,
  sticky actors, seq-e2e, md2html customfig 时序图; 或长时序图、端到端冷启动、
  推荐阅读主图、阶段 0/阶段 1 分隔、阶段带、Note over 阶段。
  不是分层卡片墙、flowchart subgraph、甘特替代时序。
---

# HTML 泳道时序图（seq-e2e）

Markdown 预览继续用 Mermaid `sequenceDiagram`。生成的独立 HTML 里，复杂时序用本格式替换 sidecar，不要改成蓝/绿卡片墙。

## 何时用

- `md2html` 把 `sequenceDiagram` 降级为 `doc.figures/mermaid-N.html`
- 用户要求下滑时顶部模块保持可见
- 对照 Markdown 预览，HTML 时序必须「长得像 Mermaid」
- **长时序 / 端到端主图**：消息跨多个因果段落（谁先有电、谁后上场），需要「阶段 0 / 阶段 1」类阅读分隔 → **§长时序图阶段带**（Markdown 源和 HTML sidecar 同一套）

分层架构卡、数据流卡仍走 `markdown-to-html` §3 / §7.6 其它模式。
其它图种分诊 → `diagram-style-catalog`。

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
| 阶段 / Note | 橙色底 `#F18F01`、黑字，只覆盖相关列；长图用编号阶段带（见下节） | 通栏橙条（除非 Note 真覆盖全部角色）；用 flowchart `subgraph` / 甘特代替阶段带 |
| 自消息 `A->>A` | 生命线右侧 **回弯箭头**，线色 `#E8EAED`，右侧白字 | 纯文字无箭头；蓝/绿卡片；涂成向右蓝或向左绿 |
| 跨角色消息 | 向右实线 `#3370FF`，向左虚线 `#00A870`；标签在线上方，字色仍为 `#E8EAED` | 黑底胶囊切断线条；左右箭头同一灰色 |
| alt / opt | 左上色块 + 虚线框；分支名 `[实体键]` 叠在该箭头正中上方 | 紫底大卡片、else 写成左对齐长标题抢泳道 |
| 时间推进 | **一行一事**（一个 `.seq-row` 只放一条消息或一张 Note） | grid 自动把多条事件挤进同一行 |

文案尽量用 Mermaid 原文，不要为「塞进一列」过度缩写。

## 长时序图阶段带

对照：`come_x86_complete_power_on_sequence.md` §7 端到端冷启动主图。阶段带是**扫读分隔**，让读者在长图里知道「现在讲到哪一段」，不是 MCU/`enum`、也不是每条消息的旁注。

**Markdown 围栏**的同源规则在 `mermaid-flowchart-layout` 的 layout.md **§4.2**（写 `.md` 时走那条，不要只改 HTML）。本页管 sidecar 几何。

### 何时必须加

出现任一条就加阶段带，不要等用户再点名：

- 标题含「端到端 / 冷启动 / 推荐阅读主图」，或后文会按阶段开章节
- 角色 ≥4，且消息跨 **≥2 个因果段落**（电源轨换档、新角色上电、协议从握手进入数据）
- 一眼扫不完：大约 **≥8～10 条**消息，中间没有别的分组（`alt`/`opt` 只分组分支，不算阶段带）

短握手（三五条、同一对角色）不要硬编阶段号。

### 怎么切

按**读者会问的一个因果**切，不按函数名、文件名、代码步骤号切。

| 切法 | 例（冷启动主图） |
|------|------------------|
| 故事开始前已经成立的状态 | 阶段 0：仅数字背板 MCU 吃待机轨 |
| 谁被唤醒 / 哪根轨起来 | 阶段 1：唤醒 COMe EC；阶段 2：S3 开 12V |
| 跟随者开始干活 | 阶段 3：数字背板跟随主电源 |
| 真正换主角（BIOS / 枚举） | 阶段 4：模组出复位，BIOS 才启动 |

编号：**有「开始前已成立」用 0**，否则从 1。连续整数，不跳号。图前可写一句：`阶段划分是为了讨论，不是某一颗 MCU 里的 enum`。后文 `## 阶段 N：…` 与图上编号、冒号后因果对齐。

### 写法（Mermaid 源 = HTML 文案）

插在**该阶段第一条消息之前**，单独一行；`Note over` 只盖本阶段真正上场的角色，不要默认通栏。

```mermaid
Note over DMCU: 阶段 0：仅数字背板 MCU 吃待机轨；处理器板 MCU 尚未上电
Note over User,COMe: 阶段 1：唤醒 COMe EC（处理器板 MCU 仍未上电）
```

句式固定：`阶段 N：一句能扫到的因果`。禁止只写 `阶段 1`。一句里可补「谁还没上场」，不要把下一阶段的动作塞进来。

**阶段带 vs 普通 Note：** 编号阶段带 = 段落标题。局部事实（`PC8 已为高`、某路径用不上）继续用**不编号** `Note over`，不要升级成阶段。

HTML：每个阶段带独占 `.seq-row` + `.seq-note`，`grid-column` 与 `Note over A,B` 同范围。

### 禁止

| 借口 | 实际 |
|------|------|
| 消息已经很清楚，阶段带浪费行 | 长图读者先找段落再读箭头；主图靠阶段带扫读 |
| 用 flowchart `subgraph` / `rect` 框住一段更醒目 | `sequenceDiagram` 用橙色 Note；不要改成流程图 |
| 另画一张甘特就够了 | 甘特可作总览伴侣，**不能**替代主时序图里的阶段带 |
| 每条自调用都标阶段 | 阶段是段落，不是逐步注释 |
| Note 一律拉满所有泳道 | 只盖本阶段相关列 |
| 阶段带放在该段消息之后当小结 | 放段首，当标题 |
| 阶段号 = 固件状态机 | 讨论切片；代码没有对应 `enum` 也没关系 |

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

    <div class="seq-row"><div class="seq-note" style="grid-column:2/6">阶段 0：仅数字背板 MCU 吃待机轨</div></div>
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

向右请求 `#3370FF` 实线，向左返回 `#00A870` 虚线，自调用 `#E8EAED`。标签 `#E8EAED`，Note `#F18F01` / 字 `#1A1A1A`，alt `#6A4C93`，opt `#2D936C`。浅色飞书画板的自调用用 `#1F2329`，见 `feishu-doc-format`。

## 打磨清单

- [ ] 下滑时 `.seq-e2e-head` 贴在视口顶（祖先不要 `overflow:hidden` / `overflow-x:auto`，否则 sticky 失效）
- [ ] 自消息每条都有回弯箭头，箭头落在对应生命线上
- [ ] 跨列箭头从源列中心到目标列中心
- [ ] Note / 阶段条只盖 `Note over A,B` 的列范围
- [ ] 长图：段首有 `阶段 N：因果`；局部 Note 不编号；未改成 subgraph/甘特替代
- [ ] 无卡片化自消息、无切断线条的标签胶囊、无同行重叠
- [ ] 角色栏单行；过长用短名 + `title` 全称

## 参考实现

`digitalboard_for_SteppleEagle/ai.cursor/come_x86_complete_power_on_sequence.figures/`  
`mermaid-10.html` + `extra.css`（8 泳道冷启动时序）。
