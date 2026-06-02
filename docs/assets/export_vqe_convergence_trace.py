#!/usr/bin/env python3
"""Regenerate ``docs/assets/data/vqe_h2_sto3g_jw_near_casci_trace.json`` for VQE convergence figures.

Uses ``configs/example_h2_vqe_figure_near_casci.yaml``: **UCCSD** (JW) with **bounded L-BFGS-B**
(cluster amplitudes in ``±0.38`` rad, initial ``0`` = HF reference) to produce a stable
convergence trace for H₂/sto-3g (2e/2o), near the PySCF CASCI reference.

Run from repo root::

    PYTHONPATH=src python docs/assets/export_vqe_convergence_trace.py

Requires PySCF.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = Path(__file__).resolve().parent / "data" / "vqe_h2_sto3g_jw_near_casci_trace.json"
CFG_REL = "configs/example_h2_vqe_figure_near_casci.yaml"

_FIGURE_UCCSD_ANGLE_BOUND = 0.38
# Softer tolerances + generous maxfun so L-BFGS-B records enough line-search evaluations
# for a readable convergence figure (still bounded to stay variational vs CASCI).
_SCIPY_OPTIONS: dict[str, float | int] = {"ftol": 1e-11, "gtol": 1e-7, "maxfun": 1200}


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))

    import numpy as np
    from pyscf import mcscf

    from qchem_stack.backends.factory import executor_from_spec
    from qchem_stack.chem.bridges.reference_factory import pyscf_rhf_result_from_config
    from qchem_stack.chem.molecular_problem_build import (
        restricted_active_space_quantum_problem_from_config,
    )
    from qchem_stack.config import backend_spec_from_config, load_experiment_config
    from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

    cfg_path = ROOT / CFG_REL
    cfg = load_experiment_config(cfg_path)
    q = cfg.quantum
    asp = cfg.active_space

    rhf = pyscf_rhf_result_from_config(cfg)
    mf = rhf.mf
    mo_coeff = mf.mo_coeff
    mo = mo_coeff if isinstance(mo_coeff, np.ndarray) else np.asarray(mo_coeff[0], dtype=float)

    cas = mcscf.CASCI(mf, int(asp.n_active_orbitals), int(asp.n_active_electrons))
    casci_total_ha = float(cas.kernel(mo)[0])

    prob = restricted_active_space_quantum_problem_from_config(cfg)
    qh = prob.qubit_hamiltonian
    exe = executor_from_spec(backend_spec_from_config(cfg))

    if q.variational_ansatz != "uccsd":
        raise ValueError("export_vqe_convergence_trace expects variational_ansatz='uccsd'.")

    b = float(_FIGURE_UCCSD_ANGLE_BOUND)
    if q.uccsd_trotter_steps is not None:
        ur = UCCSDTrotterVQE(
            qh,
            executor=exe,
            n_trotter_steps=int(q.uccsd_trotter_steps),
        )
        npar = ur.n_params
        bounds = [(-b, b)] * npar
        x0 = np.zeros(npar, dtype=float)
        vr = ur.run(
            maxiter=int(q.vqe_maxiter),
            seed=int(cfg.random_seed),
            executor=exe,
            record_energy_trace=True,
            scipy_method="L-BFGS-B",
            bounds=bounds,
            initial_parameters=x0,
            scipy_options=dict(_SCIPY_OPTIONS),
        )
    else:
        ur = UCCSDVQE(qh, executor=exe)
        npar = ur.n_params
        bounds = [(-b, b)] * npar
        x0 = np.zeros(npar, dtype=float)
        vr = ur.run(
            maxiter=int(q.vqe_maxiter),
            seed=int(cfg.random_seed),
            executor=exe,
            record_energy_trace=True,
            scipy_method="L-BFGS-B",
            bounds=bounds,
            initial_parameters=x0,
            scipy_options=dict(_SCIPY_OPTIONS),
        )

    payload = {
        "schema": "vqe_convergence_asset_v1",
        "config_path": CFG_REL,
        "experiment_id": cfg.experiment_id,
        "random_seed": int(cfg.random_seed),
        "variational_ansatz": q.variational_ansatz,
        "uccsd_trotter_steps": q.uccsd_trotter_steps,
        "vqe_maxiter": int(q.vqe_maxiter),
        "optimizer": "L-BFGS-B",
        "scipy_options": dict(_SCIPY_OPTIONS),
        "uccsd_angle_bound_rad": b,
        "uccsd_initial_cluster_amplitudes": "zeros_hf_reference",
        "fermion_qubit_mapping": asp.fermion_qubit_mapping,
        "backend_provider": cfg.backend.provider,
        "scf_energy_ha": float(rhf.e_tot),
        "reference_casci_total_ha": casci_total_ha,
        "variational_final_ha": float(vr.energy),
        "energy_trace_ha": [float(x) for x in (vr.meta.get("energy_trace") or [])],
        "nfev": int(vr.nfev),
        "note": (
            "UCCSD cluster amplitudes optimized with scipy L-BFGS-B; each trace point is one "
            "statevector energy <psi(theta)|H|psi(theta)>. Parameter box |theta|<=0.38 rad "
            "gives a stable figure trace and converges near CASCI for this H2/sto-3g active space."
        ),
    }
    if len(payload["energy_trace_ha"]) != payload["nfev"]:
        raise RuntimeError("energy_trace length must equal nfev")

    err_mha = (float(vr.energy) - casci_total_ha) * 1000.0
    if err_mha < -0.5:
        raise RuntimeError(
            f"variational energy {vr.energy} Ha is more than 0.5 mHa below CASCI {casci_total_ha} Ha; "
            "review Hamiltonian / optimizer settings."
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({payload['nfev']} evals, final−CASCI = {err_mha:.3f} mHa)")


if __name__ == "__main__":
    main()
