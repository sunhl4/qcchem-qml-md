"""L2 integration helpers: driver_meta conventions and external-driver checklists."""

from qchem_stack.chem.integration.checklist import (
    IntegrationChecklistReport,
    run_integration_checklist,
)
from qchem_stack.chem.integration.meta_schema import (
    DRIVER_META_SCHEMA_VERSION,
    append_kernel_bindings,
    binding_mean_field_scf,
    merge_integration_driver_meta,
    merge_rdm_correction_bindings_into_reference,
)
from qchem_stack.chem.integration.presets import (
    capabilities_precomputed_offline,
    capabilities_psi4_production,
    capabilities_pyscf_production,
)

__all__ = [
    "DRIVER_META_SCHEMA_VERSION",
    "append_kernel_bindings",
    "binding_mean_field_scf",
    "merge_integration_driver_meta",
    "merge_rdm_correction_bindings_into_reference",
    "IntegrationChecklistReport",
    "run_integration_checklist",
    "capabilities_pyscf_production",
    "capabilities_psi4_production",
    "capabilities_precomputed_offline",
]
