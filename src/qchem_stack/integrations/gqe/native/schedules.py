"""Training schedules for native GQE (β annealing, etc.)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BetaScheduleKind = Literal["constant", "linear", "exponential"]


@dataclass(frozen=True)
class BetaSchedule:
    """Inverse-temperature schedule used in logit-matching / sampling.

    Nakaji GPT-QE: start with small β and gradually increase.
    """

    kind: BetaScheduleKind = "linear"
    beta_start: float = 1.0
    beta_end: float = 20.0

    def value(self, epoch: int, n_epochs: int) -> float:
        n = max(int(n_epochs), 1)
        e = min(max(int(epoch), 0), n - 1)
        if self.kind == "constant":
            return float(self.beta_end)
        frac = e / max(n - 1, 1)
        if self.kind == "linear":
            return float(self.beta_start + frac * (self.beta_end - self.beta_start))
        # exponential: beta_start * (beta_end/beta_start)^frac
        if self.beta_start <= 0 or self.beta_end <= 0:
            raise ValueError("exponential beta schedule requires positive beta_start/end")
        return float(self.beta_start * (self.beta_end / self.beta_start) ** frac)


CHEMICAL_ACCURACY_HARTREE = 1.6e-3
"""≈ 1 kcal/mol in Hartree."""


def chemical_accuracy_report(
    *,
    best_energy: float,
    reference_energy: float,
    scf_energy: float | None = None,
) -> dict[str, float | bool]:
    """Compare GQE best energy to an exact/FCI reference."""
    err = float(best_energy) - float(reference_energy)
    abs_err = abs(err)
    out: dict[str, float | bool] = {
        "best_energy": float(best_energy),
        "reference_energy": float(reference_energy),
        "error_hartree": float(err),
        "abs_error_hartree": float(abs_err),
        "chemical_accuracy_hartree": float(CHEMICAL_ACCURACY_HARTREE),
        "within_chemical_accuracy": bool(abs_err <= CHEMICAL_ACCURACY_HARTREE),
    }
    if scf_energy is not None:
        out["scf_energy"] = float(scf_energy)
        out["correlation_captured"] = float(scf_energy) - float(best_energy)
        out["correlation_available"] = float(scf_energy) - float(reference_energy)
    return out
