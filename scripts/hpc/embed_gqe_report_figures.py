#!/usr/bin/env python3
"""Generate GQE figures and embed them into the project report markdown."""

from __future__ import annotations

import base64
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "docs/assets/gqe_nakaji"
SOURCE = REPO / "docs/gqe_nakaji_项目汇报报告_source.md"
REPORT = REPO / "docs/gqe_nakaji_项目汇报报告.md"
BRIEF = REPO / "docs/gqe_nakaji_repro_report.md"


def generate_figures() -> None:
    subprocess.run(
        [sys.executable, str(REPO / "scripts/hpc/plot_gqe_report_figures.py")], check=True
    )
    subprocess.run(
        [sys.executable, str(REPO / "scripts/hpc/compare_gqe_uccsd_resources.py")],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(REPO / "scripts/hpc/plot_gqe_circuit_metrics.py")],
        check=True,
    )


def embed_images(text: str, assets_dir: Path) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\((?:\./)?assets/gqe_nakaji/([^)]+)\)")

    def repl(m: re.Match[str]) -> str:
        alt, name = m.group(1), m.group(2)
        png = assets_dir / name
        if not png.is_file():
            raise FileNotFoundError(png)
        b64 = base64.b64encode(png.read_bytes()).decode("ascii")
        return f"![{alt}](data:image/png;base64,{b64})"

    return pattern.sub(repl, text)


def main() -> int:
    generate_figures()
    if not SOURCE.is_file():
        raise SystemExit(f"missing source report: {SOURCE}")

    source_text = SOURCE.read_text(encoding="utf-8")
    embedded = embed_images(source_text, ASSETS)

    # legacy path replacements if regex missed (e.g. after prior partial embed)
    for name in ("gqe_circuit_depth_gates.png", "gqe_uccsd_ansatz_compare.png"):
        png = ASSETS / name
        if png.is_file():
            b64 = base64.b64encode(png.read_bytes()).decode("ascii")
            uri = f"data:image/png;base64,{b64}"
            embedded = embedded.replace(f"](assets/gqe_nakaji/{name})", f"]({uri})")

    header = (
        "<!-- 本文件由 gqe_nakaji_项目汇报报告_source.md 自动生成，图片已 base64 内嵌 -->\n"
        "<!-- 重新生成: python scripts/hpc/embed_gqe_report_figures.py -->\n\n"
    )
    REPORT.write_text(header + embedded, encoding="utf-8")
    print(f"wrote {REPORT} ({REPORT.stat().st_size // 1024} KB)")

    # brief report: only refresh if it still uses path refs (skip already-embedded)
    if BRIEF.is_file():
        brief_text = BRIEF.read_text(encoding="utf-8")
        if "assets/gqe_nakaji/" in brief_text and "data:image" not in brief_text:
            BRIEF.write_text(embed_images(brief_text, ASSETS), encoding="utf-8")
            print(f"wrote {BRIEF}")
        else:
            print(f"skip {BRIEF.name} (already embedded or no path refs)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
