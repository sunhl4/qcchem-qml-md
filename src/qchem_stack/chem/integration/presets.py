"""Capability presets for new classical chemistry drivers."""

from __future__ import annotations

from qchem_stack.chem.solvers.base import SolverCapabilities


def capabilities_driver_scf_only(backend_id: str) -> SolverCapabilities:
    """Minimal L1 adapter: molecular SCF + RHF family only."""
    return SolverCapabilities(
        backend_id=str(backend_id),
        supports_molecular_scf=True,
        supports_pbc_scf=False,
        supports_pbc_k_mesh=False,
        supports_rhf=True,
        supports_rohf=False,
        supports_uhf=False,
        supports_implicit_solvent_ddcosmo=False,
        supports_qmmm=False,
        supports_restricted_active_space_qubit_hamiltonian=False,
        supports_projection_fragment_mulliken_hamiltonian=False,
        supports_schmidt_atomic_hamiltonian=False,
        supports_embedding_input_ao_lowdin=False,
        supports_casscf_orbital_audit=False,
        supports_avas_active_space_projection=False,
        supports_rdm_correction_hooks=False,
        supports_rdm_nevpt2_casci=False,
        supports_get_integrals=False,
    )


def capabilities_with_delegated_cas_path(backend_id: str) -> SolverCapabilities:
    """SCF-only driver that delegates CAS/AVAS to L3 PySCF-style kernels (document in meta)."""
    base = capabilities_driver_scf_only(backend_id)
    return SolverCapabilities(
        backend_id=base.backend_id,
        supports_molecular_scf=base.supports_molecular_scf,
        supports_pbc_scf=base.supports_pbc_scf,
        supports_pbc_k_mesh=base.supports_pbc_k_mesh,
        supports_rhf=base.supports_rhf,
        supports_rohf=base.supports_rohf,
        supports_uhf=base.supports_uhf,
        supports_implicit_solvent_ddcosmo=base.supports_implicit_solvent_ddcosmo,
        supports_qmmm=base.supports_qmmm,
        supports_restricted_active_space_qubit_hamiltonian=True,
        supports_projection_fragment_mulliken_hamiltonian=base.supports_projection_fragment_mulliken_hamiltonian,
        supports_schmidt_atomic_hamiltonian=base.supports_schmidt_atomic_hamiltonian,
        supports_embedding_input_ao_lowdin=base.supports_embedding_input_ao_lowdin,
        supports_casscf_orbital_audit=base.supports_casscf_orbital_audit,
        supports_avas_active_space_projection=True,
        supports_rdm_correction_hooks=base.supports_rdm_correction_hooks,
        supports_rdm_nevpt2_casci=base.supports_rdm_nevpt2_casci,
        supports_get_integrals=base.supports_get_integrals,
        capability_notes={
            "avas_active_space_projection": "Typically PySCF mcscf.avas on imported MO.",
            "restricted_active_space_qubit_hamiltonian": "Delegate casci_active_integrals to L3.",
        },
    )
