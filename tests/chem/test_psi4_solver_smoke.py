"""Psi4 backend optional mean-field path remains capability-gated."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.integration.presets import capabilities_psi4_production
from qchem_stack.chem.solvers import create_solver
from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference


@pytest.fixture()
def psi4_hf_config(tmp_path: Path) -> ExperimentConfig:
    p = tmp_path / "psi4.yaml"
    p.write_text(
        """
schema_version: "2"
experiment_id: psi4_smoke
random_seed: 0
molecule:
  symbols: ["H"]
  coordinates:
    - [0.0, 0.0, 0.0]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 2
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 1
    n_electrons: 1
""",
        encoding="utf-8",
    )
    return load_experiment_config(p)


def test_psi4_solver_capabilities_match_production_preset(
    psi4_hf_config: ExperimentConfig,
) -> None:
    s = Psi4IntegralSolver.from_experiment_config(psi4_hf_config)
    assert s.capabilities == capabilities_psi4_production()
    assert create_solver(psi4_hf_config).capabilities == capabilities_psi4_production()


def test_psi4_create_solver_runtime_behavior(psi4_hf_config: ExperimentConfig) -> None:
    s = create_solver(psi4_hf_config)
    assert isinstance(s, Psi4IntegralSolver)
    try:
        out = s.compute_mean_field(periodic=False)
        assert out.e_tot == pytest.approx(float(out.e_tot))
        assert out.driver_meta.get("driver_family") == "psi4"
    except RuntimeError as exc:
        assert "Psi4 SCF unavailable" in str(exc)
    with pytest.raises(ValueError, match="cell_vectors_bohr"):
        s.run_periodic_mean_field()
    with pytest.raises(ValueError, match="cell_vectors_bohr"):
        s.compute_mean_field(periodic=True)
    with pytest.raises(ValueError, match="n_active_orbitals"):
        s.get_integrals()


def test_run_scf_no_longer_hard_gates_driver(psi4_hf_config: ExperimentConfig) -> None:
    try:
        out = run_scf_reference(psi4_hf_config)
        assert out.backend_tag() == "psi4"
    except RuntimeError as exc:
        assert "Psi4 SCF unavailable" in str(exc)
