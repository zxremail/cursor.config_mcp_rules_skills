"""Mermaid 代码块启发式分析：判断是否需要降级为 customfig。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MermaidBlock:
    index: int
    start: int
    end: int
    source: str
    reasons: list[str] = field(default_factory=list)

    @property
    def should_downgrade(self) -> bool:
        return bool(self.reasons)


_FENCE_RE = re.compile(
    r"```[ \t]*mermaid[^\n]*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)

_NODE_PATTERNS = [
    re.compile(r"\[[^\]]+\]"),  # [text]
    re.compile(r"\(\([^)]+\)\)"),  # ((text))
    re.compile(r"\(\[[^\]]+\]\)"),  # ([text])
    re.compile(r"\{[^}]+\}"),  # {text}
    re.compile(r"\>[^\<\n]+\]"),  # asymmetric
    re.compile(r"\[\[[^\]]+\]\]"),  # [[text]]
]

_SUBGRAPH_RE = re.compile(r"^\s*subgraph\b", re.MULTILINE | re.IGNORECASE)
_BIDIR_RE = re.compile(r"<[-=]+>|<[-=]+>|[-=]+>")
_MULTILINE_NODE_RE = re.compile(
    r"\[[^\]]*\n[^\]]*\]|\(\[[^\]]*\n[^\]]*\]\)|\{[^}]*\n[^}]*\}",
    re.MULTILINE,
)
_LIST_IN_NODE_RE = re.compile(r"\[[^\]]*(?:<br\s*/?>|\\n).*?(?:[-*•]|\d+\.)", re.IGNORECASE)


def extract_mermaid_blocks(markdown: str) -> list[MermaidBlock]:
    blocks: list[MermaidBlock] = []
    for i, m in enumerate(_FENCE_RE.finditer(markdown)):
        blocks.append(
            MermaidBlock(
                index=i,
                start=m.start(),
                end=m.end(),
                source=m.group(1).strip(),
            )
        )
    return blocks


def _count_nodes(src: str) -> int:
    seen: set[str] = set()
    count = 0
    for pat in _NODE_PATTERNS:
        for m in pat.finditer(src):
            key = m.group(0)
            if key not in seen:
                seen.add(key)
                count += 1
    # flowchart 行内节点 id[Label]
    for m in re.finditer(r"^\s*([A-Za-z_][\w-]*)\s*[\[\(\{]", src, re.MULTILINE):
        key = m.group(1)
        if key.lower() not in ("subgraph", "end", "class", "style", "click"):
            if key not in seen:
                seen.add(key)
                count += 1
    return count


def _estimate_vertical_layers(src: str) -> int:
    """粗略估计纵向分层：subgraph 深度 + 连续 TB/BT 流向段落。"""
    max_depth = 0
    depth = 0
    for line in src.splitlines():
        if _SUBGRAPH_RE.search(line):
            depth += 1
            max_depth = max(max_depth, depth)
        if re.match(r"^\s*end\s*$", line, re.IGNORECASE):
            depth = max(0, depth - 1)
    # 无 subgraph 时用节点行数粗估
    if max_depth == 0:
        node_lines = [
            ln
            for ln in src.splitlines()
            if re.search(r"[\[\(\{].*[\]\)\}]", ln) and not ln.strip().startswith("%%")
        ]
        return min(6, max(1, len(node_lines) // 4))
    return max_depth


def _count_parallel_subgraphs(src: str) -> int:
    return len(_SUBGRAPH_RE.findall(src))


def _count_bidir_edges(src: str) -> int:
    return len(_BIDIR_RE.findall(src))


def analyze_block(block: MermaidBlock) -> MermaidBlock:
    src = block.source
    reasons: list[str] = []

    nodes = _count_nodes(src)
    if nodes > 15:
        reasons.append(f"节点数 {nodes} > 15")

    layers = _estimate_vertical_layers(src)
    if layers > 4:
        reasons.append(f"纵向层级约 {layers} > 4")

    subgraphs = _count_parallel_subgraphs(src)
    if subgraphs > 3:
        reasons.append(f"subgraph 数 {subgraphs} > 3")

    if _MULTILINE_NODE_RE.search(src):
        reasons.append("节点含多行文本")

    if _count_bidir_edges(src) >= 3:
        reasons.append("双向/复杂连接较多")

    if _LIST_IN_NODE_RE.search(src):
        reasons.append("节点内嵌列表或表格样式内容")

    block.reasons = reasons
    return block


def analyze_markdown(markdown: str) -> list[MermaidBlock]:
    return [analyze_block(b) for b in extract_mermaid_blocks(markdown)]
