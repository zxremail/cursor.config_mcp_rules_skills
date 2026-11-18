---
name: build-shell-script
description: >-
  任意新项目/仓库中 Bash 编译、构建、cmake/make 包装脚本的编写与改版规范（用户级 Skill，与具体
  产品无关）。只要用户要求新建、改写「编译脚本」「构建脚本」「build_*.sh」「一键编译」、
  本地构建入口，或给 --help 加颜色/分阶段日志，就必须先 Read 并遵守本 Skill。强制：彩色
  help、编译过程分阶段彩色提示、帮助「示例」区每行命令带行尾 # 中文注释。即使用户未提颜色
  也默认适用。无参数必须只打帮助、不执行编译。Triggers: 编译脚本、构建脚本、build script、
  cmake 包装、make 一键、彩色 help、logStep、无参 help、新项目构建脚本。
---

# Bash 编译脚本终端规范（通用）

Skill 路径：`~/.cursor/skills/build-shell-script/SKILL.md`（用户级，适用各新项目，不进业务主仓 `.cursor/skills`）。

## 何时必须用本 Skill

- 在任意仓库新增/修改 **编译、配置、打包前的构建** 类 Bash 脚本（`scripts/build_*.sh`、`tools/build.sh`、工作区 `ai.cursor/` 下的构建脚本等）
- 用户提到 **一键编译**、**彩色 help**、**分阶段编译提示**、**构建脚本示例要带注释**
- **建议**：把「同步仓库 / 拉代码 / 装依赖」与「纯编译」**拆成不同入口**，避免一个脚本承担无关职责（各项目自有命名，如 `sync.sh` vs `build_*.sh`）

## 三条硬性要求

| # | 要求 | 违反即不合格 |
|---|------|----------------|
| 1 | `usage()` / `--help` **必须彩色** | 禁止纯 `cat <<EOF` 无 ANSI |
| 2 | 编译主路径 **分阶段彩色日志**（至少「配置」「编译」两步） | 禁止全程无步骤提示 |
| 3 | 帮助 **示例** 区 **每一行一条命令 + 行尾 `# 中文说明`** | 禁止无注释的裸命令行 |
| 4 | **无参数** 仅输出彩色 `usage()` 并 **exit 0**，不触发编译 | 禁止无参悄悄开编 |

## 颜色与 TTY

脚本**最前面**（在业务逻辑之前）初始化颜色；**非 TTY** 或 **`NO_COLOR`** 时变量置空。

| 变量 | 用途 |
|------|------|
| `C_BLUE` | 标签、`[build-xxx]`、示例中的命令路径 |
| `C_CYAN` | 路径、步骤序号、技术文件名 |
| `C_GREEN` | 选项名、成功、关键开关 ON |
| `C_YELLOW` | 章节标题「选项」「示例」、步骤括号内参数 |
| `C_BRIGHT_BLACK` | **仅**示例区行尾 `# 中文注释`（ANSI **90** 亮黑，多数终端呈深灰，与命令区分） |
| `C_MAGENTA` | 目标名、版本号、工具子命令 |
| `C_RED` | 错误、OFF、禁止 |
| `C_RESET` | 复位 |

初始化示例：`C_BRIGHT_BLACK='\033[0;90m'`

帮助用 **`echo -e`** 分段打印，禁止无着色的整页 heredoc help。

## 日志 API（编译过程）

至少实现：`logInfo`、`logOk`、`logWarn`（stderr）、`logError`（stderr）、`logStep`（`步骤 n/m` + 标题 + 可选黄字参数）。

```bash
logStep "1/2" "CMake 配置" "${CMAKE_BUILD_TYPE}, ..."
# cmake / make configure / cargo build --config 等
logStep "2/2" "增量编译" "-j${s32Jobs}"
# cmake --build / make / ninja 等
logOk "编译完成: ${TARGET_BIN}"
```

**configure + build**（或等价两阶段）必须有彩色步骤；子模块、clean、环境检查可额外 `logStep`/`logInfo`。

## `usage()` 结构（彩色）

顺序：**用法**（写明无参=帮助）→ **说明** → **选项**（黄标题）→ **示例**（每行带 `#`）→ **产物/输出路径**。

无参行为在 **用法** 下用一行亮黑 `# 无参数：…` 写清。实际编译用显式子命令（如 `build`）或至少一个构建选项；示例里分别展示「无参→帮助」与「build / 带选项→编译」。

## 示例区格式（强制）

```bash
echo -e "${C_YELLOW}示例:${C_RESET}"
echo -e "  ${C_BLUE}./scripts/build.sh${C_RESET}  ${C_BRIGHT_BLACK}# 无参：显示帮助${C_RESET}"
echo -e "  ${C_BLUE}./scripts/build.sh${C_RESET} ${C_GREEN}build${C_RESET}  ${C_BRIGHT_BLACK}# Debug 一键编译${C_RESET}"
echo -e "  ${C_BLUE}./scripts/build.sh${C_RESET} ${C_GREEN}-c -j8${C_RESET}  ${C_BRIGHT_BLACK}# 全量重编 + 8 并行${C_RESET}"
```

**禁止**用 `C_YELLOW` 渲染示例行尾 `#` 注释（易与章节标题混淆）；统一 **`C_BRIGHT_BLACK`**。

一行一条命令；`#` 后 **中文** 短说明。README 里示例同样遵守「每行命令后有 `#` 注释」。

## 工程根目录解析（通用）

脚本若放在 **嵌套目录或独立 git 子仓**（如 `ai.cursor/`），**不要只信** `git -C "$SCRIPT_DIR" rev-parse --show-toplevel`。

应 **向上遍历** 直到找到项目约定的根标记，例如：

- `src/CMakeLists.txt`、根目录 `CMakeLists.txt`
- `package.json` + 构建配置、`Cargo.toml`、`meson.build` 等

将解析逻辑封装为函数，找不到则 `logError` 退出。

## 脚本基础

- `set -euo pipefail`
- 复杂函数建议中文块注释（名称、功能、参数、返回值）；团队无要求时可从简

## 工作目录（`cd -`）

- **禁止**在调用方 shell 里随意 `cd` 后又不恢复；`cmake -S/-B`、`git -C`、绝对路径优先。
- **`./build.sh` 子进程执行**：全程不改调用方 `pwd`；若脚本内误 `cd`，用 `EXIT` trap 恢复到启动时 `pwd -P`。
- **`source build.sh`**：若需进入工程根再编，只 `cd` **一次**到根目录且**不要在 EXIT 时 back**（保留 `OLDPWD`），编完后调用方执行 **`cd -`** 应能回到 source 前的目录。
- 帮助里可用一行亮黑注释说明 `./` vs `source` 行为差异。

## 参考实现（可选 Read）

若当前工作区存在 **`ai.cursor/build_scope.sh`**，可作为彩色 help / `logStep` / 示例注释的 **样例对照**；其它项目无此文件时，**以本 Skill 为准** 新建脚本，照抄 API 与配色表即可。

## Agent 自检清单

- [ ] `--help` 在终端有颜色
- [ ] 示例 **每行** 有 `C_BRIGHT_BLACK`（亮黑 90）行尾 `# ...` 注释
- [ ] 至少 2 个分阶段 `logStep`（或等价）
- [ ] `NO_COLOR` / 非 TTY 不乱码
- [ ] 编译脚本与无关职责（如同步仓库）未混在同一入口（除非用户明确要求）
- [ ] **`$# -eq 0`** 只打彩色 help，不编译