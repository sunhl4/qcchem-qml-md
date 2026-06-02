"""UQC circuit_scale_fold: per-scale HEA depth + grouped Pauli cloud submissions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.mitigation.zne import richardson_extrapolation
from qchem_stack.protocols.protocol_hea import hea_angles_for_depth
from qchem_stack_uqc.uqc_mitigation import zne_config_from_meta

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec


def _effective_hea_depth(base_depth: int, scale: float) -> int:
    return max(1, int(base_depth) + int(max(0.0, round(float(scale) - 1.0))))


def run_uqc_zne_circuit_fold(
    hamiltonian: QubitOperator,
    n_qubits: int,
    hea_depth: int,
    angles: np.ndarray,
    shots_per_circuit: int,
    client: Any,
    spec: BackendSpec,
    *,
    energy_fn: Any | None = None,
) -> tuple[float, dict[str, Any], dict[str, Any]]:
    """Run grouped Pauli UQC shots at each ZNE scale (HEA depth fold).

    Returns ``(extrapolated_energy, protocol_counts, mitigation_trace)``.
    """
    meta = spec.meta or {}
    zne = zne_config_from_meta(meta)
    if zne is None:
        raise ValueError("run_uqc_zne_circuit_fold requires backend.meta.uqc_mitigation.zne.enabled")
    scales = [float(x) for x in (zne.get("scales") or [1.0, 1.5, 2.0])]
    if len(scales) < 2:
        raise ValueError("circuit_scale_fold requires at least two ZNE scales")

    from qchem_stack_uqc.uqc_pauli_shots import energy_estimate_grouped_uqc_shots

    angles = np.asarray(angles, dtype=float).ravel()
    base_depth = int(hea_depth)
    curve: list[float] = []
    for scale in scales:
        eff_depth = _effective_hea_depth(base_depth, scale)
        ang = hea_angles_for_depth(
            angles,
            n_qubits=int(n_qubits),
            base_depth=base_depth,
            eff_depth=eff_depth,
        )
        if energy_fn is not None:
            e_scale = float(
                energy_fn(hamiltonian, n_qubits, ang, eff_depth, shots_per_circuit, client, spec)
            )
        else:
            e_scale = energy_estimate_grouped_uqc_shots(
                hamiltonian,
                n_qubits,
                eff_depth,
                ang,
                int(shots_per_circuit),
                client,
                spec,
            )
        curve.append(float(e_scale))

    extrapolated = richardson_extrapolation(curve, scales, order=min(1, len(scales) - 1))
    protocol_counts: dict[str, Any] = {
        "zne_curve": list(curve),
        "zne_energies": list(curve),
        "zne_mode": "circuit_scale_fold",
        "zne_scales": list(scales),
        "zne_extrapolated_energy": float(extrapolated),
        "zne_base_hea_depth": base_depth,
    }
    trace = {
        "schema": "uqc_mitigation_zne_v1",
        "raw_energy": float(curve[0]),
        "zne_scales": scales,
        "zne_energies": curve,
        "zne_extrapolated_energy": float(extrapolated),
        "zne_extrapolation": "richardson",
        "zne_mode": "circuit_scale_fold",
        "zne_effective_depths": [_effective_hea_depth(base_depth, s) for s in scales],
    }
    return float(extrapolated), protocol_counts, trace


def uqc_zne_mode(meta: dict[str, Any]) -> str | None:
    zne = zne_config_from_meta(meta)
    if zne is None:
        return None
    return str(zne.get("mode") or "energy_stub")


__all__ = ["run_uqc_zne_circuit_fold", "uqc_zne_mode"]
