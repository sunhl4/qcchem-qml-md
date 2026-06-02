from __future__ import annotations

from dataclasses import dataclass

from qchem_stack.quantum.algorithms.tolerances import UNIT_PER_DEPTH, UNIT_PER_SHOT


@dataclass
class CostEstimate:
    """Upper-bound style cost proxy (HQC-like units arbitrary until cloud adapter)."""

    estimated_circuits: int
    estimated_total_shots: int
    native_twoq_depth_sum: int
    hqc_units: float

    @staticmethod
    def from_resource_rows(
        rows: list[dict],
        unit_per_circuit: float = 1.0,
        unit_per_shot: float = UNIT_PER_SHOT,
        unit_per_depth: float = UNIT_PER_DEPTH,
    ) -> CostEstimate:
        nc = len(rows)
        shots = sum(int(r.get("total_shots", 0)) for r in rows)
        depth = sum(int(r.get("depth", 0)) for r in rows)
        hqc = nc * unit_per_circuit + shots * unit_per_shot + depth * unit_per_depth
        return CostEstimate(
            estimated_circuits=nc,
            estimated_total_shots=shots,
            native_twoq_depth_sum=depth,
            hqc_units=float(hqc),
        )


class CostProvider:
    """Pluggable hook for real cloud pricing."""

    def estimate(self, rows: list[dict]) -> CostEstimate:  # pragma: no cover - default
        return CostEstimate.from_resource_rows(rows)
