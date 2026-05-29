#!/usr/bin/env python3
"""Compare UQC VQE energy: mock (statevector) vs cloud (grouped Pauli) on base H2 geometry."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load_dotenv() -> None:
    from qchem_stack.backends.uqc_env import load_repo_dotenv

    load_repo_dotenv()


def main() -> int:
    _load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--experiment",
        type=Path,
        default=REPO / "configs" / "example_h2_uqc_cloud_sim_md_ml.yaml",
    )
    ap.add_argument("--cloud", action="store_true", help="Also run uqc_mode=real (needs network)")
    args = ap.parse_args()

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    for mode in ("mock", "real") if args.cloud else ("mock",):
        cfg = load_experiment_config(args.experiment)
        cfg.backend.uqc_mode = mode
        cfg.backend.meta = dict(cfg.backend.meta or {})
        cfg.backend.meta["uqc_mode"] = mode
        if mode == "real" and not (os.environ.get("UQC_API_TOKEN") or os.environ.get("USER_TOKEN")):
            print("SKIP cloud: no UQC_API_TOKEN", file=sys.stderr)
            continue
        print(f"=== uqc_mode={mode} ===")
        out = run_pipeline_sync(cfg)
        e_scf = out.get("scf_energy")
        e_var = out.get("energy_after_variational")
        print(f"  scf_energy (HF):              {e_scf}")
        print(f"  energy_after_variational:    {e_var}")
        if e_scf is not None and e_var is not None:
            print(f"  |Δ| (var - scf):             {float(e_var) - float(e_scf):.6f} Ha")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
