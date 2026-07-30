#!/usr/bin/env python3
"""竞品能力打分板：正式版（去掉口语提示，只保留强弱对比信息）。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

for fp in ["/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf"]:
    if Path(fp).exists():
        font_manager.fontManager.addfont(fp)
        name = font_manager.FontProperties(fname=fp).get_name()
        plt.rcParams.update({"font.sans-serif": [name, "DejaVu Sans"], "axes.unicode_minus": False})
        break

ROWS = [
    ("Methods / repro 可审计", 3, 2, 2, 2, 5),
    ("国内云 / UQC 适配", 4, 4, 3, 3, 5),
    ("MD/ML 力场在线学习", 2, 2, 1, 3, 5),
    ("论文复现友好（可加插件）", 3, 3, 2, 3, 5),
    ("开源可检证", 1, 5, 5, 5, 5),
    ("配置 / YAML 纪律", 5, 2, 2, 2, 5),
    ("工作流编排成熟度", 5, 3, 2, 2, 4),
    ("算法广度", 5, 5, 3, 2, 4),
    ("经典化学 / 嵌入深度", 5, 5, 3, 2, 4),
    ("企业商业云（Nexus 级）", 5, 2, 3, 2, 3),
    ("可微分 / 通用 QML", 1, 1, 2, 5, 3),
]
COLS = ["InQuanto", "Tangelo", "Qiskit Nature", "PennyLane", "本平台"]
mat = np.array([[*r[1:]] for r in ROWS], float)
ylabels = [r[0] for r in ROWS]
n_r, n_c = len(ROWS), 5

BG = "#F7F5F2"
SURFACE = "#FFFFFF"
INK = "#1C1917"
MUTED = "#78716C"
RULE = "#E7E5E4"
NAVY = "#172554"
TEAL = "#0F766E"
TEAL_SOFT = "#F0FDFA"
TEAL_EDGE = "#5EEAD4"
AMBER = "#9A3412"

def face(v, ours):
    v = int(v)
    if ours:
        return {1: "#CCFBF1", 2: "#99F6E4", 3: "#5EEAD4", 4: "#14B8A6", 5: "#0F766E"}[v]
    return {1: "#FAFAF9", 2: "#F5F5F4", 3: "#E7E5E4", 4: "#A8A29E", 5: "#44403C"}[v]

def tcol(v, ours):
    v = int(v)
    if ours:
        return "#115E59" if v <= 3 else "#FFFFFF"
    return INK if v <= 3 else "#FFFFFF"

fig = plt.figure(figsize=(12.5, 14.6), dpi=220, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

def R(x, y, w, h, fc, ec=None, lw=0, z=2, rad=1.0):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rad}",
        facecolor=fc, edgecolor=ec if ec is not None else fc,
        linewidth=lw, zorder=z))

# Header — factual only
R(0, 92.5, 100, 7.5, NAVY, rad=0)
ax.text(50, 96.9, "竞品能力打分板", ha="center", va="center",
        fontsize=32, fontweight="bold", color="white", zorder=5)
ax.text(50, 94.0, "评分 1–5（弱→强）　·　青色列 = 本平台　·　依据公开能力面自评",
        ha="center", va="center", fontsize=13, color="#94A3B8", zorder=5)

# Matrix — slightly taller since footer strategy line removed
cx0, cy0, cw, ch = 4.0, 33.0, 92.0, 57.5
R(cx0, cy0, cw, ch, SURFACE, RULE, lw=1.15, rad=1.4, z=1)

pad = 3.0
ix, iy = cx0 + pad, cy0 + pad
iw, ih = cw - 2 * pad, ch - 2 * pad
label_w = 32.0
col_w = (iw - label_w) / n_c
head_h = 6.5
body_h = ih - head_h
row_h = body_h / n_r

R(ix + label_w + 4 * col_w + 0.4, iy + 0.5, col_w - 0.8, ih - 1.0,
  TEAL_SOFT, TEAL_EDGE, lw=1.0, rad=0.9, z=2)

for j, name in enumerate(COLS):
    ax.text(ix + label_w + (j + 0.5) * col_w, iy + ih - head_h * 0.48, name,
            ha="center", va="center", fontsize=15,
            fontweight="bold" if j == 4 else "medium",
            color=TEAL if j == 4 else INK, zorder=4)

ax.plot([ix, ix + iw], [iy + ih - head_h, iy + ih - head_h], color=RULE, lw=1.2, zorder=3)

pill_h = row_h * 0.56
pill_w = min(col_w * 0.58, 5.2)

for i, lab in enumerate(ylabels):
    ry = iy + ih - head_h - (i + 0.5) * row_h
    ax.text(ix + 0.6, ry, lab, ha="left", va="center", fontsize=13.5, color=INK, zorder=4)
    if i < n_r - 1:
        ax.plot([ix, ix + iw], [iy + ih - head_h - (i + 1) * row_h] * 2,
                color="#F5F5F4", lw=1.0, zorder=3)
    for j in range(n_c):
        v = int(mat[i, j])
        px = ix + label_w + (j + 0.5) * col_w
        ours = j == 4
        R(px - pill_w / 2, ry - pill_h / 2, pill_w, pill_h, face(v, ours), rad=0.65, z=4)
        ax.text(px, ry - 0.05, str(v), ha="center", va="center", fontsize=15,
                fontweight="bold", color=tcol(v, ours), zorder=5)

# Bottom summary — formal titles, no coaching language
gap = 3.0
bw = (100 - 8 - gap) / 2
by, bh = 4.5, 26.0
left, right = 4.0, 4.0 + bw + gap

us = [
    "Methods / repro 可审计（5）",
    "国内云 / UQC 适配（5）",
    "MD/ML 力场在线学习（5）",
    "论文复现友好 / 可加插件（5）",
    "开源可检证、YAML 配置纪律（5）",
]
them = [
    "工作流编排成熟度 — InQuanto（5）",
    "算法广度 / 经典化学嵌入 — InQuanto · Tangelo（5）",
    "企业商业云（Nexus 级）— InQuanto（5）",
    "可微分 / 通用 QML — PennyLane（5）",
    "IBM 生态标准件 — Qiskit Nature",
]

def card(x, title, accent, lines):
    R(x, by, bw, bh, SURFACE, RULE, lw=1.15, rad=1.3, z=2)
    th = 4.8
    R(x + 0.15, by + bh - th - 0.1, bw - 0.3, th, accent, rad=0.85, z=3)
    ax.add_patch(Rectangle((x + 0.15, by + bh - th - 0.1), bw - 0.3, 1.3,
                           facecolor=accent, edgecolor="none", zorder=3))
    ax.text(x + bw / 2, by + bh - th / 2 - 0.12, title,
            ha="center", va="center", fontsize=16, fontweight="bold",
            color="white", zorder=4)
    top = by + bh - th - 2.2
    bottom = by + 2.2
    span = top - bottom
    step = span / len(lines)
    for k, line in enumerate(lines):
        ly = top - (k + 0.5) * step
        ax.add_patch(Circle((x + 2.8, ly), 0.5, facecolor=accent, edgecolor="none", zorder=4))
        ax.text(x + 4.5, ly, line, ha="left", va="center", fontsize=13.2, color=INK, zorder=4)

card(left, "本平台优势维度", TEAL, us)
card(right, "竞品优势维度", AMBER, them)

# neutral footnote only
ax.text(50, 2.0,
        "说明：对公开产品能力面的对照评分，非闭源内部基准测试。",
        ha="center", va="center", fontsize=11.5, color=MUTED, zorder=5)

outs = [
    Path("docs/assets/shuzhi_demo/principle/competitor_scoreboard.png"),
    Path("/tmp/shuzhi_unified/figures/principle/competitor_scoreboard.png"),
    Path("docs/assets/competitor_scoreboard.png"),
]
for out in outs:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=240, facecolor=BG, edgecolor="none")
    print("wrote", out, out.stat().st_size)
plt.close()
