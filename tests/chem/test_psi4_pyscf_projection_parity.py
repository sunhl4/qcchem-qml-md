"""Psi4 vs PySCF H2 Mulliken projection Hamiltonian parity (optional dependencies)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference
from tests.embedding_nested import embedding_projection
from tests.helpers.paths import configs_path, repo_root

# Soft thresholds aligned with canonical-pack parity (see test_psi4_pyscf_h2_canonical_parity.py).
PSI4_PYSCF_H2_PROJECTION_IDENTITY_ATOL = 5e-3


def _h2_projection_cfg(root: Path, *, driver: str) -> ExperimentConfig:
    base = load_experiment_config(configs_path("example_h2.yaml"))
    return base.model_copy(
        update={
            "scf": base.scf.model_copy(update={"driver": driver}),
            "embedding": embedding_projection(
                quantum_hamiltonian="fragment_mulliken_mo",
                fragment_atom_indices=[0, 1],
            ),
        }
    )


def _identity_coefficient(qh: object) -> float:
    terms = getattr(getattr(qh, "operator", None), "terms", None)
    if not isinstance(terms, dict):
        raise TypeError("expected QubitHamiltonian with OpenFermion QubitOperator")
    return float(terms.get((), 0.0))


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_pyscf_h2_projection_mulliken_near_parity() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = repo_root()
    cfg_py = _h2_projection_cfg(root, driver="pyscf")
    cfg_psi = _h2_projection_cfg(root, driver="psi4")
    ref_py = run_scf_reference(cfg_py)
    ref_psi = run_scf_reference(cfg_psi)
    p_py, audit_py = molecular_hamiltonian_fragment_mulliken_projection(ref_py, cfg_py)
    p_psi, audit_psi = molecular_hamiltonian_fragment_mulliken_projection(ref_psi, cfg_psi)
    assert p_py.meta["integral_source"] == "pyscf_projection_fragment_mulliken_v1"
    assert p_psi.meta["integral_source"] == "psi4_projection_fragment_mulliken_v1"
    assert audit_py["selected_mo_indices"] == audit_psi["selected_mo_indices"]
    assert p_py.n_qubits == p_psi.n_qubits
    c_py = _identity_coefficient(p_py)
    c_psi = _identity_coefficient(p_psi)
    assert abs(c_py - c_psi) < PSI4_PYSCF_H2_PROJECTION_IDENTITY_ATOL
