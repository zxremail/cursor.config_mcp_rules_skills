---
name: task-roadmap-timeline
description: >-
  Use when 用户要画项目推进时间计划表、任务计划时间表、阶段路线图、
  季度/月份泳道 roadmap、多阶段排期、重要时间节点横条、菱形里程碑、
  嵌套能力分组、或阶梯式开放时间线；以及对照「基础框架发布 / 模块化框架推广」
  这类左栏阶段 + 顶栏季度的计划图生成下一份排期。不要用 Mermaid gantt。
---

# 项目推进时间计划表（roadmap-tl）

这是**项目推进时间计划表**（阶段 × 时间的路线图），不是个人待办或工单甘特。
浅色横向布局：**左栏阶段、顶栏时间、顶行里程碑横条、泳道内圆角卡片**。
嵌套分组、菱形节点、阶梯排布都靠 CSS Grid，**禁止**用 Mermaid `gantt` / `flowchart` 硬凑。

配合 `markdown-to-html` sidecar：根元素 `.customfig.roadmap-tl`。也可 `--standalone` 出独立页。

## 工作流

1. 把用户口述/文档收成 YAML（字段见下）。时间用 **1-indexed 闭开区间**：覆盖第 2～3 格 → `start: 2, end: 4`。
2. 同一泳道里时间重叠的卡片必须换 `row`，禁止叠字。
3. 渲染：

```bash
python ~/.cursor/skills/task-roadmap-timeline/scripts/render.py plan.yaml \
  -o doc.figures/fig-roadmap.html
# 独立页：再加 --standalone
```

缺 PyYAML：`pip install pyyaml`。不要手写 Grid 数学，改 YAML 再渲染。
4. sidecar：CSS 拷进 `doc.figures/extra.css`（或让片段自带 `<style>`，脚本默认内联）。Markdown 写 `<!-- FIGURE: fig-roadmap -->`。
5. 浏览器核对下方清单。

完整样例（原图结构）：[examples/sample.yaml](examples/sample.yaml)。骨架：[templates/skeleton.html](templates/skeleton.html)。样式源：[templates/roadmap.css](templates/roadmap.css)。

## YAML 模型

```yaml
time_axis:
  ticks: ["2026 Q3", "2026 Q4", "2027 Q1"]   # 列数 = 长度
milestones:
  label: 重要时间节点                         # 可省略本块
  segments:
    - { text: 基础框架发布, start: 1, end: 3, icon: trophy }  # trophy | carrot | 任意 emoji
lanes:
  - title: 第一阶段：架构验证                  # 含「：」时自动拆成两行
    subtitle: ""                              # 可选，覆盖自动拆分
    theme: purple                             # ms|purple|orange|green|blue|teal|rose|slate
    subrows: 3                                # 泳道内子行数，必须 ≥ 最大 row
    items:
      - { text: 任务 A, start: 1, end: 2, row: 1 }
      - { marker: diamond, at: 2, row: 1 }    # 落在第 at 格左缘（季度分隔线）
      - { type: group-bg, start: 2, end: 5, row: 1, rowspan: 4 }
      - { type: group-title, text: 分组标题, start: 2, end: 5, row: 1 }
      - { type: group-foot, text: 底栏, start: 2, end: 5, row: 4 }
```

`start`/`end` 相对 **全局 tick**，分组内外同一套序号。`row` 从 1 起。

| 布局 | 怎么表达 |
|------|----------|
| 普通卡片 | `text` + `start/end/row` |
| 菱形节点 | `marker: diamond` + `at` + `row` |
| 嵌套分组 | 先 `group-bg`（垫底），再 `group-title` / 内部卡片 / `group-foot`，全用全局列号 |
| 阶梯瀑布 | 每张卡片单独 `row`，`start` 逐项右移 |

## 视觉规则

| 元素 | 做法 | 禁止 |
|------|------|------|
| 画布 | 浅灰底、无暗色 customfig 皮肤 | 套用架构图深蓝卡片墙 |
| 时间轴 | 顶栏居中季度/月份；全图浅灰竖虚线 | 表格、甘特条、隐藏虚线 |
| 行标签 | 左栏实心圆角块，阶段色，白字（黄行深字） | 把阶段名写进时间区 |
| 里程碑行 | **一条**圆角横条，内部分段 + 可选图标 | 拆成互不相连的黄卡片 |
| 任务卡片 | 浅底、无描边、大圆角、宽度 = 时长 | 拉满空闲格；同行重叠 |
| 分组 | 浅底大圆角容器 + 顶标题 + 可选底栏 | 当成多个无关卡片 |
| 菱形 | 空心旋转正方形，压在竖虚线上 | 用圆点、emoji 方块代替 |

主题（标签实色 / 卡片浅底）：

| theme | 实色 | 浅底 |
|-------|------|------|
| `ms` | `#F5C518` | `#FFF4B8` |
| `purple` | `#6B5CE7` | `#EDE7F8` |
| `orange` | `#F5A020` | `#FFE8C4` |
| `green` | `#2DB86A` | `#D4F3E0` |
| `blue` | `#4B90E2` | `#D4E8F8` |
| `teal` / `rose` / `slate` | 见 CSS | 见 CSS |

阶段超过 4 条时从 `teal` 起接着用，**相邻泳道必须不同色**。

## 收集输入时补全

用户没给结构时按这个问（能推断则不要问）：

1. 时间粒度与起止（默认季度）
2. 顶栏里程碑分段（没有就省略 `milestones`）
3. 泳道 = 阶段/工作流（每条一个主题色）
4. 每项：文案、起止格、是否检查点（菱形）、是否属于某分组、是否阶梯

不要把依赖关系画成箭头；本格式是排期，不是网络图。

## 打磨清单

- [ ] 顶栏 tick 数 = YAML `ticks` 长度 = 各泳道 `--rm-cols`
- [ ] 竖虚线穿过整张图（含黄条与卡片）
- [ ] 卡片宽度随 `end-start` 变化，没有无故拉满
- [ ] 同泳道重叠项已换行；分组底栏在内部卡片之下
- [ ] 菱形在季度边界上，不是格子正中
- [ ] 浅色皮肤，未串用暗色 `.customfig` 变量当字色
- [ ] 左栏标签两行时第一行是「第 N 阶段：」

## 明确不要

- 当成 `task-assignment-timeline`（任务落地分工：人员、人力、分支合入、底栏星星）
- Mermaid `gantt`、`timeline`、`flowchart` 冒充本图
- HTML `<table>` 做格子
- 深色分层架构卡（那是 `markdown-to-html` §3）
- 飞书画板/draw.io 当默认输出（用户明确要求再另转）
- 为塞进一格而过度缩写；宁肯加 `subrows`
