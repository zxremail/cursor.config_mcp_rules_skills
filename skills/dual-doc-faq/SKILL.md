---
name: dual-doc-faq
description: >-
  双文档答疑工作流：用户对某份主文档提问时，在主文档中添加简短注解，同时在配套 FAQ 文档中添加完整 Q&A 条目。
  适用于任何"主文档 + FAQ 文档"的答疑场景。
  Use when the user asks to explain terms, concepts, or mechanisms from a document
  and wants both a brief inline annotation and a detailed FAQ entry,
  or mentions "答疑", "解释一下", "啥意思", "什么意思", "介绍下", "补充进文档", "补充说明".
---

# 双文档答疑工作流

用户在阅读一份**主文档**时提问术语和概念。每次回答需**同步更新两个文件**：主文档保持精炼，FAQ 文档保持详尽。

## 前提

使用本 Skill 前，需要确认两个目标文件：

| 角色 | 说明 | 更新策略 |
|------|------|----------|
| **主文档** | 用户正在阅读的文档（架构设计、技术方案等） | **简短**：在原文附近插入 blockquote 注解 + 扩展术语表（如有） |
| **FAQ 文档** | 配套的答疑参考文档 | **详尽**：完整 Q&A 条目（多层子节、表格、类比、一句话总结） |

如果 FAQ 文档尚不存在，按 [附录 A：FAQ 文档初始化模板](#appendix-a) 创建。

---

## 工作流

### Step 1：定位原文

在主文档中找到用户引用的原文位置（章节号、段落），确认上下文语境。

### Step 2：更新主文档（简短注解）

在**原文附近**（紧接段落之后、表格之后、或相关注解组内）插入一条简短注解。

根据主文档格式选择合适的注解形式：

**Markdown 主文档**：

```markdown
> **名词解读 · {术语名}**：{2-4 句话的精炼解释}。

> **常见疑问：{问题}？** {2-4 句话的精炼回答}。
```

**HTML 主文档**：

```html
<blockquote>
<b>名词解读 · {术语名}</b>：{2-4 句话的精炼解释}。
</blockquote>
```

如果主文档有术语表/词汇表章节，检查是否已包含该术语：
- **已有**：视需要微调措辞
- **没有**：在术语表末尾追加条目

### Step 3：更新 FAQ 文档（详尽 Q&A）

依次完成以下修改：

#### 3a. 导航

在侧边栏/目录的列表末尾追加链接，N = 当前最大编号 + 1：

```html
<li><a href="#qN">QN · {短标题}</a></li>
```

#### 3b. Q&A 条目

在内容区末尾（`</main>` 之前）插入完整条目：

```html
<!-- ==================== QN ==================== -->
<div class="faq-item" id="qN">
<div class="faq-q">
  <span class="q-tag">QN</span>
  <div class="q-text">
    {问题全文}
    <span class="q-source">原文：§X.Y — "{引用的原文片段}"</span>
  </div>
</div>
<div class="faq-a">

<h3>{子话题 1}</h3>
<p>{详细说明}</p>

<h3>{子话题 2}</h3>
<table>
<tr><th>维度</th><th>A</th><th>B</th></tr>
<tr><td>...</td><td>...</td><td>...</td></tr>
</table>

<!-- 按需使用：代码块、有序/无序列表、blockquote、多个 h3/h4 子节 -->

<div class="summary-box">
<b>一句话总结</b>：{一句话概括核心要点}。
</div>
</div>
</div>
```

#### 3c. 内容要求

| 要求 | 说明 |
|------|------|
| **深度** | 假设读者了解本领域但不了解该术语，从"为什么需要"讲起 |
| **结构** | 每个 Q&A 至少 2-3 个 `<h3>` 子节 + 一个对比/总结表格 |
| **类比** | 尽量提供一个日常生活类比帮助理解 |
| **一句话总结** | 必须有，放在 `<div class="summary-box">` 中 |

---

## 注意事项

- 主文档注解要**简短克制**（≤ 4 行），不要让主文档变臃肿
- FAQ 条目要**详尽充分**，不怕长，定位就是深度参考
- 两个文件中同一术语的措辞保持一致
- FAQ 编号从当前最大值 +1 递增，不要跳号
- 如果用户引用的原文横跨多个概念，可以拆成多个 Q&A 条目
- 如果用户没有指定主文档或 FAQ 文档，先询问确认

---

<h2 id="appendix-a">附录 A：FAQ 文档初始化模板</h2>

当 FAQ 文档不存在时，用以下模板创建。将 `{DOC_TITLE}` 替换为实际标题，`{MAIN_DOC_FILE}` 替换为主文档文件名。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{DOC_TITLE} — 术语与概念答疑</title>
<style>
:root{
  --bg:#0d1117; --panel:#161b22; --panel2:#21262d; --border:#30363d;
  --text:#c9d1d9; --muted:#8b949e; --dim:#484f58;
  --blue:#58a6ff; --bluebg:#0d2137; --bluetxt:#79c0ff;
  --green:#3fb950; --greenbg:#122117; --greentxt:#7ee787; --greenborder:#238636;
  --orange:#f0883e; --orangebg:#1a150d; --orangetxt:#ffcc80;
  --purple:#a371f7; --purplebg:#1a1428; --purpletxt:#d2a8ff; --purpleborder:#6e40c9;
  --red:#f85149; --redbg:#2d1215; --redtxt:#ffa198; --redborder:#da3633;
  --yellow:#d4a017; --yellowbg:#1f1a0c; --yellowtxt:#f0d68c;
  --teal:#39c5cf; --tealbg:#0c1f21; --tealtxt:#8be9fd;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;
  font-size:15px;line-height:1.8;}
#layout{display:grid;grid-template-columns:280px 1fr;min-height:100vh}
#sidebar{position:sticky;top:0;height:100vh;overflow:auto;
  background:#0a0d12;border-right:1px solid var(--border);padding:18px 14px;}
#sidebar h1{font-size:14px;color:var(--purple);margin:0 0 4px;letter-spacing:.5px;}
#sidebar h1 small{color:var(--orange);font-size:11px;display:block;margin-top:4px;letter-spacing:0;}
#sidebar .version{font-size:11px;color:var(--dim);margin-bottom:16px;}
#sidebar ol{list-style:none;padding:0;margin:0;font-size:13px;}
#sidebar ol li{margin:3px 0}
#sidebar a{color:var(--muted);text-decoration:none;display:block;padding:4px 8px;border-radius:4px;}
#sidebar a:hover{background:#161b22;color:var(--purpletxt);}
main{padding:40px 56px 120px;max-width:1100px}

.faq-item{margin-bottom:48px;border-bottom:1px dashed var(--border);padding-bottom:40px;}
.faq-item:last-child{border-bottom:none;}
.faq-q{
  display:flex;align-items:flex-start;gap:12px;margin-bottom:18px;
  background:var(--purplebg);border:1px solid var(--purpleborder);border-radius:8px;padding:14px 18px;
}
.faq-q .q-tag{
  background:var(--purple);color:#fff;font-size:10px;font-weight:bold;
  padding:2px 10px;border-radius:10px;white-space:nowrap;margin-top:2px;
}
.faq-q .q-text{color:var(--purpletxt);font-size:16px;font-weight:bold;line-height:1.5;}
.faq-q .q-source{display:block;font-size:11px;color:var(--muted);font-weight:normal;margin-top:4px;}

.faq-a h3{color:var(--orangetxt);margin:20px 0 10px;font-size:16px;}
.faq-a h4{color:var(--greentxt);margin:16px 0 8px;font-size:14px;}
.faq-a p{margin:10px 0}
.faq-a strong{color:#f0f6fc}
.faq-a code{background:#161b22;padding:2px 6px;border-radius:4px;color:var(--orangetxt);font-family:"SF Mono","Cascadia Code",Consolas,monospace;font-size:.9em;border:1px solid var(--border);}
.faq-a pre{background:#161b22;border:1px solid var(--border);padding:14px 18px;border-radius:8px;overflow-x:auto;font-family:"SF Mono","Cascadia Code",Consolas,monospace;font-size:13px;line-height:1.55;}
.faq-a pre code{background:none;border:none;padding:0;color:var(--text);}
.faq-a table{border-collapse:collapse;margin:14px 0;width:100%;font-size:14px;}
.faq-a th,.faq-a td{border:1px solid var(--border);padding:8px 12px;text-align:left;}
.faq-a th{background:#161b22;color:var(--purpletxt);}
.faq-a tr:nth-child(even){background:#0f141a}
.faq-a blockquote{border-left:4px solid var(--purple);background:#161b22;margin:12px 0;padding:12px 18px;color:var(--muted);border-radius:0 6px 6px 0;}
.faq-a blockquote strong{color:var(--text);}
.faq-a ul,.faq-a ol{padding-left:24px}
.faq-a li{margin:4px 0}

.summary-box{
  background:var(--panel);border-radius:8px;border-left:4px solid var(--green);
  padding:14px 18px;margin:16px 0;font-size:14px;line-height:1.7;
}
.summary-box b{color:var(--greentxt);}

@media (max-width:900px){
  #layout{grid-template-columns:1fr}
  #sidebar{position:static;height:auto;}
  main{padding:24px 20px 80px}
}
</style>
</head>
<body>
<div id="layout">
<nav id="sidebar">
<h1>{DOC_TITLE}<small>术语与概念答疑</small></h1>
<div class="version">配套文档：{MAIN_DOC_FILE}</div>
<ol>
<!-- Q&A 导航项在此追加 -->
</ol>
</nav>

<main>

<h1 style="color:#f0f6fc;border-bottom:2px solid var(--purple);padding-bottom:8px;font-size:28px;">{DOC_TITLE} — 术语与概念答疑</h1>
<p style="color:var(--muted);font-size:13px;">本文档收录阅读过程中的常见问题及详细解答，作为 <code>{MAIN_DOC_FILE}</code> 的配套参考。</p>

<!-- Q&A 条目在此追加 -->

</main>
</div>
</body>
</html>
```
