#!/usr/bin/env python3
"""Generate all GQE Nakaji reproduction figures for report documents."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CHEM = 1.6e-3
REPO = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def plot_h2_pes(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = np.array([r["bond_angstrom"] for r in rows])
    fci = np.array([r["fci"] for r in rows])
    best = np.array([r["best_energy_min"] for r in rows])
    mean = np.array([r["best_energy_mean"] for r in rows])

    by_bond: dict[float, float] = {}
    for t in summary.get("trials", []):
        b = float(t["bond_angstrom"])
        if b not in by_bond:
            by_bond[b] = float(t["scf"])
    scf = np.array([by_bond[b] for b in bonds])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(bonds, fci, "k-", lw=2, label="FCI")
    ax.plot(bonds, scf, ":", color="0.45", lw=1.5, label="HF/SCF")
    ax.scatter(bonds, best, c="#2ca02c", s=70, zorder=3, label="GPT-QE best (min trial)")
    ax.errorbar(bonds, mean, yerr=np.abs(mean - best), fmt="none", ecolor="#2ca02c", alpha=0.35)
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Energy (Ha)")
    ax.set_title("H₂ PES — Nakaji GPT-QE reproduction (sto-3g)")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_h2_error(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = np.array([r["bond_angstrom"] for r in rows])
    fci = np.array([r["fci"] for r in rows])
    best = np.array([r["best_energy_min"] for r in rows])
    err = np.abs(best - fci)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.semilogy(
        bonds, err, "o-", color="#2ca02c", ms=8, lw=1.5, label="|GPT-QE − FCI| (best trial)"
    )
    ax.axhline(CHEM, color="#1f77b4", ls="--", lw=1.5, label="Chemical accuracy (1.6 mHa)")
    for b, e in zip(bonds, err, strict=False):
        color = "#2ca02c" if e <= CHEM else "#d62728"
        ax.annotate(
            f"{e * 1e3:.2f}",
            (b, e),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=7,
            color=color,
        )
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Absolute error (Ha)")
    ax.set_title("H₂ GPT-QE error vs FCI")
    ax.legend()
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_h2_chem_acc_rate(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = [r["bond_angstrom"] for r in rows]
    counts = [r["within_chem_acc_count"] for r in rows]
    totals = [r["n_trials"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(bonds))
    colors = [
        "#2ca02c" if c == t else "#ff7f0e" if c > 0 else "#d62728"
        for c, t in zip(counts, totals, strict=False)
    ]
    bars = ax.bar(x, counts, color=colors, edgecolor="k", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{b:.1f}" for b in bonds])
    ax.set_ylim(0, 3.5)
    ax.axhline(3, color="gray", ls=":", alpha=0.5)
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Trials within chemical accuracy (of 3)")
    ax.set_title("H₂ chemical accuracy pass rate per bond length")
    for bar, c, t in zip(bars, counts, totals, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            f"{c}/{t}",
            ha="center",
            fontsize=9,
        )
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_h2_r20_retry(summary: dict, *, out: Path) -> None:
    orig = [t for t in summary["trials"] if abs(t["bond_angstrom"] - 2.0) < 1e-6]
    retry = summary.get("h2_r20_retry", [])
    fci = orig[0]["fci"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels, errs, colors = [], [], []
    for i, t in enumerate(orig):
        e = abs(t["best_energy"] - fci)
        labels.append(f"orig s{i}")
        errs.append(e)
        colors.append("#d62728" if e > CHEM else "#2ca02c")
    for t in retry:
        tag = t.get("tag", "retry")
        e = abs(t["best_energy"] - fci)
        labels.append(tag.replace("retry400_", "r400 "))
        errs.append(e)
        colors.append("#d62728" if e > CHEM else "#2ca02c")

    x = np.arange(len(labels))
    ax.bar(x, np.array(errs) * 1e3, color=colors, edgecolor="k", lw=0.5)
    ax.axhline(CHEM * 1e3, color="#1f77b4", ls="--", label="1.6 mHa")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Error vs FCI (mHa)")
    ax.set_title("H₂ R = 2.0 Å — original vs retry400 (dissociation region)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_h2_trial_spread(summary: dict, *, out: Path) -> None:
    by_bond: dict[float, list] = defaultdict(list)
    for t in summary["trials"]:
        by_bond[float(t["bond_angstrom"])].append(abs(t["best_energy"] - t["fci"]))

    bonds = sorted(by_bond)
    spreads = [(max(v) - min(v)) * 1e3 for v in [by_bond[b] for b in bonds]]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([f"{b:.1f}" for b in bonds], spreads, color="#9467bd", edgecolor="k", lw=0.5)
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Trial spread (max−min error, mHa)")
    ax.set_title("H₂ seed sensitivity (3 independent trials)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_lih_pes(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = np.array([r["bond_angstrom"] for r in rows])
    fci = np.array([r["fci"] for r in rows])
    scf = np.array([r["scf"] for r in rows])
    gqe = np.array([r["best_energy_min"] for r in rows])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(bonds, fci, "k-", lw=2, label="FCI")
    ax.plot(bonds, scf, ":", color="0.45", lw=1.5, label="HF/SCF")
    ax.scatter(bonds, gqe, c="#ff7f0e", s=80, zorder=3, label="GPT-QE pilot")
    ax.plot(bonds, gqe, "-", color="#ff7f0e", alpha=0.5)
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Energy (Ha)")
    ax.set_title("LiH PES — GPT-QE pilot (200 ep, seq=20, d=64, L=2)")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_lih_error(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = np.array([r["bond_angstrom"] for r in rows])
    err = np.array([r["abs_error_min"] for r in rows])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar([f"{b:.1f}" for b in bonds], err * 1e3, color="#ff7f0e", edgecolor="k", lw=0.5)
    ax.axhline(CHEM * 1e3, color="#1f77b4", ls="--", lw=1.5, label="Chemical accuracy (1.6 mHa)")
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Error vs FCI (mHa)")
    ax.set_title("LiH pilot — absolute error (none within chem. acc.)")
    for bar, e in zip(bars, err, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.15,
            f"{e * 1e3:.2f}",
            ha="center",
            fontsize=9,
        )
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_lih_correlation(summary: dict, *, out: Path) -> None:
    rows = summary["summary_by_bond"]
    bonds = np.array([r["bond_angstrom"] for r in rows])
    scf = np.array([r["scf"] for r in rows])
    fci = np.array([r["fci"] for r in rows])
    gqe = np.array([r["best_energy_min"] for r in rows])
    avail = scf - fci
    cap = np.clip(scf - gqe, 0, None)
    pct = 100 * cap / np.maximum(avail, 1e-12)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([f"{b:.1f}" for b in bonds], pct, width=0.35, color="#ff7f0e", edgecolor="k", lw=0.5)
    ax.axhline(100, color="k", ls=":", lw=1)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Bond length R (Å)")
    ax.set_ylabel("Correlation energy captured (%)")
    ax.set_title("LiH pilot — fraction of SCF→FCI correlation recovered")
    for i, p in enumerate(pct):
        ax.text(i, p + 2, f"{p:.0f}%", ha="center", fontsize=10)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_overview(h2: dict, lih: dict | None = None, *, out: Path) -> None:
    """H₂-only overview (PES + error). ``lih`` kept for call-site compatibility."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    rows = h2["summary_by_bond"]
    bonds = [r["bond_angstrom"] for r in rows]

    ax = axes[0]
    ax.plot(bonds, [r["fci"] for r in rows], "k-", lw=2.2, label="FCI")
    ax.scatter(
        bonds,
        [r["best_energy_min"] for r in rows],
        c="#2ca02c",
        s=64,
        zorder=3,
        label="GPT-QE best",
    )
    ax.set_title("H₂ PES (GPT-QE vs FCI)", fontsize=12)
    ax.set_xlabel("R (Å)")
    ax.set_ylabel("E (Ha)")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(alpha=0.25)

    ax = axes[1]
    err = [abs(r["best_energy_min"] - r["fci"]) * 1e3 for r in rows]
    ax.semilogy(bonds, err, "o-", color="#2ca02c", ms=8, lw=1.6, label="|GPT-QE − FCI|")
    ax.axhline(CHEM * 1e3, color="#1f77b4", ls="--", lw=1.5, label="chem. acc. 1.6 mHa")
    ax.set_title("H₂ error (mHa)", fontsize=12)
    ax.set_xlabel("R (Å)")
    ax.set_ylabel("|ΔE| (mHa)")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(True, which="both", alpha=0.25)

    fig.suptitle("Nakaji GPT-QE reproduction — H₂ results overview", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--h2-summary", type=Path, default=REPO / "results/hpc_gqe_h2_scan_summary.json"
    )
    parser.add_argument(
        "--lih-summary", type=Path, default=REPO / "results/hpc_gqe_lih_pilot_summary.json"
    )
    parser.add_argument("--out-dir", type=Path, default=REPO / "docs/assets/gqe_nakaji")
    parser.add_argument("--results-dir", type=Path, default=REPO / "results")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.results_dir / "gqe_h2_pes").mkdir(parents=True, exist_ok=True)
    (args.results_dir / "gqe_lih_pes").mkdir(parents=True, exist_ok=True)

    h2 = load_json(args.h2_summary)
    lih = load_json(args.lih_summary)

    figures = {
        "gqe_repro_overview.png": lambda p: plot_overview(h2, lih, out=p),
        "h2_pes_fig4_style.png": lambda p: plot_h2_pes(h2, out=p),
        "h2_error_vs_fci.png": lambda p: plot_h2_error(h2, out=p),
        "h2_chem_acc_rate.png": lambda p: plot_h2_chem_acc_rate(h2, out=p),
        "h2_r20_retry_comparison.png": lambda p: plot_h2_r20_retry(h2, out=p),
        "h2_trial_spread.png": lambda p: plot_h2_trial_spread(h2, out=p),
        "lih_pes_pilot.png": lambda p: plot_lih_pes(lih, out=p),
        "lih_error_vs_fci.png": lambda p: plot_lih_error(lih, out=p),
        "lih_correlation_captured.png": lambda p: plot_lih_correlation(lih, out=p),
    }

    for name, fn in figures.items():
        doc_path = args.out_dir / name
        fn(doc_path)
        print(f"wrote {doc_path}")
        if name.startswith("h2_"):
            fn(args.results_dir / "gqe_h2_pes" / name)
        elif name.startswith("lih_"):
            fn(args.results_dir / "gqe_lih_pes" / name)

    manifest = {
        "figures": list(figures.keys()),
        "h2_summary": str(args.h2_summary),
        "lih_summary": str(args.lih_summary),
        "doc_assets_dir": str(args.out_dir),
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
