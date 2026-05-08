from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.solvers.registry import register_solver
from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline import (
    _hamiltonian_with_schmidt_context,
    _schmidt_hamiltonian_and_context,
    run_pipeline_sync,
)


class _MockChemSolver:
    def __init__(self, cfg):
        self.cfg = cfg

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(backend_id="mockchem", supports_molecular_scf=True)

    def set_physical_data(self, cfg) -> None:
        self.cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            raise NotImplementedError("mockchem supports molecular only")
        return MolecularMeanFieldResult(
            mf={"backend": "mockchem"},
            e_tot=0.0,
            mo_energy=np.zeros(2, dtype=float),
            driver_meta={"driver_family": "mockchem"},
        )


def test_pipeline_rejects_backend_without_canonical_active_space_pack() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(p)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    cfg.scf.driver = "psi4"  # emulate a backend lacking canonical-pack capability
    with pytest.raises(PipelineError, match="canonical active-space integral pack"):
        _hamiltonian_with_schmidt_context(cfg, rhf, cfg_path=p)


def test_plugin_mode_bypasses_backend_active_space_gate() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(p)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    cfg.scf.driver = "psi4"
    qh, _ctx = _hamiltonian_with_schmidt_context(cfg, rhf, cfg_path=p)
    assert qh.meta.get("integral_source") == "decomposition_plugin_toy_v1"


def test_schmidt_path_rejects_backend_without_schmidt_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(p)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    cfg.scf.driver = "psi4"
    with pytest.raises(PipelineError, match="schmidt_atomic_production"):
        _schmidt_hamiltonian_and_context(cfg, rhf)


def test_projection_fragment_mulliken_rejects_backend_without_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h4_projection_mulliken.yaml"
    cfg = load_experiment_config(p)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    cfg.scf.driver = "psi4"
    with pytest.raises(PipelineError, match="projection\\.fragment_mulliken_mo"):
        _hamiltonian_with_schmidt_context(cfg, rhf, cfg_path=p)


def test_mockchem_canonical_pack_capability_missing() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(p)
    register_solver("mockchem", _MockChemSolver)
    cfg.scf.driver = "mockchem"
    with pytest.raises(PipelineError, match="canonical active-space integral pack"):
        run_pipeline_sync(cfg, cfg_path=p)
