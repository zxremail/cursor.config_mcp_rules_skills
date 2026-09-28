---
name: rebuild-clangd-index
description: >-
  Use when the user says 重建索引、重建 clangd 索引、clangd index、refresh clangd、
  compile_commands.json 过期，或跳转/补全失效想重编 C/C++ 语言服务索引。
---

# 重建 clangd 索引

## 强制：先反问，未确认不得动手

用户说「重建索引」（或同义说法）时，**先只发这一句反问，然后停下**：

是否是对当前工作区采用 clangd 重建索引

- 不要生成 `compile_commands.json`
- 不要删 `.cache/clangd`
- 不要跑 `clangd`
- 不要假设用户已经同意

仅当用户明确确认（如：是、对、确认、好、clangd、当前工作区）后再执行下面步骤。

用户明确否认或指向别的索引（ctags、cscope、IDE 全局、别的仓库）时：停止本流程，按对方意图处理。

同一轮里已写明「当前工作区 + clangd」的，视为已确认，可直接重建。

## 确认后：重建当前工作区

工作区根目录：Cursor 打开的 workspace（本对话的工程根）。不要清 `~/.cache/clangd` 全局缓存。

1. **编译数据库**
   - 有 `make compile_commands`（或等价目标）→ 执行它
   - 否则有 CMake 构建目录里的 `compile_commands.json` → 复制或软链到工作区根
   - 否则根上已有 `compile_commands.json` → 保留并用它
   - 都没有 → 停下来说明缺编译数据库，不要假装索引已重建
2. **清项目缓存**：删除工作区根下 `.cache/clangd`（若存在）
3. **可选校验**：`clangd --check=<一个源文件> --compile-commands-dir=<工作区根>`；失败则报告，仍继续提示重载
4. **完成后必须提示**（原话，可附一句操作路径）：

重载窗口

可补：命令面板执行 `Developer: Reload Window`，或 `Clangd: Restart language server`。

## 省 tokens：禁止把仓库和产物读进对话

本流程只用 **Shell**，不要 Read / Grep / Glob / Task 扫源码。clangd 在本机建索引，不需要模型看见头文件。

允许看的输出（截断）：

- `make compile_commands` 的几行 stderr
- `python3 -c "import json; print(len(json.load(open('compile_commands.json'))))"` 只打条目数
- `clangd --check=... 2>&1 | tail -20`（一个源文件）
- `ls` / `test -f` 判断 `compile_commands.json`、`.cache/clangd` 是否存在

禁止：

- `Read` 整份 `compile_commands.json` 或任意 `.idx` / clangd 日志
- 把 `clangd --check` 的完整 stdout 贴进回复
- 为「搞清工程结构」而 Explore 全仓库、读 Makefile 全文（有 `make compile_commands` 直接跑）
- 清 `~/.cache/clangd`

工具结果已经进上下文：命令本身就要短，用 `tail` / `wc` / `len()`，不要 `cat`。

## 常见借口

| 借口 | 实际 |
|------|------|
| 「用户就是要重建，反问浪费时间」 | 必须先反问那一句 |
| 「顺手把 Makefile 脚本也改了」 | 未要求则不改生成脚本 |
| 「清掉 ~/.cache/clangd 更彻底」 | 只清当前工作区 `.cache/clangd` |
| 「先读完工程再重建更稳」 | 本流程不读源码；缺编译数据库就停 |
| 「把 compile_commands 读进来核对」 | 只报条目数；内容给 clangd 用 |
