"""
Executable **linear** mitigation schedule (open stack — not Quantinuum Qermit).

Consumes the same YAML flags as :func:`qchem_stack.mitigation.qermit_analog.build_qermit_style_mitigation_report`
and applies toy PMSV (stderr inflation) + ZNE (``zne_scale_energy`` curve) to a scalar energy.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.config import ExperimentConfig
from qchem_stack.mitigation.zne import zne_scale_energy


def execute_mitigation_dag_runtime(
    cfg: ExperimentConfig, out: dict[str, Any]
) -> dict[str, Any] | None:
    """If mitigation is on and an energy is present in ``out``, return an execution trace."""
    m = cfg.mitigation
    if not (m.pmsv_enabled or m.zne_enabled or m.spam_calibration_enabled):
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
    return execute_mitigation_dag(float(e_raw), stderr, graph, cfg, protocol_counts=pc)


def execute_mitigation_dag(
    energy: float,
    energy_stderr: float | None,
    graph_report: dict[str, Any] | None,
    cfg: ExperimentConfig,
    *,
    protocol_counts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run PMSV then ZNE stubs in graph order; attach report id for audit."""
    m = cfg.mitigation
    trace: list[dict[str, Any]] = []
    e = float(energy)
    se = float(energy_stderr) if energy_stderr is not None else None

    if m.spam_calibration_enabled:
        trace.append(
            {
                "node": "SPAM_readout_calibration_stub",
                "energy_in": e,
                "energy_out": e,
                "energy_stderr_in": se,
                "energy_stderr_out": se,
                "note": "Scalar-energy identity stub; bitstring-level readout correction is not applied here.",
            }
        )

    if m.pmsv_enabled:
        rr = float(m.pmsv_retention_rate)
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

    if m.zne_enabled:
        scales = [float(x) for x in m.zne_scales] if m.zne_scales else [1.0, 1.5, 2.0]
        pc_ex = protocol_counts or {}
        zcurve = pc_ex.get("zne_curve")
        use_protocol_curve = (
            m.zne_mode == "circuit_scale_fold"
            and isinstance(zcurve, list)
            and len(zcurve) == len(scales)
        )
        if use_protocol_curve:
            curve = [float(x) for x in zcurve]
            ex_opt = pc_ex.get("zne_extrapolated_energy")
            ex = float(ex_opt) if ex_opt is not None else float(np.mean(np.array(curve, dtype=float)))
        else:
            curve = [zne_scale_energy(e, s) for s in scales]
            ex = float(np.mean(np.array(curve, dtype=float)))
        trace.append(
            {
                "node": "ZNE_extrapolation_stub",
                "zne_scales": scales,
                "zne_energies": curve,
                "zne_extrapolated_energy": ex,
                "zne_extrapolated_stub": ex,
            }
        )
        e = ex

    gr = graph_report if isinstance(graph_report, dict) else None
    gid = gr.get("schema") if gr else None
    return {
        "schema": "qermit_runtime_v1",
        "graph_schema": gid,
        "final_energy": e,
        "final_energy_stderr": se,
        "trace": trace,
    }
