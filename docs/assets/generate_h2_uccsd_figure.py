#!/usr/bin/env python3
"""Publication figure: H2 UCCSD vs SCF vs FCI (述职 / examples)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

# Load verified numbers if present (else fall back to constants below).
_VERIFIED = Path(__file__).resolve().parents[2] / "results/h2_uccsd_verified/summary.json"
if _VERIFIED.is_file():
    import json as _json

    _v = _json.loads(_VERIFIED.read_text(encoding="utf-8"))
    E_SCF = float(_v["scf_energy"])
    E_UCCSD = float(_v["energy_after_variational"])
    E_FCI = float(_v["fci_energy"])
else:
    # Verified 2026-07-17: example_h2_uccsd.yaml + PySCF RHF/FCI (H–H=1.4 Bohr, sto-3g)
    E_SCF = -1.116714325062551
    E_UCCSD = -1.137275940454672
    E_FCI = -1.1372759436170439

OUTS = [
    Path(__file__).resolve().parent / "shuzhi_demo/pipeline/h2_uccsd_vs_scf.png",
    Path("/tmp/shuzhi_unified/figures/pipeline/h2_uccsd_vs_scf.png"),
    Path(__file__).resolve().parents[2] / "examples/plots/h2_uccsd_vs_scf.png",
]

FONT_CANDIDATES = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf",
]

INK = "#0F172A"
BODY = "#1E293B"
SOFT = "#475569"
HAIR = "#D0D7E0"
PAPER = "#F7F5F1"
PANEL = "#FFFFFF"

C_SCF = "#1E3A5F"
C_UCC = "#0F766E"
C_FCI = "#C2410C"
C_ACC = "#64748B"


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


def _style(ax) -> None:
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=BODY, labelsize=12, length=4, width=0.9)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#94A3B8")
        ax.spines[sp].set_linewidth(1.1)
    ax.grid(True, axis="y", color="#E8EEF4", lw=0.85, zorder=0)


def main() -> None:
    _setup_font()

    d_scf_mha = (E_SCF - E_FCI) * 1e3
    d_ucc_ha = abs(E_UCCSD - E_FCI)
    d_ucc_mha = max(d_ucc_ha * 1e3, 1e-9)
    corr_mha = abs(E_UCCSD - E_SCF) * 1e3
    chem_acc = 1.6

    fig = plt.figure(figsize=(13.4, 7.6), dpi=120, facecolor=PAPER)
    # leave clear room for header + footer (no overlap with axes)
    gs = GridSpec(
        1,
        2,
        figure=fig,
        width_ratios=[1.25, 1.0],
        wspace=0.34,
        left=0.09,
        right=0.97,
        top=0.80,
        bottom=0.20,
    )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    _style(ax0)
    _style(ax1)
    ax1.grid(True, axis="x", color="#E8EEF4", lw=0.85, zorder=0)
    ax1.grid(False, axis="y")

    # ---- Header (above axes) ----
    fig.text(
        0.5,
        0.94,
        "H2 UCCSD：SCF vs 变分 vs FCI",
        ha="center",
        va="center",
        fontsize=19,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.5,
        0.885,
        "sto-3g · H–H = 1.4 Bohr · example_h2_uccsd.yaml 实跑  ·  同几何 PySCF FCI 对账",
        ha="center",
        va="center",
        fontsize=11.5,
        color=SOFT,
    )

    # ---- (a) Energy ladder — stagger UCCSD / FCI labels (energies nearly identical) ----
    x_line0, x_line1 = 0.28, 0.72

    # SCF level
    ax0.plot([x_line0, x_line1], [E_SCF, E_SCF], color=C_SCF, lw=2.6, solid_capstyle="round", zorder=2)
    ax0.scatter([x_line0], [E_SCF], s=160, color=C_SCF, edgecolors="white", linewidths=1.8, zorder=4)
    ax0.text(x_line0 - 0.04, E_SCF, "SCF (RHF)", ha="right", va="center", fontsize=12.5, fontweight="bold", color=C_SCF)
    ax0.text(x_line1 + 0.04, E_SCF, f"{E_SCF:.6f} Ha", ha="left", va="center", fontsize=11.5, fontweight="bold", color=C_SCF)

    # Shared lower band (UCCSD ≈ FCI) — one line, two staggered labels
    ax0.axhspan(E_FCI - 0.0010, E_FCI + 0.0010, color=C_FCI, alpha=0.08, zorder=0)
    ax0.plot([x_line0, x_line1], [E_FCI, E_FCI], color=C_FCI, lw=2.2, ls="--", zorder=2)
    ax0.scatter([x_line0], [E_UCCSD], s=150, color=C_UCC, edgecolors="white", linewidths=1.8, zorder=5)
    ax0.scatter([x_line0 + 0.06], [E_FCI], s=130, color=C_FCI, edgecolors="white", linewidths=1.6, zorder=4, marker="D")

    # labels ABOVE / BELOW the shared line — never on the line
    dy = 0.0038
    ax0.text(
        x_line0 - 0.04,
        E_UCCSD + dy,
        "UCCSD (VQE)",
        ha="right",
        va="bottom",
        fontsize=12.5,
        fontweight="bold",
        color=C_UCC,
    )
    ax0.text(
        x_line1 + 0.04,
        E_UCCSD + dy,
        f"{E_UCCSD:.6f} Ha",
        ha="left",
        va="bottom",
        fontsize=11.5,
        fontweight="bold",
        color=C_UCC,
    )
    ax0.text(
        x_line0 - 0.04,
        E_FCI - dy,
        "FCI (参考)",
        ha="right",
        va="top",
        fontsize=12.5,
        fontweight="bold",
        color=C_FCI,
    )
    ax0.text(
        x_line1 + 0.04,
        E_FCI - dy,
        f"{E_FCI:.6f} Ha",
        ha="left",
        va="top",
        fontsize=11.5,
        fontweight="bold",
        color=C_FCI,
    )

    # correlation arrow — place to the right of mid-gap, clear of labels
    ax0.annotate(
        "",
        xy=(0.50, E_UCCSD + 0.0012),
        xytext=(0.50, E_SCF - 0.0012),
        arrowprops=dict(arrowstyle="<->", color=SOFT, lw=1.5, mutation_scale=11),
        zorder=3,
    )
    ax0.text(
        0.54,
        0.5 * (E_SCF + E_UCCSD),
        f"相关能 {corr_mha:.1f} mHa",
        ha="left",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color=SOFT,
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#FFFFFF", edgecolor=HAIR, linewidth=1.0, alpha=0.96),
        zorder=6,
    )

    ax0.set_xlim(-0.15, 1.15)
    ax0.set_ylim(E_FCI - 0.012, E_SCF + 0.010)
    ax0.set_xticks([])
    ax0.set_ylabel("总能量  (Hartree)", fontsize=13, color=BODY, labelpad=6)
    ax0.set_title("(a)  能量阶梯（放大相关能区间）", fontsize=14, fontweight="bold", color=INK, pad=10, loc="left")

    # ---- (b) Error log bars ----
    y = np.array([1.15, 0.40])
    ax1.axvspan(1e-9, chem_acc, color="#D1FAE5", alpha=0.50, zorder=0)
    ax1.axvline(chem_acc, color=C_ACC, ls="--", lw=1.6, zorder=2)
    ax1.text(
        chem_acc * 1.2,
        1.78,
        "化学精度\n1.6 mHa",
        ha="left",
        va="top",
        fontsize=10.5,
        color=C_ACC,
        fontweight="bold",
    )

    ax1.barh(y, [d_scf_mha, d_ucc_mha], height=0.40, color=[C_SCF, C_UCC], edgecolor="white", linewidth=1.3, log=True, zorder=3)

    # value labels to the RIGHT of bars, with padding from bar end
    ax1.text(d_scf_mha * 1.12, y[0], f"{d_scf_mha:.2f} mHa", va="center", ha="left", fontsize=12.5, fontweight="bold", color=C_SCF)
    ax1.text(3e-5, y[1], f"{d_ucc_ha:.2e} Ha ≈ 0", va="center", ha="left", fontsize=12.5, fontweight="bold", color=C_UCC)

    ax1.set_yticks(y)
    ax1.set_yticklabels(["SCF", "UCCSD"], fontsize=13.5, fontweight="bold", color=INK)
    ax1.set_xlabel(r"$|E - E_{\mathrm{FCI}}|$  (mHa, 对数轴)", fontsize=12.5, color=BODY, labelpad=6)
    ax1.set_xlim(1e-9, 100)
    ax1.set_ylim(-0.1, 2.05)
    ax1.set_title("(b)  相对 FCI 误差", fontsize=14, fontweight="bold", color=INK, pad=10, loc="left")

    # ---- Footer verdict — reserved band below axes, no overlap ----
    fig.patches.append(
        FancyBboxPatch(
            (0.16, 0.035),
            0.68,
            0.085,
            boxstyle="round,pad=0.012,rounding_size=0.016",
            facecolor="#ECFDF5",
            edgecolor="#6EE7B7",
            linewidth=1.3,
            transform=fig.transFigure,
            figure=fig,
            clip_on=False,
            zorder=10,
        )
    )
    fig.text(
        0.5,
        0.078,
        f"结论：UCCSD 与 FCI 相差 {d_ucc_ha:.2e} Ha  ·  远低于化学精度（1.6 mHa）",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color=C_UCC,
        zorder=11,
    )

    for out in OUTS:
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            # pad_inches keeps footer clear of crop
            fig.savefig(out, dpi=260, facecolor=PAPER, bbox_inches="tight", pad_inches=0.28)
            print(f"wrote {out} ({out.stat().st_size})")
        except OSError as e:
            print(f"skip {out}: {e}")
    plt.close(fig)


if __name__ == "__main__":
    main()
