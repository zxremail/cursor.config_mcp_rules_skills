"""组装最终 HTML 页面。"""

from __future__ import annotations

import html
import re
from importlib import resources
from pathlib import Path

from .figures import (
    default_figures_dir,
    load_extra_css,
    load_figure_templates,
    render_templates_block,
)
from .frontmatter import DocMeta, split_frontmatter, title_from_markdown
from .mermaid_analyze import MermaidBlock, analyze_markdown, extract_mermaid_blocks

_FIGURE_COMMENT_RE = re.compile(
    r"<!--\s*FIGURE:\s*([a-zA-Z0-9_-]+)\s*-->",
    re.IGNORECASE,
)


def _escape_md_for_script(md: str) -> str:
    return md.replace("</script>", "<\\/script>")


def _preprocess_figure_comments(md: str) -> str:
    def repl(m: re.Match[str]) -> str:
        fid = m.group(1)
        return f"\n```customfig:{fid}\n```\n"

    return _FIGURE_COMMENT_RE.sub(repl, md)


def _replace_mermaid_with_customfig(
    markdown: str, blocks: list[MermaidBlock], templates: dict[str, str]
) -> tuple[str, list[str]]:
    """将应降级的 mermaid 块替换为 customfig 引用（若存在 mermaid-N sidecar）。"""
    applied: list[str] = []
    if not blocks:
        return markdown, applied

    out: list[str] = []
    pos = 0
    for block in blocks:
        out.append(markdown[pos : block.start])
        chunk = markdown[block.start : block.end]
        if block.should_downgrade:
            fig_id = f"mermaid-{block.index}"
            if fig_id in templates:
                chunk = f"```customfig:{fig_id}\n```"
                applied.append(
                    f"块 #{block.index} → customfig:{fig_id}（{'; '.join(block.reasons)}）"
                )
            else:
                chunk = markdown[block.start : block.end]
        out.append(chunk)
        pos = block.end
    out.append(markdown[pos:])
    return "".join(out), applied


def _load_template() -> str:
    return (
        resources.files("md2html")
        .joinpath("templates", "page.html")
        .read_text(encoding="utf-8")
    )


def _load_base_css() -> str:
    return (
        resources.files("md2html")
        .joinpath("templates", "base.css")
        .read_text(encoding="utf-8")
    )


def _load_runtime_js() -> str:
    return (
        resources.files("md2html")
        .joinpath("templates", "runtime.js")
        .read_text(encoding="utf-8")
    )


class BuildResult:
    def __init__(
        self,
        output_path: Path,
        warnings: list[str],
        downgrades_applied: list[str],
        mermaid_blocks: list[MermaidBlock],
    ):
        self.output_path = output_path
        self.warnings = warnings
        self.downgrades_applied = downgrades_applied
        self.mermaid_blocks = mermaid_blocks


def build_html(
    md_path: Path,
    *,
    figures_dir: Path | None = None,
    strict_figures: bool = False,
    title_override: str | None = None,
) -> BuildResult:
    md_path = md_path.resolve()
    raw = md_path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    body = _preprocess_figure_comments(body)

    fig_dir = figures_dir or default_figures_dir(md_path)
    templates = load_figure_templates(fig_dir)
    extra_css = load_extra_css(fig_dir)

    blocks = analyze_markdown(body)
    warnings: list[str] = []
    for b in blocks:
        if b.should_downgrade:
            fig_id = f"mermaid-{b.index}"
            if fig_id not in templates:
                msg = (
                    f"Mermaid 块 #{b.index} 建议降级（{'; '.join(b.reasons)}），"
                    f"缺少 sidecar：{fig_dir / (fig_id + '.html')}"
                )
                warnings.append(msg)
                if strict_figures:
                    raise SystemExit(f"严格模式：{msg}")

    body, downgrades = _replace_mermaid_with_customfig(body, blocks, templates)

    # 校验 customfig / FIGURE 引用
    for m in re.finditer(r"```customfig:([a-zA-Z0-9_-]+)", body):
        fid = m.group(1)
        if fid not in templates:
            msg = f"引用 customfig:{fid} 但 sidecar 中无 {fid}.html"
            warnings.append(msg)
            if strict_figures:
                raise SystemExit(f"严格模式：{msg}")

    fallback_title = md_path.stem
    doc_title = title_override or meta.title or title_from_markdown(body, fallback_title)
    sidebar_title = meta.sidebar_title or doc_title
    sidebar_subtitle = meta.sidebar_subtitle
    version = meta.version

    page = _load_template()
    css = _load_base_css() + ("\n" + extra_css if extra_css else "")
    runtime_js = _load_runtime_js()
    figures_html = render_templates_block(templates)

    html_out = (
        page.replace("{{TITLE}}", html.escape(doc_title))
        .replace("{{SIDEBAR_TITLE}}", html.escape(sidebar_title))
        .replace("{{SIDEBAR_SUBTITLE}}", html.escape(sidebar_subtitle))
        .replace("{{VERSION}}", html.escape(version))
        .replace("{{BASE_CSS}}", css)
        .replace("{{FIGURES_TEMPLATES}}", figures_html)
        .replace("{{RUNTIME_JS}}", runtime_js)
        .replace("{{MD_SOURCE}}", _escape_md_for_script(body))
    )

    # 侧栏副标题：有内容时包 <small>
    if sidebar_subtitle:
        sub_html = f"<small>{html.escape(sidebar_subtitle)}</small>"
    else:
        sub_html = ""
    html_out = html_out.replace("{{SIDEBAR_SUBTITLE_HTML}}", sub_html)

    version_html = (
        f'<div class="version">{html.escape(version)}</div>' if version else ""
    )
    html_out = html_out.replace("{{VERSION_HTML}}", version_html)

    out_path = md_path.with_suffix(".html")
    out_path.write_text(html_out, encoding="utf-8")

    return BuildResult(out_path, warnings, downgrades, blocks)
