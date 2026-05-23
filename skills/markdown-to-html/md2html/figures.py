"""customfig sidecar 目录加载与合并。"""

from __future__ import annotations

from pathlib import Path


def default_figures_dir(md_path: Path) -> Path:
    return md_path.with_suffix(".figures")


def load_figure_templates(figures_dir: Path) -> dict[str, str]:
    """加载 sidecar：{fig-id}.html → template 片段 HTML。"""
    if not figures_dir.is_dir():
        return {}

    templates: dict[str, str] = {}
    for path in sorted(figures_dir.glob("*.html")):
        fig_id = path.stem
        raw = path.read_text(encoding="utf-8").strip()
        if raw.lower().startswith("<template"):
            templates[fig_id] = raw
        else:
            templates[fig_id] = f'<template id="{fig_id}">\n{raw}\n</template>'
    return templates


def load_extra_css(figures_dir: Path) -> str:
    extra = figures_dir / "extra.css"
    if extra.is_file():
        return extra.read_text(encoding="utf-8")
    return ""


def render_templates_block(templates: dict[str, str]) -> str:
    if not templates:
        return ""
    parts = ["<!-- ============ 自绘图模板 (sidecar) ============ -->"]
    parts.extend(templates.values())
    return "\n\n".join(parts) + "\n"
