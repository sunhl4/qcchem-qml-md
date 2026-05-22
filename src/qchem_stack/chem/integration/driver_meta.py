"""Backward-compatible re-export; prefer :mod:`qchem_stack.chem.integration.meta_schema`."""

from qchem_stack.chem.integration.meta_schema import (
    DRIVER_META_SCHEMA_VERSION,
    append_kernel_bindings,
    binding_avas_projection,
    binding_casci_active_integrals,
    binding_mean_field_scf,
    binding_nevpt2_casci,
    merge_integration_driver_meta,
    merge_rdm_correction_bindings_into_reference,
    record_casci_active_integrals_binding,
)

__all__ = [
    "DRIVER_META_SCHEMA_VERSION",
    "append_kernel_bindings",
    "binding_avas_projection",
    "binding_casci_active_integrals",
    "binding_mean_field_scf",
    "binding_nevpt2_casci",
    "merge_integration_driver_meta",
    "merge_rdm_correction_bindings_into_reference",
    "record_casci_active_integrals_binding",
]
