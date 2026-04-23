---
name: cards-to-drawio
description: 将"分层彩色卡片布局"架构图（来自 markdown-to-html skill 的 customfig / 由 .layer + .halbox 等 HTML/CSS 卡片绘制的图）转换为可在 draw.io 中继续编辑的 .drawio 文件，保持原有四层结构、颜色语义与跨列布局。Use when the user asks to convert layered card diagrams to drawio, or mentions "分层卡片转 drawio", "彩色卡片图转 drawio", "卡片布局转 drawio", "把这个图转换成 drawio", "convert layered cards to drawio", "card layout to drawio".
---

# 分层彩色卡片图 → Draw.io

将由 `markdown-to-html` skill 产出的"分层彩色卡片图"（四层结构 / 彩色 `.layer` / `.halbox` / `.customfig` 卡片）转换为等价的 Draw.io 文件，保持配色语义与几何布局，使其可在 draw.io 中继续编辑、再导出 SVG/PNG。

---

## 1. 适用范围

- 输入：HTML 片段（`<template>` 中的 `.customfig` / `.layer` / `.halbox` 结构）、Markdown 中描述的多层架构图、或一张已经渲染好的分层卡片截图。
- 输出：单个 `.drawio` XML 文件（`<mxfile>` 根节点）。
- 不适用：流程图、时序图、状态机（这些请用 `mermaid-to-drawio` 或直接保留 Mermaid）。

## 2. 文件命名与位置

- 与源 Markdown / HTML 同目录。
- 文件名：英文小写连字符，描述图的内容主体。例：`rxie-shmc-service-internal.drawio`。
- 不要追加 `-cards` / `-drawio` 后缀。
- 不要追加日期 / 版本号前缀（如 `2026-04-21-xxx.drawio`），这些元信息由源文档承载。

### 2.1 多图拆分原则（强制）

**一份源文档里有多张分层卡片图时，必须拆成多个独立 `.drawio` 文件，不得合并到一个 `mxfile` 的多个 `<diagram>` 页签里。**

理由：
- 每张架构图承担不同的语义职责（整体视图 / 子系统内部 / 数据流），应可独立引用、独立版本化、独立嵌入其他文档。
- 合并成多页签后，drawio 默认只渲染首页，VS Code 插件里切页签体验差，导出 PNG/SVG 需要逐页操作。
- 跨图交叉修改时，独立文件能避免误动其他页签。

命名约定（多图场景）：每份文件名用"主体对象 + 视角"命名，不要加序号前缀。例：

```
docs/specs/
  rxie-overall-layered-architecture.drawio      # 整体 6 层视图
  rxie-shmc-service-internal.drawio             # ShMC Service 内部
  rxie-hal-service-internal.drawio              # HAL Service 内部
  rxie-shmc-mcu-firmware-tasks.drawio           # MCU 固件任务
  rxie-zero-copy-dma-dataflow.drawio            # 零拷贝数据流
```

每份文件都是一个完整的 `<mxfile>`，内部只含一个 `<diagram>`。

**例外**：只有当用户明确要求"合并为一份 drawio 文件"/"多页签形式"时，才允许输出单 `mxfile` 多 `<diagram>`。默认总是拆分。

## 3. 画布参数（mxfile 骨架）

```xml
<mxfile host="app.diagrams.net" version="22.1.0" type="device">
  <diagram name="<diagram-name>" id="<unique-id>">
    <mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1040" pageHeight="700"
                  math="0" shadow="0" background="#0d1117">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 各 layer / card / arrow / legend cells -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**约定**：
- 画布宽度固定 `1040`（与 markdown-to-html 主题宽度匹配）。
- 高度按层数动态计算：`Σ(每层高度) + Σ(箭头说明高度) + 上下边距 30`。
- 背景必须设为 `#0d1117`（与 GitHub Dark / markdown-to-html 主题一致）。

## 4. 配色映射（与 markdown-to-html skill 完全对齐）

| 层语义 | 边框 | 填充 | 文字 |
|--------|------|------|------|
| I/O 边界 · MCU/外设通道 | `#58a6ff` 蓝 | `#0d2137` | `#79c0ff` |
| I/O 边界 · 对内服务 IPC | `#da3633` 红 | `#2d1215` | `#ffa198` |
| I/O 边界 · 运维 CLI | `#6e40c9` 紫 | `#1a1428` | `#d2a8ff` |
| 事件中枢 / 调度总线 | `#f0883e` 橙 | `#1a150d` | `#ffcc80` |
| 核心业务 / 数据面 | `#238636` 绿 | `#122117` | `#7ee787` |
| 基础设施 / 共享支撑 | `#30363d` 灰 | `#21262d` | `#8b949e` |
| 内核驱动 / 底层模块 | `#6e40c9` 紫 | `#1a1428` | `#d2a8ff` |
| 关键支柱（基础设施中的高亮） | `#238636` 绿虚线 | `#0a1e0a` | `#7ee787` |

**层外框**：`fillColor=#0d1117`，`strokeColor=` 取该层主色，`strokeWidth=2`。

## 5. 布局算法（等宽分列）

### 5.1 通用参数

- 画布左右内边距 `15`，每层内左右内边距 `10` → 内容区域 x ∈ `[25, 1015]`，可用宽 `W = 990`。
- 层与层之间留 `25~30` 用于箭头说明。
- 卡片之间 `gap = 10`。

### 5.2 N 列等宽公式

对 `N` 列布局，每个卡片宽度 `w = (W − (N−1) × gap) / N`：

| 列数 N | 卡片宽 w | 起始 x 坐标 |
|--------|---------|-------------|
| 2 | 490 | 25, 525 |
| 3 | 323 | 25, 358, 691 |
| 4 | 240 | 25, 275, 525, 775 |
| 5 | 190 | 25, 225, 425, 625, 825 |

### 5.3 高度参考

| 元素 | 高度 |
|------|------|
| 层标题文本（layer-label） | 30 |
| I/O 卡片（标题 + 1~2 行说明） | 85 |
| 中枢/业务卡片（标题 + 3~4 行） | 70~115 |
| 基础设施扁卡（单行） | 50 |
| 箭头说明（layer 之间） | 20~22 |

## 6. 单元格样式模板

### 6.1 层外框（带颜色边）

```xml
<mxCell id="L1box" value=""
        style="rounded=1;arcSize=2;fillColor=#0d1117;strokeColor=<层主色>;strokeWidth=2;"
        vertex="1" parent="1">
  <mxGeometry x="15" y="<层起 y>" width="1010" height="<层高>" as="geometry"/>
</mxCell>
```

### 6.2 层标题文本

```xml
<mxCell id="L1title" value="L1 · I/O 边界（4 类外部接口，全部挂在同一个 epoll 上）"
        style="text;html=1;align=center;verticalAlign=middle;fontColor=<层主色>;fontSize=14;fontStyle=1;"
        vertex="1" parent="1">
  <mxGeometry x="20" y="<层起 y + 7>" width="1000" height="30" as="geometry"/>
</mxCell>
```

### 6.3 内部卡片（彩色 box）

```xml
<mxCell id="L1c1"
        value="&lt;b style=&quot;font-size:13px&quot;&gt;① 卡片标题&lt;/b&gt;&lt;br&gt;&lt;br&gt;副标题/技术规格&lt;br&gt;补充说明"
        style="rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=<填充>;strokeColor=<边框>;fontColor=<文字>;fontSize=11;align=left;verticalAlign=middle;spacingLeft=10;spacingRight=8;"
        vertex="1" parent="1">
  <mxGeometry x="<列起 x>" y="<层起 y + 45>" width="<列宽>" height="<卡片高>" as="geometry"/>
</mxCell>
```

### 6.4 层间箭头说明（纯文本，无连线）

颜色按方向语义选择：入站 = 橙 `#f0883e`，出站 = 绿 `#3fb950`，命令回送 = 蓝 `#79c0ff`。

```xml
<mxCell id="arrow1" value="↓ 输入流说明 &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; ↑ 输出流说明"
        style="text;html=1;align=center;verticalAlign=middle;fontColor=#f0883e;fontSize=11;"
        vertex="1" parent="1">
  <mxGeometry x="15" y="<两层之间 y>" width="1010" height="20" as="geometry"/>
</mxCell>
```

### 6.5 高亮卡片（虚线突出）

```xml
style="...;dashed=1;strokeStyle=dashed;strokeColor=#238636;fillColor=#0a1e0a;fontColor=#7ee787;"
```

## 7. HTML → mxCell value 转义

drawio 的 `value` 字符串既支持 HTML（需 `html=1`），也是 XML 属性，需要双重转义：

| HTML 源 | drawio value 中写法 |
|---------|--------------------|
| `<b>` | `&lt;b&gt;` |
| `</b>` | `&lt;/b&gt;` |
| `<br>` | `&lt;br&gt;` |
| `&nbsp;` | `&amp;nbsp;` |
| 内联 style 属性 | `style=&quot;…&quot;` |
| 中文 / Unicode 箭头 ↓ ↑ → | 直接写，无需转义 |

**只允许使用** `<b>`、`<br>`、`<i>`、内联 `style=` 这几种最小子集，避免 drawio 渲染兼容问题。

## 8. 转换工作流（按此顺序执行）

```
任务进度：
- [ ] 1. 解析输入：识别层数 L、每层列数 Nᵢ、每个卡片的标题/副标题/颜色语义
- [ ] 2. 计算几何：按 §5 算每层 y 坐标、每列 x 坐标
- [ ] 3. 选配色：每层按 §4 表对号入座（找不到匹配语义时选最接近）
- [ ] 4. 写骨架：mxfile + mxGraphModel + root
- [ ] 5. 逐层产出：层外框 → 层标题 → 卡片们 → 紧跟的箭头说明
- [ ] 6. 底部加标题/图例（可选）
- [ ] 7. 写文件到与源同目录，命名按 §2
- [ ] 8. 提示用户打开方式（draw.io Desktop / VS Code 插件 / app.diagrams.net）
```

## 9. 完整最小示例

3 层（I/O 蓝 / 业务绿 / 基础设施灰），每层 2 列：

```xml
<mxfile host="app.diagrams.net" version="22.1.0" type="device">
  <diagram name="example" id="ex1">
    <mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" page="1"
                  pageWidth="1040" pageHeight="420" background="#0d1117">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="L1box" value="" style="rounded=1;arcSize=2;fillColor=#0d1117;strokeColor=#58a6ff;strokeWidth=2;" vertex="1" parent="1">
          <mxGeometry x="15" y="15" width="1010" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="L1title" value="L1 · I/O 边界" style="text;html=1;align=center;verticalAlign=middle;fontColor=#58a6ff;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="20" y="22" width="1000" height="30" as="geometry"/>
        </mxCell>
        <mxCell id="L1c1" value="&lt;b&gt;① 入站&lt;/b&gt;&lt;br&gt;&lt;br&gt;TCP 长连接" style="rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#0d2137;strokeColor=#58a6ff;fontColor=#79c0ff;fontSize=11;align=left;verticalAlign=middle;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="25" y="60" width="490" height="65" as="geometry"/>
        </mxCell>
        <mxCell id="L1c2" value="&lt;b&gt;② 出站&lt;/b&gt;&lt;br&gt;&lt;br&gt;Unix Socket" style="rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#0d2137;strokeColor=#58a6ff;fontColor=#79c0ff;fontSize=11;align=left;verticalAlign=middle;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="525" y="60" width="490" height="65" as="geometry"/>
        </mxCell>

        <mxCell id="arrow1" value="↓ 入站事件 &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp; ↑ 命令回送" style="text;html=1;align=center;verticalAlign=middle;fontColor=#f0883e;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="15" y="140" width="1010" height="20" as="geometry"/>
        </mxCell>

        <!-- L2 / L3 同理 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 10. 不要做的事

- **不要**画连线（mxCell `edge="1"`）来表达层间关系——用纯文本 arrow 说明，避免布局重叠。
- **不要**自己发明配色——必须从 §4 的色板里选，保证与 HTML / Markdown 视图视觉一致。
- **不要**让卡片宽度不等——同一层必须等宽（例外：基础设施层内"epoll 主循环"等关键支柱可放最右且更宽）。
- **不要**在 value 里使用 `<div>` `<span>` `<table>`——drawio 渲染会出错；只用 `<b>` `<br>` `<i>` + 内联 `style=`。
- **不要**改背景色——必须 `#0d1117`，否则浅色卡片在浅背景下完全看不见。
- **不要**生成后不告诉用户怎么打开——要给出 draw.io Desktop / VS Code Draw.io Integration / app.diagrams.net 的三种打开方式。
- **不要**把源文档里的多张卡片图合并进同一个 `mxfile` 的多个 `<diagram>` 页签——默认每张图输出一份独立 `.drawio` 文件（详见 §2.1）。只有用户显式要求"合并"时才例外。
- **不要**在文件名里加日期 / 版本号前缀（如 `2026-04-21-xxx.drawio`）——这些元信息由源文档承载，drawio 文件只保留内容主体名。

## 11. 与其他 Skill 的协同

- 与 [markdown-to-html](../markdown-to-html/SKILL.md) 配色与布局规范完全对齐，可双向往返。
- 产出的 `.drawio` 可被 [drawio-to-feishu-canvas](../drawio-to-feishu-canvas/SKILL.md) 直接导入飞书文档画板。
- 不要与 [mermaid-to-drawio](../mermaid-to-drawio/SKILL.md) 混用——后者专门处理 Mermaid 时序图，本 skill 只处理已经降级为彩色卡片的架构图。
