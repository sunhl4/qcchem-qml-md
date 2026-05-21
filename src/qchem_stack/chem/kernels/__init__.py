"""L3 shared algorithm kernels (may delegate to PySCF, Psi4 Mints, OpenFermion, …).

See ``docs/execution/multi_backend_integration_philosophy.md`` for the three-layer model.
"""

from qchem_stack.chem.kernels.catalog import (
    KERNEL_AVAS_PROJECTION,
    KERNEL_CASCI_ACTIVE_INTEGRALS,
    KERNEL_MEAN_FIELD_SCF,
    KERNEL_NEVPT2_CASCI,
    KERNEL_QUBIT_FERMION_MAP,
    KernelBinding,
    kernel_binding,
    list_known_kernels,
)

__all__ = [
    "KERNEL_CASCI_ACTIVE_INTEGRALS",
    "KERNEL_AVAS_PROJECTION",
    "KERNEL_MEAN_FIELD_SCF",
    "KERNEL_NEVPT2_CASCI",
    "KERNEL_QUBIT_FERMION_MAP",
    "KernelBinding",
    "kernel_binding",
    "list_known_kernels",
]
