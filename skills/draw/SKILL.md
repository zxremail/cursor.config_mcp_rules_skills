---
name: draw
description: >-
  Use when the user types /draw to pick a diagram visual language from the
  catalog, then draw. Slash menu for 画图 / 架构图 / 胶囊图 / 路线图 / 时序图.
disable-model-invocation: true
---

# /draw

**REQUIRED SUB-SKILL:** Read `diagram-style-catalog`，按它的 §0 出菜单（AskQuestion），选定后再 Read 对应样式 Skill 并开始画。

用户已点名 Skill 或贴了对照图：跳过菜单，直接走对应 Skill。
媒介未说清时再问 §2。未选定前禁止画 Mermaid、禁止直接上画板。
