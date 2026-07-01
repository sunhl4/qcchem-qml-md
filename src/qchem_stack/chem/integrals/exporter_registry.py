"""Registry mapping ``backend_tag`` → active-space integral exporter."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING

from qchem_stack.chem.integrals.psi4_active_space_exporter import Psi4ActiveSpaceIntegralExporter
from qchem_stack.chem.integrals.pyscf_active_space_exporter import PySCFActiveSpaceIntegralExporter
from qchem_stack.exceptions import PreQuantumCapabilityError

if TYPE_CHECKING:
    from qchem_stack.chem.integrals.exporter_protocol import ActiveSpaceIntegralExporter

_LOG = logging.getLogger(__name__)

_EXPORTERS: dict[str, ActiveSpaceIntegralExporter] = {
    "pyscf": PySCFActiveSpaceIntegralExporter(),
    "psi4": Psi4ActiveSpaceIntegralExporter(),
}
_REGISTRY_FROZEN = False


@lru_cache(maxsize=256)
def _normalized_backend_tag(backend_tag: str) -> str:
    return str(backend_tag).strip().lower()


def list_active_space_integral_exporters() -> tuple[str, ...]:
    """Stable sorted registry view for diagnostics/tests."""
    return tuple(sorted(_EXPORTERS))


def freeze_active_space_integral_exporters() -> None:
    """Disallow further runtime registry mutation in this process."""
    global _REGISTRY_FROZEN
    _REGISTRY_FROZEN = True


def _ensure_registry_mutable() -> None:
    if _REGISTRY_FROZEN:
        raise RuntimeError(
            "Active-space integral exporter registry is frozen for this process. "
            "Register exporters before calling freeze_active_space_integral_exporters()."
        )


def register_active_space_integral_exporter(
    backend_tag: str,
    exporter: ActiveSpaceIntegralExporter,
    *,
    allow_override: bool = False,
) -> None:
    """Register an exporter by backend tag.

    By default existing entries cannot be replaced silently. Pass
    ``allow_override=True`` for explicit replacement.
    """
    _ensure_registry_mutable()
    tag = _normalized_backend_tag(backend_tag)
    if tag in _EXPORTERS and not allow_override:
        raise ValueError(
            f"ActiveSpaceIntegralExporter {tag!r} is already registered; "
            "pass allow_override=True to replace it explicitly."
        )
    if tag in _EXPORTERS and allow_override:
        _LOG.warning("Overriding ActiveSpaceIntegralExporter for backend %s", tag)
    _EXPORTERS[tag] = exporter


def get_active_space_integral_exporter(backend_tag: str) -> ActiveSpaceIntegralExporter:
    tag = _normalized_backend_tag(backend_tag)
    exp = _EXPORTERS.get(tag)
    if exp is None:
        known = list_active_space_integral_exporters()
        raise PreQuantumCapabilityError(
            f"No ActiveSpaceIntegralExporter registered for backend {tag!r}. "
            f"Known backends: {known}."
        )
    return exp
