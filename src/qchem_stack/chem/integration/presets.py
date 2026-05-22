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


def capabilities_pyscf_production() -> SolverCapabilities:
    """Production PySCF adapter: full classical pre-quantum capability surface."""
    return SolverCapabilities(
        backend_id="pyscf",
        supports_molecular_scf=True,
        supports_pbc_scf=True,
        supports_pbc_k_mesh=True,
        supports_rhf=True,
        supports_rohf=True,
        supports_uhf=True,
        supports_implicit_solvent_ddcosmo=True,
        supports_qmmm=False,
        supports_restricted_active_space_qubit_hamiltonian=True,
        supports_projection_fragment_mulliken_hamiltonian=True,
        supports_schmidt_atomic_hamiltonian=True,
        supports_embedding_input_ao_lowdin=True,
        supports_casscf_orbital_audit=True,
        supports_avas_active_space_projection=True,
        supports_rdm_correction_hooks=True,
        supports_rdm_nevpt2_casci=True,
        supports_get_integrals=True,
        capability_notes={
            "pbc_k_mesh": "Monkhorst–Pack meshes via PySCF PBC driver.",
            "schmidt_atomic_hamiltonian": (
                "Impurity FCI solve uses PySCF direct_spin0 on spatial integrals (native=True)."
            ),
        },
    )


def capabilities_psi4_production() -> SolverCapabilities:
    """Production Psi4 adapter: L1 SCF + L3-delegated CAS/embedding (see ``capability_notes``)."""
    return SolverCapabilities(
        backend_id="psi4",
        supports_molecular_scf=True,
        supports_pbc_scf=True,
        supports_pbc_k_mesh=False,
        supports_rhf=True,
        supports_rohf=True,
        supports_uhf=True,
        supports_implicit_solvent_ddcosmo=True,
        supports_qmmm=False,
        supports_restricted_active_space_qubit_hamiltonian=True,
        supports_projection_fragment_mulliken_hamiltonian=True,
        supports_schmidt_atomic_hamiltonian=True,
        supports_embedding_input_ao_lowdin=True,
        supports_casscf_orbital_audit=True,
        supports_avas_active_space_projection=True,
        supports_rdm_correction_hooks=True,
        supports_rdm_nevpt2_casci=True,
        supports_get_integrals=True,
        capability_notes={
            "avas_active_space_projection": (
                "PySCF mcscf.avas on MO imported from Psi4 reference (native=False)."
            ),
            "casscf_orbital_audit": "Psi4 energy('casscf') on the converged RHF reference.",
            "embedding_input_ao_lowdin": "Psi4 Wavefunction + MintsHelper overlap/core tensors.",
            "get_integrals": "MO CASCI blocks via psi4_active_space_casci_raw_blocks.",
            "projection_fragment_mulliken_hamiltonian": (
                "Temporary Ca() reorder + Psi4 CASCI effective Hamiltonian."
            ),
            "rdm_correction_hooks": "RDMBundle from Psi4AOBasisView spatial AO RDM1.",
            "rdm_nevpt2_casci": (
                "PySCF mrpt.NEVPT on shadow CASCI built from Psi4 MO (native=False)."
            ),
            "schmidt_atomic_hamiltonian": (
                "Psi4 MintsHelper ao_eri + MO transform; impurity FCI via PySCF direct_spin0 "
                "(native=False for MO/ERI source)."
            ),
            "classical_post_hf_benchmarks": (
                "Not implemented for Psi4; registry returns stub_backend.run_psi4_placeholder."
            ),
            "pbc_k_mesh": "Gamma-only (all pbc_kpoint_mesh entries must be 1).",
        },
    )


def capabilities_precomputed_offline() -> SolverCapabilities:
    """File-backed classical reference; qubit Hamiltonian must ship in the bundle."""
    return SolverCapabilities(
        backend_id="precomputed",
        supports_molecular_scf=True,
        supports_pbc_scf=False,
        supports_rhf=True,
        supports_rohf=True,
        supports_uhf=True,
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
        capability_notes={
            "restricted_active_space_qubit_hamiltonian": (
                "Use bundle.pre_quantum_input.qubit_hamiltonian (PreQuantumPath.PRECOMPUTED_BUNDLE)."
            ),
            "rdm_correction_hooks": "Live backend hooks unavailable; bundle is static.",
        },
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
