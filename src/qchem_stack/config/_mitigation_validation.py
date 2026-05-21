"""Cross-field validation helpers for :mod:`qchem_stack.config.mitigation`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mitigation import MitigationSpec


def validate_mitigation_cross_fields(spec: MitigationSpec) -> None:
    if spec.pmsv.enabled:
        labels = [str(s).strip() for s in spec.pmsv.stabilizers if str(s).strip()]
        if not labels:
            raise ValueError(
                "mitigation.pmsv.enabled requires non-empty mitigation.pmsv.stabilizers."
            )
    if spec.zne.enabled and not spec.zne.scales:
        raise ValueError("mitigation.zne.enabled requires non-empty mitigation.zne.scales.")
