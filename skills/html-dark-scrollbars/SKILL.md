---
name: html-dark-scrollbars
description: >-
  Styles HTML scrollbars, progress bars, meters, and range sliders as dark
  (not OS-default bright/white). Use when writing or editing HTML/CSS, local
  dashboards, 暗色页, 深色主题; when the user mentions 进度条, 滚动条, scrollbar,
  progress, meter, range, 太亮, 亮得刺眼, or 改成暗色.
---

# HTML 暗色滚动条 / 进度条

暗色页面不要用系统默认浅色滚动条（白槽灰块）。`progress`、`meter`、`input[type=range]` 同样不要留成亮色。

## 必须做

1. 根上设 `color-scheme: dark`（否则 Chromium/Edge 仍画浅色系统条）。
2. 同时写 Firefox `scrollbar-color` 和 WebKit `::-webkit-scrollbar*`。
3. 有 `overflow` 的面板（日志、表格、侧栏）跟全局同一套，不要只改 `body`。
4. `progress` / `meter` / `range` 用暗槽 + 中灰填充，不要用高饱和亮色当默认。

## 复制这份 CSS

颜色可随页面微调，但**槽必须暗、块必须暗灰**，对比不要高于周围面板。

```css
html {
  color-scheme: dark;
  scrollbar-width: thin;
  scrollbar-color: #4a5568 #161a21; /* thumb track */
}

*::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
*::-webkit-scrollbar-track,
*::-webkit-scrollbar-corner {
  background: #161a21;
}
*::-webkit-scrollbar-thumb {
  background: #3d4654;
  border-radius: 8px;
  border: 2px solid #161a21;
}
*::-webkit-scrollbar-thumb:hover {
  background: #5a6578;
}

progress,
meter,
input[type="range"] {
  accent-color: #5a6578;
}
progress {
  background: #161a21;
}
progress::-webkit-progress-bar {
  background: #161a21;
}
progress::-webkit-progress-value,
progress::-moz-progress-bar {
  background: #4a5568;
}
```

## 禁止

- 只改页面底色、不改滚动条，让系统画白槽。
- 滚动条 thumb 用金/绿高亮（那是强调色，不是条本身）。
- 浅色主题页强行套这份（浅色页用浅槽深块，另写一套）。
