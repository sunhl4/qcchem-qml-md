"""Optional repro sidecars attached after variational / Pauli stages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import QPE_ALGORITHM_THREE_PACK_V1
from qchem_stack.jobs.nexus_analog import nexus_analog_ledger_from_rows
from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig


def attach_nexus_mitigation_tn(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Nexus / HQC analog, Qermit-style mitigation graph report, optional CuTensorNet stub."""
    if cfg.nexus_analog.enabled:
        rows = out.get("resource_rows")
        if rows is None:
            rows = out.get("pauli_measurement_ledger")
        led = nexus_analog_ledger_from_rows(list(rows or []), cfg)
        if led is not None:
            out["nexus_analog_ledger"] = led
    mgr = build_qermit_style_mitigation_report(cfg)
    if mgr is not None:
        out["mitigation_graph_report"] = mgr
    dex = execute_mitigation_dag_runtime(cfg, out)
    if dex is not None:
        out["mitigation_dag_execution"] = dex
    nc = nexus_cloud_repro_sidecar(cfg)
    if nc is not None:
        out["nexus_cloud_repro"] = nc
    if cfg.quantum.tensornet.expectation_stub:
        from qchem_stack.tensornet import run_cutensornet_expectation_stub

        out["tensornet_protocol_stub"] = run_cutensornet_expectation_stub(
            qh.n_qubits, requested_backend=cfg.quantum.tensornet.contraction_engine
        )


def attach_qpe_demo_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional dense QPE + Bayesian toy, same as ``scripts/run_qpe_track_demo.py``."""
    if not cfg.quantum.qpe_demo_track_requested():
        return
    from qchem_stack.qpe_qec_demo.pipeline_track import qpe_demo_track_payload

    out["qpe_demo_track"] = qpe_demo_track_payload(
        qh, bits=int(cfg.quantum.demos.qpe.demo_track_n_bits)
    )


def attach_vqs_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional VQS / McLachlan dynamics on variational parameters."""
    if not cfg.quantum.vqs_track_requested():
        return
    ang = out.get("angles")
    if ang is None:
        return
    from qchem_stack.quantum.algorithms.vqs_pipeline_track import vqs_track_payload

    q = cfg.quantum
    out["vqs_track"] = vqs_track_payload(
        qh,
        ang,
        mode=q.demos.vqs.mode,
        n_times=q.demos.vqs.n_times,
        dt=float(q.demos.vqs.dt),
        rhs_mode_yaml=q.demos.vqs.rhs_mode,
        tangent_fd_epsilon_yaml=float(q.demos.vqs.tangent_fd_epsilon),
    )


def attach_qpe_three_algorithm_pack_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Dense QPE trio from :mod:`~qchem_stack.quantum.algorithms.qpe`."""
    if not cfg.quantum.qpe_three_pack_requested():
        return
    from qchem_stack.quantum.algorithms.qpe import (
        AlgorithmDeterministicQPE,
        AlgorithmInfoTheoryQPE,
        AlgorithmKitaevQPE,
    )

    qt = cfg.quantum
    t_ev = float(qt.demos.qpe.three_pack.time)

    def _row(public: str, res: Any) -> dict[str, Any]:
        meta = getattr(res, "meta", None)
        md = dict(meta) if isinstance(meta, dict) else {}
        return {
            "algorithm": public,
            "phase_mu": float(getattr(res, "phase_mu", 0.0)),
            "phase_sigma": float(getattr(res, "phase_sigma", 0.0)),
            "energy_estimate": float(getattr(res, "energy_estimate", float("nan"))),
            "meta": md,
        }

    det = AlgorithmDeterministicQPE(
        qh, time=t_ev, n_rounds=int(qt.demos.qpe.three_pack.deterministic_rounds)
    )
    kit = AlgorithmKitaevQPE(qh, time=t_ev, n_bits=int(qt.demos.qpe.three_pack.kitaev_bits))
    inf = AlgorithmInfoTheoryQPE(qh, time=t_ev, n_samples=int(qt.demos.qpe.three_pack.info_samples))

    rd = det.build().run()  # type: ignore[union-attr]
    rk = kit.build().run()  # type: ignore[union-attr]
    ri = inf.build().run(seed=int(cfg.random_seed))  # type: ignore[union-attr]

    out["qpe_algorithm_three_pack"] = {
        "schema": QPE_ALGORITHM_THREE_PACK_V1,
        "time": float(t_ev),
        "yaml_note": (
            "Dense-spectrum emulation on the Hamiltonian Hilbert space; phase summaries are illustrative."
        ),
        "deterministic_qpe_report_v1": _row("deterministic_qpe", rd),
        "kitaev_qpe_report_v1": _row("kitaev_qpe", rk),
        "info_theory_qpe_report_v1": _row("info_theory_qpe", ri),
        "yaml_flags": {
            "qpe_three_pack_after_variational": bool(qt.demos.qpe.three_pack.after_variational)
        },
        "implementations": {
            "deterministic": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
            "kitaev": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
            "info_theory": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
        },
    }


def maybe_attach_md_ml_qmef_dataset(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> None:
    """Optional ``repro.qmef_ml_attachment_v1`` for MD→ML export."""
    if not cfg.md_ml_export.attach_single_frame_to_repro:
        return
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    from qchem_stack.md_bridge.from_pipeline import build_qmef_ml_attachment_repro_block

    repro["qmef_ml_attachment_v1"] = build_qmef_ml_attachment_repro_block(
        cfg, out, reference, cfg_path=cfg_path
    )
