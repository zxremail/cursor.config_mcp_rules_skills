"""md2html 命令行入口。"""

from __future__ import annotations

import argparse
import subprocess
import sys
import webbrowser
from pathlib import Path

from . import __version__
from .builder import build_html
from .figures import default_figures_dir
from .mermaid_analyze import analyze_markdown


def _cmd_build(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    exit_code = 0
    for md_path in paths:
        if not md_path.is_file():
            print(f"错误：找不到文件 {md_path}", file=sys.stderr)
            exit_code = 1
            continue
        figures_dir = Path(args.figures) if args.figures else None
        try:
            result = build_html(
                md_path,
                figures_dir=figures_dir,
                strict_figures=args.strict_figures,
                title_override=args.title,
            )
        except SystemExit as e:
            print(str(e), file=sys.stderr)
            exit_code = 1
            continue

        print(f"✓ {result.output_path}")
        for d in result.downgrades_applied:
            print(f"  ↳ 已降级: {d}")
        for w in result.warnings:
            print(f"  ⚠ {w}")
            exit_code = 1 if args.strict_figures else 0

        if result.warnings and not args.strict_figures:
            print("  提示：在浏览器中打开预览，确认 Mermaid / 卡片图显示正常。")

        if args.open:
            url = result.output_path.as_uri()
            if sys.platform == "linux" and not args.no_xdg:
                subprocess.run(["xdg-open", str(result.output_path)], check=False)
            else:
                webbrowser.open(url)

    return exit_code


def _cmd_analyze(args: argparse.Namespace) -> int:
    md_path = Path(args.file)
    if not md_path.is_file():
        print(f"错误：找不到文件 {md_path}", file=sys.stderr)
        return 1
    text = md_path.read_text(encoding="utf-8")
    blocks = analyze_markdown(text)
    if not blocks:
        print("未发现 mermaid 代码块。")
        return 0
    fig_dir = Path(args.figures) if args.figures else default_figures_dir(md_path)
    print(f"文件: {md_path}")
    print(f"sidecar 目录: {fig_dir}\n")
    for b in blocks:
        status = "建议降级" if b.should_downgrade else "可保留 Mermaid"
        print(f"--- 块 #{b.index} [{status}] ---")
        if b.reasons:
            for r in b.reasons:
                print(f"  · {r}")
        else:
            print("  · （未触发降级规则）")
        sidecar = fig_dir / f"mermaid-{b.index}.html"
        print(f"  sidecar: {sidecar} {'(存在)' if sidecar.is_file() else '(缺失)'}")
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="将 Markdown 转为独立 HTML（markdown-to-html 技能规范）",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="构建 HTML")
    p_build.add_argument("files", nargs="+", help="Markdown 文件路径")
    p_build.add_argument(
        "--figures",
        "-f",
        help="customfig sidecar 目录（默认：<stem>.figures/）",
    )
    p_build.add_argument(
        "--strict-figures",
        action="store_true",
        help="应降级或缺失 sidecar 时失败退出",
    )
    p_build.add_argument("--title", help="覆盖文档 <title>")
    p_build.add_argument("--open", action="store_true", help="构建后用浏览器打开")
    p_build.add_argument(
        "--no-xdg",
        action="store_true",
        help="不用 xdg-open，改用 Python webbrowser",
    )
    p_build.set_defaults(func=_cmd_build)

    p_an = sub.add_parser("analyze", help="仅分析 Mermaid 是否应降级")
    p_an.add_argument("file", help="Markdown 文件")
    p_an.add_argument("--figures", "-f", help="sidecar 目录")
    p_an.set_defaults(func=_cmd_analyze)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
