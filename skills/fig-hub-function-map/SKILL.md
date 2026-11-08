---
name: fig-hub-function-map
description: >-
  Use when 用户要画辐射功能全景、中心六边形 + 周围模块六边形 + 外侧圆角功能卡片、
  FUNCTION LIST 顶栏胶囊、虚线连到中心、催收/功能清单那种功能地图；
  或说按 INF 功能全景图画、hub-and-spoke、卫星模块、功能雷达图；
  或对照飞书辐射功能图 / Hub function map 人工精调稿落进本地 md 内联 SVG；
  或强调虚线锚点、不穿六边形心、簇心连卫星边。
  不要用：分层卡片墙、水平/垂直泳道、Mermaid flowchart / mindmap、
  贴顶时序、路线图、人员分工表、飞书「导出 SVG」（常是一张位图）。
---

# 辐射功能全景（内联 SVG）

中心一个主题六边形，周围一圈职责六边形，每个职责外侧再挂一组圆角卡片。虚线表示「属于」，不是时间轴。

不确定图种 → `diagram-style-catalog`。
交卷：目标 `.md` **内联 SVG**（开标签同一行、内部无空行）。禁止 Mermaid `flowchart` / `mindmap` 硬凑。禁止改 PNG / `![](图)`。禁止把飞书画板导出的 `<image href=…>` 当矢量真源。

对照（**连线精度优先对齐**，再套色板）：

- 代码金样：`20261005.230909.Windows.Driver/hellowdf-inf-function-map.md` §2
- 飞书人工精调 Hub function map：<https://rigolportal.feishu.cn/docx/YUV4dM9N1oTG3ExKMYScQBgSnVh>（**用 `lark-cli`**：`docs +fetch --as user --doc <url>` 得画板 token，再 `whiteboard +export --whiteboard-token … --output-type raw`；见 `lark-doc` / `lark-whiteboard`，勿先靠飞书 MCP）

锚点算法与自检清单 → `references/connection-geometry.md`（画线前 Read）。

整个底色用深彩色，以便暗色 Markdown 预览可读。

## 何时用 / 不用

| 用 | 不用 |
|---|---|
| 一个中心对象（一份 INF、一个产品、一个子系统）周围有 6～12 个职责块 | 上→下层栈 → `fig-dark-layer-cards`；左栏+顶胶囊平台图 → `fig-dark-platform-stack`；左栏层名+色带 → `fig-dark-layer-bands` |
| 每个职责还要列出 2～6 条字段/动作 | 谁的道 + 时间 → 泳道 |
| 读者要先看见「有哪些块」，不要先后顺序 | 先后顺序 → `mermaid-flowchart-layout` 或泳道 |
| 对照 FUNCTION LIST / 辐射功能图截图 | 思维导图层级 → 不要用本图冒充 mindmap |

时间顺序另画一张（可深色 Mermaid），不要画进辐射图。

## 结构

```
            [顶栏胶囊 FUNCTION LIST]
   [卡] [卡]                      [卡] [卡]
        (六边形 模块)     (六边形 模块)
                    (中心六边形)
        (六边形 模块)     (六边形 模块)
   [卡] [卡]                      [卡] [卡]
```

1. **顶栏**：左右短横线 + 圆角胶囊标题（短英文或中文专名，无句号）
2. **中心六边形**：整份对象的名字 + 一两行副标题
3. **卫星六边形**：8～12 个。再多就拆图，不要画第二圈
4. **外侧圆角卡**：每个卫星 2～6 张，一行短标签
5. **虚线**：两阶层——**卡组簇心 → 卫星外边缘**（每簇一条，`marker-end`）；**卫星外边缘 → 中心外边缘**（每卫星一条，卫星侧小菱形）。不得中心↔中心、卫星↔卫星。

## 连线（硬规则）

精度以金样与 `references/connection-geometry.md` 为准；禁止手戳「看起来像」的斜线。

| 规则 | 要求 |
|------|------|
| 端点 | 落在 flat-top 六边形**边线**上；`path` 不得穿过任何六边形内部 |
| 卡组 | 簇心 = 所属全部 `rect` 中心的平均值；多卡只出一条到卫星 |
| 卫星—中心 | 每卫星一条；**菱形**在卫星肩线锚点；**箭头**在中心外边 |
| marker | `<defs>` 按蓝/橙/紫虚线色各一，`refX="7"`，终点必须是外锚点 |
| 顶栏卡 | 指向上侧卫星时，落卫星朝下的边，不横穿胶囊 |
| 改图 | 动卡或卫星位必须**重算**锚点，禁止平移整图不还线 |

虚线样式：`stroke-dasharray="5 4"`、`stroke-width="1.6"`。详细射线—边形求交与可选脚本见 reference。

## 色板（硬规则）

画布 `#0D1117`。色块深底 + 字 `#FFFFFF`。禁止浅粉/浅橙实心卡。

| 槽 | 语义 | 六边形/卡片 `fill` | 描边 | 虚线 |
|----|------|---------------------|------|------|
| 蓝 | 身份、工具、安装入口、谁读取 | `#2E86AB` | `#1B4965` | `#58A6FF` |
| 橙 | 会改机器的拷贝、匹配、服务、改字段 | `#F18F01` | `#C67500` | `#F18F01` |
| 紫 | 显示名、绑定、本对象故意没有的项 | `#6A4C93` | `#4A3566` | `#C4B5FD` |
| 玫 | **只给中心** | `#A23B72` | `#7A2C55` | — |

固定件：顶栏胶囊底 `#161B22`、描边蓝、字白。菱形填色 = 该组虚线色。

图下用「蓝 / 橙 / 紫 / 玫」指模块时，`<span>` 字色必须等于本表 `fill`。正文 Mermaid 若没有玫/紫 `fill`，补 `classDef`（可只声明不挂节点）。

## 几何

根宽 **1080**，高随内容 **680～760**。中心约 `(540, 370)`，半径 72～80。卫星半径 40～46，均匀围一圈，不要叠进中心。

| 元件 | 建议 |
|------|------|
| 圆角卡 | `rx="6"`，高 24，宽 100～150；中文一行约 10 字 |
| 卡组 | 贴在所属卫星外侧，不要贴画布边（左边 x≥20） |
| flat-top 六边 | 卫星 `a≈36、b≈42`；中心加大；`polygon` 与 reference 顶点序一致 |
| 字体 | `Microsoft YaHei,sans-serif`；六边形主名 12 bold，副名 10，卡片 11 |

卡片增减就重算位置和 `viewBox`，禁止缩小字号去塞旧框。禁止 `<foreignObject>`。

## SVG 交卷（硬规则）

1. `<svg xmlns … viewBox="0 0 1080 H" preserveAspectRatio="xMidYMid meet" … style="max-width:100%;width:100%;height:auto;display:block;background:#0D1117;border-radius:8px;">` **同一行写完**。
2. SVG **内部禁止空行**。分组用注释或 `<g font-family="…" fill="#FFFFFF">`。`</svg>` 后可以空行。
3. **画序**：`<defs>`（marker）→ 底/顶栏 → 全部圆角卡 → 全部 `path`（按 reference 算锚点）→ 卫星 `polygon` → 中心 `polygon`（最后）。预览截断时优先保住卡片。
4. 可见标题用 `<text>`，与 `<title>` 同文。
5. 整数坐标。重复的 `font-family` / 白字放到外层 `<g>`。
6. 写完跑 `audit_mermaid.py`（收 `svg-blank` / `svg-open-split` / 图例 hex）。

## 预览陷阱（硬规则）

Markdown 预览（含 KaTeX）会把 `$…$` 当公式，从第一个 `$` 起把后面的 SVG 吃掉，只剩半截图 + `ParseError: KaTeX`。

- SVG 的 `<text>` **禁止出现 `$`**（含 `$KMDFVERSION$`、`仍有 $ 则勿安装`）。改成无美元符短句，例如 `KMDFVERSION`、`仍有占位符则勿安装`。
- 不要用 `&#36;` 碰运气。正文代码块里的 `$` 可以保留。
- 禁止超宽画布（≥1280）指望预览缩放；默认 1080。
- 飞书 `whiteboard +export --output-type svg` 常是一张 `<image>` 位图，不能当本图真源。

## 禁止项

- 浅色整图底、浅色实心卡
- Mermaid `flowchart` / `mindmap` 冒充辐射图
- 第二圈卫星、跨卫星连线、箭头当时间轴
- 中心/卫星几何心对连、线穿六边形、每张卡单独拉线到中心
- 卡片写成长段或两行（本图种一行）
- 中心不用玫、或给卫星涂玫
- 为预览空白改 `![](….png)`

## 填空（开画前）

```
标题（胶囊，短）：
中心：
  主名 / 副标题两行内
卫星（顺时针或按截图，8～12 个）：
  - 模块名 / 副标题 / 色槽（蓝橙紫）：
      - 卡片：短标签
.md 路径：
```
