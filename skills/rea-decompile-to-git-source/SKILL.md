---
name: rea-decompile-to-git-source
description: >-
  Uses REA static analysis and decompilation to iteratively write modular
  reconstructed source into a dedicated Git repo, tuning .gitignore as artifacts
  appear, and committing each logical batch with semantic messages (no push).
  Use when the user asks to 用 REA 反编译生成源码、逆向还原源码、重建源码并 git
  管理、模块化还原、持续 commit 还原仓库, or to turn REA pseudocode/decompile
  output into maintainable source with version history.
---

# REA 反编译 → 模块化 Git 源码仓库

把 REA 证据链上的观察与反编译结果，落成**可维护、分模块**的源码树，并用 **Git 全程版本化**。分析手法与工具路由见 **`reverse-engineer-anything`**；架构 HTML 见 **`rea-architecture-html`**（可选，不替代源码）。

## 硬性约束（用户要求，不得弱化）

1. **源码使用 Git 管理**：还原产物落在独立 Git 根（用户指定路径；未指定则在分析目标旁建 `<artifact>-recon/` 并 `git init`）。禁止只堆在临时目录却不初始化仓库。
2. **自动持续修改优化 `.gitignore`**：每发现新的可再生/超大/引擎私有产物，在同一工作批次内更新 `.gitignore` 并 **单独 commit**（或与紧邻的 ignore 理由绑在同一 commit 的第二段 `-m`）。见 [reference.md](reference.md) § `.gitignore`。
3. **每次修改自动 commit，禁止 push**：完成一个逻辑批次后 `git add` → `git commit`。**不得** `git push`、`git push --force`、`gh` 推送远程，除非用户**当场**写明 push/推送。
4. **Commit message 必须体现意义**：说明「还原了什么 / 为何改 ignore / 模块边界变化」。**禁止**仅用时间戳、`update`、`wip`、`auto commit` 作标题。
5. **生成的源码要有模块化思维**：按子系统分目录与命名空间；模块间依赖单向、可测试边界清晰。见 [reference.md](reference.md) § 模块布局。

**Git 安全（与仓库惯例一致）：** 禁止 `git config`；禁止 amend 已 push 的提交；hook 失败则修问题后 **新 commit**，不要 amend 失败提交。

## 何时启用

| 启用 | 不启用 |
|------|--------|
| 用户要从二进制/APK/托管程序 **写出可编辑源码树** | 只要口头解释或单次 HTML 架构页 → `rea-architecture-html` |
| 用户要求 git / commit / 模块化还原 | 已有完整源码仓库，只做普通功能开发 |
| 长周期多轮 REA + 落盘 | 单次 `procedure_pseudo_code` 看一眼就结束 |

## 仓库选型

1. **用户给出路径** → 该路径为 Git 根。
2. **否则**：在目标产物同目录创建 `<basename>-recon/`（例如 `libhal.so` → `libhal.so-recon/`）。
3. **勿**把还原源码散写进无关业务仓库根目录，除非用户明确「就在当前工作区根」且该根已是还原专用树。

若目录尚无 `.git`：`git init`，写根 `README.md`（产物身份、SHA、REA 会话要点、模块索引链接）。

## 总流程

```text
[冻结范围] → [REA 证据 + 分模块计划] → [落盘模块] → [调 .gitignore] → [语义 commit] → 下一模块 …
```

### 1. 冻结范围与模块切分

- 从用户消息取：目标路径、语言偏好（C/C#/Java…）、优先子系统、是否跟踪 `evidence/` 摘要。
- 用 REA 做最小必要静态分析（`open_binary` / 路由表见 `reverse-engineer-anything`），产出 **模块清单**（名称、职责、对外 API、依赖方向、Evidence ID）。
- 在仓库写 `docs/MODULES.md`（或更新），再开始写 `src/`。

模块切分原则（同时满足尽量多条）：

- 按 **调用边界**（公开导出 / JNI / AIDL / COM）分模块。
- 按 **设备/协议/业务域** 分，不把 HAL、网络、UI 混在同一平铺目录。
- 单文件职责单一；反编译大函数先抽 **facade + 内部实现文件**，不要一个 `decompiled_all.c`。
- 观察与推断分离：不确定的行为用 `// REA-UNKNOWN:` + `docs/unknowns.md` 条目，不要假装确定。

### 2. REA → 源码（单模块一轮）

对每个模块一轮：

1. 引用 Evidence（过程名、地址、伪代码片段）写进 `docs/evidence-index.md` 或模块头注释（短，不粘贴整页伪代码进 Git）。
2. 在 `src/<module>/` 写 **可读** 源码：重命名符号、拆函数、补类型与常量；保留「与二进制不一致处」注释。
3. 若需对照，反编译原文放 `reference/decompiled/<module>/`（默认 **gitignore**，见 reference）；Git 只跟踪清洗后的 `src/`。
4. 模块就绪后：`README` 或 `docs/MODULES.md` 更新依赖图一句。

### 3. 持续优化 `.gitignore`

在 **每次** 新建下列类别路径之前或之后，检查并更新 `.gitignore`：

- REA / Ghidra / IDA 工程、`.rep`、`.lock`、`.gpr`、未请求的 `.idb`
- 体积 ≥ 用户未要求入库的二进制、完整 `export_evidence_bundle` 目录
- 可再生：`reference/decompiled/**`、本地 `*.o`、引擎日志

规则：

- 新增 ignore 规则时在 commit message 中写清 **忽略了什么、为何不应进版本库**。
- 若用户要求跟踪某类证据，从 ignore 移除并 **单独 commit** 说明跟踪原因。
- 已跟踪文件不能靠 ignore 取消跟踪；需 `git rm --cached` 时在 message 里说明。

### 4. 自动 commit（每逻辑批次一次）

**一批** = 下列之一（不要混无关改动在同一 commit）：

- 一个模块的首批源码 + 其 `docs` 条目
- 对已有模块的重构（拆分/重命名/修正与 Evidence 对齐）
- 仅 `.gitignore` / 文档索引 / `unknowns` 更新
- 根 `README` 与模块边界变更

提交前并行看清状态（PowerShell 可用 `;` 串联）：

```bash
git status -sb
git diff
git log -8 --oneline
```

只 `git add` 本批次文件；`git status` 确认 staged。

**标题格式（祈使句，中文或英文均可，二选一贯穿仓库）：**

```text
recon(<module>): <做了什么、对齐哪块二进制行为>
```

**禁止标题示例：** `2026-11-06 update`、`save`、`临时提交`、`auto`。

**正文第二段 `-m`（推荐）：** Evidence ID、模块边界、ignore 理由、仍存在的 UNKNOWN。

示例：

```bash
git commit -m "recon(gpio): 从 HAL 导出表还原 GPIO 读写 facade" -m "依据 Evidence ev_abc123；子调用仍标 REA-UNKNOWN 见 docs/unknowns.md#gpio-mmap"
```

Windows / PowerShell 避免 SSH 式嵌套 HEREDOC；本地用双 `-m` 或 `-F` 文件。

批次结束：`git status` 确认 working tree clean（或仅剩下一模块 WIP 且用户允许 WIP 不提交——默认 **不允许** 留未提交已完成模块）。

### 5. 结束一轮任务

- REA 原生会话：`close_binary`（不再需要引擎时）；调查结束按 `reverse-engineer-anything` 做 `reset_investigation` / 导出 bundle 到 **ignore 路径**。
- 向用户汇报：Git 根路径、分支、最近 3 条 commit 标题、模块完成度、`docs/unknowns.md` 链接；写明 **未 push**。

## 与 RigolPIS 工作区并存

若 Cursor 工作区是业务仓库（如 RigolPIS），还原树仍应在 **独立 Git 根** 或用户指定子目录；不要在业务 `.gitignore` 里 bulk-ignore 整个 `src/`  unless 用户要把 recon 嵌在同一 repo 的明确子路径（例如 `recon/libfoo/`）且该路径单独维护 ignore 块。

## 借口对照

| 借口 | 实际 |
|------|------|
| 先全量 decompile 到一个文件再提交 | 违反模块化；按模块 commit |
| 时间戳 commit 省事 | 违反用户要求；必须语义化 |
| evidence 太大全进 Git | 默认 ignore + index；bundle 放仓外或 ignore |
| 还原完顺手 push | 禁止，除非用户当场要求 |
| 不改 .gitignore 也能提交 | 每轮检查；新引擎文件必须 ignore |
| REA 伪代码即最终源码 | 必须清洗、分模块、标注 UNKNOWN |

## 红旗 — 停下问用户

- 不确定 Git 根应放在哪、或与生产源码混仓
- 用户要求 push 但未给远程与授权方式
- 还原涉及密钥/许可证算法且用户未授权写入仓库
- 单 commit 混合多个无关模块且无法写清标题

## 延伸阅读

- 目录模板、ignore 清单、commit 正反例：[reference.md](reference.md)
- REA 工具与证据纪律：`reverse-engineer-anything`
