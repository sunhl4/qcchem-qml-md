"""Pauli protocol run vs skip branches for pipeline finalize."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.backends.spec import summarize_circuit_shot_rows
from qchem_stack.config.quantum_helpers import pauli_protocol_enabled, resolve_vqe_depth
from qchem_stack.orchestration.excited_stages import (
    excited_methods_unified,
    excited_shots_upper_bound,
)
from qchem_stack.orchestration.parity_finalize import finalize_open_stack_parity_snapshot
from qchem_stack.orchestration.protocol_finalize_protocol import protocol_for_job
from qchem_stack.orchestration.protocol_finalize_resource import resource_summary_excited_only
from qchem_stack.orchestration.protocol_finalize_sidecars import (
    attach_nexus_mitigation_tn,
    attach_qpe_demo_track_if_requested,
    attach_qpe_three_algorithm_pack_if_requested,
    attach_vqs_track_if_requested,
    maybe_attach_md_ml_qmef_dataset,
)
from qchem_stack.orchestration.repro_summary import attach_run_summary as attach_run_summary_impl

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.excited_stages_types import ExcitedResourceSummary
    from qchem_stack.orchestration.run_context import PipelineStageTimer


def _attach_common_sidecars(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None,
    proto: Any | None,
) -> None:
    attach_nexus_mitigation_tn(out, cfg, qh)
    attach_qpe_demo_track_if_requested(out, cfg, qh)
    attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
    attach_vqs_track_if_requested(out, cfg, qh)
    finalize_open_stack_parity_snapshot(out, cfg, proto)
    maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)


def run_protocol_and_finalize_stage(
    cfg: ExperimentConfig,
    *,
    out: dict[str, Any],
    qh: QubitHamiltonian,
    angles: Any,
    excited_rs: ExcitedResourceSummary | None,
    bspec: Any,
    exe: Any,
    bundle: Any,
    rhf: ClassicalMeanFieldReference,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any]:
    profile.mark("pre_pauli_protocol")
    emit("pre_pauli_protocol")
    if not pauli_protocol_enabled(cfg):
        if excited_rs is not None:
            out["resource_summary"] = resource_summary_excited_only(qh.n_qubits, excited_rs)
        else:
            out["resource_summary"] = {
                "n_circuits": 0,
                "sum_shots": 0,
                "max_depth": 0,
                "sum_twoq": 0,
                "n_qubits": qh.n_qubits,
                "n_pauli_terms": None,
                "n_pauli_groups": None,
                "pauli_averaging_protocol_ran": False,
            }
        _attach_common_sidecars(out, cfg, qh, rhf, cfg_path=cfg_path, proto=None)
        profile.mark("pauli_protocol_skipped")
        emit("pauli_protocol_skipped")
        profile.mark("finalize_repro")
        emit("finalize_repro")
        out["repro"]["pipeline_profile"] = profile.to_profile_dict()
        attach_run_summary_impl(out, cfg)
        return out

    proto = protocol_for_job(cfg, qh, bspec=bspec, exe=exe, bundle=bundle)
    proto.build(np.asarray(angles, dtype=float), hea_depth=resolve_vqe_depth(cfg))
    proto.compile()
    proto.run()
    e_proto = proto.evaluate()
    rows = proto.dataframe_circuit_shot_rows()
    df_sum = summarize_circuit_shot_rows(rows)
    pc = proto._counts
    resource_summary = {
        **df_sum,
        "n_pauli_terms": pc.get("n_pauli_terms"),
        "n_pauli_groups": pc.get("n_pauli_groups"),
        "pauli_averaging_protocol_ran": True,
    }
    if excited_rs is not None:
        resource_summary["excited_stages"] = excited_rs
        ub = excited_shots_upper_bound(excited_rs)
        resource_summary["excited_shots_upper_bound"] = ub
        resource_summary["sum_shots_total_with_excited_upper_bound"] = int(df_sum["sum_shots"]) + ub
        bounds = excited_rs.get("shot_channel_upper_bounds")
        if bounds is not None:
            resource_summary["excited_shot_accounting"] = bounds
        resource_summary["excited_methods_unified"] = excited_methods_unified(excited_rs)
    out.update(
        {
            "energy_pauli_protocol": float(e_proto),
            "protocol_counts": proto._counts,
            "resource_rows": rows,
            "pauli_measurement_ledger": rows,
            "resource_summary": resource_summary,
        }
    )
    _attach_common_sidecars(out, cfg, qh, rhf, cfg_path=cfg_path, proto=proto)
    profile.mark("pauli_protocol_done")
    emit("pauli_protocol_done")
    profile.mark("finalize_repro")
    emit("finalize_repro")
    out["repro"]["pipeline_profile"] = profile.to_profile_dict()
    attach_run_summary_impl(out, cfg)
    return out
