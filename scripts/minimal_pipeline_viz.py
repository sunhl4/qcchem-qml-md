#!/usr/bin/env python3
"""Minimal H2 pipeline run + matplotlib summary (requires PySCF + matplotlib).

Writes a PNG (default: ``examples/artifacts/qchem_minimal_h2_pipeline.png``) with:
  - energy ladder (SCF → variational → Pauli protocol if present)
  - ``pipeline_profile`` stage wall times when present in ``repro``.

Usage::

    python scripts/minimal_pipeline_viz.py
    python scripts/minimal_pipeline_viz.py --out /path/to/out.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Run packaged H2 YAML and plot pipeline summary.")
    root = Path(__file__).resolve().parents[1]
    ap.add_argument(
        "--out",
        type=Path,
        default=root / "examples" / "artifacts" / "qchem_minimal_h2_pipeline.png",
        help="Output PNG path",
    )
    ap.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Experiment YAML (default: configs/example_h2.yaml)",
    )
    args = ap.parse_args()

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib required: pip install matplotlib", file=sys.stderr)
        return 1

    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("PySCF required: pip install qchem-stack[chem]", file=sys.stderr)
        return 1

    cfg_path = args.config or (root / "configs" / "example_h2.yaml")
    if not cfg_path.is_file():
        print("missing config", cfg_path, file=sys.stderr)
        return 2

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    scf = float(out["scf_energy"]) if out.get("scf_energy") is not None else float("nan")
    ev = float(out["energy_after_variational"]) if out.get("energy_after_variational") is not None else float("nan")
    ep = out.get("energy_pauli_protocol")
    ep_f = float(ep) if ep is not None else None

    repro = out.get("repro") or {}
    prof = repro.get("pipeline_profile") or {}
    stages = prof.get("stages") if isinstance(prof, dict) else None

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))

    names = ["SCF", "Variational"]
    vals = [scf, ev]
    if ep_f is not None:
        names.append("Pauli protocol")
        vals.append(ep_f)
    colors = ["#2c5282", "#2f855a", "#c05621"][: len(vals)]
    axes[0].bar(names, vals, color=colors)
    axes[0].axhline(scf, color="#718096", linestyle="--", linewidth=0.8, label="SCF reference")
    axes[0].set_ylabel("Energy (Ha)")
    axes[0].set_title(f"Energies — {cfg.experiment_id}")
    axes[0].legend(loc="best", fontsize=8)

    if isinstance(stages, list) and stages:
        labels = [str(s.get("stage", "?")) for s in stages if isinstance(s, dict)]
        ms = [float(s.get("duration_ms", 0.0) or 0.0) for s in stages if isinstance(s, dict)]
        axes[1].barh(labels[::-1], ms[::-1], color="#4a5568")
        axes[1].set_xlabel("duration_ms")
        axes[1].set_title("pipeline_profile stages")
    else:
        axes[1].text(0.5, 0.5, "no pipeline_profile in repro", ha="center", va="center")
        axes[1].set_axis_off()

    fig.suptitle(f"qchem-stack minimal run — {cfg_path.name}", fontsize=11)
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print("wrote", args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
