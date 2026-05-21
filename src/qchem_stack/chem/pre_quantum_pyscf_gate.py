"""PySCF-native handle gate for branches not yet on interchange types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


def require_pyscf_reference(
    rhf: ClassicalMeanFieldReference,
    *,
    context: str,
) -> Any:
    """Return a PySCF mean-field object only for still PySCF-specific branches."""
    tag = rhf.backend_tag()
    if tag != "pyscf":
        raise PipelineError(
            f"{context} currently requires PySCF-style mean-field handle (got backend={tag!r}). "
            "Use embedding.mode=plugin for backend-agnostic Hamiltonian ingestion, "
            "or implement the corresponding backend-specific bridge."
        )
    return rhf.as_pyscf_rhf_result()
