"""
Executable **linear** mitigation schedule (open stack — not Quantinuum Qermit).

Consumes the same YAML flags as :func:`qchem_stack.mitigation.qermit_analog.build_qermit_style_mitigation_report`
and applies toy PMSV (stderr inflation) + ZNE (``zne_scale_energy`` curve) to a scalar energy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.contracts.schema_ids import QERMIT_RUNTIME_V1
from qchem_stack.mitigation.zne import zne_scale_energy

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def execute_mitigation_dag_runtime(
    cfg: ExperimentConfig, out: dict[str, Any], *, qh: Any | None = None
) -> dict[str, Any] | None:
    """If mitigation is on and an energy is present in ``out``, return an execution trace."""
    m = cfg.mitigation
    if not (
        m.pmsv.enabled or m.zne.enabled or m.stubs.spam_calibration or m.stubs.classical_shadows
    ):
        return None
    e_raw = out.get("energy_pauli_protocol")
    if e_raw is None:
        e_raw = out.get("energy_after_variational")
    if e_raw is None:
        return None
    _pc0 = out.get("protocol_counts")
    pc: dict[str, Any] = _pc0 if isinstance(_pc0, dict) else {}
    stderr = pc.get("energy_stderr")
    graph = out.get("mitigation_graph_report")
    shadows_computable = _classical_shadows_computable_batch(cfg, out, qh)
    if shadows_computable is not None:
        out["classical_shadows_computable_runtime"] = shadows_computable
    return execute_mitigation_dag(
        float(e_raw),
        stderr,
        graph,
        cfg,
        protocol_counts=pc,
        classical_shadows_computable=shadows_computable,
    )


def _classical_shadows_computable_batch(
    cfg: ExperimentConfig,
    out: dict[str, Any],
    qh: Any | None,
) -> dict[str, Any] | None:
    """Route classical-shadows expectation through runtime estimator + optional exact check."""
    if not cfg.mitigation.stubs.classical_shadows or qh is None:
        return None
    angles = out.get("angles")
    if angles is None:
        return None
    import numpy as np

    from qchem_stack.config.quantum_helpers import resolve_vqe_depth
    from qchem_stack.mitigation.classical_shadows import classical_shadows_hamiltonian_expectation
    from qchem_stack.quantum.statevector import hea_state

    depth = resolve_vqe_depth(cfg)
    st = hea_state(np.asarray(angles, dtype=float), int(qh.n_qubits), int(depth))
    shadow = classical_shadows_hamiltonian_expectation(
        st,
        qh.operator,
        int(qh.n_qubits),
        budget_pairs=int(cfg.mitigation.stubs.classical_shadows_budget_pairs),
        seed=int(cfg.random_seed),
    )
    batch = {
        "results": [{"name": "classical_shadows_expectation", "value": shadow["expectation"]}],
        "computable_meta": shadow,
        "budget_pairs_hint": int(cfg.mitigation.stubs.classical_shadows_budget_pairs),
        "protocol_name": "classical_shadows_expectation_protocol",
    }
    return batch


def execute_mitigation_dag(
    energy: float,
    energy_stderr: float | None,
    graph_report: dict[str, Any] | None,
    cfg: ExperimentConfig,
    *,
    protocol_counts: dict[str, Any] | None = None,
    classical_shadows_computable: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run optional SPAM, classical-shadows stub, PMSV, then ZNE stubs in graph order."""
    m = cfg.mitigation
    trace: list[dict[str, Any]] = []
    e = float(energy)
    se = float(energy_stderr) if energy_stderr is not None else None

    if m.stubs.spam_calibration:
        from qchem_stack.mitigation.spam import SPAMCalibration, default_two_qubit_spam_matrix

        cal = SPAMCalibration(readout_assignment=default_two_qubit_spam_matrix())
        trace.append(
            {
                "node": "SPAM_readout_calibration_stub",
                "energy_in": e,
                "energy_out": e,
                "energy_stderr_in": se,
                "energy_stderr_out": se,
                "readout_assignment": cal.readout_assignment,
                "note": "2-qubit assignment matrix registered; histogram path uses correct_two_qubit_histogram.",
            }
        )

    if m.stubs.classical_shadows:
        cs_node: dict[str, Any] = {
            "node": "classical_shadows_expectation_stub",
            "energy_in": e,
            "energy_out": e,
            "energy_stderr_in": se,
            "energy_stderr_out": se,
            "budget_pairs_hint": int(m.stubs.classical_shadows_budget_pairs),
            "note": "Identity stub — open-stack analog to shadows narratives without sampling.",
        }
        if classical_shadows_computable is not None:
            cs_node["computable_runtime"] = "classical_shadows_hamiltonian_expectation"
            cs_node["protocol_list"] = {
                "results": classical_shadows_computable.get("results"),
                "computable_meta": classical_shadows_computable.get("computable_meta"),
            }
        trace.append(cs_node)

    if m.pmsv.enabled:
        rr = float(m.pmsv.retention_rate)
        rr = max(min(rr, 1.0), 1e-9)
        # Toy: effective stderr widens when post-selection keeps fewer shots
        se2 = None if se is None else float(se / (rr**0.5))
        trace.append(
            {
                "node": "PMSV_symmetry_filter",
                "energy": e,
                "energy_stderr_in": se,
                "energy_stderr_out": se2,
                "retention_rate": rr,
            }
        )
        se = se2

    if m.zne.enabled:
        scales = [float(x) for x in m.zne.scales] if m.zne.scales else [1.0, 1.5, 2.0]
        pc_ex = protocol_counts or {}
        zcurve = pc_ex.get("zne_curve")
        use_protocol_curve = (
            m.zne.mode == "circuit_scale_fold"
            and isinstance(zcurve, list)
            and len(zcurve) == len(scales)
        )
        if use_protocol_curve and zcurve is not None:
            curve = [float(x) for x in zcurve]
            ex_opt = pc_ex.get("zne_extrapolated_energy")
            ex = (
                float(ex_opt)
                if ex_opt is not None
                else float(np.mean(np.array(curve, dtype=float)))
            )
        else:
            curve = [zne_scale_energy(e, s) for s in scales]
            from qchem_stack.mitigation.zne import richardson_extrapolation

            ex = richardson_extrapolation(curve, scales, order=min(1, len(scales) - 1))
        trace.append(
            {
                "node": "ZNE_extrapolation_stub",
                "zne_scales": scales,
                "zne_energies": curve,
                "zne_extrapolated_energy": ex,
                "zne_extrapolation": "richardson",
                "zne_extrapolated_stub": ex,
            }
        )
        e = ex

    gr = graph_report if isinstance(graph_report, dict) else None
    gid = gr.get("schema") if gr else None
    return {
        "schema": QERMIT_RUNTIME_V1,
        "graph_schema": gid,
        "final_energy": e,
        "final_energy_stderr": se,
        "trace": trace,
    }
