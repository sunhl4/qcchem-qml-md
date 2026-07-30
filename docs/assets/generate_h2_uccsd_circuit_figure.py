#!/usr/bin/env python3
"""H₂ UCCSD–VQE circuit figure (QML-FF B&W style) with strict overlap rules.

Allowed overlaps:
  - qubit wires running under white unitary / gate / measurement boxes
Forbidden:
  - text on wires (outside or inside boxes)
  - text on other text
  - text cutting gate edges
  - frames colliding with each other
  - stage titles colliding with circuit
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "results/h2_uccsd_verified/circuit_meta.json"
SUMMARY = ROOT / "results/h2_uccsd_verified/summary.json"
PARITY = ROOT / "results/h2_uccsd_verified/circuit_parity_review.json"

OUTS = [
    Path(__file__).resolve().parent / "shuzhi_demo/pipeline/h2_uccsd_circuits.png",
    Path("/tmp/shuzhi_unified/figures/pipeline/h2_uccsd_circuits.png"),
    ROOT / "examples/plots/h2_uccsd_circuits.png",
]

RAD = 0.08
LW = 1.4
LW_HEAVY = 2.0


def _rc() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "font.size": 11,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.unicode_minus": False,
        }
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def draw_box(ax, x, y, w, h, *, rounded=True, dashed=False, heavy=False, z=4):
    ls = "--" if dashed else "-"
    lw = LW_HEAVY if heavy and not dashed else LW
    kwargs = dict(facecolor="white", edgecolor="black", linewidth=lw, linestyle=ls, zorder=z)
    if rounded:
        ax.add_patch(
            FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={RAD}", **kwargs)
        )
    else:
        ax.add_patch(Rectangle((x, y), w, h, **kwargs))


def draw_measurement(ax, x, y, size=0.34):
    draw_box(ax, x - size / 2, y - size / 2, size, size, rounded=True, z=5)
    ax.add_patch(Circle((x, y), size * 0.28, facecolor="white", edgecolor="black", lw=1.15, zorder=6))
    ax.plot(
        [x, x + size * 0.18 * np.cos(np.pi / 4)],
        [y, y + size * 0.18 * np.sin(np.pi / 4)],
        "k-",
        lw=1.5,
        zorder=6,
    )


def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.35, mutation_scale=13),
        zorder=7,
    )


def draw_left_brace(ax, x, y1, y2, label, sublabel=None):
    mid = 0.5 * (y1 + y2)
    r = 0.13
    theta = np.linspace(90, 180, 25)
    ax.plot(x + r + r * np.cos(np.radians(theta)), y2 - r + r * np.sin(np.radians(theta)), "k-", lw=LW)
    theta = np.linspace(180, 270, 25)
    ax.plot(x + r + r * np.cos(np.radians(theta)), y1 + r + r * np.sin(np.radians(theta)), "k-", lw=LW)
    ax.plot([x + r, x + r], [y1 + r, y2 - r], "k-", lw=LW)
    ax.text(x - 0.40, mid + (0.22 if sublabel else 0.0), label, ha="right", va="center", fontsize=12)
    if sublabel:
        ax.text(x - 0.40, mid - 0.30, sublabel, ha="right", va="center", fontsize=10.5)


def draw_gate(ax, x, y, text, *, w=0.38, h=0.36, fs=11):
    """Square gate: white box covers wire (allowed); text centered in box."""
    draw_box(ax, x - w / 2, y - h / 2, w, h, rounded=False, z=5)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=6)


def draw_cx(ax, x, y_ctrl, y_tgt):
    ax.plot([x, x], [y_ctrl, y_tgt], "k-", lw=1.25, zorder=3)
    ax.plot(x, y_ctrl, "o", color="black", markersize=6.2, zorder=5)
    ax.add_patch(Circle((x, y_tgt), 0.115, fill=False, edgecolor="black", lw=1.25, zorder=5))
    ax.plot([x, x], [y_tgt - 0.115, y_tgt + 0.115], "k-", lw=1.25, zorder=5)


def mid(a, b):
    return 0.5 * (a + b)


def main() -> None:
    _rc()
    meta = _load(META)
    generators = meta["generators"]
    th4 = float(generators[4]["theta"])

    if PARITY.is_file():
        pr = _load(PARITY)
        occupied = list(pr["occupied"])
        bits = str(pr["bits_msb"])
        elem = pr.get("elem_counts", {})
        n_elem = int(pr.get("elem_total", 192))
    else:
        occupied = [2, 3]
        bits = "1100"
        elem = {"CX": 80, "H": 48, "SX": 24, "SXDG": 24, "RZ": 16}
        n_elem = 192

    from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import (
        pauli_rotation_angle_from_cluster,
    )

    phi = float(
        pauli_rotation_angle_from_cluster(
            float(generators[4]["theta"]),
            complex(*generators[4]["pauli_terms"][0][1]),
        )
    )

    fig = plt.figure(figsize=(15.2, 12.0), facecolor="white")
    ax = fig.add_axes([0.04, 0.035, 0.93, 0.93])
    ax.set_xlim(-3.2, 17.0)
    ax.set_ylim(-2.4, 11.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")

    # ========== Title ==========
    ax.text(7.0, 11.15, r"H$_2$ UCCSD–VQE Circuit (Jordan–Wigner)", ha="center", va="center", fontsize=18)
    ax.text(
        7.0,
        10.55,
        r"sto-3g · H–H = 1.4 Bohr · 4 qubits · 5 variational parameters $\theta$",
        ha="center",
        va="center",
        fontsize=12.5,
    )

    # ========== Panel I wires ==========
    # wire spacing 0.95 → clear inter-wire gaps for in-box text
    y_q = [8.55, 7.60, 6.65, 5.70]
    gap01, gap12, gap23 = mid(y_q[0], y_q[1]), mid(y_q[1], y_q[2]), mid(y_q[2], y_q[3])

    x_w0, x_w1 = 1.20, 11.85
    draw_left_brace(ax, 0.15, y_q[3] - 0.22, y_q[0] + 0.22, r"Qubits $q_0$–$q_3$", r"(JW spin-orbitals)")

    for i, y in enumerate(y_q):
        ax.plot([x_w0, x_w1], [y, y], "k-", lw=1.2, zorder=1)
        ax.text(x_w0 - 0.20, y, rf"$q_{i}$", ha="right", va="center", fontsize=13)

    # Stage titles: dedicated band ABOVE top wire (clearance ≥ 0.45)
    y_stage = y_q[0] + 0.72
    ax.text(2.20, y_stage, r"(1) Prepare $|\mathrm{HF}\rangle$", ha="center", va="center", fontsize=13)
    ax.text(5.05, y_stage, r"(2) Singles $U_{T_1}$", ha="center", va="center", fontsize=13)
    ax.text(8.15, y_stage, r"(3) Doubles $U_{T_2}$", ha="center", va="center", fontsize=13)
    ax.text(10.85, y_stage, r"(4) Estimate $\langle H\rangle$", ha="center", va="center", fontsize=13)

    # (1) X gates — allowed: box covers wire
    for q in occupied:
        draw_gate(ax, 2.20, y_q[q], r"$X$", w=0.44, h=0.44, fs=14)
    # |1100> in free space BELOW bottom wire, LEFT of T1 (no frame collision)
    ax.text(2.20, y_q[3] - 0.62, rf"$|{bits}\rangle$", ha="center", va="top", fontsize=12)

    # Separators in gaps only (not through labels)
    ax.plot([3.25, 3.25], [y_q[3] - 0.20, y_q[0] + 0.35], "k--", lw=1.0, alpha=0.6, zorder=2)
    ax.plot([9.70, 9.70], [y_q[3] - 0.20, y_q[0] + 0.35], "k--", lw=1.0, alpha=0.6, zorder=2)

    # (2)(3) unitary boxes — wires may run under white fill (allowed)
    pad_y = 0.42
    box_y = y_q[3] - pad_y
    box_h = (y_q[0] - y_q[3]) + 2 * pad_y

    t1_x, t1_w = 3.50, 3.00  # gap to T2 ≥ 0.35
    t2_x, t2_w = 6.85, 2.65
    assert t2_x - (t1_x + t1_w) >= 0.30

    draw_box(ax, t1_x, box_y, t1_w, box_h, rounded=True, z=4)
    draw_box(ax, t2_x, box_y, t2_w, box_h, rounded=True, heavy=True, z=4)

    # In-box text ONLY in inter-wire gaps (never on wire y)
    c1 = t1_x + t1_w / 2
    ax.text(c1, gap01 + 0.12, r"$U_{T_1}$", ha="center", va="center", fontsize=15, zorder=5)
    ax.text(c1, gap12 + 0.12, r"$e^{T_1-T_1^\dagger}$", ha="center", va="center", fontsize=12.5, zorder=5)
    ax.text(c1, gap23 + 0.18, r"$\theta_{0:3}$  (4×2 Pauli)", ha="center", va="center", fontsize=11, zorder=5)

    c2 = t2_x + t2_w / 2
    ax.text(c2, gap01 + 0.12, r"$U_{T_2}$", ha="center", va="center", fontsize=15, zorder=5)
    ax.text(c2, gap12 + 0.12, r"$e^{T_2-T_2^\dagger}$", ha="center", va="center", fontsize=12.5, zorder=5)
    ax.text(c2, gap23 + 0.18, rf"$\theta_4={th4:.3f}$  (8 Pauli)", ha="center", va="center", fontsize=11, zorder=5)

    # (4) measurements on wires (box covers wire — allowed)
    x_m = 10.45
    for y in y_q:
        draw_measurement(ax, x_m, y, size=0.34)

    # ⟨H⟩ labels in inter-wire gaps to the RIGHT of meters — NOT on wires
    ax.text(11.05, gap01, r"$\langle H\rangle$", ha="left", va="center", fontsize=14)
    ax.text(11.05, gap12, r"$=\sum_k c_k\langle P_k\rangle$", ha="left", va="center", fontsize=11)

    # Classical VQE — clear of ⟨H⟩ column (⟨H⟩ ends ~12.6)
    class_x = 13.40
    draw_box(ax, class_x, box_y, 2.95, box_h, rounded=True, dashed=True, z=4)
    cc = class_x + 2.95 / 2
    ax.text(cc, gap01 + 0.12, "Classical VQE", ha="center", va="center", fontsize=13, zorder=5)
    ax.text(cc, gap12 + 0.12, r"minimize $E(\theta)$", ha="center", va="center", fontsize=11.5, zorder=5)
    ax.text(cc, gap23 + 0.18, r"update $\theta$", ha="center", va="center", fontsize=11.5, zorder=5)
    draw_arrow(ax, 12.55, gap12, class_x - 0.08, gap12)

    # ========== Equation band (clear of panel I bottom & panel II title) ==========
    y_eq = y_q[3] - 1.25
    ax.text(
        7.0,
        y_eq,
        r"$|\psi(\theta)\rangle = e^{T_1-T_1^\dagger}\, e^{T_2-T_2^\dagger}\, |\mathrm{HF}\rangle"
        r"\qquad\qquad E(\theta)=\langle\psi(\theta)|H|\psi(\theta)\rangle$",
        ha="center",
        va="center",
        fontsize=13.5,
    )

    # ========== Panel II ==========
    y_p5 = y_eq - 0.90
    ax.text(
        7.0,
        y_p5,
        r"(5) Hardware expansion of one Pauli rotation in $U_{T_2}$:  "
        r"$R_{XXXY}(\phi)=\exp(-i\phi\,XXXY/2)$",
        ha="center",
        va="center",
        fontsize=13,
    )

    # Keep panel-II wires below enlarged (5) title (clearance ≥ 0.75)
    y2 = [2.70, 1.80, 0.90, 0.00]

    x0, x1 = 1.20, 15.2
    draw_left_brace(ax, 0.15, y2[3] - 0.18, y2[0] + 0.18, r"Same 4 qubits", None)
    for i, y in enumerate(y2):
        ax.plot([x0, x1], [y, y], "k-", lw=1.2, zorder=1)
        ax.text(x0 - 0.20, y, rf"$q_{i}$", ha="right", va="center", fontsize=12)

    # Column pitch large enough for √X† with larger font
    pitch = 0.90
    x = 1.60

    def step(dx=pitch):
        nonlocal x
        cur = x
        x += dx
        return cur

    draw_gate(ax, step(), y2[3], r"$\sqrt{X}$", w=0.54, h=0.38, fs=11)
    draw_gate(ax, step(), y2[2], r"$H$", w=0.40, h=0.38, fs=13)
    draw_cx(ax, step(), y2[3], y2[2])
    draw_gate(ax, step(), y2[1], r"$H$", w=0.40, h=0.38, fs=13)
    draw_cx(ax, step(), y2[2], y2[1])
    draw_gate(ax, step(), y2[0], r"$H$", w=0.40, h=0.38, fs=13)
    draw_cx(ax, step(), y2[1], y2[0])
    x_rz = step(pitch + 0.10)
    draw_gate(ax, x_rz, y2[0], r"$R_Z$", w=0.52, h=0.40, fs=12)
    # parameter ABOVE top wire, below panel title
    ax.text(x_rz, y2[0] + 0.42, rf"$({phi:.3f})$", ha="center", va="bottom", fontsize=10)
    draw_cx(ax, step(pitch + 0.10), y2[1], y2[0])
    draw_cx(ax, step(), y2[2], y2[1])
    draw_cx(ax, step(), y2[3], y2[2])
    draw_gate(ax, step(pitch + 0.10), y2[3], r"$\sqrt{X}^\dagger$", w=0.66, h=0.38, fs=10)
    draw_gate(ax, step(pitch + 0.06), y2[2], r"$H$", w=0.40, h=0.38, fs=13)
    draw_gate(ax, step(), y2[1], r"$H$", w=0.40, h=0.38, fs=13)
    draw_gate(ax, step(), y2[0], r"$H$", w=0.40, h=0.38, fs=13)

    # Footer below bottom wire
    y_foot = y2[3] - 0.75
    ax.text(
        7.0,
        y_foot,
        r"Every Pauli string in $T_1$/$T_2$ expands like (5).  "
        rf"Full prep = {n_elem} elementary gates "
        rf"(CX={elem.get('CX', 80)}, $H$={elem.get('H', 48)}, "
        rf"$\sqrt{{X}}$/$\sqrt{{X}}^\dagger$={elem.get('SX', 24)}/{elem.get('SXDG', 24)}, "
        rf"$R_Z$={elem.get('RZ', 16)}).",
        ha="center",
        va="center",
        fontsize=11.5,
    )

    e_line = ""
    if SUMMARY.is_file():
        s = _load(SUMMARY)
        e_line = (
            rf"Verified run:  $E_{{\mathrm{{SCF}}}}={s['scf_energy']:.6f}$, "
            rf"$E_{{\mathrm{{var}}}}={s['energy_after_variational']:.6f}$, "
            rf"$E_{{\mathrm{{FCI}}}}={s['fci_energy']:.6f}$, "
            rf"$|E_{{\mathrm{{var}}}}-E_{{\mathrm{{FCI}}}}|={s['abs_delta_var_fci']:.2e}$ Ha"
        )
    ax.text(7.0, y_foot - 0.48, e_line, ha="center", va="center", fontsize=11)

    y_time = y_foot - 1.05
    ax.annotate(
        "",
        xy=(12.8, y_time),
        xytext=(1.3, y_time),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2, mutation_scale=12),
    )
    ax.text(7.0, y_time - 0.35, "Time / algorithm flow", ha="center", va="top", fontsize=11.5)

    for out in OUTS:
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.30)
            print(f"wrote {out} ({out.stat().st_size})")
        except OSError as e:
            print(f"skip {out}: {e}")
    plt.close(fig)


if __name__ == "__main__":
    main()
