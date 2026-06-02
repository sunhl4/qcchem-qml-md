"""TypedDict schema for driver_meta dictionaries.

This module documents the structure of driver_meta dictionaries that accumulate
metadata throughout the chemistry pipeline. The TypedDict provides type hints
for the expected keys, though the runtime type remains dict[str, Any] for
flexibility.

The driver_meta dict is populated incrementally by:
- Classical chemistry drivers (PySCF, Psi4, precomputed)
- Active space processing hooks
- Cross-check validation routines
- Kernel binding records

Keys are added at different pipeline stages, so not all keys are present
in every driver_meta instance.
"""

from __future__ import annotations

from typing import Any, TypedDict


class DriverMeta(TypedDict, total=False):
    """Schema for driver_meta dictionaries.

    All fields are optional (total=False) since driver_meta is populated
    incrementally throughout the pipeline.

    Core identification:
        backend_tag: Classical backend identifier ("pyscf", "psi4", "precomputed")
        solver_type: SCF method ("RHF", "UHF", "ROHF")
        basis: Basis set name

    Active space metadata:
        active_space_strategy: "full", "cas", "avas"
        active_space_recipe: Human-readable description
        active_space_frozen_orbitals: List of frozen orbital indices
        resolved_active_space: Dict with n_electrons, n_orbitals, etc.

    AVAS-specific:
        avas_ao_labels_requested: List of requested AO labels
        avas_ao_labels_logging_only: Boolean flag
        avas_atomic_projection_executed: Boolean flag
        avas_stub_semantics: AVAS stub behavior identifier
        avas_partial_stub: Boolean flag

    Validation and auditing:
        integral_crosscheck_casci_v1: Cross-check report dict
        casscf_orbital_audit_v1: Orbital audit results
        mo_coeff_transform_hook_v1: Transform hook record

    PBC (periodic boundary conditions):
        pbc: Boolean flag
        pbc_kpoint_mesh: List of k-point mesh dimensions
        pbc_active_space_kpoint_index: Index of k-point for active space

    Precomputed bundles:
        precomputed_bundle_schema: Schema version string
        precomputed_bundle_path: Path to bundle file

    Kernel bindings:
        kernel_bindings: List of KernelBinding records
    """

    # Core identification
    backend_tag: str
    solver_type: str
    basis: str

    # Active space
    active_space_strategy: str
    active_space_recipe: str
    active_space_frozen_orbitals: list[int]
    resolved_active_space: dict[str, Any]

    # AVAS
    avas_ao_labels_requested: list[str]
    avas_ao_labels_logging_only: bool
    avas_atomic_projection_executed: bool
    avas_stub_semantics: str
    avas_partial_stub: bool

    # Validation
    integral_crosscheck_casci_v1: dict[str, Any]
    casscf_orbital_audit_v1: dict[str, Any]
    mo_coeff_transform_hook_v1: dict[str, Any]

    # PBC
    pbc: bool
    pbc_kpoint_mesh: list[int]
    pbc_active_space_kpoint_index: int

    # Precomputed
    precomputed_bundle_schema: str
    precomputed_bundle_path: str

    # Kernel bindings
    kernel_bindings: list[dict[str, Any]]


def validate_driver_meta(meta: dict[str, Any]) -> None:
    """Validate that driver_meta contains expected keys and types.

    This is a soft validation that logs warnings for unexpected keys but
    does not raise exceptions, preserving the flexible dict[str, Any] behavior.

    Args:
        meta: The driver_meta dictionary to validate

    Note:
        This function is primarily for documentation and debugging.
        Production code should not rely on this validation.
    """
    known_keys = set(DriverMeta.__annotations__.keys())
    unknown_keys = set(meta.keys()) - known_keys

    if unknown_keys:
        # Log warning but don't fail - driver_meta is intentionally flexible
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            "driver_meta contains unknown keys: %s (this may be intentional)", sorted(unknown_keys)
        )
