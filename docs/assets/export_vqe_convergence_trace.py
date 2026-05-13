#!/usr/bin/env python3
"""Regenerate ``docs/assets/data/vqe_h2_sto3g_hea_jw_cobyla_trace.json`` for figure assets.

Run from repo root::

    PYTHONPATH=src python docs/assets/export_vqe_convergence_trace.py

Requires PySCF. Matches ``configs/example_h2.yaml`` (HEA depth-1, COBYLA, JW, statevector).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = Path(__file__).resolve().parent / "data" / "vqe_h2_sto3g_hea_jw_cobyla_trace.json"
CFG_REL = "configs/example_h2.yaml"


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))

    from qchem_stack.backends.factory import executor_from_spec
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf
    from qchem_stack.config import backend_spec_from_config, load_experiment_config
    from qchem_stack.qpe_qec_demo import FaultTolerantDemoAdapter
    from qchem_stack.quantum.algorithms.vqe import VQE

    cfg_path = ROOT / CFG_REL
    cfg = load_experiment_config(cfg_path)
    q = cfg.quantum
    asp = cfg.active_space

    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    qh = molecular_hamiltonian_from_pyscf(
        rhf,
        n_active_orbitals=int(asp.n_active_orbitals),
        n_active_electrons=int(asp.n_active_electrons),
        fermion_qubit_mapping=asp.fermion_qubit_mapping,
    )
    exe = executor_from_spec(backend_spec_from_config(cfg))
    vr = VQE(qh, depth=int(q.vqe_depth), executor=exe).run(
        maxiter=int(q.vqe_maxiter),
        seed=int(cfg.random_seed),
        record_energy_trace=True,
    )
    exact = FaultTolerantDemoAdapter().ground_energy_dense(qh)

    payload = {
        "schema": "vqe_convergence_asset_v1",
        "config_path": CFG_REL,
        "experiment_id": cfg.experiment_id,
        "random_seed": int(cfg.random_seed),
        "variational_ansatz": q.variational_ansatz,
        "vqe_depth": int(q.vqe_depth),
        "vqe_maxiter": int(q.vqe_maxiter),
        "optimizer": "COBYLA",
        "fermion_qubit_mapping": asp.fermion_qubit_mapping,
        "backend_provider": cfg.backend.provider,
        "scf_energy_ha": float(rhf.e_tot),
        "exact_ground_in_active_space_ha": float(exact),
        "variational_final_ha": float(vr.energy),
        "energy_trace_ha": [float(x) for x in (vr.meta.get("energy_trace") or [])],
        "nfev": int(vr.nfev),
        "note": (
            "Each point is one HEA expectation value evaluation inside "
            "scipy.optimize.minimize (COBYLA), matching the production VQE path."
        ),
    }
    if len(payload["energy_trace_ha"]) != payload["nfev"]:
        raise RuntimeError("energy_trace length must equal nfev")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({payload['nfev']} evaluations)")


if __name__ == "__main__":
    main()
