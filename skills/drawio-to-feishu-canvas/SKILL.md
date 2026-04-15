---
name: drawio-to-feishu-canvas
description: 将 .drawio 文件导入飞书文档的画板中。包含浏览器自动化导航路径、已知限制及应对方案。Use when the user asks to import drawio files into Feishu (飞书) document canvas (画板), or mentions "drawio 导入飞书" or "画板导入".
---

# 将 DrawIO 文件导入飞书画板

将 `.drawio` 格式文件插入飞书云文档的画板（Canvas/Whiteboard）块中。

---

## 1. 前提条件

- Cursor Browser Automation 已开启（Settings → Tools & MCP → Browser Automation → On）
- 用户已在 Cursor 内置浏览器中**登录飞书**（首次需扫码）
- `.drawio` 文件已生成并存放于工作区内

## 2. 整体流程

```
生成 drawio 文件 → 打开飞书文档 → 进入/创建画板 → ⋯ → 导入 → 选择文件
                                                              ↑
                                                         需用户手动完成
```

## 3. 浏览器自动化可完成的步骤

### 3.1 导航到飞书文档

```
browser_navigate → 飞书文档 URL
```

首次访问会跳转到登录页（`accounts.feishu.cn`）。提示用户在 Cursor Browser 面板中扫码登录，登录后页面自动跳转回文档。

### 3.2 打开已有画板

画板在 accessibility snapshot 中表现为一个较大的 `generic` 元素，位于标题下方。通过 `browser_get_bounding_box` 比对位置来识别：

```
browser_get_bounding_box ref=heading  → 获取标题位置
browser_get_bounding_box ref=eXX     → 找到 y 值在标题下方、面积较大的 generic 元素
browser_click ref=eXX doubleClick=true → 双击打开画板
```

### 3.3 在文档中新建画板

若需新增画板块：

1. 在文档编辑模式下，点击目标位置
2. 输入 `/` 调出块菜单
3. 选择"画板"

### 3.4 画板内导航到"导入"

画板打开后的 UI 结构：

| 区域 | 内容 |
|------|------|
| 左上角 | `退出` 按钮 + "画板"标识 |
| 左侧栏 | 绘图工具按钮（约 12 个无名 button） |
| 右上角 | `分享` → `编辑` → 搜索 → 复制 → `⋯`（更多选项） |
| 中央 | 画布区域 |
| 右下角 | 撤销/重做 + 缩放控件 |

导航到导入菜单的步骤：

```
1. browser_snapshot → 获取画板内元素 refs
2. 找到右上角 ⋯ 按钮：
   - 位于 `分享`、`编辑` 按钮右侧
   - 通过 bounding box 识别（x 最大、y ≈ 26、w=32、h=32 的 button）
3. browser_click ref=⋯按钮 → 弹出设置菜单
4. browser_snapshot → 找到 menuitem name="导入"
5. browser_click ref=导入menuitem
```

菜单结构（从上到下）：

```
协作者光标  [开关]
快捷创建    [开关]
网格背景    [开关]
精准框选    [开关]
显示尺寸    [开关]
显示工具栏  [开关]
────────────
翻译为      >
导入          ← 目标
导出        >
```

## 4. 已知限制：原生文件对话框

**关键限制**：点击"导入"后弹出操作系统原生文件选择器，当前浏览器 MCP 工具集**没有 `setInputFiles` 等效工具**，无法自动完成文件选择。

### 附加问题：远程工作区场景

当 Cursor 连接远程工作区时（如 SSH Remote），drawio 文件在远程 Linux 机器上，而浏览器运行在本地 Windows/macOS 上。即便能控制文件对话框，也无法直接选到远程文件。

## 5. 应对方案

### 方案 A：半自动（推荐）

自动化完成导航，文件选择由用户手动完成：

1. Agent 通过浏览器自动化打开画板、导航到"导入"菜单
2. **解锁浏览器**（`browser_unlock`）
3. 提示用户：
   - 从 Cursor 文件树右键 drawio 文件 → **Download** 到本地
   - 在飞书画板中 `⋯` → 导入 → 选择已下载的文件
4. 用户完成后，Agent 继续后续画板的创建和导航

### 方案 B：通过飞书 MCP（全自动）

如果 `feishu-mcp` 可用，绕过浏览器直接调用飞书 API 操作文档：

- 使用飞书文档 API 创建画板块
- 通过 API 上传文件并关联到画板

前提：feishu-mcp 服务正常连接，且飞书 App 具备文档读写权限。

### 方案 C：转图片插入（降级方案）

将 drawio 渲染为 PNG/SVG 后作为图片插入文档：

- 优点：可全自动完成
- 缺点：失去画板内编辑能力

## 6. 多图批量操作流程

当需要插入多个 drawio 文件时：

```
FOR 每个 drawio 文件:
  1. 在文档中创建新画板块（输入 / → 画板）
  2. 双击打开画板
  3. 导航到 ⋯ → 导入
  4. [用户选择文件]
  5. 点击「退出」回到文档
  6. 滚动到文档末尾，准备下一个
```

## 7. 元素识别技巧

飞书画板的 accessibility snapshot 中大量元素为无名 `button` 和 `generic`，需通过以下方式定位：

| 方法 | 适用场景 |
|------|---------|
| `name` 属性 | 有名元素：`退出`、`分享`、`编辑`、`导入`、`导出` |
| `bounding_box` 位置 | 无名工具栏按钮：按 x/y 坐标判断 |
| 上下文推断 | 画板区域：标题下方最大面积的 `generic` 元素 |
| `states` 属性 | 当前激活/聚焦的元素 |
