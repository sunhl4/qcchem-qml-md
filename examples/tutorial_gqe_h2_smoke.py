#!/usr/bin/env python3
"""Minimal H₂ GPT-QE smoke (Nakaji Plan B via stable API).

Install:
  pip install -e '.[chem,gqe]'

Run:
  python examples/tutorial_gqe_h2_smoke.py
  python examples/tutorial_gqe_h2_smoke.py --config configs/example_h2_gqe_plan_b.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="GQE H2 smoke via run_gqe_from_config")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/example_h2_gqe_plan_b.yaml"),
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from qchem_stack.integrations.gqe import run_gqe_from_config
    from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        print("Install JAX/optax: pip install 'qchem-stack[gqe]'")
        print(json.dumps(probe, indent=2))
        return 1

    report = run_gqe_from_config(args.config)
    ca = report.get("chemical_accuracy") or {}
    print(
        f"schema={report.get('schema')} mode={report.get('gqe_mode')} paper={report.get('paper')}"
    )
    print(f"best_energy={report.get('best_energy'):.10f}")
    print(f"n_energy_evals={report.get('n_energy_evals')}")
    if ca:
        print(
            f"abs_err_fci={ca.get('abs_error_hartree')} "
            f"within_chem_acc={ca.get('within_chemical_accuracy')}"
        )
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # Drop bulky history for a short artifact
        slim = {k: v for k, v in report.items() if k != "history"}
        slim["history_len"] = len(report.get("history") or [])
        args.out.write_text(json.dumps(slim, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
