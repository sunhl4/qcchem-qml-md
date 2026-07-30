#!/usr/bin/env python3
"""Publication-quality MD/ML active-learning flowchart (Chinese)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent / "md_ml_active_learning_flow.png"
OUT_ALT = [
    Path("/tmp/shuzhi_unified/figures/principle/md_ml_active_learning_flow.png"),
    Path(__file__).resolve().parent / "shuzhi_demo/principle/md_ml_active_learning_flow.png",
]

# Nature-Methods-like restrained palette
INK = "#0F172A"
BODY = "#1E293B"   # nearly as dark as title — readable when shrunk
SOFT = "#334155"
HAIR = "#C8D0DA"
PAPER = "#F4F1EC"
BAND = "#EDE9E3"

P1 = "#2A4F8A"
P1_FILL = "#C5D6EF"
P1_BAND = "#E6EDF6"
P2 = "#4E3F6E"
P2_FILL = "#D5CBE6"
P2_BAND = "#EDE8F3"
P3 = "#8A4333"
P3_FILL = "#E6CBBF"
P3_BAND = "#F3E9E4"
DEC = "#7A5F18"
DEC_BG = "#F0E0A8"
OK = "#246044"
OK_BG = "#C5E0D0"
LOOP = "#5A5046"

FONT_CANDIDATES = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf",
]


def _setup_font() -> None:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            name = font_manager.FontProperties(fname=path).get_name()
            plt.rcParams.update(
                {
                    "font.family": "sans-serif",
                    "font.sans-serif": [name, "DejaVu Sans"],
                    "axes.unicode_minus": False,
                    "pdf.fonttype": 42,
                    "ps.fonttype": 42,
                }
            )
            return


def _band(ax, x, y, w, h, title, num, accent, wash):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=0.16",
            facecolor=wash,
            edgecolor=HAIR,
            linewidth=0.9,
            zorder=0,
        )
    )
    # numbered square
    s = 0.38
    sx, sy = x + 0.22, y + h - 0.52
    ax.add_patch(
        FancyBboxPatch(
            (sx, sy),
            s,
            s,
            boxstyle="round,pad=0.0,rounding_size=0.08",
            facecolor=accent,
            edgecolor="none",
            zorder=1,
        )
    )
    ax.text(sx + s / 2, sy + s / 2, num, ha="center", va="center", fontsize=13.5, fontweight="bold", color="white", zorder=2)
    ax.text(sx + s + 0.16, sy + s / 2, title, ha="left", va="center", fontsize=13.5, fontweight="bold", color=accent, zorder=2)


def _card(ax, x, y, w, h, title, lines, fill, accent):
    # solid phase-colored fill — no nested white plate
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.12",
            facecolor=fill,
            edgecolor=accent,
            linewidth=1.55,
            zorder=3,
        )
    )
    cx = x + w / 2
    ax.text(
        cx,
        y + h * 0.68,
        title,
        ha="center",
        va="center",
        fontsize=14.5,
        fontweight="bold",
        color=INK,
        zorder=5,
    )
    ax.text(
        cx,
        y + h * 0.30,
        "\n".join(lines),
        ha="center",
        va="center",
        fontsize=11.5,
        color=BODY,
        linespacing=1.5,
        zorder=5,
    )


def _diamond(ax, cx, cy, w, h, title, subtitle, fill, accent):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor=accent, linewidth=1.6, zorder=4))
    if subtitle:
        ax.text(cx, cy + h * 0.14, title, ha="center", va="center", fontsize=13.5, fontweight="bold", color=INK, zorder=5)
        ax.text(cx, cy - h * 0.18, subtitle, ha="center", va="center", fontsize=11.0, color=BODY, zorder=5)
    else:
        ax.text(cx, cy, title, ha="center", va="center", fontsize=13.5, fontweight="bold", color=INK, zorder=5)


def _mini(ax, x, y, w, h, title, sub, fill, accent):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=0.10",
            facecolor=fill,
            edgecolor=accent,
            linewidth=1.55,
            zorder=3,
        )
    )
    ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=14.0, fontweight="bold", color=INK, zorder=5)
    ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=11.0, color=BODY, zorder=5)


def _arrow(ax, pts, color=SOFT, lw=1.5, ms=11):
    for i in range(len(pts) - 1):
        last = i == len(pts) - 2
        ax.add_patch(
            FancyArrowPatch(
                pts[i],
                pts[i + 1],
                arrowstyle="-|>" if last else "-",
                mutation_scale=ms,
                linewidth=lw,
                color=color,
                shrinkA=0,
                shrinkB=0,
                zorder=2,
                joinstyle="round",
                capstyle="round",
            )
        )


def _chip(ax, x, y, text, color, bg):
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=12.0,
        fontweight="bold",
        color=color,
        zorder=6,
        bbox=dict(boxstyle="round,pad=0.20", facecolor=bg, edgecolor="none", alpha=0.96),
    )


def main() -> None:
    _setup_font()

    fig, ax = plt.subplots(figsize=(13.6, 9.2), dpi=100)
    ax.set_xlim(0, 13.6)
    ax.set_ylim(0, 9.2)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    # header
    ax.text(6.8, 8.82, "在线学习主动环", ha="center", va="center", fontsize=22.0, fontweight="bold", color=INK)
    ax.text(
        6.8,
        8.42,
        "qchem-stack · md_bridge    ·    冷启动 → 训练 / MD / 采样 → 量子标注 → 难例回灌",
        ha="center",
        va="center",
        fontsize=11.5,
        color=SOFT,
    )
    ax.add_patch(Rectangle((0.7, 8.18), 12.2, 0.012, facecolor=HAIR, edgecolor="none", zorder=0))

    # bands
    bx, bw = 0.45, 12.7
    by1, bh = 5.95, 2.05
    by2 = 3.35
    by3 = 0.58
    bh3 = 2.25

    _band(ax, bx, by1, bw, bh, "初始化", "1", P1, P1_BAND)
    _band(ax, bx, by2, bw, bh, "每轮：训练 → MD → 采样", "2", P2, P2_BAND)
    _band(ax, bx, by3, bw, bh3, "标注 → 验证 → 收敛判断", "3", P3, P3_BAND)

    # node geometry — leave clear top margin under phase title
    nh = 1.32
    ny1 = by1 + 0.22
    ny2 = by2 + 0.22
    ny3 = by3 + 0.32
    left = 1.15

    # phase 1
    wa = 2.42
    g = 0.26
    xa = left
    xb = xa + wa + g
    xc = xb + wa + g
    wc = 2.42
    d_cx, d_cy = 11.05, ny1 + nh / 2
    dw, dh = 2.35, 1.55

    _card(ax, xa, ny1, wa, nh, "A  冷启动", ["label_base_geometry_only", "1 帧 QMEF"], P1_FILL, P1)
    _card(ax, xb, ny1, wa, nh, "B  种子扩增（可选）", ["bond_stretch / jitter", "n_seed 帧"], P1_FILL, P1)
    _card(ax, xc, ny1, wc, nh, "C  构建力场", ["build_force_field_handle", "qmlff / classical_h2"], P1_FILL, P1)
    _diamond(ax, d_cx, d_cy, dw, dh, "D  轮次", "round 1 … max_rounds", DEC_BG, DEC)

    # phase 2
    w2 = 3.05
    g2 = 0.34
    xd1 = left + 0.2
    xd2 = xd1 + w2 + g2
    xd3 = xd2 + w2 + g2
    _card(ax, xd1, ny2, w2, nh, "D1  训练", ["train_force_field_on_qmef", "warm_start"], P2_FILL, P2)
    _card(ax, xd2, ny2, w2, nh, "D2  分子动力学", ["run_jaxmd_trajectory", "NVT-Langevin"], P2_FILL, P2)
    _card(ax, xd3, ny2, w2, nh, "D3  轨迹采样", ["select_geometries", "n_candidate_frames"], P2_FILL, P2)

    # phase 3
    w3 = 2.72
    g3 = 0.28
    xd4 = left + 0.1
    xd5 = xd4 + w3 + g3
    c_cx, c_cy = 8.15, ny3 + nh / 2 + 0.08
    cw, ch = 2.25, 1.48
    xe = 10.35
    we, he = 2.2, 0.72
    ye = ny3 + 0.78
    yh = ny3 - 0.02

    _card(ax, xd4, ny3, w3, nh, "D4  量子标注", ["label_geometries", "UQC VQE / mock"], P3_FILL, P3)
    _card(ax, xd5, ny3, w3, nh, "D5  能量验证", ["|E_QML − E_qchem|", "vs tolerance"], P3_FILL, P3)
    _diamond(ax, c_cx, c_cy, cw, ch, "全部收敛？", "", DEC_BG, DEC)
    _mini(ax, xe, ye, we, he, "结束", "summary + extxyz", OK_BG, OK)
    _mini(ax, xe, yh, we, he, "难例回灌", "merge top-k", P3_FILL, P3)

    # arrows
    cy1 = ny1 + nh / 2
    _arrow(ax, [(xa + wa, cy1), (xb, cy1)], P1, 1.55)
    _arrow(ax, [(xb + wa, cy1), (xc, cy1)], P1, 1.55)
    _arrow(ax, [(xc + wc, cy1), (d_cx - dw / 2, cy1)], P1, 1.55)

    mid12 = by2 + bh + 0.10
    _arrow(ax, [(d_cx, d_cy - dh / 2), (d_cx, mid12), (xd1 + w2 / 2, mid12), (xd1 + w2 / 2, ny2 + nh)], SOFT, 1.4)

    cy2 = ny2 + nh / 2
    _arrow(ax, [(xd1 + w2, cy2), (xd2, cy2)], P2, 1.55)
    _arrow(ax, [(xd2 + w2, cy2), (xd3, cy2)], P2, 1.55)

    mid23 = by3 + bh3 + 0.12
    _arrow(ax, [(xd3 + w2 / 2, ny2), (xd3 + w2 / 2, mid23), (xd4 + w3 / 2, mid23), (xd4 + w3 / 2, ny3 + nh)], SOFT, 1.4)

    cy3 = ny3 + nh / 2
    _arrow(ax, [(xd4 + w3, cy3), (xd5, cy3)], P3, 1.55)
    _arrow(ax, [(xd5 + w3, cy3), (c_cx - cw / 2, cy3)], P3, 1.55)

    _arrow(ax, [(c_cx + cw * 0.28, c_cy + 0.26), (xe, ye + he / 2)], OK, 1.6, 12)
    _chip(ax, (c_cx + cw / 2 + xe) / 2 + 0.05, ye + he / 2 + 0.28, "是", OK, OK_BG)

    _arrow(ax, [(c_cx + cw * 0.28, c_cy - 0.26), (xe, yh + he / 2)], P3, 1.6, 12)
    _chip(ax, (c_cx + cw / 2 + xe) / 2 + 0.05, yh + he / 2 - 0.28, "否", P3, P3_FILL)

    rail = 12.85
    _arrow(ax, [(xe + we, yh + he / 2), (rail, yh + he / 2), (rail, d_cy), (d_cx + dw / 2, d_cy)], LOOP, 1.45, 11)
    by = (yh + he / 2 + d_cy) / 2
    ax.add_patch(Circle((rail, by), 0.30, facecolor=PAPER, edgecolor=LOOP, linewidth=1.2, zorder=5))
    ax.text(rail, by, "回灌", ha="center", va="center", fontsize=9.5, fontweight="bold", color=LOOP, zorder=6)

    ax.text(
        6.8,
        0.22,
        "主动学习：MD 轨迹上 |ΔE| 大的构型 → 量子标注 → 扩训练集 → 再训力场",
        ha="center",
        va="center",
        fontsize=11.0,
        color=SOFT,
        style="italic",
    )

    fig.tight_layout(pad=0.12)
    for path in [OUT, *OUT_ALT]:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=240, bbox_inches="tight", facecolor=PAPER, pad_inches=0.20)
            print(f"wrote {path}")
        except OSError as e:
            print(f"skip {path}: {e}")
    plt.close(fig)


if __name__ == "__main__":
    main()
