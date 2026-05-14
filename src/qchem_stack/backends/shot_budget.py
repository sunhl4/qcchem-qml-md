from __future__ import annotations

import math
from dataclasses import dataclass

from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan


@dataclass
class EnergyUncertaintyEstimate:
    """Conservative classical shot-noise bookkeeping (commuting groups, same ``N`` shots per circuit)."""

    mean: float
    stderr: float
    shots_per_circuit: int
    n_circuits: int
    total_shots: int
    model: str = "conservative_sum_bound"


def conservative_stderr_equal_shots(
    plan: PauliMeasurementPlan, h_terms: dict, shots_per_circuit: int
) -> float:
    """
    Upper-bound style: per group ``g``, contribution std ≤ ``sum_{t∈g}|c_t| / sqrt(N)`` (all |λ(P)|≤1).
    Total variance ≤ sum of squares of these bounds (independence across circuits).
    """
    if not plan.groups:
        return 0.0
    if shots_per_circuit <= 0:
        return float("inf")
    n = float(shots_per_circuit)
    var_sum = 0.0
    for g in plan.groups:
        amp = sum(abs(float(h_terms[t].real)) for t in g)  # real weights for Hermitian H
        var_sum += (amp**2) / n
    return math.sqrt(var_sum)


def energy_estimate_with_uncertainty(
    mean_energy: float,
    plan: PauliMeasurementPlan,
    h: dict,
    shots_per_circuit: int,
) -> EnergyUncertaintyEstimate:
    se = conservative_stderr_equal_shots(plan, h, shots_per_circuit)
    nc = plan.n_circuits
    return EnergyUncertaintyEstimate(
        mean=mean_energy,
        stderr=se,
        shots_per_circuit=shots_per_circuit,
        n_circuits=nc,
        total_shots=shots_per_circuit * nc,
    )


def recommended_shots_per_circuit(
    plan: PauliMeasurementPlan,
    h_terms: dict,
    target_stderr: float,
    *,
    min_shots: int = 8,
    max_shots: int = 1_000_000,
) -> int:
    """Invert conservative bound: pick ``N`` so ``stderr(N) ≤ target_stderr`` (if possible within max)."""
    if target_stderr <= 0:
        return max_shots
    lo, hi = min_shots, max_shots
    best = hi
    while lo <= hi:
        mid = (lo + hi) // 2
        if conservative_stderr_equal_shots(plan, h_terms, mid) <= target_stderr:
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return int(best)
