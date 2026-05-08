"""Protocol surface: every classical QC package exports the same interchange object."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.config import ExperimentConfig


@runtime_checkable
class ClassicalChemistrySoftwareBridge(Protocol):
    """Contract: upstream mean-field → :class:`~qchem_stack.chem.solvers.base.MolecularMeanFieldResult`.

    Implementations may wrap PySCF, Psi4, etc. The returned ``driver_meta`` MUST pass through
    :func:`qchem_stack.chem.bridges.merge_canonical_classical_bridge_headers` before leaving the bridge.
    """

    def to_interchange_mean_field(self, cfg: ExperimentConfig) -> MolecularMeanFieldResult: ...
