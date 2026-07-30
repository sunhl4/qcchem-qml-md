#!/usr/bin/env python3
"""Bar charts: GQE vs UCCSD ansatz resources per energy evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=REPO / "results/gqe_circuit_metrics.json")
    parser.add_argument(
        "--out", type=Path, default=REPO / "docs/assets/gqe_nakaji/gqe_circuit_depth_gates.png"
    )
    parser.add_argument(
        "--out-compare",
        type=Path,
        default=REPO / "docs/assets/gqe_nakaji/gqe_uccsd_ansatz_compare.png",
    )
    args = parser.parse_args()

    data = json.loads(args.metrics.read_text(encoding="utf-8"))
    mols = ["h2", "lih", "beh2", "n2"]
    labels = ["H₂", "LiH", "BeH₂", "N₂"]

    depth_gqe = [data[m]["per_eval_ansatz_avg"]["depth"] for m in mols]
    n2q_gqe = [data[m]["per_eval_ansatz_avg"]["n2"] for m in mols]
    depth_ucc = [data[m]["uccsd"]["per_eval_ansatz_one_layer_avg"]["depth"] for m in mols]
    n2q_ucc = [data[m]["uccsd"]["per_eval_ansatz_one_layer_avg"]["n2"] for m in mols]
    seq = [data[m]["seq_len"] for m in mols]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w / 2, depth_gqe, w, label="GQE depth (seq_len)", color="#1f77b4")
    ax.bar(x + w / 2, np.array(n2q_gqe) / 10, w, label="GQE CX (÷10)", color="#ff7f0e")
    for i, s in enumerate(seq):
        ax.text(i - w / 2, depth_gqe[i] + 30, f"L={s}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Count (depth / CX÷10)")
    ax.set_title("GQE ansatz resource per energy evaluation (paper seq_len)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(f"wrote {args.out}")

    # GQE vs UCCSD comparison (depth and CX)
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    w2 = 0.35
    ax1.bar(x - w2 / 2, depth_gqe, w2, label="GQE", color="#1f77b4")
    ax1.bar(x + w2 / 2, depth_ucc, w2, label="UCCSD (1 layer)", color="#2ca02c")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Ansatz circuit depth")
    ax1.set_title("Depth per energy eval")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.25)

    ax2.bar(x - w2 / 2, n2q_gqe, w2, label="GQE", color="#1f77b4")
    ax2.bar(x + w2 / 2, n2q_ucc, w2, label="UCCSD (1 layer)", color="#2ca02c")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Two-qubit gates (CX)")
    ax2.set_title("CX per energy eval")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.25)
    fig2.suptitle("GQE vs standard UCCSD-VQE ansatz (JW, dense product layer)", y=1.02)
    fig2.tight_layout()
    fig2.savefig(args.out_compare, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"wrote {args.out_compare}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
