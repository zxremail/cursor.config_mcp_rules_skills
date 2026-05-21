"""GitHub / VS Code 兼容的 Markdown 标题锚点（github-slugger 算法）。"""
from __future__ import annotations

import re
from pathlib import Path

_PATTERN_FILE = Path(__file__).with_name("github_slugger_regex.pattern")
_SLUG_RE = re.compile(_PATTERN_FILE.read_text(encoding="utf-8"))


def slug(value: str, *, maintain_case: bool = False) -> str:
    if not isinstance(value, str):
        return ""
    if not maintain_case:
        value = value.lower()
    return _SLUG_RE.sub("", value).replace(" ", "-")


class Slugger:
    """与 github-slugger 一致：重复标题自动追加 -1、-2。"""

    def __init__(self) -> None:
        self._occurrences: dict[str, int] = {}
        self.reset()

    def reset(self) -> None:
        self._occurrences = {}

    def slug(self, value: str, *, maintain_case: bool = False) -> str:
        result = slug(value, maintain_case=maintain_case)
        original = result
        while result in self._occurrences:
            self._occurrences[original] = self._occurrences.get(original, 0) + 1
            result = f"{original}-{self._occurrences[original]}"
        self._occurrences[result] = 0
        return result
