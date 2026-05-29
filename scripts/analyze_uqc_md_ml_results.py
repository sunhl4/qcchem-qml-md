#!/usr/bin/env python3
"""Analyze and plot UQC cloud MD/ML online-learning results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]


def _load_summary(results_dir: Path) -> dict:
    path = results_dir / "md_validation_summary.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _load_training_histories(results_dir: Path) -> dict[int, dict]:
    ckpt = results_dir / "qmlff_checkpoints"
    out: dict[int, dict] = {}
    if not ckpt.is_dir():
        return out
    for sub in sorted(ckpt.glob("round_*")):
        hist_path = sub / "training_history.json"
        if not hist_path.is_file():
            continue
        idx = int(sub.name.split("_", 1)[1])
        out[idx] = json.loads(hist_path.read_text(encoding="utf-8"))
    return out


def plot_results(results_dir: Path, out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or (results_dir / "plots")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = _load_summary(results_dir)
    rounds = summary.get("rounds") or []
    histories = _load_training_histories(results_dir)
    saved: list[Path] = []

    if not rounds:
        raise ValueError("No rounds in md_validation_summary.json")

    ridx = [r["round_index"] for r in rounds]
    n_train = [r["n_train_after"] for r in rounds]
    max_de = [r["max_abs_delta_hartree"] for r in rounds]
    mean_de = [r["mean_abs_delta_hartree"] for r in rounds]
    tol = float((summary.get("config") or {}).get("energy_tolerance_hartree", 0.08))

    # 1) Dataset growth & energy gap vs tolerance
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.bar(ridx, n_train, color="#3498db", alpha=0.85, label="train frames")
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Training set size", color="#3498db")
    ax1.tick_params(axis="y", labelcolor="#3498db")
    ax2 = ax1.twinx()
    ax2.plot(ridx, max_de, "o-", color="#e74c3c", linewidth=2, markersize=8, label="max |ΔE|")
    ax2.plot(ridx, mean_de, "s--", color="#f39c12", linewidth=1.5, markersize=7, label="mean |ΔE|")
    ax2.axhline(tol, color="#2ecc71", linestyle=":", linewidth=2, label=f"tol = {tol} Ha")
    ax2.set_ylabel("Energy gap (Hartree)")
    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, loc="upper right")
    ax1.set_title("UQC cloud online learning: dataset & QML vs qchem gap")
    fig.tight_layout()
    p1 = out_dir / "rounds_dataset_and_delta_e.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    saved.append(p1)

    # 2) Per-frame QML vs qchem energies
    frames_qml, frames_qc, frames_r, frames_t = [], [], [], []
    for r in rounds:
        for fr in r.get("frames") or []:
            frames_r.append(r["round_index"])
            frames_t.append(fr.get("time_ps", 0))
            frames_qml.append(fr["energy_qml_hartree"])
            frames_qc.append(fr["energy_qchem_hartree"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(frames_qml))
    w = 0.35
    ax.bar(x - w / 2, frames_qml, width=w, label="QML-FF", color="#9b59b6", alpha=0.9)
    ax.bar(x + w / 2, frames_qc, width=w, label="qchem (UQC label)", color="#1abc9c", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"R{r}" for r in frames_r], rotation=0)
    ax.set_ylabel("Energy (Ha)")
    ax.set_xlabel("Validated MD frame (by round)")
    ax.set_title("Absolute energies on sampled MD frames")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p2 = out_dir / "frame_energies_qml_vs_qchem.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    saved.append(p2)

    # 3) |ΔE| per frame
    abs_de = [abs(a - b) for a, b in zip(frames_qml, frames_qc, strict=True)]
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(abs_de)))
    ax.bar(range(len(abs_de)), abs_de, color=colors)
    ax.axhline(tol, color="#2ecc71", linestyle=":", linewidth=2, label=f"tol = {tol} Ha")
    ax.set_xticks(range(len(abs_de)))
    ax.set_xticklabels([f"R{r}" for r in frames_r])
    ax.set_ylabel("|ΔE| (Ha)")
    ax.set_xlabel("Frame")
    ax.set_title("|E_QML − E_qchem| per validated frame")
    ax.legend()
    fig.tight_layout()
    p3 = out_dir / "frame_abs_delta_e.png"
    fig.savefig(p3, dpi=150)
    plt.close(fig)
    saved.append(p3)

    # 4) Force RMSE on training set per round
    f_rmse = [
        (r.get("training_metrics") or {}).get("final_metrics", {}).get("force_rmse") for r in rounds
    ]
    if any(x is not None for x in f_rmse):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(ridx, f_rmse, "D-", color="#8e44ad", linewidth=2, markersize=8)
        ax.set_xlabel("Round")
        ax.set_ylabel("Force RMSE (training)")
        ax.set_title("QML-FF force fit quality vs round")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        p_force = out_dir / "force_rmse_per_round.png"
        fig.savefig(p_force, dpi=150)
        plt.close(fig)
        saved.append(p_force)

    # 5) QML-FF training loss per round
    if histories:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for rnd, hist in sorted(histories.items()):
            th = hist.get("train_history") or []
            epochs = [h.get("epoch", i) for i, h in enumerate(th)]
            loss = [h.get("loss") for h in th]
            e_mae = [h.get("energy_mae_per_structure_phys") for h in th]
            axes[0].plot(epochs, loss, "o-", label=f"round {rnd}")
            axes[1].plot(epochs, e_mae, "o-", label=f"round {rnd}")
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Total loss")
        axes[0].set_title("Training loss")
        axes[0].legend(fontsize=8)
        axes[0].grid(alpha=0.3)
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Energy MAE / structure (Ha)")
        axes[1].set_title("Energy MAE (physical)")
        axes[1].legend(fontsize=8)
        axes[1].grid(alpha=0.3)
        fig.suptitle("QML-FF training per round", y=1.02)
        fig.tight_layout()
        p4 = out_dir / "qmlff_training_per_round.png"
        fig.savefig(p4, dpi=150, bbox_inches="tight")
        plt.close(fig)
        saved.append(p4)

    # 6) Summary text
    lines = [
        "# UQC cloud MD/ML analysis",
        f"- output: `{results_dir}`",
        f"- rounds completed: {len(rounds)} / max_rounds={(summary.get('config') or {}).get('max_rounds')}",
        f"- converged: {summary.get('converged')}",
        f"- total train frames: {summary.get('n_total_frames')}",
        "",
        "## Per round",
        "| round | n_train | max|ΔE| (Ha) | mean|ΔE| (Ha) | converged |",
        "|-------|---------|-------------|--------------|-----------|",
    ]
    for r in rounds:
        lines.append(
            f"| {r['round_index']} | {r['n_train_after']} | "
            f"{r['max_abs_delta_hartree']:.4f} | {r['mean_abs_delta_hartree']:.4f} | {r['converged']} |"
        )
    report = out_dir / "ANALYSIS.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    saved.append(report)
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "results_dir",
        type=Path,
        nargs="?",
        default=REPO / "results" / "uqc_cloud_sim_md_ml_5rounds",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    paths = plot_results(args.results_dir.resolve(), args.out)
    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
