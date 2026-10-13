# 画 flowchart 前的图种门

生成或增补 `.md`、准备写 `flowchart`、或用户说「流程图 / 画个流程」时：**先过本门，再动笔。**
未过门就写 `flowchart` = 违规。不要先占位 flowchart 再考虑换图种。
不要为此对用户 AskQuestion（生成文档时自动判定）。
用户**当场点名图种**（「就要 flowchart」「就要水平泳道」「就要时序图」）→ 以当场为准，不再改种。口头单独说「画流程图」**不算**点名 `flowchart`。

本页只选视觉语言。水平泳道画法 → `fig-horizontal-swimlane`。时序围栏细则 → 同目录 `layout.md` §4.1–§4.2。HTML 贴顶时序 → `html-sequence-swimlane`。总目录 → `diagram-style-catalog`。

## 配方（每张图画一次）

对这一张图默答四句（写在思考里即可，不必进文档）：

1. 稳定角色 / 层 **≥ 2**，且贯穿同一条因果？
2. 读者第一眼要找的是 **谁的道**（谁持球、谁交接）？
3. **时间是第一轴**（先发生什么、再发生什么）？
4. 主线是 **作业交接**（谁交给谁），不是职责墙 / 依赖网 / 决策网？

然后只选一行：

| 条件 | 写什么 |
|------|--------|
| 四句里 **≥3 句为是**，边是跨层步骤（下发 / 上报、同列对齐、同道推进） | **水平泳道**：停本 skill，Read 并走 `fig-horizontal-swimlane`（内联 SVG）。禁止 `flowchart` / `subgraph` 冒充 |
| 四句里 **≥3 句为是**，边是角色间 **消息往返**（请求-返回、ioctl、中断回调） | **垂直泳道**：写 Mermaid `sequenceDiagram`（角色在顶、时间向下）。HTML 导出走 `html-sequence-swimlane`。禁止 `flowchart` 竖列 subgraph |
| 其余（单主体阶段链、职责/结构、菱形决策网） | **flowchart**：继续本 skill 执行顺序（多 subgraph 再 Read `layout.md`） |

并列关系网 + 一条跨层作业：拆成两张，各过一次门。不要混装。

## 水平 vs 垂直

| | 水平泳道 | 垂直泳道 |
|--|----------|----------|
| 角色 | 左栏 | 顶栏 |
| 时间 | 左 → 右 | 上 → 下 |
| 边 | 同列下落/上报、同道水平 | 生命线上的消息、自调用 |
| `.md` 媒介 | 内联 SVG | `sequenceDiagram` |

「垂直泳道」在本套规范里 = 时序泳道，**不要**再开一套列向 SVG，也 **不要**用 `subgraph` 每列一个角色冒充。

## 对照

| 故事 | 结果 |
|------|------|
| `sudo reboot` → systemd 停服务 → fwupd 不退出 → 内核迟迟不重启 | 水平泳道 |
| USB 未枚举 → udev 无节点 → HAL open 失败 → UI 打不开 | 水平泳道 |
| BIOS → GRUB → Kernel → systemd，只标各阶段耗时 | flowchart |
| 已枚举 / 未枚举设备对照、模块依赖 | flowchart |
| HAL ioctl → 内核编程 FPGA → MSI 回来 | 垂直泳道（`sequenceDiagram`） |

## 红旗

出现下面任一想法：停下来重过本门，不要把已写的 `flowchart` 围栏当既成事实。

- 口头「画流程图」= 必须 `flowchart`（单独说「流程图」要过门；「就要 flowchart」才算点名）
- `markdown-export` 写「图表用 Mermaid」，所以不能 SVG
- 先画 flowchart 占位，泳道以后再换
- 用几个 `subgraph` 当水平 / 垂直泳道
- 启动阶段 A→B→C 也上泳道（单主体阶段链应 flowchart）
- 有菱形决策所以上泳道（分支网应 flowchart）
