#!/usr/bin/env python3
"""Generate PPT-ready MD/ML active-learning flowchart (Chinese + clean layout)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

FONT = "/mnt/c/Windows/Fonts/msyh.ttc"
OUT = Path(__file__).resolve().parent / "md_ml_active_learning_flow.png"

X0 = 0.6
BW = 15.4  # band width

# band_y, band_h, label, bg, node_y
PHASES = [
    (7.35, 2.55, "①  初始化", "#F8FAFF", 7.88),
    (4.35, 2.55, "②  每轮：训练 → MD → 采样", "#FBF7FF", 4.88),
    (1.35, 2.55, "③  标注 → 验证 → 收敛判断", "#FFF8F7", 1.88),
]

NODES = [
    (1.0, 7.88, 3.35, 1.55, "A  冷启动", "label_base_geometry_only\n1 帧 QMEF", "#E8F0FE", "#4285F4", "box"),
    (4.65, 7.88, 3.35, 1.55, "B  种子扩增（可选）", "bond_stretch / jitter\nn_seed 帧", "#E8F0FE", "#4285F4", "box"),
    (8.3, 7.88, 3.35, 1.55, "C  构建力场", "build_force_field_handle\nqmlff / classical_h2", "#E8F0FE", "#4285F4", "box"),
    (12.45, 7.72, 2.75, 1.85, "D  轮次", "round 1 … max_rounds", "#FEF7E0", "#F9AB00", "diamond"),
    (1.0, 4.88, 3.35, 1.55, "D1  训练", "train_force_field_on_qmef\nwarm_start", "#F3E8FD", "#9334E6", "box"),
    (4.65, 4.88, 3.35, 1.55, "D2  分子动力学", "run_jaxmd_trajectory\nNVT-Langevin", "#F3E8FD", "#9334E6", "box"),
    (8.3, 4.88, 3.35, 1.55, "D3  轨迹采样", "select_geometries\nn_candidate_frames", "#F3E8FD", "#9334E6", "box"),
    (1.0, 1.88, 3.65, 1.55, "D4  量子标注", "label_geometries\nUQC VQE / mock", "#FCE8E6", "#EA4335", "box"),
    (5.05, 1.88, 3.65, 1.55, "D5  能量验证", "abs(E_QML - E_qchem)\nvs tol", "#FCE8E6", "#EA4335", "box"),
    (9.25, 1.72, 2.55, 1.85, "全部收敛？", "", "#FEF7E0", "#F9AB00", "diamond"),
    (12.35, 2.78, 2.75, 1.25, "结束", "summary + extxyz", "#E6F4EA", "#34A853", "box"),
    (12.35, 1.48, 2.75, 1.25, "难例回灌", "merge top-k", "#FCE8E6", "#EA4335", "box"),
]


def _setup_font() -> None:
    font_manager.fontManager.addfont(FONT)
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei"],
            "axes.unicode_minus": False,
        }
    )


def _box(ax, node, zorder=2):
    x, y, w, h, title, subtitle, fc, ec, shape = node
    if shape == "diamond":
        cx, cy = x + w / 2, y + h / 2
        ax.add_patch(
            Polygon(
                [(cx, y), (x + w, cy), (cx, y + h), (x, cy)],
                closed=True,
                facecolor=fc,
                edgecolor=ec,
                linewidth=2.0,
                zorder=zorder,
            )
        )
        ax.text(cx, cy + 0.1, title, ha="center", va="center", fontsize=13.5, fontweight="bold", color="#202124", zorder=zorder + 1)
        if subtitle:
            ax.text(cx, cy - 0.25, subtitle, ha="center", va="center", fontsize=9.5, color="#5F6368", zorder=zorder + 1)
    else:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.1",
                facecolor=fc,
                edgecolor=ec,
                linewidth=2.0,
                zorder=zorder,
            )
        )
        ax.text(x + w / 2, y + h * 0.67, title, ha="center", va="center", fontsize=13.5, fontweight="bold", color="#202124", zorder=zorder + 1)
        if subtitle:
            ax.text(x + w / 2, y + h * 0.28, subtitle, ha="center", va="center", fontsize=9.5, color="#5F6368", linespacing=1.35, zorder=zorder + 1)


def _arrow(ax, pts, color="#444", lw=2.0, label=None, label_offset=(0, 0)):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        is_last = i == len(pts) - 2
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>" if is_last else "-",
                mutation_scale=16,
                linewidth=lw,
                color=color,
                shrinkA=0,
                shrinkB=0,
                zorder=1,
            )
        )
    if label:
        x1, y1 = pts[-2]
        x2, y2 = pts[-1]
        ax.text(
            (x1 + x2) / 2 + label_offset[0],
            (y1 + y2) / 2 + label_offset[1],
            label,
            fontsize=11,
            color=color,
            fontweight="bold",
            zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.9),
        )


def main() -> None:
    _setup_font()
    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 11.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # header — isolated from first band (gap >= 0.35)
    ax.text(8.0, 10.72, "在线学习主动环", ha="center", va="center", fontsize=26, fontweight="bold", color="#202124")
    ax.text(8.0, 10.32, "qchem-stack · md_bridge", ha="center", va="center", fontsize=12, color="#5F6368")

    for band_y, band_h, label, bg, _ in PHASES:
        ax.add_patch(
            FancyBboxPatch(
                (X0, band_y),
                BW,
                band_h,
                boxstyle="round,pad=0.01,rounding_size=0.06",
                facecolor=bg,
                edgecolor="#E0E0E0",
                linewidth=1.0,
                zorder=0,
            )
        )
        # phase title: top strip inside band, above all nodes
        ax.text(
            X0 + 0.25,
            band_y + band_h - 0.28,
            label,
            fontsize=12,
            fontweight="bold",
            color="#1A73E8",
            va="top",
            ha="left",
        )

    for n in NODES:
        _box(ax, n)

    cy1, cy2, cy3 = 8.655, 5.655, 2.655

    _arrow(ax, [(4.35, cy1), (4.65, cy1)], "#4285F4")
    _arrow(ax, [(8.0, cy1), (8.3, cy1)], "#4285F4")
    _arrow(ax, [(11.65, cy1), (12.45, cy1)], "#4285F4")

    _arrow(ax, [(13.825, 7.72), (13.825, 6.95), (2.675, 6.95), (2.675, 6.43)], "#777")

    _arrow(ax, [(4.35, cy2), (4.65, cy2)], "#9334E6")
    _arrow(ax, [(8.0, cy2), (8.3, cy2)], "#9334E6")

    _arrow(ax, [(9.65, 4.88), (9.65, 3.98), (2.825, 3.98), (2.825, 3.43)], "#777")

    _arrow(ax, [(4.65, cy3), (5.05, cy3)], "#EA4335")
    _arrow(ax, [(8.7, cy3), (9.25, cy3)], "#EA4335")

    _arrow(ax, [(11.8, 2.98), (12.35, 3.405)], "#34A853", label="是", label_offset=(-0.2, 0.1))
    _arrow(ax, [(11.6, 2.35), (12.35, 2.1)], "#EA4335", label="否", label_offset=(-0.25, 0.0))

    _arrow(ax, [(13.85, 2.1), (15.35, 2.1), (15.35, 8.4), (15.2, 8.4)], "#999", lw=1.8)

    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
