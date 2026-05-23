"""简单 YAML frontmatter 解析（无第三方依赖）。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class DocMeta:
    title: str = ""
    sidebar_title: str = ""
    sidebar_subtitle: str = ""
    version: str = ""
    extra: dict[str, str] = field(default_factory=dict)


_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_simple_yaml(body: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip("'\"")
        data[key] = val
    return data


def split_frontmatter(markdown: str) -> tuple[DocMeta, str]:
    m = _FM_RE.match(markdown)
    if not m:
        return DocMeta(), markdown
    raw = _parse_simple_yaml(m.group(1))
    body = markdown[m.end() :]
    meta = DocMeta(
        title=raw.get("title", ""),
        sidebar_title=raw.get("sidebar_title", raw.get("sidebar-title", "")),
        sidebar_subtitle=raw.get("sidebar_subtitle", raw.get("sidebar-subtitle", "")),
        version=raw.get("version", ""),
        extra={k: v for k, v in raw.items() if k not in ("title", "sidebar_title", "sidebar_subtitle", "version", "sidebar-title", "sidebar-subtitle")},
    )
    return meta, body


def title_from_markdown(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback
