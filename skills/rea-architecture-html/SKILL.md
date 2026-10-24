---
name: rea-architecture-html
description: >-
  Use when 用户要用 REA 反编译 / 逆向结果输出架构分析文档、architecture.html、
  类似 architecture.html、静态分析分层页；或分析 .so / .apk / ELF 并要一份可双击打开的架构 HTML。
  不要用：markdown-to-html sidecar、.layer / customfig、Mermaid flowchart、
  fig-dark-layer-cards 内联 SVG 进 md、飞书文档/画板（除非用户另点名）、
  /draw 菜单（本图种已点名）。
---

# REA 架构分析 HTML

把 REA 静态分析结果写成**单文件深色 HTML**：指标卡 + 分层内联 SVG + 调用链 + 对照表 + 同目录证据链接。对照实现：`architecture.html`（APK）与 `b.libhal.so/architecture.html`（ELF）。

**REQUIRED：** 先 `Read` 同目录 [shell.html](shell.html)，整段复制 `<style>`，禁止另起主题、禁止 md2html。

不确定是否本图种 → `diagram-style-catalog`。用户已说 REA / 反编译 / 逆向 / architecture.html → **跳过 /draw 菜单**，直接本 skill。

## 何时用 / 不用

| 用 | 不用 |
|---|---|
| REA 已给出或即将给出 `decompiled/`、符号、字符串、inspect | 知识库说明 md → `markdown-export` |
| 要一份和现有 `architecture.html` 同壳的架构页 | HTML sidecar `.layer` → `markdown-to-html` §3 |
| 产物是 `.so` / `.apk` / ELF，读者要看分层与证据链 | md 内联深色卡片墙 → `fig-dark-layer-cards` |
| | 关系折线 SVG → `fig-dark-layer-relations`；时序 → `html-sequence-swimlane` |

## 落点

1. 用户消息里的路径优先。
2. 否则写在**产物旁**：`<产物目录>/architecture.html`（如 `b.libhal.so/architecture.html`）。同一工作区多份产物时每份各写一份，不要互相覆盖。
3. 有 `ai.cursor/` 且用户要进知识库时，才走 `ai-cursor-doc-output`；默认仍贴产物目录。
4. 证据链接用相对路径，指向同目录 `decompiled/`、`classes/`、`native/` 等，不要绝对路径。

禁止把分析页写到仓库根「图方便」，除非工作区根**就是**该产物的分析根（已有根级 `architecture.html` 那种）。

## 分析（先证据，后画）

只静态分析，不执行产物、不校验签名、不编造未观察到的行为。

按需读（有则用，无则跳过）：

- `inspect.json` / `inspect-artifact.json`：格式、体积、SHA-256、过程数
- 导出 / `dynsym` / demangle：对外 ABI
- `strings.txt`：设备路径、源文件路径、日志模块
- 反编译 C / Java：入口、虚表、工厂、调用链
- APK：`AndroidManifest`、AIDL、native 方法名

先结论：对外接口、主实现落点、物理/设备边界。层从上到下是**调用方向**（调用方在上、设备在下），不是时间。

## 页面合同（缺一块 = 未完成）

顺序固定：

1. **kicker** `REA static analysis · <产物名>`
2. **h1** 中文标题（职责，不要只写文件名）
3. **meta** 身份一行：包名或 SONAME、架构、体积或版本、运行身份
4. **四个** `.fact`（短标签 + 一句结论）
5. **分层架构** `.diagram`：图例四色 + `viewBox="0 0 1280 H"` 内联 SVG + `.note` 写证据边界
6. **调用链** `.flow`（`<b>` 步骤名 + `<p>` 谁对谁做什么）
7. **对照表**（能力族 / 路由 / 返回码，按产物选；至少一张）
8. **同目录证据** `ul.files` 相对链接

中文：先结论；专名用「」；标识符用 `<code>`。正文不要可见的长 SHA，截断即可。

## SVG（硬规则）

| 件 | 值 |
|----|-----|
| 层带 | `fill="#101820"` `stroke="#2a3b4d"` `rx="10"`；层号+层名 13px |
| 内卡 | `fill="#1b2733"` `rx="8"`；描边用语义色 |
| 硬件卡 | `fill="#2a1c22"` `stroke="#f0b4a8"` |
| 原生强调 | `fill="#173028"` `stroke="#8fd6b0"` |
| 箭头 | `#8aa0b5`，`<marker id="arrow">`；层间一条竖线居中 |
| 字 | 标题 14–16 `#e7eef5` 或语义色；说明 12 `#93a6b8` |
| 色 | 调用方 `#8ec5ff` · 接口 `#f0c36a` · 原生 `#8fd6b0` · 硬件 `#f0b4a8` |

层数随产物（常见 4–5）。相邻层必须换语义色。禁止 Mermaid、禁止外链图、禁止把 CSS 改成 GitHub Dark / md2html 那套。

`<style>` 必须与 [shell.html](shell.html) 字节级同主题：保留 `--java/--aidl/--native/--hw`、`.facts` 四列、`.flow`、`.files` 两栏。只改正文，不改选择器。

## 借口对照

| 借口 | 实际 |
|------|------|
| 先写 md 再 md2html 更快 | 交卷就是手写单文件 HTML；sidecar 是另一种图 |
| 分层该用 Mermaid / 深色卡片墙 | 本页图是层带+内卡 SVG，不是 flowchart，也不是 md 内联墙 |
| 工作区有 architecture.html，改那一份就行 | 新产物写新文件，贴在产物目录 |
| 没有 decompiled 就先猜层 | 先读符号和字符串；缺证据写在 `.note`，不要编节点 |
| /draw 要先出菜单 | REA 架构页已点名本 skill |
| CSS 我记得 | 未 Read `shell.html` 不得写 `<style>` |

## 红旗

- 准备跑 `md2html` 或写 `*.figures/mermaid-N.html`
- SVG 里出现 `flowchart` / `subgraph`
- 改了 `:root` 色名或去掉 `.facts`
- 没有「同目录证据」或链接指到仓库外
- 把 APK 页和 `.so` 页写成同一文件
