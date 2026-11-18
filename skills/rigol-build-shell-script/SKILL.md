---
name: rigol-build-shell-script
description: >-
  RIGOL Scope 及 ai.cursor 下 Bash 编译/构建脚本的编写与改版规范。只要用户要求新建、改写、
  润色「编译脚本」「构建脚本」「build_*.sh」「一键编译」「cmake 包装脚本」，或修改
  ai.cursor/build_scope.sh 一类脚本，就必须先 Read 并遵守本 Skill。强制：--help 彩色输出、
  编译过程分阶段彩色日志、帮助里「示例」区每一行命令必须带行尾 # 中文注释。即使用户
  未提颜色或示例注释，也默认适用。Triggers: 编译脚本、构建脚本、build script、help 颜色、
  logStep、ai.cursor 编译、cmake 一键。
---

# Bash 编译脚本终端规范

Skill 路径：`~/.cursor/skills/rigol-build-shell-script/SKILL.md`（用户级，不进主仓 `.cursor/skills`）。

## 何时必须用本 Skill

- 在 **主仓 `scripts/`** 或 **`ai.cursor/`** 新增/修改 **编译、打包、cmake 驱动** 类 Bash 脚本
- 用户提到 **一键编译**、**build_scope**、**彩色 help**、**分阶段编译提示**
- **不要**把编译入口与主仓根目录 **`./x.sh`**（同步仓库）混在同一脚本里；编译脚本放 `ai.cursor/` 或 `scripts/build_*.sh`

## 三条硬性要求

| # | 要求 | 违反即不合格 |
|---|------|----------------|
| 1 | `usage()` / `--help` **必须彩色** | 禁止纯 `cat <<EOF` 无 ANSI |
| 2 | 编译主路径 **分阶段彩色日志**（至少「配置」「编译」两步） | 禁止全程无步骤提示 |
| 3 | 帮助 **示例** 区 **每一行一条命令 + 行尾 `# 中文说明`** | 禁止无注释的裸命令行 |

## 颜色与 TTY

脚本**最前面**（在业务逻辑之前）初始化颜色；**非 TTY** 或设置了 **`NO_COLOR`** 时全部置空（与主仓 `x.sh` 一致）。

| 变量 | 用途 |
|------|------|
| `C_BLUE` | 标签、`[build-xxx]`、示例中的命令路径 |
| `C_CYAN` | 路径、步骤序号、技术文件名 |
| `C_GREEN` | 选项名、成功、关键开关 ON |
| `C_YELLOW` | 章节标题「选项」「示例」、步骤括号内参数 |
| `C_MAGENTA` | 目标名、版本号、CMake 子命令 |
| `C_RED` | 错误、OFF、禁止 |
| `C_RESET` | 复位 |

**禁止**在帮助里依赖 `cat <<EOF` 输出整页（无法按字段着色）；用 **`echo -e`** 分段打印。

## 日志 API（编译过程）

至少实现：

```bash
logInfo()   # 蓝标 + 正文
logOk()     # 绿标 + 绿字成功
logWarn()   # 黄 WARN，stderr
logError()  # 红 ERROR，stderr
logStep()   # 蓝标 + 青「步骤 n/m」+ 绿标题 + 黄参数（可选）
```

**分阶段示例**（按实际步骤改 `n/m`）：

```bash
logStep "1/2" "CMake 配置" "${strBuildType}, STEPPE_EAGLE=ON, ..."
cmake "${CMAKE_ARGS[@]}"
logStep "2/2" "增量编译" "-j${s32Jobs}"
# 或全量：logStep "2/2" "全量编译" "--clean-first, -j${s32Jobs}"
cmake --build "$BUILD_DIR" ...
logOk "编译完成: ${TARGET_BIN}"
```

可选：子模块、`clean-first`、环境检查各用 `logStep` 或 `logInfo`，但 **configure + build** 两步必须有颜色步骤。

## `usage()` 结构（彩色）

顺序固定：

1. **用法**（蓝「用法」+ 青命令 + 品红 `[选项]`）
2. **说明**段落（路径/宏用青、绿、品红点缀）
3. **选项**（黄标题；绿选项名 + 正文）
4. **示例**（黄标题；**每行**见下节）
5. **产物**（黄「产物」+ 青绝对或相对路径）

## 示例区格式（强制）

帮助里 **每一条** 示例单独一行 `echo -e`，命令后必须跟 **黄色 `# 注释`**：

```bash
echo -e "${C_YELLOW}示例:${C_RESET}"
echo -e "  ${C_BLUE}./ai.cursor/build_scope.sh${C_RESET}  ${C_YELLOW}# 无参：Debug 一键配置并编译${C_RESET}"
echo -e "  ${C_BLUE}./ai.cursor/build_scope.sh${C_RESET} ${C_GREEN}-r -c -j16${C_RESET}  ${C_YELLOW}# Release + 全量重编 + 16 并行${C_RESET}"
echo -e "  ${C_BLUE}./ai.cursor/build_scope.sh${C_RESET} ${C_GREEN}--no-gles${C_RESET}  ${C_YELLOW}# 主机无 GLES3 头时使用${C_RESET}"
```

规则：

- **一行一条可复制命令**；说明写在 **同一行** 的 `#` 后，**中文**，简短动宾短语
- 若示例在脚本外（如 README），同样 **每行命令后必须有 `#` 注释**；帮助里优先用终端黄色显示 `# ...`
- 不要用表格替代「示例」区；不要用多行命令块且只有块首一条注释

## 主仓根目录解析（ai.cursor 脚本）

`ai.cursor` 可能是 **独立 git 仓库**，禁止仅用 `git -C "$SCRIPT_DIR" rev-parse --show-toplevel`。应 **向上查找 `src/CMakeLists.txt`** 定主仓根（见参考实现）。

## 脚本头注释（本项目）

函数须有中文块注释（名称、功能、参数、返回值、作者、修改日期）；`set -euo pipefail`。

## 参考实现（修改前先 Read）

**Canonical 样例**：工作区内的 `ai.cursor/build_scope.sh`（草原雕 Steppe Eagle 主仓）。

- 彩色 `usage()`
- `logStep` 1/2 配置、2/2 编译
- 示例行尾 `#` 注释
- `buildScopeResolveMainRepoRoot`

改写 `build_scope.sh` 或新建兄弟脚本时，**风格与该文件对齐**，不要削弱颜色或删掉示例注释。

## Agent 自检清单

交付前确认：

- [ ] `--help` 在真实终端有颜色（段落、选项、示例可区分）
- [ ] 示例区 **每一行** 含 `${C_YELLOW}# ...${C_RESET}` 或等价黄色行尾注释
- [ ] 编译路径至少 2 个 `logStep`（或明确等价分阶段日志）
- [ ] `NO_COLOR` / 非 TTY 不输出裸 ESC 乱码
- [ ] 未与主仓 `./x.sh` 混装编译逻辑