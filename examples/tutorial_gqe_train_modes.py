#!/usr/bin/env python3
"""Run GPT / prefill / condition GQE modes on H₂ (smoke-scaled).

Usage:
  pip install -e '.[chem,gqe]'
  python examples/tutorial_gqe_train_modes.py                 # all three
  python examples/tutorial_gqe_train_modes.py --mode prefill
  python examples/tutorial_gqe_train_modes.py --mode condition --out /tmp/gqe_modes.json

Paper-scale prefill (N_warmup=200):
  python examples/gqe_nakaji_paper_repro.py --train-mode prefill --warmup 200
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="GQE train_mode smoke runner")
    parser.add_argument(
        "--mode",
        choices=("gpt", "prefill", "condition", "all"),
        default="all",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from qchem_stack.integrations.gqe import run_gqe_from_config
    from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        print("[gqe-modes] install jax/optax: pip install 'qchem-stack[gqe]'")
        return 1

    root = Path(__file__).resolve().parents[1] / "configs"
    mapping = {
        "gpt": root / "example_h2_gqe_gpt.yaml",
        "prefill": root / "example_h2_gqe_prefill.yaml",
        "condition": root / "example_h2_gqe_condition.yaml",
    }
    modes = list(mapping) if args.mode == "all" else [args.mode]
    reports: dict[str, dict] = {}
    for mode in modes:
        path = mapping[mode]
        print(f"[gqe-modes] train_mode={mode} config={path.name}")
        report = run_gqe_from_config(path)
        ca = report.get("chemical_accuracy") or {}
        print(
            f"  best_E={report.get('best_energy'):.8f} "
            f"n_evals={report.get('n_energy_evals')} "
            f"within={ca.get('within_chemical_accuracy')}"
        )
        reports[mode] = {
            "best_energy": report.get("best_energy"),
            "n_energy_evals": report.get("n_energy_evals"),
            "train_mode": report.get("train_mode"),
            "chemical_accuracy": ca,
            "config": report.get("config"),
        }

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(reports, indent=2), encoding="utf-8")
        print(f"[gqe-modes] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
