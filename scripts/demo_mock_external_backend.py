#!/usr/bin/env python3
"""Demo: register a custom backend and run plugin-mode pipeline end-to-end."""

from __future__ import annotations

import json
from pathlib import Path

from qchem_stack.chem.solvers import register_mock_external_solver
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(cfg_path)
    register_mock_external_solver()
    cfg.scf.driver = "mock_external"
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    payload = {
        "schema": "mock_external_demo_v1",
        "backend": cfg.scf.driver,
        "scf_energy": float(out["scf_energy"]),
        "hamiltonian_integral_source": (out.get("hamiltonian_meta") or {}).get("integral_source"),
        "energy_after_variational": float(out["energy_after_variational"]),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
