from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.embedding.dmet import DMETContext, VQEFragmentSolverStub
from qchem_stack.chem.embedding.dmet_self_consistent import OneShotEmbeddingDriver
from qchem_stack.config.embedding_enums import DmetHamiltonianSource, EmbeddingMode
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels, require_dmet
from qchem_stack.config.quantum_helpers import (
    pauli_run_qiskit_shots,
    resolve_tensornet_contraction_engine,
    resolve_vqe_depth,
    tensornet_expectation_stub_enabled,
)
from qchem_stack.contracts.schema_ids import (
    CUTENSORTNET_PROTOCOL_STUB_V1,
    SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1,
    SCHMIDT_PER_FRAGMENT_VQE_V1,
    TKET_STATS_SKIPPED_V1,
    ZNE_QISKIT_UNIFICATION_V1,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def schmidt_per_fragment_vqe_parity_summary(spfv: dict[str, Any]) -> dict[str, Any]:
    """Compact JSON digest for repro parity snapshot."""
    fr = spfv.get("fragments") or []
    rows: list[dict[str, Any]] = []
    nfev_total = 0
    for r in fr:
        if not isinstance(r, dict):
            continue
        nfev_total += int(r.get("nfev", 0))
        rows.append(
            {
                "fragment_id": r.get("fragment_id"),
                "energy_au": r.get("energy"),
                "n_qubits": r.get("n_qubits"),
                "nfev": r.get("nfev"),
            }
        )
    return {
        "schema": SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1,
        "n_fragments": len(rows),
        "total_nfev": nfev_total,
        "vqe_depth": spfv.get("vqe_depth"),
        "vqe_maxiter_per_fragment": spfv.get("vqe_maxiter_per_fragment"),
        "fragments": rows,
    }


def finalize_open_stack_parity_snapshot(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    proto: PauliAveragingProtocol | None,
) -> None:
    """Runtime parity snapshot fields."""
    pis = cfg.parity_integrations
    if not pis.enabled:
        return
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    snap = repro.get("parity_snapshot")
    if not isinstance(snap, dict):
        return

    if pis.tket_first_circuit_stats:
        if proto is not None:
            compiled = (
                proto.compiled_circuits
                if hasattr(proto, "compiled_circuits")
                else getattr(proto, "_compiled", None) or []
            )
            if compiled:
                from qchem_stack.integrations.tket_fullchain import circuit_ir_to_tket_stats_or_none

                snap["tket_first_compiled_circuit_probe"] = circuit_ir_to_tket_stats_or_none(
                    compiled[0]
                )
            else:
                snap["tket_first_compiled_circuit_probe"] = {
                    "schema": TKET_STATS_SKIPPED_V1,
                    "reason": "no_compiled_circuits_after_compile",
                }
        else:
            snap["tket_first_compiled_circuit_probe"] = {
                "schema": TKET_STATS_SKIPPED_V1,
                "reason": "pauli_protocol_disabled_no_circuit_ir",
            }

    if pis.dmet_stub_one_shot_ledger and cfg.embedding.mode == EmbeddingMode.DMET:
        emb = require_dmet(cfg.embedding)
        dmet = emb.dmet
        if dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
            snap["dmet_solver_mode"] = "schmidt_atomic_production"
            hm = snap.get("hamiltonian_meta")
            if isinstance(hm, dict) and isinstance(hm.get("schmidt_production_audit"), dict):
                snap["schmidt_embedding_production"] = hm["schmidt_production_audit"]
        elif out.get("dmet_fragment_solve"):
            snap["dmet_one_shot_open_ledger"] = out["dmet_fragment_solve"]
            snap["dmet_solver_mode"] = dmet.hamiltonian_source
        elif out.get("dmet_fragment_solve_error"):
            snap["dmet_fragment_solve_error"] = out["dmet_fragment_solve_error"]
            snap["dmet_solver_mode"] = dmet.hamiltonian_source
        else:
            labels = nonempty_fragment_labels(emb) or ["fragment_0"]
            ctx = DMETContext(
                fragments=labels, solver=VQEFragmentSolverStub(depth=resolve_vqe_depth(cfg))
            )
            hams = {
                fid: {
                    "open_stack_placeholder": True,
                    "n_active_electrons": cfg.active_space.cas.n_electrons,
                    "n_active_orbitals": cfg.active_space.cas.n_orbitals,
                }
                for fid in labels
            }
            snap["dmet_one_shot_open_ledger"] = OneShotEmbeddingDriver.run(ctx, hams)
            snap["dmet_solver_mode"] = "parity_stub"

    spfv = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv, dict) and spfv.get("schema") == SCHMIDT_PER_FRAGMENT_VQE_V1:
        snap["schmidt_per_fragment_vqe_summary"] = schmidt_per_fragment_vqe_parity_summary(spfv)

    if out.get("dmet_uniform_multifragment_toy"):
        snap["dmet_uniform_multifragment_toy"] = out["dmet_uniform_multifragment_toy"]

    dmet_loop = out.get("dmet_self_consistency_loop")
    if isinstance(dmet_loop, dict):
        snap["dmet_self_consistency_loop"] = {
            k: v for k, v in dmet_loop.items() if not str(k).startswith("_")
        }

    tnstub = out.get("tensornet_protocol_stub")
    if isinstance(tnstub, dict) and str(tnstub.get("schema")) == CUTENSORTNET_PROTOCOL_STUB_V1:
        eng = tnstub.get("engine_resolved") or tnstub.get("requested_backend")
        snap["tensornet_engine_resolved"] = str(eng if eng is not None else "stub")
        st = tnstub.get("status")
        snap["tensornet_fallback_reason"] = (
            str(st) if st is not None else "cutensornet_stub_no_status"
        )
    elif pis.enabled:
        snap["tensornet_engine_resolved"] = resolve_tensornet_contraction_engine(cfg)
        if tensornet_expectation_stub_enabled(cfg):
            snap["tensornet_fallback_reason"] = "tensornet_stub_not_emitted_pipeline_branch"
        else:
            snap["tensornet_fallback_reason"] = "tensornet_expectation_stub_disabled"

    vm = out.get("vqe_meta")
    if isinstance(vm, dict) and vm.get("uccsd_n_parameters") is not None:
        snap["uccsd_n_parameters"] = int(vm["uccsd_n_parameters"])
    if isinstance(vm, dict) and vm.get("uccsd_trotter_steps") is not None:
        snap["uccsd_trotter_steps"] = int(vm["uccsd_trotter_steps"])

    pc_fold = out.get("protocol_counts")
    if cfg.mitigation.zne.enabled and pauli_run_qiskit_shots(cfg):
        zm = cfg.mitigation.zne.mode
        proto_mode = pc_fold.get("zne_mode") if isinstance(pc_fold, dict) else None
        fb = pc_fold.get("zne_circuit_fold_fallback_reason") if isinstance(pc_fold, dict) else None
        snap["zne_qiskit_unification_v1"] = {
            "schema": ZNE_QISKIT_UNIFICATION_V1,
            "mitigation_zne_mode_yaml": zm,
            "protocol_counts_zne_mode": proto_mode,
            "circuit_fold_fallback_reason": fb,
            "epistemic_bound": (
                "Open stack: circuit_scale_fold on Qiskit shot counts runs grouped Pauli "
                "readouts at amplified HEA depths per ZNE scale; mitigation_dag_execution "
                "reuses protocol_counts.zne_curve when present."
            ),
        }
