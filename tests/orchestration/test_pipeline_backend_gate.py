from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.pre_quantum_build import (
    build_pre_quantum_input_with_context,
    schmidt_hamiltonian_and_context,
)
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.solvers.registry import register_solver
from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.fixtures.classical_reference import pyscf_rhf_from_config
from tests.helpers.paths import configs_path


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
    p = configs_path("example_h2.yaml")
    cfg = load_experiment_config(p)
    from qchem_stack.orchestration.scf_stage import run_scf_reference

    register_solver("mockchem", _MockChemSolver)
    cfg.scf.driver = "mockchem"
    rhf = run_scf_reference(cfg)
    with pytest.raises(PipelineError, match="canonical active-space integral pack"):
        build_pre_quantum_input_with_context(cfg, rhf, cfg_path=p)


def test_plugin_mode_bypasses_backend_active_space_gate() -> None:
    p = configs_path("example_decomposition_plugin_toy.yaml")
    cfg = load_experiment_config(p)
    rhf = pyscf_rhf_from_config(cfg)
    cfg.scf.driver = "psi4"
    pre_q, _ctx = build_pre_quantum_input_with_context(cfg, rhf, cfg_path=p)
    hmeta = pre_q.qubit_hamiltonian.meta
    assert hmeta.get("integral_source") == "decomposition_plugin_toy_v1"
    assert hmeta.get("hamiltonian_fingerprint")
    assert hmeta.get("integral_openfermion_bridge") == "decomposition_plugin_pauli_terms_v1"
    assert pre_q.meta.get("source") == "embedding_plugin"


def test_schmidt_path_rejects_backend_without_schmidt_capability() -> None:
    p = configs_path("example_h2.yaml")
    cfg = load_experiment_config(p)
    rhf = pyscf_rhf_from_config(cfg)
    register_solver("mockchem", _MockChemSolver)
    cfg.scf.driver = "mockchem"
    with pytest.raises(PipelineError, match="schmidt_atomic_production"):
        schmidt_hamiltonian_and_context(cfg, rhf)


def test_projection_fragment_mulliken_rejects_backend_without_capability() -> None:
    p = configs_path("example_h4_projection_mulliken.yaml")
    cfg = load_experiment_config(p)
    rhf = pyscf_rhf_from_config(cfg)
    register_solver("mockchem", _MockChemSolver)
    cfg.scf.driver = "mockchem"
    with pytest.raises(PipelineError, match="projection\\.fragment_mulliken_mo"):
        build_pre_quantum_input_with_context(cfg, rhf, cfg_path=p)


def test_mockchem_canonical_pack_capability_missing() -> None:
    p = configs_path("example_h2.yaml")
    cfg = load_experiment_config(p)
    register_solver("mockchem", _MockChemSolver)
    cfg.scf.driver = "mockchem"
    with pytest.raises(PipelineError, match="supports_restricted_active_space_qubit_hamiltonian"):
        run_pipeline_sync(cfg, cfg_path=p)
