---
name: layer-action-capsule-diagram
description: >-
  Use when 用户要画分层能力改造图、层域行动清单、
  关/改/加/留/决策胶囊图、平台角标嵌在胶囊里、图例文字放进色块、
  L0–L7 / 硬件层卡片，或对照左栏层级 + 色带双卡片 + 行动胶囊；
  以及抱怨色块是图片、
  图例是小色点加框外文字、Flex 大白底盖住内容、角标和胶囊分离。
  不要用 Mermaid flowchart / gantt 硬凑。
---

# 分层行动胶囊图

浅色纵向层域图：**左栏层级名、横向色带、带内两张白卡片、卡片里嵌平台角标的行动胶囊**。
图例的关/改/加/留/决策是**包住文字的圆角色块**，不是色点。

飞书上传走 **lark-whiteboard**（raw OpenAPI）。本 skill 覆盖 whiteboard-cli 默认色板。
不确定是不是这种图 → 先读 `diagram-style-catalog`。

## 何时用 / 不用

| 用 | 不用 |
|---|---|
| 按栈分层的改造/能力清单（上 UI 下硬件） | 时间排期 → `task-roadmap-timeline` |
| 每条动作要标「关/改/加/留/决策」+ 平台 | 时序 → `html-sequence-swimlane` |
| 层与层之间有一条政策箭头 | 关系/流向架构 → `mermaid-flowchart-layout` |
| 浅色色带 + 白卡片 + 胶囊 | 深色卡片墙 → `markdown-to-html` §3；浅底白分组彩卡片 → `fig-tinted-layer-cards` |

## 结构（从上到下）

1. **标题**（居中，20 bold `#111827`）
2. **图例一行**：5 个行动胶囊（文字在色块内）+ 平台小标（色块内字母，名称在右侧）
3. **层**（可重复）：左栏层级名 | 色带（内嵌 1～2 张白卡片）
4. **层间箭头**：`↓ 一句话政策 ↓`（11 `#6B7280`，居中）
5. 卡片内：模块名（13 bold，跟层色）+ 灰色副标题 + **多枚行动胶囊**（自动换行）

```
标题
[关：…] [改：…] [加：…] [留：…] [决策：…]  [A] Android  [R] RIGOLOS  [共] A&R
L6～L7 │ ╔色带══════════════════════════╗
       │ ║ 白卡片          白卡片        ║
       │ ║ [共]改：…  [A]关：…          ║
       │ ╚════════════════════════════╝
              ↓ 层间政策 ↓
```

## 色板（硬规则）

行动胶囊：**填充 = 描边**，文字统一深灰，不靠字色区分动作。

| 动作 | 填充/描边 | 含义 |
|------|-----------|------|
| 关 | `#FECDD3` | 关闭 / 删除 |
| 改 | `#FDE68A` | 加固改造 |
| 加 | `#BBF7D0` | 新增控制 |
| 留 | `#BFDBFE` | 已有 / 维持 |
| 决策 | `#FDBA74` | 须进一步讨论 |

平台角标（白字）：

| 标 | 填充 | 默认名称 |
|----|------|----------|
| 共 | `#0F766E` | A&R |
| A | `#BE123C` | Android |
| R | `#1D4ED8` | RIGOLOS |

层色带（上浅下深、每层一色）。模块标题用对应深色：

| 层（上→下示例） | 带 fill | 带 border | 模块标题 |
|-----------------|---------|-----------|----------|
| 面板 / 远程 | `#EEF5FF` | `#93C5FD` | `#1E3A8A` |
| 应用 / 会话 | `#EEF2FF` | `#A5B4FC` | `#3730A3` |
| 防火墙 / 程控 | `#ECFEFF` | `#67E8F9` | `#0E7490` |
| 出厂 / 更新 | `#F3E8FF` | `#C4B5FD` | `#6B21A8` |
| 内核 / 构建 | `#ECFDF3` | `#86EFAC` | `#166534` |
| 硬件 / 信任根 | `#FFF7ED` | `#FDBA74` | `#9A3412` |

白卡片：fill `#FFFFFF`，border `#E5E7EB`。画布白底。左栏层级名 13 bold `#4B5563`。

## 几何

绝对坐标。不要 Flex `fill-container` 父级铺满。

| 元件 | 尺寸 | 圆角 | 边框 |
|------|------|------|------|
| 行动胶囊 | h=`23.5`，宽随文字 | 6 | `extra_narrow`，色=填充 |
| 胶囊内角标 | `18×15` | 3 | 同填充 |
| 图例行动胶囊 | h=`23.5`，宽=`文字宽+16` | 6 | 同填充 |
| 图例平台小标 | `12×12` | 3 | 同填充 |
| 色带 | 宽 `1290`，高随内容 | 12 | `narrow` |
| 白卡片 | 宽 `628`，高=色带高−24 | 10 | `extra_narrow` `#E5E7EB` |

胶囊内部（先角标，后文字，二者都在胶囊矩形内）：

- 角标距胶囊左 **7**，垂直居中
- 行动文字 11 regular `#1F2937`，在角标右侧 **gap 5**，垂直居中
- 文字右侧留 **6**
- 角标字母 9 bold `#FFFFFF`，落在 `18×15` 框内
- 胶囊宽 = `7 + 18 + 5 + 文字宽 + 6`

图例行动胶囊：**无角标**。文字 12 `#4B5563`，左右各 pad **8**，垂直居中。禁止「小色点 + 框外文字」。

层：色带 `x=166`；两卡片 `x=178` 与 `x=816`；色带间距 **28**（含箭头行）。

## 飞书画板画法

**REQUIRED SUB-SKILL：** 读写画板用 `lark-whiteboard`。本图用 OpenAPI `raw`，不要 Mermaid/SVG 充数。

每个色块 = `composite_shape` + `round_rect` + `fill_color`。文字 = 独立 `text_shape` 叠在色块上。

**禁止** `type: image` / 内嵌 SVG 当色块。改旧图时先把图片色块换成填充矩形。

z 序（小→大，后画在上）：

1. 色带
2. 白卡片
3. 行动胶囊（含图例行动胶囊）
4. 平台角标
5. 全部文字（标题、模块名、胶囊文、角标字母、箭头）

写回：去掉 `id` / `parent_id` / `children` 再 `--overwrite`。同一次逻辑更新复用同一个 `--idempotent-token`。

### 一枚胶囊（OpenAPI 骨架）

```json
[
  {
    "type": "composite_shape",
    "composite_shape": {"type": "round_rect"},
    "x": 345.15, "y": 137.75, "width": 140.7, "height": 23.5,
    "style": {
      "fill_color": "#fecdd3", "fill_color_type": 1, "fill_opacity": 100,
      "border_color": "#fecdd3", "border_color_type": 1, "border_opacity": 100,
      "border_width": "extra_narrow", "border_style": "solid",
      "border_radius": {"top_left": 6, "top_right": 6, "bottom_left": 6, "bottom_right": 6}
    }
  },
  {
    "type": "composite_shape",
    "composite_shape": {"type": "round_rect"},
    "x": 352.4, "y": 142, "width": 18, "height": 15,
    "style": {
      "fill_color": "#0f766e", "fill_color_type": 1, "fill_opacity": 100,
      "border_color": "#0f766e", "border_color_type": 1, "border_opacity": 100,
      "border_width": "extra_narrow", "border_style": "solid",
      "border_radius": {"top_left": 3, "top_right": 3, "bottom_left": 3, "bottom_right": 3}
    }
  }
]
```

角标字母 `共`、行动文字 `关：默认 HTTP :8080` 用 `text_shape` 叠在对应矩形上，z 大于色块。

## 常见错误

| 做法 | 结果 | 改成 |
|------|------|------|
| SVG/PNG 当粉红底、深蓝小标 | 不能改色、缩放发糊 | `round_rect` 填色 |
| 图例：12×12 色点 + 右侧文字 | 和正文胶囊不像一套 | 文字放进同色圆角底 |
| Flex 根/`fill-container` 铺满 | 大白底盖住下层，预览「空空如也」 | 绝对坐标；不要父级填色盖子 |
| 角标画在胶囊外 | 平台和动作拆成两枚 | 角标嵌在胶囊左内 |
| 行动文字用动作色（玫红/棕） | 和本色板不一致 | 胶囊内正文一律 `#1F2937` |
| 覆盖时保留 `parent_id` | `2890002` overwrite 失败 | 写回前剥 id/parent_id |
| 大色带 z 高于胶囊 | 色带盖住条目 | 按上面 z 序 |

## 检查清单

- [ ] 关/改/加/留/决策色值与上表一致
- [ ] 图例行动文字在色块内
- [ ] 每枚正文胶囊：左角标 + 右文字，都在同一圆角底里
- [ ] 画板 raw 里 `type: image` 为 0
- [ ] 无全画布白色 Flex 遮罩
- [ ] 层间有 `↓ … ↓` 政策句
- [ ] 导出 preview 能看到全部层，不是只剩标题/图例
