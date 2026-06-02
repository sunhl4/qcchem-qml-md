"""TypedDict schema for QubitHamiltonian.meta dictionaries.

This module documents the structure of QubitHamiltonian.meta dictionaries that
accumulate metadata throughout the Hamiltonian construction pipeline.

The meta dict is populated by:
- Hamiltonian build functions (hamiltonian_build.py)
- Assembly helpers (hamiltonian_build_assembly.py)
- Mapping functions (hamiltonian_mapping.py)
- Reference energy attachment (hamiltonian_meta.py)

Keys are added at different build stages, so not all keys are present
in every QubitHamiltonian.meta instance.
"""

from __future__ import annotations

from typing import Any, TypedDict


class HamiltonianMeta(TypedDict, total=False):
    """Schema for QubitHamiltonian.meta dictionaries.

    All fields are optional (total=False) since meta is populated
    incrementally throughout the build process.

    Core identification:
        fermion_to_qubit_mapping: Mapping method ("jordan_wigner", "bravyi_kitaev", etc.)
        build_route: Build path identifier ("restricted_spatial_fermion", etc.)
        n_qubits: Number of qubits in the Hamiltonian
        hamiltonian_fingerprint: SHA256 hash of the operator

    Active space info:
        n_active_orbitals: Number of active orbitals
        n_active_electrons: Number of active electrons
        integral_source: Source tag for integrals
        integral_openfermion_bridge: Bridge version/method

    Reference energies:
        scf_energy_au: SCF energy in atomic units
        reference_energy_au: Reference energy (may differ from SCF)

    Driver metadata:
        classical_driver: Driver metadata dict (non-PySCF)
        pyscf_driver: PySCF-specific driver metadata
        canonical_integral_pack: Integral pack schema and provenance

    Spatial orbital data:
        spatial_mo_constant: Nuclear repulsion + frozen core energy
        spatial_mo_h1: One-electron integrals as list
        spatial_mo_h2: Two-electron integrals as list (if available)

    Build flags:
        hamiltonian_fingerprint_truncated: True if fingerprint was truncated
        jordan_wigner_coeff_atol: Coefficient tolerance for JW mapping
    """

    # Core identification
    fermion_to_qubit_mapping: str
    build_route: str
    n_qubits: int
    hamiltonian_fingerprint: str

    # Active space
    n_active_orbitals: int
    n_active_electrons: int
    integral_source: str
    integral_openfermion_bridge: str

    # Reference energies
    scf_energy_au: float
    reference_energy_au: float

    # Driver metadata
    classical_driver: dict[str, Any]
    pyscf_driver: dict[str, Any]
    canonical_integral_pack: dict[str, Any]

    # Spatial orbital data
    spatial_mo_constant: float
    spatial_mo_h1: list[list[float]]
    spatial_mo_h2: list[list[list[list[float]]]]

    # Build flags
    hamiltonian_fingerprint_truncated: bool
    jordan_wigner_coeff_atol: float


def validate_hamiltonian_meta(meta: dict[str, Any]) -> None:
    """Validate that QubitHamiltonian.meta contains expected keys and types.

    This is a soft validation that logs warnings for unexpected keys but
    does not raise exceptions, preserving the flexible dict[str, Any] behavior.

    Args:
        meta: The QubitHamiltonian.meta dictionary to validate

    Note:
        This function is primarily for documentation and debugging.
        Production code should not rely on this validation.
    """
    known_keys = set(HamiltonianMeta.__annotations__.keys())
    unknown_keys = set(meta.keys()) - known_keys

    if unknown_keys:
        # Log warning but don't fail - meta is intentionally flexible
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            "QubitHamiltonian.meta contains unknown keys: %s (this may be intentional)",
            sorted(unknown_keys),
        )
