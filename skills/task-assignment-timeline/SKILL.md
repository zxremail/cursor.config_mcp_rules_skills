---
name: task-assignment-timeline
description: >-
  Use when 用户要画任务落地分工时间表、人员分工排期、人力投入、
  项目空间/任务空间分支、Git 式主干与特性分支合入、人员胶囊任务、
  底栏星星里程碑，或对照顶栏阶段条 + 日期虚线 + 人员泳道的落地分工图。
  不要用项目推进时间计划表（那是阶段卡片泳道，无人员）。不要用 Mermaid gantt。
---

# 任务落地分工时间表（assign-tl）

这是**任务落地分工时间表**：谁在何时做哪块、占多少人力、工作从哪条分支长出再合回。
不是项目推进时间计划表（`task-roadmap-timeline`，阶段×季度卡片）。

浅色横向图：**顶栏阶段色条、日期虚线、空间分支线、人员胶囊、底栏星星**。
用 CSS + 少量 SVG，**禁止** Mermaid `gantt` / `flowchart`。
阶段×时间路线图不是本图 → `task-roadmap-timeline`。不确定图种 → `diagram-style-catalog`。

配合 `markdown-to-html` sidecar：根元素 `.customfig.assign-tl`。也可 `--standalone`。

## 工作流

1. 收成 YAML。时间坐标是 **tick 浮点**：`1` = 第一个日期，`n` = 最后一个日期，`0` = 左端（开始），`n+1` = 右端（结束）。`start`/`end` 半开，可小数（如 `2.3`）。
2. 同一人员泳道里时间重叠的胶囊必须换 `row`。
3. 渲染：

```bash
python ~/.cursor/skills/task-assignment-timeline/scripts/render.py plan.yaml \
  -o doc.figures/fig-assign.html
# 独立页：再加 --standalone
```

缺 PyYAML：`pip install pyyaml`。不要手写百分位，改 YAML 再渲染。
4. sidecar：脚本默认内联 CSS。Markdown 写 `<!-- FIGURE: fig-assign -->`。
5. 浏览器核下方清单。

样例：[examples/sample.yaml](examples/sample.yaml)。样式：[templates/assign.css](templates/assign.css)。骨架：[templates/skeleton.html](templates/skeleton.html)。

## YAML 模型

```yaml
title: 任务落地分工时间表
time_axis:
  ticks: ["2026/6/30", "2026/8/30", "2026/9/30"]  # 竖虚线 + 底栏星星对齐于此
  weights: [2, 1]     # 相邻日期之间的相对宽度，默认全 1；长度必须 = ticks-1
  lead: 0.4           # 第一个日期左侧（「开始」）
  tail: 0.4           # 最后日期右侧（「结束」）
phases:
  - { text: 开始, region: lead, theme: pink, icon: start }
  - { text: 阶段一, start: 1, end: 2, theme: orange }
  - { text: 结束, region: tail, theme: mint }
milestones:
  - { text: 基线建立, at: 1 }          # 底栏星星，at 对齐某个日期
lanes:
  - type: branch
    title: 白尾雷鸟项目空间
    line: { text: 白尾雷鸟分支, theme: main }
  - type: branch
    title: 性能优化任务空间
    line: { text: LXI 开发分支, theme: feature, color: green, fork_at: 1.2, merge_at: 3 }
  - type: person
    name: 蔡佑杰
    fte: 0.5
    theme: green                      # 胶囊底色
    items:
      - { text: LXI1.6新增特性开发, start: 1.2, end: 1.9 }
```

连续的 `type: branch` 画成一组 Git 图：第一条 `main` 黑粗线带箭头，后续 `feature` 从 `fork_at` 垂下、在 `merge_at` 合回。

| 布局 | 怎么表达 |
|------|----------|
| 阶段色条 | `phases`：`region: lead/tail` 或 `start`/`end`（tick） |
| 日期 | `time_axis.ticks`，灰胶囊坐在虚线上 |
| 主干/特性分支 | `type: branch` + `line.theme: main\|feature` |
| 人员任务 | `type: person` + 圆角色胶囊；文案可换行 |
| 验收节点 | `milestones` 底栏空心星 + 题注 |

人员标签写成 `{name}-{fte}人力`。无头像文件时用姓名首字圆标。

## 视觉规则

| 元素 | 做法 | 禁止 |
|------|------|------|
| 画布 | 白/浅灰底 | 暗色架构卡、项目推进的阶段色块墙 |
| 阶段条 | 顶栏一条连续色带，开始/结束为端帽 | 拆成互不相连的色块 |
| 日期 | 灰圆角胶囊 + 贯穿全图竖虚线 | 把日期写进阶段条里 |
| 主干 | 黑粗线 + 右箭头 + 线中分支名 | 用卡片表示仓库 |
| 特性分支 | 彩色折线：下分 → 平行 → 上合（箭头） | 与主干错位对不齐合入点 |
| 人员 | 左栏头像+人力；胶囊宽度 = 工期 | 拉满空闲格；同行重叠 |
| 星星 | 底栏空心五角星，对准日期 | 奖杯/菱形（那是另一张图） |

人员主题：`green` / `blue` / `rose` / `orange` / `purple` / `teal` / `slate`。相邻人必须不同色。

阶段主题：`pink`（开始）`orange` `blue` `yellow` `green` `mint`（结束）。

## 收集输入时补全

能推断则不要问：

1. 关键日期（默认作为 ticks 与底栏星星）
2. 顶栏阶段名与起止日期
3. 项目空间 / 任务空间（有无特性分支、从哪天拉出、哪天合回）
4. 每个人：姓名、人力、任务胶囊文案与起止
5. 每个日期对应的验收节点（星星题注）

不要把人员依赖画成箭头网络；依赖只体现在分支合入与先后排期。

## 打磨清单

- [ ] 竖虚线、日期胶囊、底栏星星三者同一 `left%`
- [ ] 阶段条分段接缝对齐日期（阶段 i 的右缘 = tick i+1）
- [ ] 特性分支 `fork_at` / `merge_at` 落在主干上，合入有向上箭头
- [ ] 人员胶囊不叠字；人力格式 `姓名-N人力`
- [ ] 浅色皮肤；未套用 `.roadmap-tl` 或暗色 customfig

## 明确不要

- 当成 `task-roadmap-timeline`（项目推进：左栏阶段、黄条里程碑、无人员）
- Mermaid `gantt` / `gitGraph` 冒充本图
- HTML `<table>` 做格子
- 飞书画板/draw.io 当默认输出（用户明确要求再另转）
