---
name: build-shell-script
description: >-
  用户级 Skill：Agent 新建或改写的任意脚本都必须先 Read 并遵守（不限编译）。覆盖 Bash / POSIX
  sh、以及同仓库里同类入口（.py 若当 CLI 且有 --help 也适用帮助/着色约定）。强制：彩色
  usage/--help、无参数只打帮助不执行危险/主操作、示例区每行命令带行尾 # 中文注释且注释颜色
  必须是亮黑 ANSI 90、蓝色一律亮蓝 ANSI 94。先后依赖的干活工序才用 logStep；运行时分段
  横幅用黄字 logSection。list/status 等分组展示不要写「步骤」。编译/cmake/make 只是其中
  一类，不是唯一触发条件。即使用户未提颜色也默认适用。Triggers: 新建脚本、写脚本、改脚本、
  shell 脚本、bash、.sh、帮助上颜色、彩色 help、示例注释、亮黑、logStep、logSection、
  分段横幅、步骤字样、分组展示、无参 help、编译脚本、构建脚本、build script、cmake、
  make 一键、固件脚本、bios-update、工具脚本、终端颜色、ANSI、亮蓝。
---

# 任意新脚本终端与帮助规范

Skill 路径：`~/.cursor/skills/build-shell-script/SKILL.md`（用户级，适用各仓库，不进业务主仓 `.cursor/skills`）。

**目录名 `build-shell-script` 是历史命名，范围不是「只针对编译脚本」。**  
真正意图：**凡 Agent 生成或改写的新脚本都适用**（工具、固件升级、串口、备份、包装器、安装、同步、以及编译/构建）。编译只是子集，额外遵守下文「编译类追加」。

## 何时必须用本 Skill

Agent 一旦要 **新建** 或 **改写** 脚本，就必须先读本文件再写，包括但不限于：

- `*.sh`、仓库根 `x.sh`、`scripts/*.sh`、`tools/*.sh`、`ai.cursor/` 下脚本
- 用户说「写个脚本」「帮我写脚本」「升级脚本」「包装命令」「加 --help / 上颜色」
- 编译/构建类：`build_*.sh`、cmake/make 包装、「一键编译」

用户未提颜色、未提 help，**仍然适用**（默认彩色帮助 + 无参不干活）。

## 对所有脚本的硬性要求

| # | 要求 | 违反即不合格 |
|---|------|----------------|
| 1 | `usage()` / `--help` **必须彩色**（`echo -e` 分段） | 禁止纯 `cat <<EOF` 无 ANSI |
| 2 | 帮助 **示例** 区 **每一行一条命令 + 行尾 `# 中文说明`** | 禁止无注释的裸命令行 |
| 3 | **用法/示例** 命令行右侧说明必须是 **亮黑 ANSI 90**（有无 `#` 都一样） | 禁止默认白/黄/绿渲染「查看当前 BIOS…」这类注释 |
| 4 | **无参数**（`$# -eq 0`）仅输出彩色 `usage()` 并 **exit 0** | 禁止无参直接刷写、编译、删除、安装、联网 |
| 5 | 需要蓝色时用 **亮蓝 ANSI 94** | 禁止深蓝 ANSI **34**（含 `\033[0;34m`、`\033[1;34m`） |
| 6 | 干活主路径若有 **≥2 个先后依赖的工序**，用彩色 `logStep` | 禁止把 list/status 等**分组展示**写成「步骤 n/m」；无工序则不要 `logStep`（单步可只 `logInfo`/`logOk`） |
| 7 | 运行时**已有**分段横幅时必须用 **`${C_YELLOW}`** | 禁止无色 `=== … ===` / `---` 横幅；无分段则不必硬造 |

## 颜色与 TTY

脚本**最前面**（在业务逻辑之前）初始化颜色；**非 TTY** 或 **`NO_COLOR`** 时变量置空。

| 变量 | 用途 |
|------|------|
| `C_BLUE` | 标签、脚本路径、示例中的命令路径。**值必须是亮蓝 `\033[0;94m`** |
| `C_CYAN` | 路径、步骤序号、技术文件名 |
| `C_GREEN` | 选项名、子命令、成功、关键开关 ON |
| `C_YELLOW` | 章节标题「用法」「选项」「示例」；运行时 **分段提示**；步骤括号内参数 |
| `C_BRIGHT_BLACK` | **命令行右侧说明**（强制）：用法区无 `#` 的中文释义、示例区 `# 中文注释`，ANSI **90** 亮黑 |
| `C_MAGENTA` | 目标名、版本号、ROM/产物名 |
| `C_RED` | 错误、OFF、风险注意 |
| `C_RESET` | 复位 |

初始化：`C_BLUE='\033[0;94m'`　`C_BRIGHT_BLACK='\033[0;90m'`

### 蓝色一律用亮蓝

**任何终端输出**（help、logStep、logInfo、错误、表格、横幅）需要蓝色时 **只用 94**，**禁止 34**。

| 禁止 | 必须 |
|------|------|
| `\033[0;34m`、`\033[34m`、`\033[1;34m`、SGR **34** | `\033[0;94m`（与亮黑 90 同一组） |
| `C_BLUE` 赋值为 34 | 变量可仍叫 `C_BLUE`，赋值必须是 **94** |

暗色终端里 34 发闷；不要用加粗深蓝 `\033[1;34m` 顶替 94。绿/黄/红/青/品红不在此条范围内。

### 行尾说明 / 注释一律用亮黑

命令、子命令、选项写完之后，**右侧给人看的说明文字**一律亮黑，与命令正文区分开。**不要求必须带 `#`**，两种写法都要 90：

```bash
# 用法区（无井号也算注释）
echo -e "  sudo ${C_BLUE}\$0${C_RESET} ${C_GREEN}status${C_RESET}  ${C_BRIGHT_BLACK}查看当前 BIOS 与 update/ 内 ROM${C_RESET}"
# 示例区（井号 + 中文）
echo -e "  sudo ${C_BLUE}\$0${C_RESET} ${C_GREEN}status${C_RESET}  ${C_BRIGHT_BLACK}# 查看版本与 ROM 列表${C_RESET}"
```

| 禁止 | 必须 |
|------|------|
| 说明文字无色 / 默认白（看起来像命令的一部分） | `${C_BRIGHT_BLACK}查看当前 BIOS 与 update/ 内 ROM${C_RESET}` |
| `${C_YELLOW}` / `${C_GREEN}` / `${C_CYAN}` 包说明或 `# …` | `${C_BRIGHT_BLACK}# 中文说明${C_RESET}` |
| `\033[0;30m`（普通黑，暗底看不见）、`\033[1;30m` | `\033[0;90m`（ANSI **90**） |

章节标题「用法:」「示例:」仍用 `${C_YELLOW}`。子命令、路径、ROM 名不要涂成 90，只涂 **释义/注释**。

### 分隔提示一律着色

运行时分段横幅与帮助里的章节标题同级，**必须用 `${C_YELLOW}`**，不要默认白。  
硬性要求是**着色**，不是某种装饰符：`=== … ===`、`--- … ---`、`*** … ***`、或只有标题都行。

```bash
logSection() { echo -e "${C_YELLOW}$*${C_RESET}"; }
logSection "=== 当前 BIOS（dmidecode）==="
logSection "--- 系统依赖 ---"
```

| 禁止 | 必须 |
|------|------|
| `echo "=== 当前 BIOS（dmidecode）==="` 无 ANSI | `${C_YELLOW}…${C_RESET}`（装饰写进参数，不要把 `===` 写死进规范） |
| 分隔符用深蓝 34 | 黄标题；路径仍用青、成功用绿 |
| 单步小工具为过清单硬插一条横幅 | 有分段才 `logSection`；没有分段只 `logInfo`/`logOk` |
| `status`/`list` 打 `[步骤 1/2]` | 分组展示用 `logSection`，文案不要「步骤」 |

## 日志 API

至少实现：`logInfo`、`logOk`、`logWarn`（stderr）、`logError`（stderr）。

- **`logSection`**（黄字标题）：list、status、按系统/用户分组打印。**分组展示 ≠ 分步执行**，禁止写「步骤 n/m」。
- **`logStep`**：仅当后一步依赖前一步的干活路径（准备→执行、配置→编译）。文案可以带「步骤 n/m」。无此工序则不要定义或调用 `logStep`，不要为过清单硬加。

```bash
# 工序：才用 logStep
logStep "1/2" "准备" "检查工具与输入"
logStep "2/2" "执行" "${CMD}"
logOk "完成"

# 分组展示：只用 logSection
logSection "=== 系统单元 ==="
logSection "=== 用户单元 ==="
```

## `usage()` 结构（彩色）

顺序：**用法**（写明无参=帮助）→ **说明** → **选项/子命令**（黄标题）→ 如有依赖则 **系统依赖** → **示例**（每行带 `#`）→ 如有则 **产物/日志路径**。

无参行为在用法下用一行亮黑 `# 无参数：…` 写清。真正干活必须有 **显式子命令或选项**。示例里分别展示「无参→帮助」与「带子命令→执行」。

编译类可额外提供 `check-deps`；CMake 失败时追加 apt 提示。非编译脚本不要硬套 cmake/apt。

## 示例区格式（强制）

```bash
echo -e "${C_YELLOW}示例:${C_RESET}"
echo -e "  ${C_BLUE}./scripts/foo.sh${C_RESET}  ${C_BRIGHT_BLACK}# 无参：显示帮助${C_RESET}"
echo -e "  ${C_BLUE}./scripts/foo.sh${C_RESET} ${C_GREEN}status${C_RESET}  ${C_BRIGHT_BLACK}# 只读查看${C_RESET}"
echo -e "  sudo ${C_BLUE}./scripts/foo.sh${C_RESET} ${C_GREEN}run${C_RESET}  ${C_BRIGHT_BLACK}# 执行主操作${C_RESET}"
```

**强制**：行尾 `#` 用 **`${C_BRIGHT_BLACK}`**（`\033[0;90m`），禁止用黄/绿/其它色。一行一条命令；`#` 后 **中文** 短说明。README 里示例同样带 `#` 注释（Markdown 无 ANSI 时保持 `#` 中文即可）。

## 脚本基础

- `set -euo pipefail`（Bash）
- 复杂函数建议中文块注释（名称、功能、参数、返回值）；团队无要求时可从简
- 危险操作（刷固件、rm、dd、覆盖系统配置）默认确认；`--yes` 才跳过

## 工程根目录解析

脚本若放在 **嵌套目录或独立 git 子仓**，**不要只信** `git -C "$SCRIPT_DIR" rev-parse --show-toplevel`。向上遍历直到项目约定根标记（`x.sh`、`CMakeLists.txt`、`package.json`、本仓库约定的知识库 `_INDEX_.md` 等）。封装成函数，找不到则 `logError` 退出。非工程类单文件脚本可用 `HERE="$(cd "$(dirname "$0")" && pwd)"`。

## 工作目录（`cd -`）

- **禁止**在调用方 shell 里随意 `cd` 后又不恢复；优先绝对路径、`git -C`。
- **`./script.sh` 子进程**：全程不改调用方 `pwd`；若脚本内误 `cd`，用 `EXIT` trap 恢复到启动时 `pwd -P`。
- **`source script.sh`**：若必须进工程根，只 `cd` **一次**且**不要在 EXIT 时 back**（保留 `OLDPWD`），调用方 `cd -` 应能回去。
- 帮助里可用一行亮黑说明 `./` vs `source`。

## 编译类追加（仅当脚本确实是构建入口）

- 建议把「同步仓库 / 拉代码 / 装依赖」与「纯编译」拆成不同入口。
- 主路径至少两步彩色 `logStep`（配置 + 编译，或等价）。
- 无参只打帮助，**不触发编译**。
- `usage` 可含 apt 依赖与 `check-deps`。
- 可选对照：工作区若有 `ai.cursor/build_scope.sh`，可作彩色 help / `logStep` 样例。

## Agent 自检清单

- [ ] 本文件在写脚本 **之前** 已 Read（任何新脚本，不限编译）
- [ ] `--help` / 无参在终端有颜色
- [ ] 蓝色为 **`C_BLUE='\033[0;94m'`**，全文无 SGR 34
- [ ] 用法区右侧中文说明（如「查看当前 BIOS 与 update/ 内 ROM」）与示例区 `# …` 均为 **`C_BRIGHT_BLACK='\033[0;90m'`**，无默认白注释
- [ ] `NO_COLOR` / 非 TTY 不乱码
- [ ] **`$# -eq 0`** 只打彩色 help，不执行主操作
- [ ] 若有分段横幅：用 **`${C_YELLOW}`**（`logSection`），无默认白；无分段则不硬造
- [ ] 确有先后工序才 `logStep`（编译类：配置+编译）；仅分组输出只用 `logSection`，不要为过清单硬加「步骤」字样
- [ ] 未把无关职责硬塞进同一入口（除非用户明确要求）
