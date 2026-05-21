from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np


@dataclass
class PMSVConfig:
    """Partition measurement symmetry verification (retention rate is exogenous here)."""

    stabilizers: list[str] = field(default_factory=list)
    retention_rate: float = 0.85
    report_extension: str = "default"
    """Dispatch key for :func:`finalize_pmsv_report` (lab-specific postprocessing)."""
    extra: dict[str, Any] = field(default_factory=dict)
    """Merged into the published ``pmsv_report`` under ``extra`` when non-empty."""


def filter_shots_pmsv(raw_shots: int, retention_rate: float, rng: np.random.Generator) -> int:
    """Return kept shot count after symmetry post-selection (Bernoulli toy)."""
    if raw_shots <= 0:
        return 0
    return int(rng.binomial(raw_shots, min(max(retention_rate, 0.0), 1.0)))


def finalize_pmsv_report(
    base: dict[str, Any],
    pmsv: PMSVConfig,
) -> dict[str, Any]:
    """
    Extensible PMSV report: always copies *base*, adds ``report_extension`` and optional ``extra``.

    Override or extend by registering new keys in :attr:`PMSVConfig.report_extension` and
    handling them here (or pass metadata only via :attr:`PMSVConfig.extra`).
    """
    out: dict[str, Any] = dict(base)
    out["report_extension"] = pmsv.report_extension
    if pmsv.extra:
        out["extra"] = dict(pmsv.extra)
    return out
