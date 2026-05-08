"""
Classical QC software → qchem_stack **interchange** (stable headers + façade entry).

Upstream packages (PySCF, Psi4, …) are reached only via :class:`~qchem_stack.chem.solvers.base.ChemIntegralSolver`
implementations registered in ``qchem_stack.chem.solvers``; façade output is always
:class:`~qchem_stack.chem.solvers.base.MolecularMeanFieldResult` decorated with canonical bridge meta.
"""

from qchem_stack.chem.bridges.canonical_integral_pack import (
    SCHEMA_V1 as CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK_SCHEMA_V1,
)
from qchem_stack.chem.bridges.canonical_integral_pack import (
    CanonicalActiveSpaceIntegralPack,
)
from qchem_stack.chem.bridges.facade import (
    RegistryBackedClassicalBridge,
    classical_mean_field_via_solver_bridge,
    molecular_system_from_experiment,
)
from qchem_stack.chem.bridges.interchange import (
    CANONICAL_CLASSICAL_BRIDGE_META_VERSION,
    merge_canonical_classical_bridge_headers,
)
from qchem_stack.chem.bridges.mean_field_like import MeanFieldLike, wrap_mean_field_like
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.protocol import ClassicalChemistrySoftwareBridge

__all__ = [
    "CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK_SCHEMA_V1",
    "CANONICAL_CLASSICAL_BRIDGE_META_VERSION",
    "CanonicalActiveSpaceIntegralPack",
    "ClassicalMeanFieldReference",
    "ClassicalChemistrySoftwareBridge",
    "MeanFieldLike",
    "RegistryBackedClassicalBridge",
    "classical_mean_field_via_solver_bridge",
    "merge_canonical_classical_bridge_headers",
    "molecular_system_from_experiment",
    "wrap_mean_field_like",
]
