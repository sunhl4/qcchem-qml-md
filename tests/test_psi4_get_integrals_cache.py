"""Psi4 get_integrals reuse of cached mean-field state."""

from __future__ import annotations

import pytest

from qchem_stack.config import ExperimentConfig


def test_psi4_get_integrals_reuses_last_mean_field_without_rescf() -> None:
    pytest.importorskip("psi4")
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver

    cfg = ExperimentConfig.from_yaml_dict(
        {
            "schema_version": "2",
            "experiment_id": "psi4_integrals_cache",
            "random_seed": 1,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "scf": {"driver": "psi4", "method": "RHF"},
            "embedding": {"mode": "none"},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    solver = Psi4IntegralSolver.from_experiment_config(cfg)
    first = solver.run_molecular_mean_field()
    out = solver.get_integrals(
        run_scf=False,
        n_active_orbitals=2,
        n_active_electrons=2,
    )
    assert float(out["scf_energy"]) == pytest.approx(float(first.e_tot))
    assert out["backend_id"] == "psi4"
