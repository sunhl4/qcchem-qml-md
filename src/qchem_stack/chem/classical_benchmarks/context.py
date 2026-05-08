"""Typed bundle passed into classical post-HF benchmark backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


@dataclass(frozen=True)
class ClassicalBenchmarkContext:
    """Shared inputs for classical post-HF benchmarks.

    ``mean_field_reference`` is the unified post-SCF handle from the orchestration pipeline.
    PySCF-backed runners require ``backend_tag() == "pyscf"`` and use ``as_pyscf_rhf_result()``.
    """

    mean_field_reference: ClassicalMeanFieldReference | None = None
    reference_scf_method: str = "RHF"
    n_active_orbitals: int | None = None
    n_active_electrons: int | None = None
