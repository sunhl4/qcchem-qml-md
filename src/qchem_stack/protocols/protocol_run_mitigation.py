"""Pauli support export and PMSV/ZNE post-processing for protocol RUN stage."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.mitigation.pmsv import filter_shots_pmsv, finalize_pmsv_report
from qchem_stack.mitigation.zne import zne_scale_energy
from qchem_stack.protocols.pauli_support import hamiltonian_pauli_term_records
from qchem_stack.protocols.protocol_hea import hea_angles_for_depth

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def attach_pauli_support_and_mitigation(
    proto: PauliAveragingProtocol,
    plan: Any,
    shots: int,
    n_groups: int,
    noise_rng: np.random.Generator,
    exe: HamiltonianExpectationExecutor,
) -> None:
    records = hamiltonian_pauli_term_records(proto.hamiltonian)
    n_full = len(records)
    ps = [r["pauli_string"] for r in records]
    truncated = False
    cap = proto.pauli_support_max_terms
    if cap is not None and cap >= 0 and n_full > cap:
        truncated = True
        records = records[:cap]
        ps = ps[:cap]
    proto._counts["hamiltonian_pauli_term_records"] = records
    proto._counts["hamiltonian_pauli_strings"] = ps
    proto._counts["n_hamiltonian_pauli_terms"] = len(ps)
    proto._counts["pauli_support_truncated"] = truncated
    if truncated:
        proto._counts["n_hamiltonian_pauli_terms_full"] = n_full
    metas_post = plan.to_circuit_metas()
    proto._counts["pauli_group_ids"] = [int(m.get("group_id", 0)) for m in metas_post]

    e_val = float(proto._counts["expectation"])
    if proto.pmsv and (proto.pmsv.stabilizers or 0.0 < float(proto.pmsv.retention_rate) < 1.0):
        proto._counts["kept_shots"] = filter_shots_pmsv(shots, proto.pmsv.retention_rate, noise_rng)
    if proto.zne_scales:
        _apply_zne(proto, shots=shots, n_groups=n_groups, e_val=e_val, exe=exe)
    if proto.pmsv is not None:
        _apply_pmsv_report(proto)


def _apply_zne(
    proto: PauliAveragingProtocol,
    *,
    shots: int,
    n_groups: int,
    e_val: float,
    exe: HamiltonianExpectationExecutor,
) -> None:
    scales_f = [float(s) for s in (proto.zne_scales or ())]
    fold_requested = proto.zne_mode == "circuit_scale_fold"
    unsupported_fold = fold_requested and (proto.run_sampled or proto.run_qiskit_shots)
    if fold_requested and not unsupported_fold:
        base_depth = int(proto.hea_depth)
        curve: list[float] = []
        for s in scales_f:
            eff_depth = max(1, base_depth + int(max(0.0, round(s - 1.0))))
            ang = hea_angles_for_depth(
                proto.angles,
                n_qubits=proto.n_qubits,
                base_depth=base_depth,
                eff_depth=eff_depth,
            )
            curve.append(
                float(
                    exe.expectation_hea(
                        proto.hamiltonian,
                        proto.n_qubits,
                        ang,
                        eff_depth,
                    )
                )
            )
        proto._counts["zne_curve"] = curve
        proto._counts["zne_energies"] = curve
        proto._counts["zne_mode"] = "circuit_scale_fold"
        arr_s = np.asarray(scales_f, dtype=float)
        arr_e = np.asarray(curve, dtype=float)
        if arr_e.size >= 2:
            coef = np.polyfit(arr_s, arr_e, 1)
            proto._counts["zne_extrapolated_energy"] = float(np.polyval(coef, 1.0))
        else:
            proto._counts["zne_extrapolated_energy"] = float(curve[0])
        base_budget = int(proto._counts.get("total_shots_budget", shots * max(1, n_groups)))
        shot_mult = sum(max(1, int(round(s))) for s in scales_f)
        proto._counts["total_shots_budget"] = base_budget * shot_mult
    else:
        proto._counts["zne_energies"] = [zne_scale_energy(e_val, s) for s in scales_f]
        proto._counts["zne_mode"] = "scalar_stub"
        if unsupported_fold:
            proto._counts["zne_circuit_fold_fallback_reason"] = (
                "circuit_scale_fold requires exact executor path "
                "(disable run_sampled / run_qiskit_shots)"
            )


def _apply_pmsv_report(proto: PauliAveragingProtocol) -> None:
    if proto.pmsv is None:
        return
    rr = float(proto.pmsv.retention_rate)
    discard = max(0.0, min(1.0, 1.0 - rr))
    pr = {
        "stabilizers": list(proto.pmsv.stabilizers),
        "stabilizer_count": len(proto.pmsv.stabilizers),
        "retention_rate": rr,
        "discard_fraction": discard,
        "effective_kept_shots_fraction": rr,
        "stderr_inflation_from_postselection": float(proto._counts.get("pmsv_stderr_scale", 1.0)),
        "pmsv_stderr_scale": float(proto._counts.get("pmsv_stderr_scale", 1.0)),
        "kept_shots_simulated": proto._counts.get("kept_shots"),
    }
    proto._counts["pmsv_report"] = finalize_pmsv_report(pr, proto.pmsv)
