"""Resource summary helpers for protocol finalize (excited-only path)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.orchestration.excited_stages import (
    excited_methods_unified,
    excited_shots_upper_bound,
)

if TYPE_CHECKING:
    from qchem_stack.orchestration.excited_stages_types import ExcitedResourceSummary


def resource_summary_excited_only(
    n_qubits: int, excited_rs: ExcitedResourceSummary
) -> dict[str, object]:
    ub = excited_shots_upper_bound(excited_rs)
    rs: dict[str, object] = {
        "n_circuits": 0,
        "sum_shots": 0,
        "max_depth": 0,
        "sum_twoq": 0,
        "n_qubits": n_qubits,
        "n_pauli_terms": None,
        "n_pauli_groups": None,
        "pauli_averaging_protocol_ran": False,
        "excited_stages": excited_rs,
        "excited_shots_upper_bound": ub,
        "sum_shots_total_with_excited_upper_bound": ub,
    }
    bounds = excited_rs.get("shot_channel_upper_bounds")
    if bounds is not None:
        rs["excited_shot_accounting"] = bounds
    rs["excited_methods_unified"] = excited_methods_unified(excited_rs)
    return rs
