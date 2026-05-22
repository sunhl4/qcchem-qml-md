"""``scf_stage.refine_mean_field_for_active_space`` wiring (AVAS / CASSCF gates)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.solvers.registry import register_solver
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.scf_stage import (
    refine_mean_field_for_active_space,
    run_scf_reference,
)
from tests.helpers.solver_registry_state import reset_solver_registry_state


def _minimal_h2_cfg(*, strategy: str = "cas") -> ExperimentConfig:
    raw: dict = {
        "schema_version": "2",
        "experiment_id": "scf_stage_refinement",
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
            "strategy": strategy,
            "cas": {"n_orbitals": 2, "n_electrons": 2},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "embedding": {"mode": "none"},
        "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
    }
    if strategy == "avas":
        raw["chemistry_extended"] = {"avas": {"ao_labels": ["H 1s"]}}
    return ExperimentConfig.from_yaml_dict(raw)


@pytest.mark.pyscf
def test_refine_cas_strategy_is_noop_on_config() -> None:
    pytest.importorskip("pyscf")
    cfg = _minimal_h2_cfg(strategy="cas")
    ref = run_scf_reference(cfg)
    out = refine_mean_field_for_active_space(cfg, ref)
    assert out is cfg
    assert out.active_space.strategy == "cas"


def test_refine_avas_without_capability_raises_pipeline_error() -> None:
    reset_solver_registry_state()

    class _MockChemSolver:
        def __init__(self, cfg: ExperimentConfig) -> None:
            self.cfg = cfg

        @property
        def capabilities(self) -> SolverCapabilities:
            return SolverCapabilities(
                backend_id="mockchem",
                supports_molecular_scf=True,
                supports_avas_active_space_projection=False,
            )

        def set_physical_data(self, cfg: ExperimentConfig) -> None:
            self.cfg = cfg

        def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
            import numpy as np

            return MolecularMeanFieldResult(
                mf={"backend": "mockchem"},
                e_tot=0.0,
                mo_energy=np.zeros(2),
                driver_meta={"driver_family": "mockchem"},
            )

    register_solver("mockchem", _MockChemSolver)
    cfg = _minimal_h2_cfg(strategy="avas")
    cfg.scf.driver = "mockchem"
    ref = run_scf_reference(cfg)
    with pytest.raises(PipelineError, match="AVAS capability"):
        refine_mean_field_for_active_space(cfg, ref)


@pytest.mark.pyscf
def test_refine_avas_invokes_run_avas_when_capable() -> None:
    pytest.importorskip("pyscf")
    cfg = _minimal_h2_cfg(strategy="avas")
    ref = run_scf_reference(cfg)
    with patch("qchem_stack.chem.kernels.dispatch.run_avas") as run_avas:
        out = refine_mean_field_for_active_space(cfg, ref)
    run_avas.assert_called_once_with(cfg, ref)
    assert out is cfg
