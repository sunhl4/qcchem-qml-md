"""Psi4 get_integrals reuse of cached mean-field state."""

from __future__ import annotations

import pytest

from qchem_stack.config import ExperimentConfig
from tests.helpers.h2_yaml import h2_yaml_dict


def test_psi4_get_integrals_reuses_last_mean_field_without_rescf() -> None:
    pytest.importorskip("psi4")
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver

    cfg = ExperimentConfig.from_yaml_dict(
        h2_yaml_dict(
            experiment_id="psi4_integrals_cache",
            scf={"driver": "psi4", "method": "RHF"},
            quantum={
                "algorithm": "vqe",
                "vqe": {"depth": 1, "maxiter": 5},
                "pauli": {"use_protocol": False},
            },
        )
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
