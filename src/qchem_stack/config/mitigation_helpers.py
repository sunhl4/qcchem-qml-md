"""Read-only helpers for :class:`~qchem_stack.config.mitigation.MitigationSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .experiment import ExperimentConfig
    from .mitigation import MitigationSpec


def zne_enabled(spec: MitigationSpec) -> bool:
    return bool(spec.zne.enabled)


def zne_mode(spec: MitigationSpec) -> str:
    return str(spec.zne.mode)


def zne_scales(spec: MitigationSpec) -> list[float]:
    return list(spec.zne.scales)


def pmsv_enabled(spec: MitigationSpec) -> bool:
    return bool(spec.pmsv.enabled)


def pmsv_stabilizers(spec: MitigationSpec) -> list[str]:
    return list(spec.pmsv.stabilizers)


def pmsv_retention_rate(spec: MitigationSpec) -> float:
    return float(spec.pmsv.retention_rate)


def pmsv_report_extension(spec: MitigationSpec) -> str:
    return str(spec.pmsv.report_extension)


def pmsv_extra(spec: MitigationSpec) -> dict[str, Any]:
    return dict(spec.pmsv.extra)


def spam_calibration_enabled(spec: MitigationSpec) -> bool:
    return bool(spec.stubs.spam_calibration)


def pec_literature_stub_enabled(spec: MitigationSpec) -> bool:
    return bool(spec.stubs.pec_literature)


def classical_shadows_stub_enabled(spec: MitigationSpec) -> bool:
    return bool(spec.stubs.classical_shadows)


def classical_shadows_budget_pairs(spec: MitigationSpec) -> int:
    return int(spec.stubs.classical_shadows_budget_pairs)


def mitigation_repro_core_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """Stable repro snapshot keys derived from mitigation config."""
    m = cfg.mitigation
    return {
        "pmsv_enabled": pmsv_enabled(m),
        "zne_enabled": zne_enabled(m),
        "spam_calibration_enabled": spam_calibration_enabled(m),
        "classical_shadows_stub_enabled": classical_shadows_stub_enabled(m),
        "classical_shadows_budget_pairs": classical_shadows_budget_pairs(m),
        "mitigation_execution_class": m.execution_class,
        "mitigation_zne_scales": [float(x) for x in zne_scales(m)],
        **({"mitigation_zne_mode": zne_mode(m)} if zne_enabled(m) else {}),
    }
