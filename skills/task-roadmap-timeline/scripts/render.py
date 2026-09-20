#!/usr/bin/env python3
"""YAML → .customfig.roadmap-tl HTML fragment (or standalone page)."""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

ICONS = {"trophy": "🏆", "carrot": "🥕"}
THEMES = {"ms", "purple", "orange", "green", "blue", "teal", "rose", "slate"}
SKILL_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = SKILL_DIR / "templates" / "roadmap.css"


def load_plan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise SystemExit("需要 PyYAML：pip install pyyaml") from exc
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit("计划文件根节点必须是 mapping")
    return data


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def split_title(title: str, subtitle: str | None) -> tuple[str, str]:
    if subtitle:
        return title, subtitle
    for sep in ("：", ":"):
        if sep in title:
            left, right = title.split(sep, 1)
            return f"{left}{sep}", right
    return title, ""


def vlines(n: int) -> str:
    return '<div class="rm-vlines" aria-hidden="true">' + "".join("<span></span>" for _ in range(n)) + "</div>"


def icon_span(name: str | None) -> str:
    if not name:
        return ""
    glyph = ICONS.get(str(name), str(name))
    return f'<span class="rm-ico">{esc(glyph)}</span>'


def validate(plan: dict) -> tuple[list[str], int]:
    ticks = (plan.get("time_axis") or {}).get("ticks") or []
    n = len(ticks)
    errors: list[str] = []
    if n < 1:
        errors.append("time_axis.ticks 不能为空")

    def check_span(label: str, start, end) -> None:
        if not isinstance(start, int) or not isinstance(end, int):
            errors.append(f"{label}: start/end 必须是整数")
            return
        if start < 1 or end > n + 1 or start >= end:
            errors.append(f"{label}: 列区间 [{start}, {end}) 超出 1..{n}+1 或为空")

    ms = plan.get("milestones") or {}
    for i, seg in enumerate(ms.get("segments") or []):
        check_span(f"milestones.segments[{i}]", seg.get("start"), seg.get("end"))

    for li, lane in enumerate(plan.get("lanes") or []):
        theme = lane.get("theme") or "slate"
        if theme not in THEMES:
            errors.append(f"lanes[{li}].theme={theme!r} 不在 {sorted(THEMES)}")
        subrows = int(lane.get("subrows") or 1)
        max_row = 0
        for j, item in enumerate(lane.get("items") or []):
            tag = f"lanes[{li}].items[{j}]"
            if item.get("marker") == "diamond":
                at = item.get("at")
                row = int(item.get("row") or 1)
                max_row = max(max_row, row)
                if not isinstance(at, int) or at < 1 or at > n + 1:
                    errors.append(f"{tag}: diamond.at 必须在 1..{n + 1}")
                continue
            start, end = item.get("start"), item.get("end")
            check_span(tag, start, end)
            row = int(item.get("row") or 1)
            rowspan = int(item.get("rowspan") or 1)
            max_row = max(max_row, row + rowspan - 1)
        if max_row > subrows:
            errors.append(f"lanes[{li}]: subrows={subrows} < 实际最大行 {max_row}")
    return errors, n


def render_label(theme: str, title: str, subtitle: str = "") -> str:
    kicker, sub = split_title(title, subtitle or None)
    inner = f'<span class="rm-kicker">{esc(kicker)}</span>'
    if sub:
        inner += f'<span class="rm-sub">{esc(sub)}</span>'
    return f'<aside class="rm-label t-{esc(theme)}">{inner}</aside>'


def item_style(item: dict) -> str:
    if item.get("marker") == "diamond":
        return f"grid-column:{int(item['at'])};grid-row:{int(item.get('row') or 1)}"
    start, end = int(item["start"]), int(item["end"])
    row = int(item.get("row") or 1)
    rowspan = int(item.get("rowspan") or 1)
    if rowspan > 1:
        return f"grid-column:{start}/{end};grid-row:{row} / span {rowspan}"
    return f"grid-column:{start}/{end};grid-row:{row}"


def render_item(item: dict) -> str:
    style = item_style(item)
    if item.get("marker") == "diamond":
        return f'<i class="rm-dia" style="{style}"></i>'
    kind = item.get("type") or "card"
    text = esc(item.get("text") or "")
    if kind == "group-bg":
        return f'<div class="rm-group-bg" style="{style}"></div>'
    if kind == "group-title":
        return f'<div class="rm-group-title" style="{style}">{text}</div>'
    if kind == "group-foot":
        return f'<div class="rm-group-foot" style="{style}">{text}</div>'
    return f'<div class="rm-card" style="{style}">{text}</div>'


def render_milestones(plan: dict, n: int) -> str:
    ms = plan.get("milestones")
    if not ms:
        return ""
    segs = []
    for seg in ms.get("segments") or []:
        start, end = int(seg["start"]), int(seg["end"])
        body = icon_span(seg.get("icon")) + esc(seg.get("text") or "")
        segs.append(f'<div class="rm-ms-seg" style="grid-column:{start}/{end}">{body}</div>')
    label = ms.get("label") or "重要时间节点"
    return f"""
      <div class="rm-row rm-row-ms">
        {render_label("ms", label)}
        <div class="rm-track t-ms" style="--rm-cols:{n}">
          {vlines(n)}
          <div class="rm-ms-bar">{"".join(segs)}</div>
        </div>
      </div>"""


def render_lane(lane: dict, n: int) -> str:
    theme = lane.get("theme") or "slate"
    subrows = int(lane.get("subrows") or 1)
    items = "".join(render_item(it) for it in (lane.get("items") or []))
    return f"""
      <div class="rm-row">
        {render_label(theme, lane.get("title") or "", lane.get("subtitle") or "")}
        <div class="rm-track t-{esc(theme)}" style="--rm-cols:{n};--rm-subrows:{subrows}">
          {vlines(n)}
          {items}
        </div>
      </div>"""


def render_fragment(plan: dict, css: str) -> str:
    errors, n = validate(plan)
    if errors:
        raise SystemExit("计划校验失败：\n- " + "\n- ".join(errors))
    ticks = (plan.get("time_axis") or {}).get("ticks") or []
    tick_html = "".join(f"<div>{esc(t)}</div>" for t in ticks)
    lanes = "".join(render_lane(lane, n) for lane in (plan.get("lanes") or []))
    style = f"<style>\n{css.strip()}\n</style>\n" if css else ""
    return f"""{style}<div class="customfig roadmap-tl">
  <div class="rm-shell">
    <div class="rm-axis">
      <div></div>
      <div class="rm-ticks" style="--rm-cols:{n}">{tick_html}</div>
    </div>
    <div class="rm-body">
      {render_milestones(plan, n)}
      {lanes}
    </div>
  </div>
</div>
"""


STANDALONE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
</head>
<body style="margin:0;background:#fff;">
{body}
</body>
</html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description="将任务计划 YAML 渲染为 roadmap-tl HTML")
    p.add_argument("plan", type=Path, help="plan.yaml 或 plan.json")
    p.add_argument("-o", "--output", type=Path, help="输出路径（默认 stdout）")
    p.add_argument("--standalone", action="store_true", help="包成完整 HTML 页")
    p.add_argument("--no-inline-css", action="store_true", help="不内联 CSS（改走 extra.css）")
    args = p.parse_args()

    plan = load_plan(args.plan)
    css = "" if args.no_inline_css else CSS_PATH.read_text(encoding="utf-8")
    body = render_fragment(plan, css)
    if args.standalone:
        title = esc(plan.get("title") or "任务计划时间表")
        body = STANDALONE.format(title=title, body=body)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
