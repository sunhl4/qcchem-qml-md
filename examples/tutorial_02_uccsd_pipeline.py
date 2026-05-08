#!/usr/bin/env python3
"""Tutorial 2: closed-shell JW UCCSD variational ansatz (requires PySCF)."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("tutorial_02: skip (install PySCF)")
        return 0
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_uccsd.yaml"
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(load_experiment_config(p), cfg_path=p)
    print("tutorial_02: energy_after_variational", out.get("energy_after_variational"))
    print("tutorial_02: uccsd_n_parameters", (out.get("vqe_meta") or {}).get("uccsd_n_parameters"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
