#!/usr/bin/env python3
"""Publication figures for HPC job 6759: H2 bond-scan → pretrain → online learning."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/h2_bondscan_ol_statevector_r20_6759"
OUT_DIR = DATA / "figures"
OUT_ALT = [
    ROOT / "docs/assets/shuzhi_demo/uqc",
    Path("/tmp/shuzhi_unified/figures/uqc"),
]

INK = "#142033"
MUTED = "#4E5D6C"
ACCENT = "#2A4F8A"
ACCENT2 = "#8A4333"
OK = "#246044"
GRID = "#E2E8F0"
PAPER = "#FAF8F5"


def _setup_font() -> None:
    for fp in (
        "/mnt/c/Windows/Fonts/msyh.ttc",
        "/mnt/c/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ):
        if Path(fp).exists():
            font_manager.fontManager.addfont(fp)
            name = font_manager.FontProperties(fname=fp).get_name()
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            break
    plt.rcParams.update(
        {
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#C8D0DA",
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": INK,
            "axes.titlesize": 12,
            "axes.labelsize": 10.5,
            "legend.fontsize": 9,
            "figure.dpi": 160,
        }
    )


def _bonds_from_xyz(path: Path) -> list[float]:
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    bonds: list[float] = []
    while i < len(lines):
        n = int(lines[i])
        i += 2  # skip count + comment
        pos = []
        for _ in range(n):
            parts = lines[i].split()
            pos.append([float(x) for x in parts[1:4]])
            i += 1
        arr = np.asarray(pos, float)
        if arr.shape[0] == 2:
            bonds.append(float(np.linalg.norm(arr[0] - arr[1])))
    return bonds


def _save(fig: plt.Figure, name: str) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [OUT_DIR / name]
    for alt in OUT_ALT:
        alt.mkdir(parents=True, exist_ok=True)
        paths.append(alt / name)
    for p in paths:
        fig.savefig(p, dpi=180, bbox_inches="tight", facecolor="white")
        print("wrote", p)
    return paths


def plot_overview(summary: dict, hist: list[dict], bonds0: list[float], bonds_f: list[float]) -> None:
    rounds = summary["rounds"]
    xs = [r["round_index"] for r in rounds]
    max_de = [r["max_abs_delta_hartree"] for r in rounds]
    mean_de = [r["mean_abs_delta_hartree"] for r in rounds]
    n_train = [r["n_train_after"] for r in rounds]
    mae = [r["training_metrics"]["final_metrics"]["energy_mae"] for r in rounds]
    frmse = [r["training_metrics"]["final_metrics"]["force_rmse"] for r in rounds]
    tol = float(summary["config"]["energy_tolerance_hartree"])

    fig, axes = plt.subplots(2, 2, figsize=(11.2, 8.2))
    fig.suptitle(
        "H2 QML-FF：键长扫描预训练 → 20 轮在线学习（HPC job 6759）",
        fontsize=13.5,
        fontweight="bold",
        color=INK,
        y=0.98,
    )

    ax = axes[0, 0]
    ax.plot(xs, max_de, "o-", color=ACCENT, lw=1.8, ms=5.5, label="max |ΔE|")
    ax.plot(xs, mean_de, "s--", color=ACCENT2, lw=1.5, ms=4.5, label="mean |ΔE|")
    ax.axhline(tol, color=OK, ls=":", lw=1.4, label=f"目标 {tol:g} Ha")
    ax.set_yscale("log")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("|E_QML − E_VQE| (Ha)")
    ax.set_title("校验误差随轮次（对数轴）")
    ax.grid(True, which="both", color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")
    best_i = int(np.argmin(max_de))
    ax.annotate(
        f"最好 max={max_de[best_i]:.3f}\n@ round {xs[best_i]}",
        xy=(xs[best_i], max_de[best_i]),
        xytext=(xs[best_i] + 1.2, max_de[best_i] * 1.8),
        fontsize=8.5,
        color=MUTED,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9),
    )

    ax = axes[0, 1]
    ax.fill_between(xs, [17] + n_train[:-1], n_train, step="pre", color=ACCENT, alpha=0.12)
    ax.plot(xs, n_train, "o-", color=ACCENT, lw=1.8, ms=5)
    ax.axhline(17, color=MUTED, ls="--", lw=1.2, label="预训练后 17 帧")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("累计训练帧数")
    ax.set_title("训练集增长（17 → 56）")
    ax.set_ylim(0, max(n_train) + 8)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False)

    ax = axes[1, 0]
    ep = [h["epoch"] for h in hist]
    ax.plot(ep, [h["loss"] for h in hist], color=ACCENT, lw=1.5, label="train loss")
    ax.set_xlabel("预训练 epoch")
    ax.set_ylabel("Loss")
    ax.set_title(f"Phase B 预训练曲线（120 epoch，{hist[-1].get('total_time', 0):.0f}s 墙钟见 history）")
    # fix title - total_time is in parent
    ax.set_title("Phase B 预训练曲线（120 epoch）")
    ax.grid(True, color=GRID, lw=0.8)
    ax2 = ax.twinx()
    ax2.plot(ep, [h["energy_mae"] for h in hist], color=ACCENT2, lw=1.3, alpha=0.85, label="E MAE")
    ax2.set_ylabel("Energy MAE (Ha)", color=ACCENT2)
    ax2.tick_params(axis="y", labelcolor=ACCENT2)
    lines1, lab1 = ax.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, lab1 + lab2, frameon=False, loc="upper right")

    ax = axes[1, 1]
    phys0 = [b for b in bonds0 if b < 5]
    phys_f = [b for b in bonds_f if b < 5]
    bad_f = [b for b in bonds_f if b >= 5]
    bins = np.linspace(0.7, 2.6, 20)
    ax.hist(phys0, bins=bins, color=MUTED, alpha=0.55, label=f"预训练后 ({len(phys0)})")
    ax.hist(phys_f, bins=bins, color=ACCENT, alpha=0.45, label=f"最终物理键长 ({len(phys_f)})")
    ax.set_xlabel("H–H 键长 (Bohr)")
    ax.set_ylabel("构型数")
    ax.set_title(f"训练集键长覆盖（另有 {len(bad_f)} 个解离/非物理帧）")
    ax.grid(True, axis="y", color=GRID, lw=0.8)
    ax.legend(frameon=False)

    fig.text(
        0.5,
        0.01,
        "Source: HPC job 6759 · statevector VQE · 30 CPU / 120G · wall 9h05m · "
        f"tol={tol:g} Ha · converged=False",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    _save(fig, "h2_bondscan_ol_6759_overview.png")
    plt.close(fig)

    # second figure: training metrics during OL + parity-ish scatter of last-round frames
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    fig.suptitle("在线学习训练指标与末轮能量对照", fontsize=13, fontweight="bold", color=INK)

    ax = axes[0]
    ax.plot(xs, mae, "o-", color=ACCENT, lw=1.7, ms=5, label="train Energy MAE")
    ax.plot(xs, frmse, "s--", color=ACCENT2, lw=1.5, ms=4.5, label="train Force RMSE")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("训练集误差 (Ha / Ha/Bohr)")
    ax.set_title("每轮训练结束时的 fit 误差")
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False)

    ax = axes[1]
    eq = []
    em = []
    for r in rounds:
        for fr in r.get("frames") or []:
            if fr.get("energy_qchem_hartree") == fr.get("energy_qchem_hartree"):
                eq.append(float(fr["energy_qchem_hartree"]))
                em.append(float(fr["energy_qml_hartree"]))
    lo = min(eq + em)
    hi = max(eq + em)
    pad = 0.05 * (hi - lo + 1e-6)
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "--", color=MUTED, lw=1.2, label="y = x")
    # color by round index via scatter of last few rounds more opaque
    colors = []
    for r in rounds:
        for _ in r.get("frames") or []:
            colors.append(r["round_index"])
    sc = ax.scatter(eq, em, c=colors, cmap="viridis", s=28, alpha=0.85, edgecolors="none")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("轮次")
    ax.set_xlabel("E_VQE (Ha)")
    ax.set_ylabel("E_QML (Ha)")
    ax.set_title("MD 校验帧：QML vs VQE 能量")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    _save(fig, "h2_bondscan_ol_6759_train_parity.png")
    plt.close(fig)


def main() -> int:
    _setup_font()
    summary = json.loads((DATA / "md_validation_summary.json").read_text(encoding="utf-8"))
    hist_wrap = json.loads((DATA / "training_history.json").read_text(encoding="utf-8"))
    hist = hist_wrap["train_history"]
    bonds0 = _bonds_from_xyz(DATA / "train_after_pretrain.xyz")
    bonds_f = _bonds_from_xyz(DATA / "train_final.xyz")
    plot_overview(summary, hist, bonds0, bonds_f)

    # short analysis markdown
    max_de = [r["max_abs_delta_hartree"] for r in summary["rounds"]]
    mean_de = [r["mean_abs_delta_hartree"] for r in summary["rounds"]]
    best = int(np.argmin(max_de))
    n_bad = sum(1 for b in bonds_f if b >= 5)
    md = f"""# H₂ 键长扫描 + 预训练 + 在线学习结果分析（job 6759）

## 结论摘要

1. **流水线完整跑通**：Phase A 扫描 16 点 → Phase B 预训练 120 epoch → Phase C 20 轮 OL。
2. **校验误差明显下降**：max|ΔE| 从第 1 轮 **{max_de[0]:.3f} Ha** 降到最好 **{max_de[best]:.3f} Ha**（第 {best+1} 轮），约降到 1/4；末轮 **{max_de[-1]:.3f} Ha**。
3. **未达收敛阈值** `{summary["config"]["energy_tolerance_hartree"]}` Ha（差约两个数量级）。
4. **训练集膨胀伴随风险**：最终 56 帧中有 **{n_bad}** 个键长 ≥5 Bohr 的解离/非物理构型（来自 MD 校验帧被并入），会污染后续拟合。

## 关键数字

| 指标 | 值 |
|------|-----|
| 墙钟 | 9h05m（30 核 / 120G） |
| 预训练帧 / 最终帧 | 17 / 56 |
| 预训练末 E-MAE | {hist[-1]["energy_mae"]:.3f} Ha |
| 预训练末 F-RMSE | {hist[-1]["force_rmse"]:.3f} |
| max\\|ΔE\\| r1 → best → r20 | {max_de[0]:.3f} → {max_de[best]:.3f} → {max_de[-1]:.3f} |
| mean\\|ΔE\\| r1 → best → r20 | {mean_de[0]:.3f} → {mean_de[int(np.argmin(mean_de))]:.3f} → {mean_de[-1]:.3f} |

## 图

- `figures/h2_bondscan_ol_6759_overview.png`
- `figures/h2_bondscan_ol_6759_train_parity.png`

## 改进建议

- 过滤 MD 解离帧（键长上限，如 <3 Bohr）再并入训练集
- 预训练启用 `energy_normalization: subtract_mean`，加长 epoch / 加密扫描
- 适当放宽或分阶段设置 `energy_tolerance_hartree`（先 0.05 → 0.01 → 5e-4）
"""
    (DATA / "ANALYSIS.md").write_text(md, encoding="utf-8")
    print("wrote", DATA / "ANALYSIS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
