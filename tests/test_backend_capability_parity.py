"""PySCF vs Psi4 capability bit parity (registry contract)."""

from __future__ import annotations

from pathlib import Path

from qchem_stack.chem.solvers import create_solver
from qchem_stack.config import load_experiment_config

_SHARED_PARITY_FIELDS = (
    "supports_restricted_active_space_qubit_hamiltonian",
    "supports_rhf",
    "supports_rohf",
    "supports_uhf",
)
_PYSCF_ONLY_FIELDS = (
    "supports_projection_fragment_mulliken_hamiltonian",
    "supports_schmidt_atomic_hamiltonian",
    "supports_embedding_input_ao_lowdin",
    "supports_casscf_orbital_audit",
    "supports_avas_active_space_projection",
    "supports_rdm_correction_hooks",
    "supports_rdm_nevpt2_casci",
    "supports_get_integrals",
)


def test_pyscf_psi4_pre_quantum_capability_parity() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "pyscf"
    pyscf_caps = create_solver(cfg).capabilities
    cfg.scf.driver = "psi4"
    psi4_caps = create_solver(cfg).capabilities
    for field in _SHARED_PARITY_FIELDS:
        assert getattr(pyscf_caps, field) == getattr(psi4_caps, field), (
            f"capability mismatch on {field}"
        )
    for field in _PYSCF_ONLY_FIELDS:
        assert getattr(pyscf_caps, field) is True
        assert getattr(psi4_caps, field) is False
