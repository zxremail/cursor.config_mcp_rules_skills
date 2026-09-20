#!/usr/bin/env python3
"""YAML → .customfig.assign-tl HTML fragment (or standalone page)."""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = SKILL_DIR / "templates" / "assign.css"
PHASE_THEMES = {"pink", "orange", "blue", "yellow", "green", "mint"}
PERSON_THEMES = {"green", "blue", "rose", "orange", "purple", "teal", "slate"}
STAR_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 2.6l2.7 5.6 6.2.9-4.5 4.3 1.1 6.1L12 16.8 6.5 19.5l1.1-6.1L3.1 9.1l6.2-.9z" '
    'fill="none" stroke="#8B7CF6" stroke-width="1.7" stroke-linejoin="round"/></svg>'
)
START_ICO = (
    '<svg class="as-ico" width="14" height="14" viewBox="0 0 16 16" aria-hidden="true">'
    '<rect x="2" y="1.5" width="10" height="13" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
    '<path d="M6.2 5.2v5.6L11 8z" fill="currentColor"/></svg>'
)


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


def rich(value) -> str:
    raw = "" if value is None else str(value)
    return html.escape(raw, quote=True).replace("&lt;br&gt;", "<br>").replace("&lt;br/&gt;", "<br>")


def ticks_of(plan: dict) -> list:
    ticks = (plan.get("time_axis") or {}).get("ticks") or []
    if len(ticks) < 2:
        raise SystemExit("time_axis.ticks 至少 2 个日期")
    return ticks


def axis_xs(plan: dict) -> list[float]:
    """Percent positions of each tick (len = n)."""
    ticks = ticks_of(plan)
    n = len(ticks)
    axis = plan.get("time_axis") or {}
    weights = axis.get("weights")
    if weights is None:
        weights = [1] * (n - 1)
    if len(weights) != n - 1:
        raise SystemExit(f"weights 长度必须为 ticks-1（{n - 1}），实际 {len(weights)}")
    lead = float(axis.get("lead") if axis.get("lead") is not None else 0.4)
    tail = float(axis.get("tail") if axis.get("tail") is not None else 0.4)
    total = lead + tail + sum(float(w) for w in weights)
    xs = []
    acc = lead
    xs.append(100.0 * acc / total)
    for w in weights:
        acc += float(w)
        xs.append(100.0 * acc / total)
    return xs


def x_of(t: float, xs: list[float]) -> float:
    n = len(xs)
    if t <= 0:
        return 0.0
    if t >= n + 1:
        return 100.0
    if t <= 1:
        return xs[0] * t
    if t >= n:
        return xs[n - 1] + (100.0 - xs[n - 1]) * (t - n)
    i = int(t)
    frac = t - i
    return xs[i - 1] + (xs[i] - xs[i - 1]) * frac


def region_span(item: dict, xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    region = item.get("region")
    if region == "lead":
        return 0.0, xs[0]
    if region == "tail":
        return xs[-1], 100.0
    start = float(item["start"])
    end = float(item["end"])
    if end <= start:
        raise SystemExit(f"区间无效 start={start} end={end}")
    return x_of(start, xs), x_of(end, xs)


def vlines(xs: list[float]) -> str:
    marks = "".join(f'<span class="as-vline" style="left:{x:.3f}%"></span>' for x in xs)
    return f'<div class="as-vlines" aria-hidden="true">{marks}</div>'


def validate(plan: dict) -> None:
    errors: list[str] = []
    ticks = (plan.get("time_axis") or {}).get("ticks") or []
    n = len(ticks)
    if n < 2:
        errors.append("time_axis.ticks 至少 2 个日期")
    xs = axis_xs(plan) if n >= 2 else []

    for i, ph in enumerate(plan.get("phases") or []):
        theme = ph.get("theme") or "slate"
        if theme not in PHASE_THEMES:
            errors.append(f"phases[{i}].theme={theme!r} 不在 {sorted(PHASE_THEMES)}")
        if ph.get("region") not in ("lead", "tail", None) and ph.get("region"):
            errors.append(f"phases[{i}].region 只能是 lead/tail")
        if not ph.get("region"):
            if "start" not in ph or "end" not in ph:
                errors.append(f"phases[{i}] 需要 start/end 或 region")

    for i, ms in enumerate(plan.get("milestones") or []):
        at = ms.get("at")
        if not isinstance(at, (int, float)) or at < 1 or at > n:
            errors.append(f"milestones[{i}].at 必须在 1..{n}")

    lanes = plan.get("lanes") or []
    for li, lane in enumerate(lanes):
        kind = lane.get("type")
        if kind not in ("branch", "person"):
            errors.append(f"lanes[{li}].type 必须是 branch 或 person")
        if kind == "person":
            theme = lane.get("theme") or "slate"
            if theme not in PERSON_THEMES:
                errors.append(f"lanes[{li}].theme={theme!r} 不在 {sorted(PERSON_THEMES)}")
            for j, it in enumerate(lane.get("items") or []):
                if "start" not in it or "end" not in it:
                    errors.append(f"lanes[{li}].items[{j}] 需要 start/end")
                elif float(it["end"]) <= float(it["start"]):
                    errors.append(f"lanes[{li}].items[{j}] 区间为空")
        if kind == "branch":
            line = lane.get("line") or {}
            theme = line.get("theme") or "main"
            if theme not in ("main", "feature"):
                errors.append(f"lanes[{li}].line.theme 必须是 main 或 feature")
            if theme == "feature" and ("fork_at" not in line or "merge_at" not in line):
                errors.append(f"lanes[{li}] feature 需要 fork_at 与 merge_at")
    if errors:
        raise SystemExit("计划校验失败：\n- " + "\n- ".join(errors))
    return xs


def pack_rows(items: list[dict]) -> list[int]:
    """Assign a 1-based row index to each item; no overlap on the same row."""
    rows_end: list[float] = []
    assigned = []
    for it in items:
        start, end = float(it["start"]), float(it["end"])
        placed = None
        for r, last in enumerate(rows_end):
            if start >= last:
                rows_end[r] = end
                placed = r + 1
                break
        if placed is None:
            rows_end.append(end)
            placed = len(rows_end)
        assigned.append(placed)
    return assigned


def render_phases(plan: dict, xs: list[float]) -> str:
    segs = []
    widths = []
    for ph in plan.get("phases") or []:
        x0, x1 = region_span(ph, xs)
        w = max(x1 - x0, 0.2)
        widths.append(w)
        theme = esc(ph.get("theme") or "orange")
        ico = START_ICO if ph.get("icon") == "start" else ""
        segs.append(f'<div class="as-phase t-{theme}" style="flex:{w:.4f}">{ico}{esc(ph.get("text") or "")}</div>')
    return f"""
    <div class="as-row as-row-phases">
      <aside class="as-side"></aside>
      <div class="as-track"><div class="as-phasebar">{"".join(segs)}</div></div>
    </div>"""


def render_dates(plan: dict, xs: list[float]) -> str:
    ticks = ticks_of(plan)
    caps = []
    for t, x in zip(ticks, xs):
        caps.append(f'<span class="as-date" style="left:{x:.3f}%">{esc(t)}</span>')
    return f"""
    <div class="as-row as-row-dates">
      <aside class="as-side"><span class="as-side-sub">时间轴线</span></aside>
      <div class="as-track">
        {vlines(xs)}
        <div class="as-date-line"></div>
        {"".join(caps)}
      </div>
    </div>"""


def git_groups(lanes: list[dict]) -> list[tuple[str, list]]:
    """Split lanes into ('git', [branch...]) or ('person', [lane])."""
    out = []
    buf = []
    for lane in lanes:
        if lane.get("type") == "branch":
            buf.append(lane)
            continue
        if buf:
            out.append(("git", buf))
            buf = []
        out.append(("person", [lane]))
    if buf:
        out.append(("git", buf))
    return out


def split_space_title(title: str) -> str:
    if title.endswith("项目空间") or title.endswith("任务空间"):
        head, tail = title[:-4], title[-4:]
        return f'<span>{esc(head)}</span><span class="as-side-sub">{esc(tail)}</span>'
    return f"<span>{esc(title)}</span>"


def render_git(group: list[dict], xs: list[float]) -> str:
    rows = len(group)
    h = 56 * rows
    labels = []
    for i, lane in enumerate(group):
        inner = split_space_title(lane.get("title") or "")
        labels.append(
            f'<aside class="as-side" style="grid-column:1;grid-row:{i + 1}">'
            f'<div class="as-side-text">{inner}</div></aside>'
        )

    main_i = 0
    for i, lane in enumerate(group):
        if (lane.get("line") or {}).get("theme") != "feature":
            main_i = i
            break
    main_y = 56 * main_i + 28

    lines = [
        f'<line x1="1.2" y1="{main_y}" x2="97.4" y2="{main_y}" '
        f'stroke="#1A1A1A" stroke-width="5" stroke-linecap="round"/>',
        f'<polygon points="99.6,{main_y} 96.4,{main_y - 7} 96.4,{main_y + 7}" fill="#1A1A1A"/>',
    ]
    captions = []
    main_text = (group[main_i].get("line") or {}).get("text") or ""
    if main_text:
        captions.append(
            f'<div class="as-git-caption as-git-main" style="left:52%;top:{main_y - 18}px">{esc(main_text)}</div>'
        )

    for i, lane in enumerate(group):
        line = lane.get("line") or {}
        if (line.get("theme") or "main") != "feature":
            continue
        y = 56 * i + 28
        color = line.get("color") or "#2BB85A"
        fx = x_of(float(line["fork_at"]), xs)
        mx = x_of(float(line["merge_at"]), xs)
        lines.append(
            f'<path d="M {fx:.3f} {main_y} L {fx:.3f} {y} L {mx:.3f} {y} L {mx:.3f} {main_y}" '
            f'fill="none" stroke="{esc(color)}" stroke-width="3.2" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        lines.append(
            f'<polygon points="{mx:.2f},{main_y} {mx - 1.05:.2f},{main_y + 9} {mx + 1.05:.2f},{main_y + 9}" '
            f'fill="{esc(color)}"/>'
        )
        text = line.get("text") or ""
        if text:
            mid = (fx + mx) / 2
            captions.append(
                f'<div class="as-git-caption as-git-feat" style="left:{mid:.2f}%;top:{y + 6}px;color:{esc(color)}">'
                f"{esc(text)}</div>"
            )

    return f"""
    <div class="as-git" style="--git-rows:{rows}">
      {"".join(labels)}
      <div class="as-git-canvas">
        {vlines(xs)}
        <svg width="100%" height="100%" viewBox="0 0 100 {h}" preserveAspectRatio="none" aria-hidden="true">
          {"".join(lines)}
        </svg>
        {"".join(captions)}
      </div>
    </div>"""


def render_person(lane: dict, xs: list[float]) -> str:
    items = list(lane.get("items") or [])
    rows = pack_rows(items) if items else [1]
    nsub = max(rows) if rows else 1
    theme = esc(lane.get("theme") or "slate")
    name = lane.get("name") or ""
    fte = lane.get("fte")
    fte_s = str(fte).rstrip("0").rstrip(".") if isinstance(fte, float) else str(fte)
    label = f"{name}-{fte_s}人力" if fte is not None else name
    initial = esc(name[:1] if name else "?")
    avatar = lane.get("avatar")
    if avatar:
        av = f'<div class="as-avatar"><img src="{esc(avatar)}" alt=""></div>'
    else:
        av = f'<div class="as-avatar">{initial}</div>'
    pills = []
    for it, row in zip(items, rows):
        x0, x1 = region_span(it, xs)
        top_pct = ((row - 1) + 0.5) / nsub * 100
        pills.append(
            f'<div class="as-pill p-{theme}" style="left:{x0:.3f}%;width:{max(x1 - x0, 1):.3f}%;'
            f'top:{top_pct:.2f}%;transform:translateY(-50%)">{rich(it.get("text") or "")}</div>'
        )
    return f"""
    <div class="as-row as-row-person">
      <aside class="as-side">{av}<div class="as-side-text"><span>{esc(label)}</span></div></aside>
      <div class="as-track" style="--as-subrows:{nsub};min-height:{max(56, nsub * 48)}px">
        {vlines(xs)}
        {"".join(pills)}
      </div>
    </div>"""


def render_stars(plan: dict, xs: list[float]) -> str:
    stars = []
    for ms in plan.get("milestones") or []:
        x = x_of(float(ms["at"]), xs)
        stars.append(
            f'<div class="as-star" style="left:{x:.3f}%">{STAR_SVG}<span>{esc(ms.get("text") or "")}</span></div>'
        )
    return f"""
    <div class="as-row as-row-stars">
      <aside class="as-side"></aside>
      <div class="as-track">
        {vlines(xs)}
        {"".join(stars)}
      </div>
    </div>"""


def render_fragment(plan: dict, css: str) -> str:
    xs = validate(plan)
    chunks = [render_phases(plan, xs), render_dates(plan, xs)]
    for kind, group in git_groups(plan.get("lanes") or []):
        if kind == "git":
            chunks.append(render_git(group, xs))
        else:
            chunks.append(render_person(group[0], xs))
    chunks.append(render_stars(plan, xs))
    style = f"<style>\n{css.strip()}\n</style>\n" if css else ""
    return f"""{style}<div class="customfig assign-tl">
  <div class="as-shell">
    {"".join(chunks)}
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
    p = argparse.ArgumentParser(description="将任务落地分工 YAML 渲染为 assign-tl HTML")
    p.add_argument("plan", type=Path, help="plan.yaml 或 plan.json")
    p.add_argument("-o", "--output", type=Path, help="输出路径（默认 stdout）")
    p.add_argument("--standalone", action="store_true", help="包成完整 HTML 页")
    p.add_argument("--no-inline-css", action="store_true", help="不内联 CSS")
    args = p.parse_args()

    plan = load_plan(args.plan)
    css = "" if args.no_inline_css else CSS_PATH.read_text(encoding="utf-8")
    body = render_fragment(plan, css)
    if args.standalone:
        title = esc(plan.get("title") or "任务落地分工时间表")
        body = STANDALONE.format(title=title, body=body)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
