#!/usr/bin/env python3
"""Render static PNG charts for docs/qwen三模型评测报告.md."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "qwen_benchmark"
FONT_PATH = ROOT / "docs" / "assets" / "fonts" / "SimHei.ttf"

OUT.mkdir(parents=True, exist_ok=True)

if not FONT_PATH.exists():
    raise SystemExit(
        f"Missing CJK font: {FONT_PATH}\n"
        "Copy SimHei.ttf from Windows Fonts or install fonts-noto-cjk."
    )

font_manager.fontManager.addfont(str(FONT_PATH))
FONT_NAME = font_manager.FontProperties(fname=str(FONT_PATH)).get_name()

plt.rcParams.update(
    {
        "font.family": FONT_NAME,
        "font.sans-serif": [FONT_NAME],
        "axes.unicode_minus": False,
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }
)

COLORS = {
    "flash": "#43a047",
    "coder": "#1e88e5",
    "max": "#e53935",
}

LEGEND = {
    "flash": "qwen-flash",
    "coder": "qwen3-coder-next",
    "max": "qwen3.7-max",
}


def save(fig: plt.Figure, name: str) -> None:
    path = OUT / name
    fig.savefig(path, facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"wrote {path}")


def chart_model_routing() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.0, 3.4)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec="#333"):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1.2,
            edgecolor=ec,
            facecolor=fc,
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

    box(0.2, 1.1, 1.4, 0.8, "问题/需求", "#fafafa")
    box(2.0, 1.1, 1.4, 0.8, "任务类型?", "#fff3e0")
    box(4.0, 1.9, 1.8, 0.9, "qwen-flash\n~60% 用量", "#e8f5e9")
    box(4.0, 0.7, 1.8, 0.9, "qwen3-coder-next\n~30% 用量", "#e3f2fd")
    box(4.0, -0.5, 1.8, 0.9, "qwen3.7-max\n~10% 用量", "#fce4ec")
    box(7.0, 1.1, 1.2, 0.8, "输出", "#fafafa")

    arrows = [
        ((1.6, 1.5), (2.0, 1.5)),
        ((3.4, 1.5), (4.0, 2.35), "问答/摘要"),
        ((3.4, 1.5), (4.0, 1.15), "写代码"),
        ((3.4, 1.5), (4.0, -0.05), "架构/推理"),
        ((5.8, 2.35), (7.0, 1.7)),
        ((5.8, 1.15), (7.0, 1.5)),
        ((5.8, -0.05), (7.0, 1.3)),
    ]
    for item in arrows:
        start, end = item[0], item[1]
        label = item[2] if len(item) > 2 else None
        ax.add_patch(
            FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12, color="#555", lw=1.1)
        )
        if label:
            mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
            ax.text(mx, my + 0.12, label, fontsize=7, ha="center", color="#666")

    ax.set_title("模型路由建议", fontsize=12, pad=8)
    save(fig, "01_model_routing.png")


def chart_score_radar() -> None:
    labels = ["S1 日常", "S2 编程", "S3 架构", "效率", "约束遵守"]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    scores = {
        "flash": [4.0, 1.5, 3.5, 5.0, 2.5],
        "coder": [4.0, 5.0, 4.0, 4.5, 3.5],
        "max": [3.5, 5.0, 5.0, 2.0, 4.5],
    }

    fig, ax = plt.subplots(figsize=(6.2, 5.8), subplot_kw={"polar": True})
    for key, vals in scores.items():
        data = vals + vals[:1]
        ax.plot(angles, data, "o-", linewidth=2, label=LEGEND[key], color=COLORS[key])
        ax.fill(angles, data, alpha=0.12, color=COLORS[key])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.grid(True, alpha=0.35)
    ax.set_title(
        "三模型场景得分（满分 5）\n含 S1-S3 正式评分 + 效率/约束补充维度", pad=20, fontsize=10
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), fontsize=8)
    save(fig, "02_score_radar.png")


def chart_latency() -> None:
    x = np.arange(3)
    labels = ["S1", "S2", "S3"]
    series = {
        "flash": [3.41, 8.01, 18.82],
        "coder": [2.11, 4.02, 12.61],
        "max": [31.77, 14.93, 34.84],
    }
    fig, ax = plt.subplots(figsize=(7, 4))
    for key, vals in series.items():
        ax.plot(x, vals, "o-", linewidth=2, markersize=7, label=LEGEND[key], color=COLORS[key])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("延迟 (秒)")
    ax.set_ylim(0, 40)
    ax.grid(True, alpha=0.3)
    ax.set_title("各场景 API 延迟对比")
    ax.legend(fontsize=8)
    save(fig, "03_latency.png")


def chart_tokens() -> None:
    x = np.arange(3)
    labels = ["S1", "S2", "S3"]
    series = {
        "flash": [472, 1085, 1804],
        "coder": [445, 1139, 2305],
        "max": [3850, 2099, 4432],
    }
    fig, ax = plt.subplots(figsize=(7, 4))
    for key, vals in series.items():
        ax.plot(x, vals, "o-", linewidth=2, markersize=7, label=LEGEND[key], color=COLORS[key])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Token 数")
    ax.set_ylim(0, 5000)
    ax.grid(True, alpha=0.3)
    ax.set_title("各场景 Token 消耗对比")
    ax.legend(fontsize=8)
    save(fig, "04_tokens.png")


def chart_pipeline_topo() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    lanes = [
        (
            "flash: Adapt + VQD + QSE 侧支",
            3.8,
            "#fff8e1",
            ["Adapt-VQE", "VQD 2态", "QSE gaussian_h"],
        ),
        (
            "coder-next: Adapt + VQD 主干",
            2.3,
            "#e3f2fd",
            ["Adapt-VQE 8轮", "VQD E1/E2", "QSE 离线验证"],
        ),
        (
            "3.7-max: Adapt + QSE（推荐）",
            0.8,
            "#e8f5e9",
            ["FermionicAdaptVQE", "QSE singles", "广义本征值"],
        ),
    ]

    for title, y, fc, nodes in lanes:
        ax.add_patch(
            FancyBboxPatch(
                (0.3, y - 0.55),
                9.4,
                1.2,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                linewidth=1,
                edgecolor="#888",
                facecolor=fc,
                alpha=0.9,
            )
        )
        ax.text(0.5, y + 0.45, title, fontsize=9, fontweight="bold", va="center")
        xs = [1.5, 4.0, 6.5]
        for i, (x, label) in enumerate(zip(xs, nodes, strict=True)):
            ax.add_patch(
                FancyBboxPatch(
                    (x, y - 0.25),
                    1.8,
                    0.55,
                    boxstyle="round,pad=0.02,rounding_size=0.05",
                    linewidth=1,
                    edgecolor="#444",
                    facecolor="white",
                )
            )
            ax.text(x + 0.9, y + 0.025, label, ha="center", va="center", fontsize=8)
            if i < len(nodes) - 1:
                ax.add_patch(
                    FancyArrowPatch(
                        (x + 1.85, y + 0.025),
                        (xs[i + 1] - 0.05, y + 0.025),
                        arrowstyle="->",
                        mutation_scale=12,
                        color="#555",
                    )
                )

    ax.set_title("H4 流水线拓扑对比", fontsize=12, pad=10)
    save(fig, "05_pipeline_topo.png")


def main() -> None:
    chart_model_routing()
    chart_score_radar()
    chart_latency()
    chart_tokens()
    chart_pipeline_topo()


if __name__ == "__main__":
    main()
