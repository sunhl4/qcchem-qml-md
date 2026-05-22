"""PySCF vs Psi4 capability bit parity (registry contract).

Complements ``test_solver_capabilities_presets.py::test_pyscf_psi4_differ_only_on_pbc_k_mesh``:
this module checks runtime ``create_solver(cfg).capabilities``; presets tests compare static factories.
"""

from __future__ import annotations

from pathlib import Path

from qchem_stack.chem.solvers import create_solver
from qchem_stack.config import load_experiment_config

_SHARED_PARITY_FIELDS = (
    "supports_restricted_active_space_qubit_hamiltonian",
    "supports_projection_fragment_mulliken_hamiltonian",
    "supports_schmidt_atomic_hamiltonian",
    "supports_embedding_input_ao_lowdin",
    "supports_casscf_orbital_audit",
    "supports_avas_active_space_projection",
    "supports_rdm_correction_hooks",
    "supports_rdm_nevpt2_casci",
    "supports_get_integrals",
    "supports_rhf",
    "supports_rohf",
    "supports_uhf",
    "supports_molecular_scf",
    "supports_pbc_scf",
    "supports_implicit_solvent_ddcosmo",
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
    assert pyscf_caps.supports_pbc_k_mesh is True
    assert psi4_caps.supports_pbc_k_mesh is False
