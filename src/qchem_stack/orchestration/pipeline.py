from __future__ import annotations

import hashlib
import json
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.spec import summarize_circuit_shot_rows
from qchem_stack.chem.active_space.mean_field_meta import (
    apply_active_space_strategy_to_mean_field_meta,
)
from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    QubitHamiltonianFragmentSolverExact,
    QubitHamiltonianFragmentSolverVQE,
    VQEFragmentSolverStub,
)
from qchem_stack.chem.energy_components import build_energy_components_v1
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    molecular_hamiltonian_from_canonical_active_space_pack,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.precomputed_bundle import qubit_hamiltonian_from_bundle, resolve_bundle_path
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import (
    ExperimentConfig,
    backend_spec_from_config,
    compiler_bundle_signature_from_config,
    compiler_pass_bundle_from_config,
    dump_experiment_config,
    load_experiment_config,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.integrations.dmet_self_consistent import OneShotEmbeddingDriver
from qchem_stack.jobs.nexus_analog import nexus_analog_ledger_from_rows
from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext
from qchem_stack.protocols.product_contract import classify_pauli_expectation_path
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

_pipeline_log = logging.getLogger(__name__)


@dataclass(slots=True)
class _ScfStageArtifacts:
    cfg: ExperimentConfig
    rhf: ClassicalMeanFieldReference
    precomputed_mode: bool
    solver_caps: Any
    energy_components: dict[str, Any]
    embedding_input_payload: dict[str, Any] | None
    classical_benchmarks: dict[str, Any] | None
    rdm_bundle_meta: dict[str, Any] | None
    rdm_correction_report: dict[str, Any] | None
    rdm_correction_readiness: dict[str, Any] | None


@dataclass(slots=True)
class _PreQuantumStageArtifacts:
    pre_quantum_input: PreQuantumInput
    schmidt_ctx: dict[str, Any] | None
    qh: QubitHamiltonian


def _package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("numpy", "scipy", "openfermion", "pandas"):
        try:
            mod = __import__(name)
            out[name] = str(getattr(mod, "__version__", "?"))
        except Exception:  # noqa: BLE001
            out[name] = "not_imported"
    try:
        import yaml as yaml_mod

        out["yaml"] = str(getattr(yaml_mod, "__version__", "?"))
    except Exception:  # noqa: BLE001
        out["yaml"] = "not_imported"
    try:
        import pyscf

        out["pyscf"] = str(getattr(pyscf, "__version__", "?"))
    except Exception:  # noqa: BLE001
        out["pyscf"] = "not_imported"
    return out


def _classical_software_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("pyscf", "psi4"):
        try:
            mod = __import__(name)
            out[name] = str(getattr(mod, "__version__", "?"))
        except Exception:  # noqa: BLE001
            out[name] = "not_imported"
    return out


def _repro_quantum_snapshot(cfg: ExperimentConfig, qh: QubitHamiltonian | None) -> dict[str, Any]:
    """Falsifiability / parity fields aligned with competitor Methods tables (public docs only)."""
    snap: dict[str, Any] = {
        "quantum_algorithm": cfg.quantum.algorithm,
        **(
            {"quantum_algorithm_factory": cfg.quantum.algorithm_factory}
            if cfg.quantum.algorithm_factory
            else {}
        ),
        "use_pauli_protocol": cfg.quantum.use_pauli_protocol,
        "vqe_depth": cfg.quantum.vqe_depth,
        "vqe_maxiter": cfg.quantum.vqe_maxiter,
        "adapt_max_iter": cfg.quantum.adapt_max_iter,
        "iqeb_max_rounds": cfg.quantum.iqeb_max_rounds,
        "fermion_qubit_mapping": cfg.active_space.fermion_qubit_mapping,
        "variational_ansatz": cfg.quantum.variational_ansatz,
        **(
            {"uccsd_trotter_steps": cfg.quantum.uccsd_trotter_steps}
            if cfg.quantum.variational_ansatz == "uccsd"
            else {}
        ),
        "run_sampled_pauli_protocol": cfg.quantum.run_sampled_pauli_protocol,
        "run_qiskit_shots_pauli_protocol": cfg.quantum.run_qiskit_shots_pauli_protocol,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(cfg.quantum),
        "record_pauli_measurement_histograms": cfg.quantum.record_pauli_measurement_histograms,
        "pauli_grouping": cfg.quantum.pauli_grouping,
        "shots_per_circuit": cfg.backend.shots_per_circuit,
        "target_energy_stderr": cfg.backend.target_energy_stderr,
        "backend_provider": cfg.backend.provider,
        "pmsv_enabled": cfg.mitigation.pmsv_enabled,
        "zne_enabled": cfg.mitigation.zne_enabled,
        "spam_calibration_enabled": cfg.mitigation.spam_calibration_enabled,
        "classical_shadows_stub_enabled": cfg.mitigation.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs": int(cfg.mitigation.classical_shadows_budget_pairs),
        "mitigation_execution_class": cfg.mitigation.execution_class,
        "mitigation_zne_scales": [float(x) for x in cfg.mitigation.zne_scales],
        **({"mitigation_zne_mode": cfg.mitigation.zne_mode} if cfg.mitigation.zne_enabled else {}),
        "compiler_native_twoq": cfg.compiler.native_twoq,
        "compiler_optimization_level": cfg.compiler.optimization_level,
        "compiler_preoptimize_passes": list(cfg.compiler.preoptimize_passes),
        "compiler_passes_yaml": list(cfg.compiler.compiler_passes),
        "compiler_bundle_signature": compiler_bundle_signature_from_config(cfg),
        "pauli_support_max_terms": cfg.quantum.pauli_support_max_terms,
        "vqd_overlap_exponent_yaml": float(cfg.quantum.vqd_overlap_exponent),
        "vqd_cobyla_maxiter_yaml": int(cfg.quantum.vqd_cobyla_maxiter),
        "vqd_after_variational": cfg.quantum.vqd_after_variational,
        "vqd_n_states": cfg.quantum.vqd_n_states,
        "vqd_penalty_weight": cfg.quantum.vqd_penalty_weight,
        "vqd_penalty_weights": cfg.quantum.vqd_penalty_weights,
        "vqd_optimizer_method_yaml": cfg.quantum.vqd_optimizer_method,
        "vqd_init_strategy_yaml": cfg.quantum.vqd_init_strategy,
        "vqd_init_noise_scale_yaml": float(cfg.quantum.vqd_init_noise_scale),
        "vqd_max_overlap_warn_yaml": cfg.quantum.vqd_max_overlap_warn,
        "vqd_overlap_mode_yaml": cfg.quantum.vqd_overlap_mode,
        "vqd_shots_objective": cfg.quantum.vqd_shots_objective,
        "vqd_shots_overlap": cfg.quantum.vqd_shots_overlap,
        "vqd_shots_weight": cfg.quantum.vqd_shots_weight,
        "qse_after_variational": cfg.quantum.qse_after_variational,
        "qse_subspace_dim": cfg.quantum.qse_subspace_dim,
        "qse_max_basis": cfg.quantum.qse_max_basis,
        "qse_shot_mode": cfg.quantum.qse_shot_mode,
        "qse_shots_per_matrix_element": cfg.quantum.qse_shots_per_matrix_element,
        "qse_shots_per_ij_term": cfg.quantum.qse_shots_per_ij_term,
        "sceom_after_variational": cfg.quantum.sceom_after_variational,
        "sceom_subspace_dim": cfg.quantum.sceom_subspace_dim,
        "sceom_shots_per_matrix_element": cfg.quantum.sceom_shots_per_matrix_element,
        "sceom_generator_strategy_yaml": cfg.quantum.sceom_generator_strategy,
        "vqs_track_after_variational": cfg.quantum.vqs_track_after_variational,
        "vqs_pipeline_integration": cfg.quantum.vqs_pipeline_integration,
        "vqs_mode": cfg.quantum.vqs_mode,
        "vqs_n_times": cfg.quantum.vqs_n_times,
        "vqs_dt": float(cfg.quantum.vqs_dt),
        "vqs_rhs_mode_yaml": cfg.quantum.vqs_rhs_mode,
        "vqs_tangent_fd_epsilon_yaml": float(cfg.quantum.vqs_tangent_fd_epsilon),
        "qpe_demo_track_after_variational_yaml": cfg.quantum.qpe_demo_track_after_variational,
        "qpe_pipeline_integration_yaml": cfg.quantum.qpe_pipeline_integration,
        "qpe_demo_track_n_bits_yaml": int(cfg.quantum.qpe_demo_track_n_bits),
        "qpe_three_pack_after_variational_yaml": cfg.quantum.qpe_three_pack_after_variational,
        "qpe_three_pack_time_yaml": float(cfg.quantum.qpe_three_pack_time),
    }
    if qh is not None and qh.meta:
        snap["hamiltonian_meta"] = dict(qh.meta)
    emb = cfg.embedding
    snap["embedding_mode"] = emb.mode
    if emb.n_scf_cycles_embedding is not None:
        snap["n_scf_cycles_embedding"] = emb.n_scf_cycles_embedding
    if emb.classical_reference_method:
        snap["classical_reference_method"] = emb.classical_reference_method
    if emb.fragment_labels:
        snap["embedding_fragment_labels"] = list(emb.fragment_labels)
    if emb.dmet_hamiltonian_source == "schmidt_atomic_production":
        snap["schmidt_dmet_max_cycles"] = int(emb.schmidt_dmet_max_cycles)
        snap["schmidt_dmet_mixing_alpha"] = float(emb.schmidt_dmet_mixing_alpha)
        if emb.schmidt_multi_fragment_atom_groups:
            snap["schmidt_multifragment"] = True
            snap["schmidt_multifragment_n"] = len(emb.schmidt_multi_fragment_atom_groups)
    snap["chemistry_extended"] = cfg.chemistry_extended.model_dump(mode="json")
    snap["nexus_analog"] = cfg.nexus_analog.model_dump(mode="json")
    snap["nexus_cloud"] = cfg.nexus_cloud.model_dump(mode="json")
    snap["tensornet_expectation_stub"] = bool(cfg.quantum.tensornet_expectation_stub)
    snap["tensornet_contraction_engine"] = cfg.quantum.tensornet_contraction_engine
    _append_open_stack_parity_fields(snap, cfg)
    return snap


def _append_open_stack_parity_fields(snap: dict[str, Any], cfg: ExperimentConfig) -> None:
    """Designed **open-stack** parity block (public-contract L1; see ``ParityIntegrationsSpec``)."""
    pis = cfg.parity_integrations
    snap["parity_integrations"] = pis.model_dump(mode="json")
    if not pis.enabled:
        return

    from qchem_stack.integrations.tket_fullchain import describe_tket_closure_layer

    snap["open_stack_contract_schema"] = "parity_open_stack_contract_v1"
    snap["open_stack_design_intent"] = (
        "Engineered open paths where vendor code is closed: keep the same workflow *stages* and "
        "auditable artifacts described in public InQuanto docs. Implementations use peer-reviewed "
        "building blocks or explicit user hooks (DMET bath updates, UCC regrouping, TN topology)."
    )
    snap["tket_closure_layer_descriptor"] = describe_tket_closure_layer()

    if pis.qnexus_probe:
        from qchem_stack.integrations.nexus_optional import probe_qnexus_installation

        snap["qnexus_probe"] = probe_qnexus_installation()
    if pis.open_qermit_reference:
        from qchem_stack.integrations.qermit_reference import qermit_capability_matrix

        snap["open_qermit_capability_matrix"] = qermit_capability_matrix()
    if pis.tensornet_closure_reference:
        from qchem_stack.integrations.tensornet_closure import tensornet_closure_strategy

        snap["tensornet_closure_reference"] = tensornet_closure_strategy()
    if pis.uccsd_excitation_reference:
        from qchem_stack.integrations.ucc_reference import count_uccsd_excitations

        n_so = 2 * int(cfg.active_space.n_active_orbitals)
        ne = int(cfg.active_space.n_active_electrons)
        snap["uccsd_reference_closed_shell"] = {
            "n_spin_orbitals": n_so,
            "n_electrons_spin": ne,
            "excitation_counts": count_uccsd_excitations(n_so, ne),
            "module": "qchem_stack.integrations.ucc_reference",
            "caveat": "Spatial active space → spin orbitals assumes closed-shell counting; "
            "open-shell or symmetry blocking needs an explicit user mapping.",
        }

    if cfg.embedding.mode == "dmet":
        snap["dmet_open_loop_architecture"] = {
            "schema": "dmet_open_architecture_v1",
            "self_consistency_loop_class": (
                "qchem_stack.integrations.dmet_self_consistent.DMETSelfConsistencyLoop"
            ),
            "one_shot_driver_class": (
                "qchem_stack.integrations.dmet_self_consistent.OneShotEmbeddingDriver"
            ),
            "fragment_solver_hook": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
            "scf_cycles_yaml": cfg.embedding.n_scf_cycles_embedding,
            "fragment_labels": list(cfg.embedding.fragment_labels),
            "dmet_hamiltonian_source": cfg.embedding.dmet_hamiltonian_source,
            "classical_reference_method": cfg.embedding.classical_reference_method,
            "workflow_note": (
                "Commercial stacks embed bath construction + global correlation updates; "
                "this repository implements the **orchestration contract** and records stub or "
                "``whole_active_system`` impurity VQE (see ``EmbeddingSpec.dmet_hamiltonian_source``). "
                "Plug bath-aware ``build_fragment_hamiltonian`` + DMETSelfConsistencyLoop for full DMET."
            ),
        }

    if cfg.embedding.mode == "projection":
        emb = cfg.embedding
        trace: dict[str, Any] = {
            "schema": "projection_embedding_open_trace_v1",
            "low_level": emb.projection_low_level,
            "high_level": emb.projection_high_level,
            "threshold": float(emb.projection_threshold),
            "projection_quantum_hamiltonian": emb.projection_quantum_hamiltonian,
            "module": "qchem_stack.chem.embedding.projection",
        }
        if emb.projection_quantum_hamiltonian == "fragment_mulliken_mo":
            trace["projection_hamiltonian_source"] = "fragment_mulliken_mo_v1"
            trace["projection_module"] = "qchem_stack.chem.embedding.projection_hamiltonian"
            trace["fermion_qubit_mapping"] = cfg.active_space.fermion_qubit_mapping
            trace["caveat"] = (
                "Variational Hamiltonian is built from RHF MOs, Mulliken-ranked fragment orbitals, "
                f"PySCF CASCI active integrals, and fermion→qubit mapping "
                f"``{cfg.active_space.fermion_qubit_mapping}`` (see projection_hamiltonian)."
            )
            trace["epistemic_bound"] = (
                "Not full many-body projection embedding of the environment; not bit-wise parity "
                "with closed vendor PySCF projection drivers."
            )
        else:
            trace["projection_hamiltonian_source"] = "global_active_space"
            trace["fermion_qubit_mapping"] = cfg.active_space.fermion_qubit_mapping
            trace["caveat"] = (
                "Variational stage uses the global :class:`ActiveSpaceSpec` qubit Hamiltonian "
                f"(mapping ``{cfg.active_space.fermion_qubit_mapping}``; same as ``embedding.mode: none`` "
                "for the qubit operator). This block records projection workflow metadata only."
            )
            trace["epistemic_bound"] = (
                "Open-stack L1 trace — not numerical parity with proprietary projection stacks."
            )
        snap["projection_embedding_open_trace"] = trace

    if pis.gap_closure_reference_bundle:
        from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference

        snap["open_gap_closure_reference"] = build_open_gap_closure_reference(cfg)


def _schmidt_per_fragment_vqe_parity_summary(spfv: dict[str, Any]) -> dict[str, Any]:
    """Compact, JSON-serializable digest for ``repro.parity_snapshot`` (audit / Methods tables)."""
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
        "schema": "schmidt_per_fragment_vqe_parity_summary_v1",
        "n_fragments": len(rows),
        "total_nfev": nfev_total,
        "vqe_depth": spfv.get("vqe_depth"),
        "vqe_maxiter_per_fragment": spfv.get("vqe_maxiter_per_fragment"),
        "fragments": rows,
    }


def _finalize_open_stack_parity_snapshot(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    proto: PauliAveragingProtocol | None,
) -> None:
    """Runtime fields: TKET stats on first compiled ``CircuitIR``, DMET stub ledger."""
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
            compiled = getattr(proto, "_compiled", None) or []
            if compiled:
                from qchem_stack.integrations.tket_fullchain import circuit_ir_to_tket_stats_or_none

                snap["tket_first_compiled_circuit_probe"] = circuit_ir_to_tket_stats_or_none(
                    compiled[0]
                )
            else:
                snap["tket_first_compiled_circuit_probe"] = {
                    "schema": "tket_stats_skipped_v1",
                    "reason": "no_compiled_circuits_after_compile",
                }
        else:
            snap["tket_first_compiled_circuit_probe"] = {
                "schema": "tket_stats_skipped_v1",
                "reason": "pauli_protocol_disabled_no_circuit_ir",
            }

    if pis.dmet_stub_one_shot_ledger and cfg.embedding.mode == "dmet":
        if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
            snap["dmet_solver_mode"] = "schmidt_atomic_production"
            hm = snap.get("hamiltonian_meta")
            if isinstance(hm, dict) and isinstance(hm.get("schmidt_production_audit"), dict):
                snap["schmidt_embedding_production"] = hm["schmidt_production_audit"]
        elif out.get("dmet_fragment_solve"):
            snap["dmet_one_shot_open_ledger"] = out["dmet_fragment_solve"]
            snap["dmet_solver_mode"] = cfg.embedding.dmet_hamiltonian_source
        elif out.get("dmet_fragment_solve_error"):
            snap["dmet_fragment_solve_error"] = out["dmet_fragment_solve_error"]
            snap["dmet_solver_mode"] = cfg.embedding.dmet_hamiltonian_source
        else:
            labels = list(cfg.embedding.fragment_labels) or ["fragment_0"]
            ctx = DMETContext(
                fragments=labels, solver=VQEFragmentSolverStub(depth=cfg.quantum.vqe_depth)
            )
            hams = {
                fid: {
                    "open_stack_placeholder": True,
                    "n_active_electrons": cfg.active_space.n_active_electrons,
                    "n_active_orbitals": cfg.active_space.n_active_orbitals,
                }
                for fid in labels
            }
            snap["dmet_one_shot_open_ledger"] = OneShotEmbeddingDriver.run(ctx, hams)
            snap["dmet_solver_mode"] = "parity_stub"

    spfv = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv, dict) and spfv.get("schema") == "schmidt_per_fragment_vqe_v1":
        snap["schmidt_per_fragment_vqe_summary"] = _schmidt_per_fragment_vqe_parity_summary(spfv)

    if out.get("dmet_uniform_multifragment_toy"):
        snap["dmet_uniform_multifragment_toy"] = out["dmet_uniform_multifragment_toy"]

    tnstub = out.get("tensornet_protocol_stub")
    if isinstance(tnstub, dict) and str(tnstub.get("schema")) == "cutensornet_protocol_stub_v1":
        eng = tnstub.get("engine_resolved") or tnstub.get("requested_backend")
        snap["tensornet_engine_resolved"] = str(eng if eng is not None else "stub")
        st = tnstub.get("status")
        snap["tensornet_fallback_reason"] = (
            str(st) if st is not None else "cutensornet_stub_no_status"
        )
    elif pis.enabled:
        snap["tensornet_engine_resolved"] = str(cfg.quantum.tensornet_contraction_engine)
        if cfg.quantum.tensornet_expectation_stub:
            snap["tensornet_fallback_reason"] = "tensornet_stub_not_emitted_pipeline_branch"
        else:
            snap["tensornet_fallback_reason"] = "tensornet_expectation_stub_disabled"

    vm = out.get("vqe_meta")
    if isinstance(vm, dict) and vm.get("uccsd_n_parameters") is not None:
        snap["uccsd_n_parameters"] = int(vm["uccsd_n_parameters"])
    if isinstance(vm, dict) and vm.get("uccsd_trotter_steps") is not None:
        snap["uccsd_trotter_steps"] = int(vm["uccsd_trotter_steps"])

    pc_fold = out.get("protocol_counts")
    if cfg.mitigation.zne_enabled and cfg.quantum.run_qiskit_shots_pauli_protocol:
        zm = cfg.mitigation.zne_mode
        proto_mode = pc_fold.get("zne_mode") if isinstance(pc_fold, dict) else None
        fb = pc_fold.get("zne_circuit_fold_fallback_reason") if isinstance(pc_fold, dict) else None
        snap["zne_qiskit_unification_v1"] = {
            "schema": "zne_qiskit_unification_v1",
            "mitigation_zne_mode_yaml": zm,
            "protocol_counts_zne_mode": proto_mode,
            "circuit_fold_fallback_reason": fb,
            "epistemic_bound": (
                "Open stack: circuit_scale_fold amplifies HEA depth only on the exact Pauli executor path; "
                "Qiskit shot counts use scalar_stub energy scaling in protocol_counts (see fallback_reason)."
            ),
        }


def _run_dmet_fragment_solve_if_requested(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    exe: Any,
    out: dict[str, Any],
) -> None:
    """Optional impurity VQE on global active Hamiltonian (single-fragment DMET *shape* demo)."""
    if cfg.embedding.mode != "dmet":
        return
    if cfg.embedding.dmet_hamiltonian_source != "whole_active_system":
        return
    emb = cfg.embedding
    labels = [x for x in emb.fragment_labels if str(x).strip()]
    mf_shared = emb.dmet_multifragment_one_shot_shared_hamiltonian
    if mf_shared:
        if len(labels) < 2:
            out["dmet_fragment_solve_error"] = (
                "expected at least two fragment labels for multifragment shared demo"
            )
            return
    elif len(labels) != 1:
        out["dmet_fragment_solve_error"] = "expected one fragment label (validator should catch)"
        return
    if emb.dmet_fragment_use_exact_solver:
        solver: Any = QubitHamiltonianFragmentSolverExact(
            max_qubits=int(emb.dmet_fragment_exact_max_qubits)
        )
    else:
        solver = QubitHamiltonianFragmentSolverVQE(
            depth=cfg.quantum.vqe_depth,
            maxiter=cfg.quantum.vqe_maxiter,
            executor=exe,
            random_seed=cfg.random_seed,
        )
    bath_n = (
        int(emb.schmidt_n_bath_spatial)
        if emb.dmet_hamiltonian_source == "schmidt_atomic_production"
        else None
    )
    ctx = DMETContext(
        fragments=labels,
        solver=solver,
        n_scf_cycles_embedding=emb.n_scf_cycles_embedding,
        classical_reference_method=emb.classical_reference_method,
        bath_spatial_orbitals=bath_n,
    )
    frag_hams = {fid: qh for fid in labels} if mf_shared else {labels[0]: qh}
    ledger = OneShotEmbeddingDriver.run(ctx, frag_hams)
    ledger["hamiltonian_source"] = "whole_active_system"
    ledger["multifragment_shared_global_hamiltonian"] = bool(mf_shared)
    out["dmet_fragment_solve"] = ledger


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    """Hashes and versions for job / publication reproducibility."""
    from qchem_stack.integrations.workflow_preview import (
        workflow_preview_payload,
        workflow_preview_qpe_track_slice_v1,
        workflow_preview_variational_execution_slice_v1,
        workflow_preview_vqs_track_slice_v1,
    )

    raw_yaml = dump_experiment_config(cfg)
    h = hashlib.sha256(raw_yaml.encode("utf-8")).hexdigest()[:16]
    classical_versions = _classical_software_versions()
    repro: dict[str, Any] = {
        "experiment_id": cfg.experiment_id,
        "random_seed": cfg.random_seed,
        "config_sha256_prefix": h,
        "config_path": str(cfg_path) if cfg_path else None,
        "python": sys.version.split()[0],
        "packages": _package_versions(),
        "classical_software_versions": classical_versions,
        # Backward-compatibility alias; kept while downstream tables migrate.
        "pyscf_version": classical_versions.get("pyscf", "not_imported"),
        "embedding_config": cfg.embedding.model_dump(mode="json"),
        "chemistry_extended_config": cfg.chemistry_extended.model_dump(mode="json"),
        "nexus_analog_config": cfg.nexus_analog.model_dump(mode="json"),
        "nexus_cloud_config": cfg.nexus_cloud.model_dump(mode="json"),
        "parity_snapshot": _repro_quantum_snapshot(cfg, qh),
        # Same blob as ``POST /v1/meta/workflow-preview`` (YAML-only); P1 alignment with API preview.
        "workflow_preview_v1": workflow_preview_payload(
            cfg,
            include_computables_rich=cfg.parity_integrations.include_computables_rich_in_repro,
        ),
    }
    ve_slice = workflow_preview_variational_execution_slice_v1(cfg)
    if ve_slice is not None:
        repro["workflow_preview_variational_execution_v1"] = ve_slice
    vqs_slice = workflow_preview_vqs_track_slice_v1(cfg)
    if vqs_slice is not None:
        repro["workflow_preview_vqs_track_v1"] = vqs_slice
    qpe_slice = workflow_preview_qpe_track_slice_v1(cfg)
    if qpe_slice is not None:
        repro["workflow_preview_qpe_track_v1"] = qpe_slice
    return repro


def _run_scf(cfg: ExperimentConfig) -> ClassicalMeanFieldReference:
    from qchem_stack.chem.bridges import (
        classical_mean_field_via_solver_bridge,
        molecular_system_from_experiment,
    )

    if cfg.active_space.strategy == "manual":
        frz = list(cfg.active_space.frozen_orbitals)
        recipe = (
            "manual:"
            f"n_active_orbitals={cfg.active_space.n_active_orbitals},"
            f"n_active_electrons={cfg.active_space.n_active_electrons},"
            f"frozen_orbitals={frz}"
        )
    elif cfg.active_space.strategy == "avas_stub":
        recipe = (
            "avas_stub:"
            f"ncas={cfg.active_space.ncas},nelecas={cfg.active_space.nelecas}:partial_open_stack_no_avas_projection"
        )
    elif cfg.active_space.strategy == "avas":
        recipe = (
            "avas:"
            f"ao_labels={cfg.chemistry_extended.avas_ao_labels}:"
            f"threshold={cfg.chemistry_extended.avas_threshold}:pyscf_mcscf_avas"
        )
    else:
        recipe = f"cas:ncas={cfg.active_space.ncas},nelecas={cfg.active_space.nelecas}"
    mf_pack = classical_mean_field_via_solver_bridge(cfg)
    rhf = ClassicalMeanFieldReference.from_mean_field_pack(
        mf_pack,
        molecular_system=molecular_system_from_experiment(cfg),
    )
    apply_active_space_strategy_to_mean_field_meta(
        rhf.driver_meta,
        strategy=cfg.active_space.strategy,
        recipe=recipe,
        avas_ao_labels=cfg.chemistry_extended.avas_ao_labels,
    )
    if cfg.active_space.frozen_orbitals:
        rhf.driver_meta["active_space_frozen_orbitals"] = list(cfg.active_space.frozen_orbitals)
    return rhf


def _require_pyscf_reference(
    rhf: ClassicalMeanFieldReference,
    *,
    context: str,
) -> Any:
    """Return a PySCF mean-field object **only** for stages that are still PySCF-plugin-specific.

    Orchestration is **backend-agnostic** once data live in :class:`ClassicalMeanFieldReference`;
    this helper marks the narrow band where we still need raw PySCF ``mf`` (AO export, Schmidt
    production, some embedding bridges). Prefer :func:`_solver_capabilities` + capability gates
    for anything that another ``ChemIntegralSolver`` could plausibly implement.
    """
    tag = rhf.backend_tag()
    if tag != "pyscf":
        raise PipelineError(
            f"{context} currently requires PySCF-style mean-field handle (got backend={tag!r}). "
            "Use embedding.mode=plugin for backend-agnostic Hamiltonian ingestion, "
            "or implement the corresponding backend-specific bridge."
        )
    return rhf.as_pyscf_rhf_result()


def _solver_capabilities(cfg: ExperimentConfig) -> Any:
    return create_solver(cfg).capabilities


def _is_precomputed_driver(cfg: ExperimentConfig) -> bool:
    return str(cfg.scf.driver).strip().lower() == "precomputed"


def _normalize_precomputed_bundle_path(
    cfg: ExperimentConfig, *, cfg_path: Path | None
) -> ExperimentConfig:
    if not _is_precomputed_driver(cfg):
        return cfg
    raw = str(cfg.scf.precomputed_bundle_path or "").strip()
    if not raw:
        return cfg
    resolved = resolve_bundle_path(raw, cfg_path=cfg_path)
    return cfg.model_copy(
        update={"scf": cfg.scf.model_copy(update={"precomputed_bundle_path": str(resolved)})}
    )


def _precomputed_pre_quantum_input(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference, *, cfg_path: Path | None
) -> PreQuantumInput:
    raw = str(cfg.scf.precomputed_bundle_path or "").strip()
    if not raw:
        raise PipelineError(
            "scf.driver='precomputed' requires scf.precomputed_bundle_path to load pre-quantum input."
        )
    qh = qubit_hamiltonian_from_bundle(raw, cfg_path=cfg_path)
    return PreQuantumInput(
        classical_reference=rhf,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=None,
        meta={"source": "precomputed_bundle"},
    )


def _run_scf_stage(
    cfg: ExperimentConfig,
    *,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> _ScfStageArtifacts:
    precomputed_mode = _is_precomputed_driver(cfg)
    solver_caps = _solver_capabilities(cfg)
    rhf = _run_scf(cfg)
    if not precomputed_mode:
        cfg = _refine_mean_field_for_active_space(cfg, rhf)
    nuclear_au: float | None
    try:
        nuclear_au = float(rhf.mf.mol.energy_nuc())
    except Exception:
        nuclear_au = None
    solvent_eps = (
        float(cfg.chemistry_extended.ddcosmo_epsilon)
        if cfg.chemistry_extended.solvent_model == "ddcosmo"
        else None
    )
    energy_components = build_energy_components_v1(
        nuclear_repulsion_au=nuclear_au,
        mean_field_total_au=float(rhf.e_tot),
        solvent_model=str(cfg.chemistry_extended.solvent_model),
        solvent_dielectric=solvent_eps,
        energy_accounting_model=str(
            rhf.driver_meta.get("energy_accounting_model", "mf_e_tot_direct")
        ),
    )
    classical_benchmarks: dict[str, Any] | None = None
    rdm_bundle_meta: dict[str, Any] | None = None
    rdm_correction_report: dict[str, Any] | None = None
    rdm_correction_readiness: dict[str, Any] | None = None
    embedding_input_payload = _embedding_input_system_payload(cfg, rhf)
    if precomputed_mode and cfg.chemistry_extended.classical_benchmark_enabled:
        raise PipelineError(
            "classical_benchmark_enabled is unsupported with scf.driver='precomputed' "
            "(no runtime post-HF backend attached)."
        )
    if cfg.chemistry_extended.classical_benchmark_enabled:
        from qchem_stack.chem.classical_benchmarks import (
            ClassicalBenchmarkContext,
            run_classical_post_hf_benchmarks,
        )

        classical_benchmarks = run_classical_post_hf_benchmarks(
            cfg,
            ClassicalBenchmarkContext(
                mean_field_reference=rhf,
                reference_scf_method=str(cfg.scf.method),
                n_active_orbitals=int(cfg.active_space.n_active_orbitals),
                n_active_electrons=int(cfg.active_space.n_active_electrons),
            ),
        )
    if precomputed_mode and cfg.chemistry_extended.rdm_correction_method != "none":
        raise PipelineError(
            "rdm_correction_method requires live backend hooks and is unsupported with "
            "scf.driver='precomputed'."
        )
    if cfg.chemistry_extended.rdm_correction_method != "none":
        from qchem_stack.integrations.rdm_corrections import (
            build_rdm_correction_readiness,
            rdm_bundle_from_mean_field,
            run_pyscf_nevpt2_casci_correction,
            run_rdm_correction,
        )

        if not solver_caps.supports_rdm_correction_hooks:
            raise PipelineError(
                "rdm_correction_method requires backend RDM extraction support "
                f"(backend={solver_caps.backend_id!r})."
            )
        rdmb = rdm_bundle_from_mean_field(rhf)
        rdm_bundle_meta = dict(rdmb.metadata)
        rdm_m = cfg.chemistry_extended.rdm_correction_method
        if rdm_m in ("stub_nevpt2", "stub_ac0"):
            rdm_correction_report = run_rdm_correction(rdm_m, rdmb)
        elif rdm_m == "pyscf_nevpt2_casci":
            if not solver_caps.supports_rdm_nevpt2_casci:
                raise PipelineError(
                    "rdm_correction_method='pyscf_nevpt2_casci' requires backend support "
                    f"(backend={solver_caps.backend_id!r})."
                )
            rdm_correction_report = run_pyscf_nevpt2_casci_correction(
                rhf,
                int(cfg.active_space.n_active_orbitals),
                int(cfg.active_space.n_active_electrons),
            )
        else:
            raise ValueError(f"Unsupported rdm_correction_method: {rdm_m!r}")
        rdm_correction_readiness = build_rdm_correction_readiness(
            requested_method=rdm_m,
            correction_report=rdm_correction_report,
            bundle_meta=rdm_bundle_meta,
        )
    profile.mark("scf_done")
    emit("scf_done")
    _pipeline_log.info(
        "pipeline scf_done experiment_id=%s E_tot_au=%.10f",
        cfg.experiment_id,
        float(rhf.e_tot),
    )
    return _ScfStageArtifacts(
        cfg=cfg,
        rhf=rhf,
        precomputed_mode=precomputed_mode,
        solver_caps=solver_caps,
        energy_components=energy_components,
        embedding_input_payload=embedding_input_payload,
        classical_benchmarks=classical_benchmarks,
        rdm_bundle_meta=rdm_bundle_meta,
        rdm_correction_report=rdm_correction_report,
        rdm_correction_readiness=rdm_correction_readiness,
    )


def _build_pre_quantum_stage(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    precomputed_mode: bool,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> _PreQuantumStageArtifacts:
    if precomputed_mode:
        pre_q_input = _precomputed_pre_quantum_input(cfg, rhf, cfg_path=cfg_path)
        schmidt_ctx = None
    else:
        pre_q_input, schmidt_ctx = _hamiltonian_with_schmidt_context(cfg, rhf, cfg_path=cfg_path)
    qh = pre_q_input.qubit_hamiltonian
    profile.mark("hamiltonian_built")
    emit("hamiltonian_built")
    _pipeline_log.info(
        "pipeline hamiltonian_ready experiment_id=%s n_qubits=%s integral_source=%s",
        cfg.experiment_id,
        qh.n_qubits,
        (qh.meta or {}).get("integral_source"),
    )
    return _PreQuantumStageArtifacts(pre_quantum_input=pre_q_input, schmidt_ctx=schmidt_ctx, qh=qh)


def _refine_mean_field_for_active_space(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> ExperimentConfig:
    """AVAS projection (optional) + shared CASSCF kernel (audit/orbital feed)."""
    from qchem_stack.chem.active_space.mo_coeff_transform_hooks import apply_mo_coeff_transform_hook
    from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
        apply_pyscf_avas_to_reference,
        casscf_energy_and_maybe_orbitals,
        patch_experiment_active_space_resolution,
    )

    caps = _solver_capabilities(cfg)
    if cfg.active_space.strategy == "avas":
        if not caps.supports_avas_active_space_projection:
            raise PipelineError(
                "active_space.strategy='avas' requires AVAS capability on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        # PySCF plugin boundary: AVAS projection requires backend-native orbital projection hooks.
        apply_pyscf_avas_to_reference(cfg, rhf)
        cfg = patch_experiment_active_space_resolution(cfg, rhf)

    audit = bool(cfg.chemistry_extended.casscf_orbital_optimization_audit)
    feed = bool(cfg.chemistry_extended.casscf_orbital_optimization_for_integrals)
    if audit or feed:
        if not caps.supports_casscf_orbital_audit:
            raise PipelineError(
                "casscf_orbital_* flags require PySCF-style CASSCF support on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
            raise PipelineError("CASSCF orbital hooks are unsupported on the PBC branch.")
        if cfg.scf.method != "RHF":
            raise PipelineError("casscf_orbital_* hooks require scf.method=RHF.")
        casscf_energy_and_maybe_orbitals(
            cfg,
            rhf,
            update_integrals_orbitals=feed,
            record_audit=audit,
        )

    apply_mo_coeff_transform_hook(cfg, rhf)

    return cfg


def _embedding_input_system_payload(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> dict[str, Any] | None:
    rep = cfg.embedding.embedding_input_representation
    if rep == "mo":
        return None
    caps = _solver_capabilities(cfg)
    if not caps.supports_embedding_input_ao_lowdin:
        raise PipelineError(
            "embedding_input_representation=ao/lowdin_orth_ao requires backend capability "
            f"'supports_embedding_input_ao_lowdin'; backend {caps.backend_id!r} lacks this capability."
        )
    if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
        raise PipelineError(
            "embedding_input_representation=ao/lowdin_orth_ao is currently molecular-only (non-PBC)."
        )
    solver = create_solver(cfg)
    try:
        return solver.build_embedding_input_system(rhf, representation=rep)
    except NotImplementedError as exc:
        raise PipelineError(
            "embedding_input_representation export is not implemented for the selected backend "
            f"{solver.capabilities.backend_id!r}."
        ) from exc


def _schmidt_hamiltonian_and_context(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> tuple[QubitHamiltonian, dict[str, Any]]:
    """Build primary Schmidt impurity ``QubitHamiltonian`` and a small context for per-fragment VQE."""
    caps = _solver_capabilities(cfg)
    if not caps.supports_schmidt_atomic_hamiltonian:
        raise PipelineError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires backend support "
            f"(backend={caps.backend_id!r})."
        )
    # TODO(capability): replace this PySCF-handle assertion with backend-neutral Schmidt adapter contracts.
    _require_pyscf_reference(rhf, context="schmidt_atomic_production")
    if cfg.scf.method != "RHF":
        raise PipelineError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires scf.method='RHF' "
            "(closed-shell single density matrix)."
        )
    from qchem_stack.chem.embedding.schmidt_production import (
        apply_chemical_potential_fragment_block,
        bisection_mu_for_fragment_electron_count,
        fci_fragment_ground_state,
        fragment_mulliken_electrons,
    )
    from qchem_stack.integrations.schmidt_dmet_self_consistent import (
        run_schmidt_density_feedback_cycles,
        run_schmidt_multifragment_density_cycles,
    )

    emb = cfg.embedding
    groups = emb.schmidt_multi_fragment_atom_groups
    if groups:
        labs = [x for x in emb.fragment_labels if str(x).strip()]
        model, dmet_loop_report, d_embed = run_schmidt_multifragment_density_cycles(
            rhf,
            fragment_atom_groups=[list(g) for g in groups],
            fragment_labels=labs if len(labs) == len(groups) else None,
            primary_fragment_index=int(emb.schmidt_multi_primary_fragment_index),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            max_cycles=int(emb.schmidt_dmet_max_cycles),
            mixing_alpha=float(emb.schmidt_dmet_mixing_alpha),
            convergence_tol=float(emb.schmidt_dmet_convergence_tol),
        )
        multifrag_audit: dict[str, Any] = {
            "schmidt_multifragment": True,
            "n_embedding_fragments": len(groups),
            "primary_fragment_index": int(emb.schmidt_multi_primary_fragment_index),
        }
        resolved_labels = list(dmet_loop_report.get("fragment_labels_used", []))
        schmidt_ctx: dict[str, Any] = {
            "D_embed": d_embed,
            "fragment_groups": [list(g) for g in groups],
            "fragment_labels": resolved_labels,
        }
    else:
        model, dmet_loop_report, d_embed = run_schmidt_density_feedback_cycles(
            rhf,
            fragment_atom_indices=list(emb.schmidt_fragment_atom_indices),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            max_cycles=int(emb.schmidt_dmet_max_cycles),
            mixing_alpha=float(emb.schmidt_dmet_mixing_alpha),
            convergence_tol=float(emb.schmidt_dmet_convergence_tol),
        )
        multifrag_audit = {}
        schmidt_ctx = {
            "D_embed": d_embed,
            "fragment_groups": None,
            "fragment_labels": list(emb.fragment_labels) if emb.fragment_labels else ["fragment_0"],
        }

    mf = rhf.mf
    s = np.asarray(mf.get_ovlp(), dtype=float)
    frag_ao = list(model.meta.get("fragment_ao_indices", []))
    mulliken_frag = fragment_mulliken_electrons(d_embed, s, frag_ao)

    mu = 0.0
    mu_report: dict[str, Any] | None = None
    if emb.schmidt_run_mu_bisection and emb.dmet_target_fragment_electrons is not None:
        mu, mu_report = bisection_mu_for_fragment_electron_count(
            model,
            target_fragment_electrons=float(emb.dmet_target_fragment_electrons),
        )

    h1_use = apply_chemical_potential_fragment_block(
        model.h1, mu=mu, n_fragment_spatial_orbitals=model.n_fragment_spatial_orbitals
    )
    ne = model.n_alpha_electrons + model.n_beta_electrons

    fci_ref: dict[str, Any] | None = None
    if mu_report is not None:
        if mu_report.get("status") == "converged" and isinstance(mu_report.get("fci_at_mu"), dict):
            fci_ref = mu_report["fci_at_mu"]  # type: ignore[assignment]
        elif mu_report.get("status") == "no_bracket" and isinstance(
            mu_report.get("fci_mu_zero"), dict
        ):
            fci_ref = mu_report["fci_mu_zero"]  # type: ignore[assignment]
    elif emb.schmidt_attach_fci_reference and model.n_spatial_orbitals <= int(
        emb.schmidt_fci_reference_max_spatial_orbitals
    ):
        fci_ref = fci_fragment_ground_state(model, mu=mu)

    audit: dict[str, Any] = {
        "schema": "schmidt_production_pipeline_v1",
        "impurity_model": dict(model.meta),
        "schmidt_dmet_self_consistency": dmet_loop_report,
        "mulliken_fragment_after_embedding_density": mulliken_frag,
        "mu_on_fragment_diagonal_au": float(mu),
        "mu_bisection_report": mu_report,
        "fci_impurity_reference": fci_ref,
        "impurity_n_spatial_orbitals": model.n_spatial_orbitals,
        "impurity_n_electrons": int(ne),
        "active_space_yaml_ignored_for_qh": True,
        "note": (
            "Main variational stage uses impurity qubit Hamiltonian "
            f"({cfg.active_space.fermion_qubit_mapping}); cfg.active_space sizes apply to "
            "ledger/stub fields only on this path."
        ),
        **multifrag_audit,
    }
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        model.constant,
        h1_use,
        model.h2,
        ne,
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
        integral_source="schmidt_impurity_spatial",
        meta_extra={"schmidt_production_audit": audit},
        pyscf_driver_meta=dict(rhf.driver_meta) if getattr(rhf, "driver_meta", None) else None,
    )
    return qh, schmidt_ctx


def _run_schmidt_per_fragment_vqe(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    schmidt_ctx: dict[str, Any],
    exe: Any,
) -> dict[str, Any] | None:
    """Independent VQE on each fragment impurity (post embedding density)."""
    groups = schmidt_ctx.get("fragment_groups")
    if not groups or len(groups) < 2:
        return None
    labels = schmidt_ctx.get("fragment_labels") or []
    if len(labels) != len(groups):
        return None
    if not cfg.embedding.schmidt_run_vqe_on_all_fragments:
        return None
    d = np.asarray(schmidt_ctx["D_embed"], dtype=float)
    emb = cfg.embedding
    from qchem_stack.chem.embedding.schmidt_production import build_schmidt_impurity_integrals

    mx = emb.schmidt_per_fragment_vqe_maxiter
    if mx is None:
        mx = cfg.quantum.vqe_maxiter
    rows: list[dict[str, Any]] = []
    # TODO(capability): support non-PySCF mean-field handles for per-fragment Schmidt VQE.
    _require_pyscf_reference(rhf, context="schmidt_run_vqe_on_all_fragments")
    for i, atoms in enumerate(groups):
        model = build_schmidt_impurity_integrals(
            rhf,
            fragment_atom_indices=list(atoms),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            density_ao=d,
        )
        ne = model.n_alpha_electrons + model.n_beta_electrons
        qh_i = qubit_hamiltonian_from_spatial_chemist_integrals(
            model.constant,
            model.h1,
            model.h2,
            ne,
            fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
            integral_source="schmidt_impurity_spatial_fragment",
            meta_extra={"fragment_id": labels[i]},
        )
        vr = VQE(qh_i, depth=cfg.quantum.vqe_depth, executor=exe).run(
            maxiter=int(mx),
            seed=int(cfg.random_seed) + i * 31,
        )
        rows.append(
            {
                "fragment_id": labels[i],
                "atom_indices": list(atoms),
                "energy": float(vr.energy),
                "nfev": int(vr.nfev),
                "n_qubits": int(qh_i.n_qubits),
            }
        )
    return {
        "schema": "schmidt_per_fragment_vqe_v1",
        "vqe_depth": cfg.quantum.vqe_depth,
        "vqe_maxiter_per_fragment": int(mx),
        "fragments": rows,
    }


def _hamiltonian_with_schmidt_context(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    if cfg.embedding.mode == "plugin":
        from qchem_stack.chem.embedding.decomposition_plugin import (
            qubit_hamiltonian_from_decomposition_plugin,
        )

        qh = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)
        qh_meta = dict(getattr(qh, "meta", {}) or {})
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={
                    "source": "embedding_plugin",
                    "integral_source": qh_meta.get("integral_source"),
                },
            ),
            None,
        )
    sol = create_solver(cfg)
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        qh, ctx = _schmidt_hamiltonian_and_context(cfg, rhf)
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={"source": "schmidt_atomic_production"},
            ),
            ctx,
        )
    if (
        cfg.embedding.mode == "projection"
        and cfg.embedding.projection_quantum_hamiltonian == "fragment_mulliken_mo"
    ):
        if not sol.capabilities.supports_projection_fragment_mulliken_hamiltonian:
            raise PipelineError(
                "projection.fragment_mulliken_mo requires backend support "
                f"(backend={sol.capabilities.backend_id!r})."
            )
        from qchem_stack.chem.embedding.projection_hamiltonian import (
            molecular_hamiltonian_fragment_mulliken_projection,
        )

        qh, _audit = molecular_hamiltonian_fragment_mulliken_projection(rhf, cfg)
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={"source": "projection_fragment_mulliken_mo"},
            ),
            None,
        )
    if not sol.capabilities.supports_restricted_active_space_qubit_hamiltonian:
        raise PipelineError(
            "This pipeline stage builds a qubit Hamiltonian from restricted active-space MO integrals; "
            f"the selected backend {sol.capabilities.backend_id!r} does not provide "
            "a canonical active-space integral pack yet."
        )
    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        rhf,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    qh = molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=cfg.active_space.prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=cfg.active_space.jordan_wigner_coeff_atol,
        classical_reference_for_meta=rhf,
    )
    return (
        PreQuantumInput(
            classical_reference=rhf,
            qubit_hamiltonian=qh,
            canonical_active_space_integral_pack=pack,
            meta={"source": "canonical_active_space_integral_pack"},
        ),
        None,
    )


def _hamiltonian(cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference) -> QubitHamiltonian:
    pre_q, _ = _hamiltonian_with_schmidt_context(cfg, rhf)
    return pre_q.qubit_hamiltonian


def _excited_protocol_contract_v1_block() -> dict[str, Any]:
    """Stable documentation slice for parity / Methods (shot semantics mirror YAML + implementation)."""

    return {
        "schema": "excited_protocol_contract_v1",
        "vqd_three_protocol": (
            "`objective`: deflation energy channel (exact statevector expectation or grouped Pauli when "
            "`vqd_shots_objective`>0). `overlap`: swap-test overlaps between solved levels when "
            "`vqd_shots_overlap`>0. `weight`: reserved coupling to overlap shot budget."
        ),
        "qse_shot_modes": {
            "exact": (
                "Dense Hamiltonian projected into QSE basis built from HEA single-reference determinants/"
                "excitations."
            ),
            "gaussian_h": (
                "`qse_shots_per_matrix_element` injects symmetric Gaussian noise on real parts of dense "
                "matrix elements — placeholder shot model vs device POVM."
            ),
            "pauli_transitions": (
                "Per-(i,j) transition channel built from Pauli transition strings; budgets via "
                "`qse_shots_per_ij_term` × schedule task count (`qse_total_shots_upper_bound`)."
            ),
        },
        "sceom_shot_semantics": (
            "When `sceom_shots_per_matrix_element`>0, apply symmetric Gaussian noise to real diagonal/"
            "off-diagonal entries of the nested-commutator matrix before GHEP (open-stack SCEOM prototype)."
        ),
    }


def build_excited_resource_summary_for_export(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """VQD / QSE / SCEOM shot book-keeping from YAML only (for ``export_parity_criteria_table`` without a run)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational:
        er["qse"] = {
            "shot_mode": q.qse_shot_mode,
            "qse_shots_per_matrix_element_yaml": q.qse_shots_per_matrix_element,
            "qse_shots_per_ij_term_yaml": q.qse_shots_per_ij_term,
        }
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = _excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = _excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = _excited_protocol_contract_v1_block()
    return er


def _build_excited_resource_summary(
    cfg: ExperimentConfig,
    out: dict[str, Any],
) -> dict[str, Any] | None:
    """YAML + run meta for Methods-style shot/task accounting (VQD / QSE / SCEOM stages)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational and "qse" in out:
        meta = out["qse"].get("meta") or {}
        block: dict[str, Any] = {"shot_mode": q.qse_shot_mode, "K": meta.get("K")}
        sched = meta.get("qse_pauli_transition_schedule")
        if isinstance(sched, dict):
            block["n_transition_tasks"] = sched.get("n_transition_tasks")
            block["total_shots_upper_bound"] = sched.get("total_shots_upper_bound")
            block["n_pauli_terms_in_schedule"] = sched.get("n_pauli_terms")
        if q.qse_shot_mode == "gaussian_h":
            k = meta.get("K")
            if isinstance(k, int) and k > 0:
                block["h_matrix_elements"] = k * k
                block["gaussian_h_shots_budget_reference"] = k * k * q.qse_shots_per_matrix_element
        if q.qse_shot_mode == "pauli_transitions":
            block["shots_per_ij_term_yaml"] = q.qse_shots_per_ij_term
        er["qse"] = {k2: v for k2, v in block.items() if v is not None}
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = _excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = _excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = _excited_protocol_contract_v1_block()
    return er


def _vqd_channel_upper(v: dict[str, Any]) -> int:
    n = 0
    pairs = int(v.get("swap_test_pair_count_if_shots") or 0)
    sov = int(v.get("shots_overlap_per_pair") or 0)
    n += pairs * sov
    levels = int(v.get("deflated_cobyla_levels") or 0)
    obj = int(v.get("shots_objective_per_reporting_level") or 0)
    n += levels * obj
    sw = int(v.get("shots_weight_channel") or 0)
    if sw > 0 and sov > 0:
        n += levels * sw
    return n


def _qse_channel_upper(qs: dict[str, Any]) -> int:
    tub = qs.get("total_shots_upper_bound")
    if isinstance(tub, (int, float)) and tub > 0:
        return int(tub)
    gref = qs.get("gaussian_h_shots_budget_reference")
    if isinstance(gref, (int, float)) and gref > 0:
        return int(gref)
    nt = qs.get("n_transition_tasks")
    sp = qs.get("shots_per_ij_term_yaml")
    if (
        isinstance(nt, (int, float))
        and isinstance(sp, (int, float))
        and int(nt) > 0
        and int(sp) > 0
    ):
        return int(nt) * int(sp)
    return 0


def _sceom_channel_upper(sc: dict[str, Any]) -> int:
    m = int(sc.get("m_matrix_elements") or 0)
    sp = int(sc.get("shots_per_matrix_element_yaml") or 0)
    if m > 0 and sp > 0:
        return m * sp
    return 0


def _excited_shot_channel_upper_bounds(excited: dict[str, Any]) -> dict[str, int]:
    """Per-channel upper bounds (VQD / QSE / SCEOM) for Methods one-table accounting."""
    out: dict[str, int] = {"vqd": 0, "qse": 0, "sceom": 0, "combined": 0}
    v = excited.get("vqd")
    if isinstance(v, dict):
        out["vqd"] = _vqd_channel_upper(v)
    qs = excited.get("qse")
    if isinstance(qs, dict):
        out["qse"] = _qse_channel_upper(qs)
    sc = excited.get("sceom")
    if isinstance(sc, dict):
        out["sceom"] = _sceom_channel_upper(sc)
    out["combined"] = int(out["vqd"] + out["qse"] + out["sceom"])
    return out


def _excited_shots_upper_bound(excited: dict[str, Any]) -> int:
    """Conservative additive upper bound on shot-like budgets declared for excited stages (YAML + QSE schedule)."""
    b = _excited_shot_channel_upper_bounds(excited)
    return int(b["combined"])


def _excited_methods_unified(excited_rs: dict[str, Any]) -> dict[str, Any]:
    """Single export shape for VQD / QSE / SCEOM (Methods one-block)."""
    return {
        "schema_version": "1",
        "vqd": excited_rs.get("vqd"),
        "qse": excited_rs.get("qse"),
        "sceom": excited_rs.get("sceom"),
        "shot_channel_upper_bounds": excited_rs.get("shot_channel_upper_bounds"),
    }


def _attach_nexus_mitigation_tn(
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
    if cfg.quantum.tensornet_expectation_stub:
        from qchem_stack.tensornet import run_cutensornet_expectation_stub

        out["tensornet_protocol_stub"] = run_cutensornet_expectation_stub(
            qh.n_qubits, requested_backend=cfg.quantum.tensornet_contraction_engine
        )


def _attach_qpe_demo_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional dense QPE + Bayesian toy, same as ``scripts/run_qpe_track_demo.py`` (NISQ + FT narrative)."""
    if not cfg.quantum.qpe_demo_track_requested():
        return
    from qchem_stack.qpe_qec_demo.pipeline_track import qpe_demo_track_payload

    out["qpe_demo_track"] = qpe_demo_track_payload(qh, bits=int(cfg.quantum.qpe_demo_track_n_bits))


def _attach_vqs_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional VQS / McLachlan dynamics on variational parameters (YAML ``vqs_rhs_mode`` for McLachlan modes)."""
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
        mode=q.vqs_mode,
        n_times=q.vqs_n_times,
        dt=float(q.vqs_dt),
        rhs_mode_yaml=q.vqs_rhs_mode,
        tangent_fd_epsilon_yaml=float(q.vqs_tangent_fd_epsilon),
    )


def _attach_qpe_three_algorithm_pack_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Dense QPE trio from :mod:`~qchem_stack.quantum.algorithms.qpe` (config ``qpe_three_pack_*``)."""
    if not cfg.quantum.qpe_three_pack_requested():
        return
    from qchem_stack.quantum.algorithms.qpe import (
        AlgorithmDeterministicQPE,
        AlgorithmInfoTheoryQPE,
        AlgorithmKitaevQPE,
    )

    qt = cfg.quantum
    t_ev = float(qt.qpe_three_pack_time)

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
        qh, time=t_ev, n_rounds=int(qt.qpe_three_pack_deterministic_rounds)
    )
    kit = AlgorithmKitaevQPE(qh, time=t_ev, n_bits=int(qt.qpe_three_pack_kitaev_bits))
    inf = AlgorithmInfoTheoryQPE(qh, time=t_ev, n_samples=int(qt.qpe_three_pack_info_samples))

    rd = det.build().run()
    rk = kit.build().run()
    ri = inf.build().run(seed=int(cfg.random_seed))

    out["qpe_algorithm_three_pack"] = {
        "schema": "qpe_algorithm_three_pack_v1",
        "time": float(t_ev),
        "yaml_note": (
            "Dense-spectrum emulation on the Hamiltonian Hilbert space; phase summaries are illustrative."
        ),
        "deterministic_qpe_report_v1": _row("deterministic_qpe", rd),
        "kitaev_qpe_report_v1": _row("kitaev_qpe", rk),
        "info_theory_qpe_report_v1": _row("info_theory_qpe", ri),
        "yaml_flags": {
            "qpe_three_pack_after_variational": bool(qt.qpe_three_pack_after_variational)
        },
        "implementations": {
            "deterministic": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
            "kitaev": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
            "info_theory": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
        },
    }


def _resource_summary_excited_only(n_qubits: int, excited_rs: dict[str, Any]) -> dict[str, Any]:
    ub = _excited_shots_upper_bound(excited_rs)
    rs: dict[str, Any] = {
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
    if isinstance(excited_rs.get("shot_channel_upper_bounds"), dict):
        rs["excited_shot_accounting"] = excited_rs["shot_channel_upper_bounds"]
    rs["excited_methods_unified"] = _excited_methods_unified(excited_rs)
    return rs


def _maybe_attach_md_ml_qmef_dataset(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> None:
    """Optional ``repro.qmef_ml_attachment_v1`` for MD→ML export (see :mod:`qchem_stack.md_bridge`)."""
    if not cfg.md_ml_export.attach_single_frame_to_repro:
        return
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    from qchem_stack.md_bridge.from_pipeline import build_qmef_ml_attachment_repro_block

    repro["qmef_ml_attachment_v1"] = build_qmef_ml_attachment_repro_block(
        cfg, out, reference, cfg_path=cfg_path
    )


def _apply_embedding_workflow_stage(
    cfg: ExperimentConfig,
    *,
    out: dict[str, Any],
    qh: QubitHamiltonian,
    exe: Any,
    embedding_input_payload: dict[str, Any] | None,
    schmidt_ctx: dict[str, Any] | None,
    rhf: ClassicalMeanFieldReference,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> None:
    if cfg.embedding.mode == "dmet":
        wf: dict[str, Any] = {
            "mode": "dmet",
            "fragment_count": len(cfg.embedding.fragment_labels),
            "fragment_labels": list(cfg.embedding.fragment_labels),
            "dmet_hamiltonian_source": cfg.embedding.dmet_hamiltonian_source,
            "fragment_solver_protocol": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
        }
        if cfg.embedding.dmet_hamiltonian_source == "whole_active_system":
            wf["impurity_solver_used"] = (
                "qchem_stack.chem.embedding.dmet.QubitHamiltonianFragmentSolverExact"
                if cfg.embedding.dmet_fragment_use_exact_solver
                else "qchem_stack.chem.embedding.dmet.QubitHamiltonianFragmentSolverVQE"
            )
            if cfg.embedding.dmet_multifragment_one_shot_shared_hamiltonian:
                wf["multifragment_one_shot_shared_hamiltonian"] = True
        elif cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
            wf["impurity_hamiltonian"] = "qchem_stack.chem.embedding.schmidt_production"
            wf["main_variational_target"] = "impurity_qubit_hamiltonian_jw"
            wf["schmidt_dmet_max_cycles"] = int(cfg.embedding.schmidt_dmet_max_cycles)
            if cfg.embedding.schmidt_multi_fragment_atom_groups:
                wf["schmidt_multifragment_atom_groups"] = [
                    list(g) for g in cfg.embedding.schmidt_multi_fragment_atom_groups
                ]
                wf["schmidt_multi_primary_fragment_index"] = int(
                    cfg.embedding.schmidt_multi_primary_fragment_index
                )
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.integrations.schmidt_dmet_self_consistent."
                    "run_schmidt_multifragment_density_cycles"
                )
            else:
                wf["schmidt_fragment_atom_indices"] = list(
                    cfg.embedding.schmidt_fragment_atom_indices
                )
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.integrations.schmidt_dmet_self_consistent.run_schmidt_density_feedback_cycles"
                )
        else:
            wf["solver_stub"] = "qchem_stack.chem.embedding.dmet.VQEFragmentSolverStub"
        bpath = (cfg.embedding.schmidt_bath_sidecar_json_path or "").strip()
        if bpath:
            if cfg.embedding.dmet_hamiltonian_source != "schmidt_atomic_production":
                raise PipelineError(
                    "embedding.schmidt_bath_sidecar_json_path requires "
                    "dmet_hamiltonian_source=='schmidt_atomic_production'"
                )
            side_path = Path(bpath)
            if not side_path.is_file() and cfg_path is not None:
                side_path = (cfg_path.parent / bpath).resolve()
            if not side_path.is_file():
                raise PipelineError(
                    f"schmidt_bath_sidecar_json_path not found: {bpath!r} (resolved {side_path})"
                )
            wf["schmidt_bath_sidecar_v1"] = json.loads(side_path.read_text(encoding="utf-8"))
        if cfg.embedding.oniom_layers_v1:
            wf["oniom_toy_v1"] = {
                "schema": "oniom_toy_v1",
                "layers": [dict(x) for x in cfg.embedding.oniom_layers_v1],
            }
        if embedding_input_payload is not None:
            wf["embedding_input_system"] = embedding_input_payload
        out["embedding_workflow"] = wf
        _run_dmet_fragment_solve_if_requested(cfg, qh, exe, out)
        if schmidt_ctx is not None:
            spfv = _run_schmidt_per_fragment_vqe(cfg, rhf, schmidt_ctx, exe)
            if spfv is not None:
                out["schmidt_per_fragment_vqe"] = spfv
                _pipeline_log.info(
                    "pipeline schmidt_per_fragment_vqe_done experiment_id=%s n_fragments=%s total_nfev=%s",
                    cfg.experiment_id,
                    len(spfv.get("fragments") or []),
                    sum(
                        int(f.get("nfev", 0))
                        for f in (spfv.get("fragments") or [])
                        if isinstance(f, dict)
                    ),
                )
        if cfg.embedding.dmet_uniform_multifragment_toy:
            labs_mc = [x for x in cfg.embedding.fragment_labels if str(x).strip()]
            if len(labs_mc) >= 2:
                from qchem_stack.integrations.dmet_multifragment_toy import (
                    run_uniform_hamiltonian_multifragment_toy,
                )

                out["dmet_uniform_multifragment_toy"] = run_uniform_hamiltonian_multifragment_toy(
                    cfg, labs_mc, qh, exe, max_cycles=1
                )
        profile.mark("embedding_dmet")
        emit("embedding_dmet")
        return
    if cfg.embedding.mode == "projection":
        emb = cfg.embedding
        wf: dict[str, Any] = {
            "mode": "projection",
            "schema": "projection_embedding_workflow_v1",
            "projection_low_level": emb.projection_low_level,
            "projection_high_level": emb.projection_high_level,
            "projection_threshold": float(emb.projection_threshold),
            "projection_quantum_hamiltonian": emb.projection_quantum_hamiltonian,
            "parity_module": "qchem_stack.chem.embedding.projection",
        }
        hm = out.get("hamiltonian_meta") or {}
        audit = hm.get("projection_mulliken_mo_audit_v1")
        if audit:
            wf["projection_selected_mo_indices"] = list(audit.get("selected_mo_indices") or [])
            wf["projection_mulliken_weights"] = list(audit.get("mulliken_weights") or [])
            wf["projection_integral_source"] = audit.get("integral_source")
        if emb.projection_quantum_hamiltonian == "fragment_mulliken_mo":
            wf["caveat"] = (
                "Main-line VQE uses fragment Mulliken-selected active integrals "
                "(qchem_stack.chem.embedding.projection_hamiltonian)."
            )
            wf["epistemic_bound"] = (
                "Fragment-local MO screening + CASCI active Hamiltonian — not full projection embedding."
            )
        else:
            wf["caveat"] = (
                "Quantum stage uses global active-space JW Hamiltonian; this branch records projection trace metadata."
            )
            wf["epistemic_bound"] = (
                "Open reproducibility — not closed-source projection driver parity."
            )
        if embedding_input_payload is not None:
            wf["embedding_input_system"] = embedding_input_payload
        out["embedding_workflow"] = wf
        profile.mark("embedding_projection")
        emit("embedding_projection")
        return
    if cfg.embedding.mode == "plugin":
        emb = cfg.embedding
        hm = out.get("hamiltonian_meta") or {}
        resolved_json = hm.get("decomposition_plugin_json")
        term_counts = hm.get("decomposition_fragment_pauli_term_counts")
        term_total = 0
        if isinstance(term_counts, dict):
            term_total = sum(int(v) for v in term_counts.values())
        out["embedding_workflow"] = {
            "schema": "embedding_workflow_v1",
            "mode": "plugin",
            "decomposition_plugin": emb.decomposition_plugin,
            "decomposition_plugin_json_path": emb.decomposition_plugin_json_path,
            "decomposition_plugin_json_resolved_path": resolved_json,
            "decomposition_primary_fragment_id": hm.get("decomposition_primary_fragment_id"),
            "decomposition_fragment_count": hm.get("decomposition_fragment_count"),
            "decomposition_fragment_ids": hm.get("decomposition_fragment_ids"),
            "decomposition_fragment_pauli_term_counts": term_counts,
            "decomposition_total_pauli_terms": term_total,
            "decomposition_plugin_schema": hm.get("decomposition_plugin_schema"),
            "decomposition_fragment_energy_terms_v1": hm.get(
                "decomposition_fragment_energy_terms_v1"
            ),
            "integral_source": hm.get("integral_source"),
            "epistemic_bound": (
                "Open decomposition-plugin contract v1 (optional per-fragment energy-term stubs) "
                "— not closed-source embedding/decomposition product parity."
                if hm.get("decomposition_plugin_schema") == "decomposition_plugin_contract_v1"
                else (
                    "Open plugin boundary (toy v1 JSON) — not closed decomposition product parity."
                )
            ),
            "note": "Toy decomposition-plugin Hamiltonian replaces molecular active-space build.",
        }
        if embedding_input_payload is not None:
            out["embedding_workflow"]["embedding_input_system"] = embedding_input_payload
        profile.mark("embedding_plugin")
        emit("embedding_plugin")
        return
    out["embedding_workflow"] = {
        "schema": "embedding_workflow_v1",
        "mode": "none",
        "note": "No DMET/projection embedding stage; variational Hamiltonian uses global active space.",
    }
    if embedding_input_payload is not None:
        out["embedding_workflow"]["embedding_input_system"] = embedding_input_payload
    profile.mark("embedding_none")
    emit("embedding_none")


def _run_excited_stages(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    exe: Any,
    angles: Any,
    energy_pre: float,
    out: dict[str, Any],
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any] | None:
    q = cfg.quantum
    ang = np.asarray(angles, dtype=float)
    if q.vqd_after_variational:
        prepare_state = None
        n_vp: int | None = None
        param_bounds: list[tuple[float, float]] | None = None
        if q.variational_ansatz == "uccsd":
            from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

            if q.uccsd_trotter_steps is not None:
                ucc = UCCSDTrotterVQE(
                    qh,
                    executor=exe,
                    n_trotter_steps=int(q.uccsd_trotter_steps),
                )
            else:
                ucc = UCCSDVQE(qh, executor=exe)
            prepare_state = ucc.prepare_state
            n_vp = int(ucc.n_params)
            param_bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * n_vp
        vqd = VQD(
            qh,
            n_states=q.vqd_n_states,
            depth=q.vqe_depth,
            penalty_weight=q.vqd_penalty_weight,
            penalty_weights=q.vqd_penalty_weights,
            overlap_exponent=q.vqd_overlap_exponent,
            cobyla_maxiter=q.vqd_cobyla_maxiter,
            optimizer_method=q.vqd_optimizer_method,
            prepare_state=prepare_state,
            n_var_parameters=n_vp,
            parameter_bounds=param_bounds,
            init_strategy=q.vqd_init_strategy,
            init_noise_scale=q.vqd_init_noise_scale,
            max_overlap_warn=q.vqd_max_overlap_warn,
            overlap_mode=q.vqd_overlap_mode,
            executor=exe,
        )
        vqd_res = vqd.run(
            seed=cfg.random_seed,
            shots_objective=q.vqd_shots_objective,
            shots_overlap=q.vqd_shots_overlap,
            shots_weight=q.vqd_shots_weight,
            pauli_grouping=q.pauli_grouping,
            ground_angles=ang,
            ground_energy=float(energy_pre),
        )
        out["vqd"] = {
            "schema": "excited_vqd_bundle_v1",
            "energies": vqd_res.energies,
            "meta": vqd_res.meta,
        }
    if q.qse_after_variational:
        qse = QSE(qh, subspace_dim=q.qse_subspace_dim)
        kb = q.qse_max_basis
        if q.qse_shot_mode == "exact":
            qse_res = qse.run_from_vqe_hea_basis(ang, q.vqe_depth, max_basis=kb)
        elif q.qse_shot_mode == "gaussian_h":
            qse_res = qse.run_from_vqe_hea_basis_shot_noise(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_matrix_element=q.qse_shots_per_matrix_element,
                seed=cfg.random_seed,
            )
        else:
            qse_res = qse.run_from_vqe_hea_basis_pauli_transitions(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_ij_term=q.qse_shots_per_ij_term,
                seed=cfg.random_seed,
            )
        qse_meta = dict(qse_res.meta)
        qse_meta["qse_shot_mode"] = q.qse_shot_mode
        out["qse"] = {
            "schema": "excited_qse_bundle_v1",
            "excitation_energies": qse_res.excitation_energies,
            "meta": qse_meta,
        }
    if q.sceom_after_variational:
        from qchem_stack.quantum.algorithms.sceom import (
            resolve_sceom_s_generators,
            run_sceom_nested_commutator_from_hea,
        )

        sceom_kw: dict[str, Any] = {}
        gens, _ = resolve_sceom_s_generators(
            strategy=q.sceom_generator_strategy,
            hamiltonian=qh,
            subspace_dim=q.sceom_subspace_dim,
        )
        if gens is not None:
            sceom_kw["s_generators"] = gens
        sceom_kw["generator_strategy_yaml"] = q.sceom_generator_strategy
        sceom_res = run_sceom_nested_commutator_from_hea(
            qh,
            ang,
            q.vqe_depth,
            subspace_dim=q.sceom_subspace_dim,
            shots_per_matrix_element=q.sceom_shots_per_matrix_element,
            seed=cfg.random_seed,
            **sceom_kw,
        )
        out["sceom"] = {
            "schema": "excited_sceom_bundle_v1",
            "energies": sceom_res.energies,
            "meta": sceom_res.meta,
        }
    excited_rs = _build_excited_resource_summary(cfg, out)
    if excited_rs is not None:
        out["excited_resource_summary"] = excited_rs
    profile.mark("excited_stages")
    emit("excited_stages")
    return excited_rs


def _run_protocol_and_finalize_stage(
    cfg: ExperimentConfig,
    *,
    out: dict[str, Any],
    qh: QubitHamiltonian,
    angles: Any,
    excited_rs: dict[str, Any] | None,
    bspec: Any,
    exe: Any,
    bundle: Any,
    rhf: ClassicalMeanFieldReference,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any]:
    q = cfg.quantum
    profile.mark("pre_pauli_protocol")
    emit("pre_pauli_protocol")
    if not q.use_pauli_protocol:
        if excited_rs is not None:
            out["resource_summary"] = _resource_summary_excited_only(qh.n_qubits, excited_rs)
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
        _attach_nexus_mitigation_tn(out, cfg, qh)
        _attach_qpe_demo_track_if_requested(out, cfg, qh)
        _attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
        _attach_vqs_track_if_requested(out, cfg, qh)
        _finalize_open_stack_parity_snapshot(out, cfg, None)
        _maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
        profile.mark("pauli_protocol_skipped")
        emit("pauli_protocol_skipped")
        profile.mark("finalize_repro")
        emit("finalize_repro")
        out["repro"]["pipeline_profile"] = profile.to_profile_dict()
        _attach_run_summary(out, cfg)
        return out
    proto = _protocol_for_job(cfg, qh, bspec=bspec, exe=exe, bundle=bundle)
    proto.build(np.asarray(angles, dtype=float), hea_depth=q.vqe_depth)
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
        ub = _excited_shots_upper_bound(excited_rs)
        resource_summary["excited_shots_upper_bound"] = ub
        resource_summary["sum_shots_total_with_excited_upper_bound"] = int(df_sum["sum_shots"]) + ub
        if isinstance(excited_rs.get("shot_channel_upper_bounds"), dict):
            resource_summary["excited_shot_accounting"] = excited_rs["shot_channel_upper_bounds"]
        resource_summary["excited_methods_unified"] = _excited_methods_unified(excited_rs)
    out.update(
        {
            "energy_pauli_protocol": float(e_proto),
            "protocol_counts": proto._counts,
            "resource_rows": rows,
            "pauli_measurement_ledger": rows,
            "resource_summary": resource_summary,
        }
    )
    _attach_nexus_mitigation_tn(out, cfg, qh)
    _attach_qpe_demo_track_if_requested(out, cfg, qh)
    _attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
    _attach_vqs_track_if_requested(out, cfg, qh)
    _finalize_open_stack_parity_snapshot(out, cfg, proto)
    _maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
    profile.mark("pauli_protocol_done")
    emit("pauli_protocol_done")
    profile.mark("finalize_repro")
    emit("finalize_repro")
    out["repro"]["pipeline_profile"] = profile.to_profile_dict()
    _attach_run_summary(out, cfg)
    return out


def _classical_benchmark_summary(cb: dict[str, Any]) -> dict[str, Any]:
    """Compact Methods-friendly digest for ``classical_benchmarks``."""
    rows: dict[str, dict[str, Any]] = {}
    for method_key in ("hf", "mp2", "ccsd", "casci"):
        v = cb.get(method_key)
        if isinstance(v, dict):
            rows[method_key] = v
    ok_vals: dict[str, float] = {}
    for k, row in rows.items():
        if row.get("status") == "ok" and row.get("value") is not None:
            ok_vals[k] = float(row["value"])
    hf = ok_vals.get("hf")
    best_method: str | None = None
    best_energy: float | None = None
    if ok_vals:
        best_method = min(ok_vals, key=ok_vals.get)
        best_energy = float(ok_vals[best_method])
    deltas_vs_hf: dict[str, float] = {}
    if hf is not None:
        for k, v in ok_vals.items():
            if k == "hf":
                continue
            deltas_vs_hf[k] = float(v - hf)
    recommended_baseline_method: str | None = None
    for preferred in ("ccsd", "mp2", "hf"):
        if preferred in ok_vals:
            recommended_baseline_method = preferred
            break
    recommended_baseline_energy: float | None = (
        float(ok_vals[recommended_baseline_method])
        if recommended_baseline_method is not None
        else None
    )
    return {
        "schema": "classical_benchmark_summary_v1",
        "recommended_baseline_policy": "prefer_ccsd_else_mp2_else_hf",
        "recommended_baseline_method": recommended_baseline_method,
        "recommended_baseline_energy_au": recommended_baseline_energy,
        "methods_reported": sorted(rows.keys()),
        "methods_ok": sorted(ok_vals.keys()),
        "methods_non_ok": sorted(k for k in rows if k not in ok_vals),
        "reference_hf_energy_au": hf,
        "best_method": best_method,
        "best_energy_au": best_energy,
        "delta_best_vs_hf_au": (
            float(best_energy - hf) if (best_energy is not None and hf is not None) else None
        ),
        "method_deltas_vs_hf_au": deltas_vs_hf,
    }


def _attach_run_summary(out: dict[str, Any], cfg: ExperimentConfig) -> None:
    """Merge machine-readable stage list and resource hints into ``out['repro']`` (single JSON blob for Methods)."""
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    q = cfg.quantum
    stages: list[str] = ["scf"]
    if cfg.embedding.mode == "projection":
        stages.append("projection_embedding_trace")
    if cfg.embedding.mode == "plugin":
        stages.append("decomposition_plugin")
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        if int(cfg.embedding.schmidt_dmet_max_cycles) > 1:
            stages.append("schmidt_dmet_density_feedback")
        elif cfg.embedding.schmidt_multi_fragment_atom_groups:
            stages.append("schmidt_embedding_multifragment_sweep")
        else:
            stages.append("schmidt_embedding_single_shot")
    stages.append("variational")
    spfv_out = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_out, dict) and spfv_out.get("schema") == "schmidt_per_fragment_vqe_v1":
        stages.append("schmidt_per_fragment_vqe")
    if q.vqd_after_variational and "vqd" in out:
        stages.append("vqd")
    if q.qse_after_variational and "qse" in out:
        stages.append("qse")
    if q.sceom_after_variational and "sceom" in out:
        stages.append("sceom")
    if q.use_pauli_protocol and "energy_pauli_protocol" in out:
        stages.append("pauli_averaging_protocol")
    sm: dict[str, Any] = {
        "stages_completed": stages,
        "quantum_algorithm": q.algorithm,
        "quantum_algorithm_yaml": q.algorithm,
        "classical_backend_id": str(cfg.scf.driver),
        "variational_ansatz_yaml": q.variational_ansatz,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(q),
        "energy_after_variational": out.get("energy_after_variational"),
        "mitigation_zne_mode_yaml": cfg.mitigation.zne_mode,
        "mitigation_zne_scales_yaml": [float(x) for x in cfg.mitigation.zne_scales],
        "spam_calibration_enabled_yaml": cfg.mitigation.spam_calibration_enabled,
        "classical_shadows_stub_enabled_yaml": cfg.mitigation.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs_yaml": int(cfg.mitigation.classical_shadows_budget_pairs),
        "embedding_input_representation_yaml": cfg.embedding.embedding_input_representation,
        "classical_benchmark_backend_yaml": cfg.chemistry_extended.classical_benchmark_backend,
    }
    if q.algorithm_factory:
        sm["quantum_algorithm_factory_yaml"] = q.algorithm_factory
    eis = out.get("embedding_input_system")
    if isinstance(eis, dict) and eis.get("schema") is not None:
        sm["embedding_input_system_schema"] = eis["schema"]
    ec = out.get("energy_components")
    if isinstance(ec, dict):
        sm["energy_components_present"] = True
        if ec.get("schema") is not None:
            sm["energy_components_schema"] = ec["schema"]
        if ec.get("mean_field_total_au") is not None:
            sm["energy_components_mean_field_total_au"] = float(ec["mean_field_total_au"])
        if ec.get("nuclear_repulsion_au") is not None:
            sm["energy_components_nuclear_repulsion_au"] = float(ec["nuclear_repulsion_au"])
    vm_rs = out.get("vqe_meta")
    if isinstance(vm_rs, dict) and vm_rs.get("uccsd_n_parameters") is not None:
        sm["uccsd_n_parameters"] = int(vm_rs["uccsd_n_parameters"])
    emb = cfg.embedding
    if emb.mode == "dmet":
        sm["dmet_embedding_active"] = True
        sm["dmet_hamiltonian_source_yaml"] = emb.dmet_hamiltonian_source
        frag_labels = [x for x in (emb.fragment_labels or []) if str(x).strip()]
        sm["dmet_fragment_count"] = len(frag_labels)
        sm["dmet_uniform_multifragment_toy_yaml"] = bool(emb.dmet_uniform_multifragment_toy)
        sm["dmet_stub_one_shot_ledger_yaml"] = bool(
            cfg.parity_integrations.dmet_stub_one_shot_ledger
        )
    elif emb.mode == "plugin":
        sm["decomposition_plugin_yaml"] = emb.decomposition_plugin
        wf = out.get("embedding_workflow")
        if isinstance(wf, dict):
            if wf.get("decomposition_primary_fragment_id") is not None:
                sm["decomposition_primary_fragment_id"] = wf["decomposition_primary_fragment_id"]
            if wf.get("decomposition_fragment_count") is not None:
                sm["decomposition_fragment_count"] = int(wf["decomposition_fragment_count"])
            if wf.get("decomposition_total_pauli_terms") is not None:
                sm["decomposition_total_pauli_terms"] = int(wf["decomposition_total_pauli_terms"])
    dfs_ledger = out.get("dmet_fragment_solve")
    if isinstance(dfs_ledger, dict):
        sm["dmet_fragment_solve_present"] = True
        if dfs_ledger.get("schema") is not None:
            sm["dmet_fragment_solve_schema"] = dfs_ledger["schema"]
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        sm["schmidt_dmet_max_cycles_yaml"] = int(cfg.embedding.schmidt_dmet_max_cycles)
        hm = out.get("hamiltonian_meta")
        if isinstance(hm, dict):
            aud = hm.get("schmidt_production_audit")
            if isinstance(aud, dict):
                dmet = aud.get("schmidt_dmet_self_consistency")
                if isinstance(dmet, dict):
                    ce = dmet.get("cycles_executed")
                    if ce is None:
                        ce = dmet.get("outer_cycles_executed")
                    if ce is not None:
                        sm["schmidt_dmet_cycles_executed"] = int(ce)
                    if (
                        dmet.get("converged_early_on_gamma") is True
                        or dmet.get("converged_early_on_sweep_max_delta") is True
                    ):
                        sm["schmidt_dmet_converged_early"] = True
    spfv_rs = out.get("schmidt_per_fragment_vqe")
    if isinstance(spfv_rs, dict) and spfv_rs.get("schema") == "schmidt_per_fragment_vqe_v1":
        frags = [f for f in (spfv_rs.get("fragments") or []) if isinstance(f, dict)]
        sm["schmidt_per_fragment_vqe_n_fragments"] = len(frags)
        sm["schmidt_per_fragment_vqe_total_nfev"] = sum(int(f.get("nfev", 0)) for f in frags)
        energies = [float(f["energy"]) for f in frags if f.get("energy") is not None]
        if energies:
            sm["schmidt_per_fragment_vqe_min_energy_au"] = min(energies)
            sm["schmidt_per_fragment_vqe_max_energy_au"] = max(energies)
    if out.get("scf_energy") is not None:
        sm["scf_energy"] = out["scf_energy"]
    cb = out.get("classical_benchmarks")
    if isinstance(cb, dict):
        sm["classical_benchmarks_present"] = True
        if cb.get("schema") is not None:
            sm["classical_benchmarks_schema"] = cb["schema"]
        for method_key in ("hf", "mp2", "ccsd", "casci"):
            blk = cb.get(method_key)
            if isinstance(blk, dict):
                if blk.get("status") is not None:
                    sm[f"classical_bench_{method_key}_status"] = str(blk["status"])
                if blk.get("value") is not None:
                    sm[f"classical_bench_{method_key}_energy_au"] = float(blk["value"])
    cbs = out.get("classical_benchmark_summary")
    if isinstance(cbs, dict):
        sm["classical_benchmark_summary_present"] = True
        if cbs.get("schema") is not None:
            sm["classical_benchmark_summary_schema"] = cbs["schema"]
        if cbs.get("recommended_baseline_method") is not None:
            sm["classical_benchmark_recommended_baseline_method"] = cbs[
                "recommended_baseline_method"
            ]
        if cbs.get("recommended_baseline_energy_au") is not None:
            sm["classical_benchmark_recommended_baseline_energy_au"] = float(
                cbs["recommended_baseline_energy_au"]
            )
        if cbs.get("best_method") is not None:
            sm["classical_benchmark_best_method"] = cbs["best_method"]
        if cbs.get("best_energy_au") is not None:
            sm["classical_benchmark_best_energy_au"] = float(cbs["best_energy_au"])
        if cbs.get("delta_best_vs_hf_au") is not None:
            sm["classical_benchmark_delta_best_vs_hf_au"] = float(cbs["delta_best_vs_hf_au"])
    rcorr = out.get("rdm_correction")
    if isinstance(rcorr, dict):
        sm["rdm_correction_present"] = True
        if rcorr.get("schema") is not None:
            sm["rdm_correction_schema"] = rcorr["schema"]
        if rcorr.get("method") is not None:
            sm["rdm_correction_method"] = rcorr["method"]
        if rcorr.get("status") is not None:
            sm["rdm_correction_status"] = rcorr["status"]
        if rcorr.get("energy_correction_au") is not None:
            sm["rdm_correction_energy_au"] = float(rcorr["energy_correction_au"])
    rr_ready = out.get("rdm_correction_readiness")
    if isinstance(rr_ready, dict):
        sm["rdm_correction_readiness_present"] = True
        if rr_ready.get("schema") is not None:
            sm["rdm_correction_readiness_schema"] = rr_ready["schema"]
        if rr_ready.get("requested_method") is not None:
            sm["rdm_correction_readiness_requested_method"] = rr_ready["requested_method"]
        if rr_ready.get("rdm1_source") is not None:
            sm["rdm_correction_readiness_rdm1_source"] = rr_ready["rdm1_source"]
        if rr_ready.get("rdm_basis") is not None:
            sm["rdm_correction_readiness_rdm_basis"] = rr_ready["rdm_basis"]
        if rr_ready.get("spin_model") is not None:
            sm["rdm_correction_readiness_spin_model"] = rr_ready["spin_model"]
        if rr_ready.get("reference_wavefunction") is not None:
            sm["rdm_correction_readiness_reference_wavefunction"] = rr_ready[
                "reference_wavefunction"
            ]
        if rr_ready.get("kernel_class") is not None:
            sm["rdm_correction_readiness_kernel_class"] = rr_ready["kernel_class"]
        if rr_ready.get("nevpt2_pyscf_status") is not None:
            sm["rdm_correction_readiness_nevpt2_pyscf_status"] = rr_ready["nevpt2_pyscf_status"]
    if q.algorithm == "vqe":
        sm["vqe_maxiter_yaml"] = q.vqe_maxiter
        if "nfev" in out:
            sm["vqe_nfev"] = out["nfev"]
    elif q.algorithm in ("adapt", "tetris_adapt"):
        sm["adapt_pool_id_yaml"] = q.adapt_pool_id
        sm["adapt_max_iter_yaml"] = q.adapt_max_iter
        am = out.get("adapt_meta")
        if isinstance(am, dict) and "total_gradient_evals" in am:
            sm["adapt_total_gradient_evals"] = am["total_gradient_evals"]
        if isinstance(am, dict):
            steps = am.get("adapt_steps")
            if isinstance(steps, list):
                sm["adapt_steps_recorded"] = len(steps)
        pool = out.get("adapt_pool")
        if isinstance(pool, list):
            sm["adapt_excitation_layers"] = len(pool)
    elif q.algorithm == "iqeb":
        sm["iqeb_pool_id_yaml"] = q.iqeb_pool_id
        sm["iqeb_max_rounds_yaml"] = q.iqeb_max_rounds
        im = out.get("iqeb_meta")
        if isinstance(im, dict) and im.get("rounds") is not None:
            sm["iqeb_outer_rounds_recorded"] = int(im["rounds"])
        if out.get("iqeb_selected_pauli_strings") is not None:
            sm["iqeb_selected_pauli_count"] = len(out["iqeb_selected_pauli_strings"])
        if "nfev" in out:
            sm["iqeb_final_inner_vqe_nfev"] = out["nfev"]
        sm["iqeb_implementation_path"] = "qchem_stack.quantum.algorithms.iqeb.IQEBVQE"
    rs = out.get("resource_summary")
    if isinstance(rs, dict):
        if "sum_shots_total_with_excited_upper_bound" in rs:
            sm["sum_shots_total_with_excited_upper_bound"] = rs[
                "sum_shots_total_with_excited_upper_bound"
            ]
        if "excited_shots_upper_bound" in rs:
            sm["excited_shots_upper_bound"] = rs["excited_shots_upper_bound"]
        if "pauli_averaging_protocol_ran" in rs:
            sm["pauli_averaging_protocol_ran"] = rs["pauli_averaging_protocol_ran"]
        if "sum_shots" in rs:
            sm["sum_shots_backend_protocol"] = rs["sum_shots"]
        if rs.get("n_pauli_terms") is not None:
            sm["n_pauli_terms"] = rs["n_pauli_terms"]
        if rs.get("n_pauli_groups") is not None:
            sm["n_pauli_groups"] = rs["n_pauli_groups"]
        if rs.get("n_circuits") is not None:
            sm["n_circuits"] = rs["n_circuits"]
        if rs.get("n_qubits") is not None:
            sm["n_qubits"] = rs["n_qubits"]
    if out.get("energy_pauli_protocol") is not None:
        sm["energy_pauli_protocol"] = out["energy_pauli_protocol"]
    pc = out.get("protocol_counts")
    if isinstance(pc, dict):
        if pc.get("expectation_source"):
            sm["protocol_expectation_source"] = pc["expectation_source"]
        if pc.get("zne_mode") is not None:
            sm["protocol_zne_mode"] = pc["zne_mode"]
        if pc.get("energy_stderr_model"):
            sm["protocol_energy_stderr_model"] = pc["energy_stderr_model"]
        if pc.get("total_shots_budget") is not None:
            sm["protocol_total_shots_budget"] = pc["total_shots_budget"]
        if pc.get("n_measurement_circuits") is not None:
            sm["protocol_n_measurement_circuits"] = pc["n_measurement_circuits"]
        if pc.get("shots_per_circuit_effective") is not None:
            sm["protocol_shots_per_circuit_effective"] = pc["shots_per_circuit_effective"]
        if pc.get("energy_stderr") is not None:
            sm["protocol_energy_stderr"] = pc["energy_stderr"]
        if isinstance(pc.get("pmsv_report"), dict):
            sm["protocol_pmsv_report"] = pc["pmsv_report"]
    vqd = out.get("vqd")
    if isinstance(vqd, dict):
        sm["vqd_n_states_yaml"] = q.vqd_n_states
        sm["vqd_overlap_exponent_yaml"] = float(q.vqd_overlap_exponent)
        sm["vqd_cobyla_maxiter_yaml"] = int(q.vqd_cobyla_maxiter)
        en = vqd.get("energies")
        if isinstance(en, list):
            sm["vqd_n_energies_recorded"] = len(en)
            sm["vqd_deflation_levels_completed"] = max(0, len(en) - 1)
        vm = vqd.get("meta")
        if isinstance(vm, dict):
            if "reused_pipeline_ground" in vm:
                sm["vqd_reused_pipeline_ground"] = vm["reused_pipeline_ground"]
            ch = vm.get("vqd_channels")
            if isinstance(ch, list):
                sm["vqd_three_protocol_present"] = any(
                    isinstance(c, dict) and "three_protocol" in c for c in ch
                )
                sm["vqd_channels_count"] = len(ch)
            if vm.get("shots_objective") is not None:
                sm["vqd_shots_objective_yaml"] = vm["shots_objective"]
            if vm.get("shots_overlap") is not None:
                sm["vqd_shots_overlap_yaml"] = vm["shots_overlap"]
            if vm.get("shots_weight") is not None:
                sm["vqd_shots_weight_yaml"] = vm["shots_weight"]
            sm["vqd_optimizer_method_yaml"] = q.vqd_optimizer_method
            sm["vqd_init_strategy_yaml"] = q.vqd_init_strategy
            sm["vqd_overlap_mode_yaml"] = q.vqd_overlap_mode
            if vm.get("vqd_warnings"):
                sm["vqd_warnings_present"] = True
            if vm.get("vqd_variety_yaml"):
                sm["vqd_variety_yaml"] = vm["vqd_variety_yaml"]
    qse_out = out.get("qse")
    if isinstance(qse_out, dict):
        sm["qse_shot_mode"] = q.qse_shot_mode
        sm["qse_subspace_dim_yaml"] = q.qse_subspace_dim
        sm["qse_max_basis_yaml"] = q.qse_max_basis
        exc = qse_out.get("excitation_energies")
        if isinstance(exc, list):
            sm["qse_n_excitation_energies"] = len(exc)
        qmeta = qse_out.get("meta")
        if isinstance(qmeta, dict):
            if qmeta.get("shot_noise_model"):
                sm["qse_shot_noise_model"] = qmeta["shot_noise_model"]
            if qmeta.get("K") is not None:
                sm["qse_basis_dimension_K"] = qmeta["K"]
            sched = qmeta.get("qse_pauli_transition_schedule")
            if isinstance(sched, dict):
                if sched.get("n_transition_tasks") is not None:
                    sm["qse_n_transition_tasks"] = sched["n_transition_tasks"]
                if sched.get("total_shots_upper_bound") is not None:
                    sm["qse_total_shots_upper_bound"] = sched["total_shots_upper_bound"]
    sceom_out = out.get("sceom")
    if isinstance(sceom_out, dict):
        sm["sceom_shots_per_matrix_element"] = q.sceom_shots_per_matrix_element
        sm["sceom_subspace_dim_yaml"] = q.sceom_subspace_dim
        sm["sceom_generator_strategy_yaml"] = q.sceom_generator_strategy
        sce = sceom_out.get("energies")
        if isinstance(sce, list):
            sm["sceom_n_energies_recorded"] = len(sce)
        sceom_meta = sceom_out.get("meta")
        if isinstance(sceom_meta, dict):
            if sceom_meta.get("shot_noise_model") is not None:
                sm["sceom_shot_noise_model"] = sceom_meta["shot_noise_model"]
            if sceom_meta.get("subspace_dim") is not None:
                sm["sceom_active_generator_count"] = int(sceom_meta["subspace_dim"])
            if sceom_meta.get("construction") is not None:
                sm["sceom_matrix_construction"] = str(sceom_meta["construction"])
    job = out.get("job")
    if isinstance(job, dict):
        if job.get("job_id") is not None:
            sm["async_job_id"] = job["job_id"]
        if job.get("protocol_hash") is not None:
            sm["protocol_hash_prefix"] = job["protocol_hash"]
    jr = out.get("job_result")
    if isinstance(jr, dict):
        if jr.get("expectation") is not None:
            sm["job_async_expectation"] = jr["expectation"]
        if jr.get("energy_stderr") is not None:
            sm["job_async_energy_stderr"] = jr["energy_stderr"]
        if jr.get("total_shots_budget") is not None:
            sm["job_async_total_shots_budget"] = jr["total_shots_budget"]
    if isinstance(out.get("qpe_demo_track"), dict):
        sm["qpe_demo_track_ran"] = True
        sm["qpe_open_stack_contract_v1"] = {
            "schema": "qpe_open_stack_contract_v1",
            "demo_track_payload_schema": out["qpe_demo_track"].get("schema"),
            "kitaev_dense_energy_fn": (
                "qchem_stack.qpe_qec_demo.pipeline_track.kitaev_qpe_energy_estimate — dense phase readout shortcut"
            ),
            "algorithm_classes": {
                "kitaev": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
                "info_theory": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
                "deterministic": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
            },
            "bayesian_stub": "qchem_stack.qpe_qec_demo.BayesianQPEStub",
            "yaml_flags": {
                "qpe_demo_track_after_variational": q.qpe_demo_track_after_variational,
                "qpe_pipeline_integration": q.qpe_pipeline_integration,
            },
            "pipeline_attach": "_attach_qpe_demo_track_if_requested (orchestration/pipeline.py)",
        }
    if isinstance(out.get("qpe_algorithm_three_pack"), dict):
        qp3 = out["qpe_algorithm_three_pack"]
        sm["qpe_three_pack_ran"] = True
        sm["qpe_three_pack_deterministic_energy_est"] = (
            qp3.get("deterministic_qpe_report_v1") or {}
        ).get("energy_estimate")
        sm["qpe_three_pack_kitaev_energy_est"] = (qp3.get("kitaev_qpe_report_v1") or {}).get(
            "energy_estimate"
        )
        sm["qpe_three_pack_info_theory_energy_est"] = (
            qp3.get("info_theory_qpe_report_v1") or {}
        ).get("energy_estimate")
    if isinstance(out.get("vqs_track"), dict):
        sm["vqs_track_ran"] = True
        sm["vqs_open_stack_contract_v1"] = {
            "schema": "vqs_open_stack_contract_v1",
            "track_payload_schema": out["vqs_track"].get("schema"),
            "implementations": {
                "vqs": "qchem_stack.quantum.algorithms.vqs.AlgorithmVQS",
                "mclachlan_real_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanRealTime",
                "mclachlan_imag_time": "qchem_stack.quantum.algorithms.vqs.AlgorithmMcLachlanImagTime",
            },
            "pipeline_track_module": "qchem_stack.quantum.algorithms.vqs_pipeline_track",
            "yaml_flags": {
                "vqs_track_after_variational": q.vqs_track_after_variational,
                "vqs_pipeline_integration": q.vqs_pipeline_integration,
                "vqs_rhs_mode_yaml": q.vqs_rhs_mode,
                "vqs_tangent_fd_epsilon_yaml": float(q.vqs_tangent_fd_epsilon),
            },
            "vqs_mode_yaml": q.vqs_mode,
            "pipeline_attach": "_attach_vqs_track_if_requested (orchestration/pipeline.py)",
        }
    if isinstance(out.get("nexus_analog_ledger"), dict):
        sm["nexus_analog_hqc_units"] = out["nexus_analog_ledger"].get("hqc_units")
    if out.get("mitigation_graph_report"):
        sm["mitigation_graph_report_present"] = True
    if out.get("mitigation_dag_execution"):
        sm["mitigation_dag_execution_present"] = True
    if isinstance(out.get("nexus_cloud_repro"), dict):
        sm["nexus_cloud_repro"] = out["nexus_cloud_repro"]
    psnap = repro.get("parity_snapshot")
    if isinstance(psnap, dict):
        qnx = psnap.get("qnexus_probe")
        if isinstance(qnx, dict) and "available" in qnx:
            sm["qnexus_client_probe_available"] = qnx.get("available")
        if psnap.get("tket_first_compiled_circuit_probe"):
            tp = psnap.get("tket_first_compiled_circuit_probe")
            if isinstance(tp, dict) and tp.get("ok") is True:
                sm["tket_first_circuit_stats_ok"] = True
        if psnap.get("dmet_one_shot_open_ledger"):
            sm["dmet_one_shot_open_ledger_present"] = True
            led = psnap.get("dmet_one_shot_open_ledger")
            if (
                isinstance(led, dict)
                and isinstance(led.get("fragments"), list)
                and led["fragments"]
            ):
                fe = led["fragments"][0].get("energy")
                if fe is not None:
                    sm["dmet_fragment_solve_energy"] = fe
        if psnap.get("dmet_solver_mode"):
            sm["dmet_solver_mode"] = psnap["dmet_solver_mode"]
        if psnap.get("open_gap_closure_reference"):
            sm["open_gap_closure_reference_present"] = True
        if psnap.get("dmet_uniform_multifragment_toy"):
            sm["dmet_uniform_multifragment_toy_present"] = True
        if isinstance(psnap.get("schmidt_per_fragment_vqe_summary"), dict):
            sm["schmidt_per_fragment_vqe_in_parity_snapshot"] = True
    pp = repro.get("pipeline_profile")
    if isinstance(pp, dict) and pp.get("schema") == "pipeline_profile_v1":
        if pp.get("total_wall_ms") is not None:
            sm["pipeline_total_wall_ms"] = pp["total_wall_ms"]
        stages_prof = pp.get("stages") or []
        if stages_prof:
            slow = max(stages_prof, key=lambda x: float(x.get("duration_ms", 0.0)))
            sm["pipeline_slowest_stage"] = slow.get("stage")
            sm["pipeline_slowest_stage_ms"] = slow.get("duration_ms")
    rc = repro.get("run_context")
    if isinstance(rc, dict) and rc.get("trace_id"):
        sm["trace_id"] = rc["trace_id"]
    if isinstance(rc, dict) and rc.get("client_request_id"):
        sm["client_request_id"] = rc["client_request_id"]
    ew = out.get("embedding_workflow")
    if isinstance(ew, dict):
        repro["embedding_workflow"] = ew
    repro["run_summary"] = sm


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run chemistry + VQE/ADAPT + optional VQD/QSE/SCEOM + optional Pauli protocol in-process.

    On completion, ``out['repro']['run_summary']`` lists ``stages_completed`` and merges
    resource / protocol semantics for a single JSON reproducibility blob.

    If ``hamiltonian_out`` is an empty list, it is replaced in-place with ``[qh]`` so callers
    (e.g. :func:`run_pipeline_from_config`) can reuse the Hamiltonian without a second PySCF pass.

    ``job_timeline_emit``: optional sink for async job consoles (e.g. ``SqliteJobStore.append_timeline_event``);
    each payload includes ``kind`` (e.g. ``pipeline_stage``), ``stage`` (pipeline segment name), and ``status``.

    Logging: enable the ``qchem_stack.orchestration.pipeline`` logger at INFO for stage milestones
    (SCF, Hamiltonian build, variational energy, optional Schmidt per-fragment VQE) suitable for
    production job tracing.
    """
    cfg = _normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)
    q = cfg.quantum
    profile = PipelineStageTimer()

    def _emit(stage: str) -> None:
        if job_timeline_emit is not None:
            job_timeline_emit(
                {"kind": "pipeline_stage", "stage": stage, "status": "RUNNING"},
            )

    scf_stage = _run_scf_stage(
        cfg,
        profile=profile,
        emit=_emit,
    )
    cfg = scf_stage.cfg
    rhf = scf_stage.rhf
    pre_q_stage = _build_pre_quantum_stage(
        cfg,
        rhf,
        precomputed_mode=scf_stage.precomputed_mode,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )
    pre_q_input = pre_q_stage.pre_quantum_input
    schmidt_ctx = pre_q_stage.schmidt_ctx
    qh = pre_q_stage.qh
    energy_components = scf_stage.energy_components
    embedding_input_payload = scf_stage.embedding_input_payload
    classical_benchmarks = scf_stage.classical_benchmarks
    rdm_bundle_meta = scf_stage.rdm_bundle_meta
    rdm_correction_report = scf_stage.rdm_correction_report
    rdm_correction_readiness = scf_stage.rdm_correction_readiness
    if hamiltonian_out is not None:
        hamiltonian_out.clear()
        hamiltonian_out.append(qh)
    repro = collect_repro_metadata(cfg, cfg_path, qh)
    if run_context is not None:
        repro["run_context"] = run_context.to_repro_dict()
    bspec = backend_spec_from_config(cfg)
    exe = executor_from_spec(bspec)
    bundle = compiler_pass_bundle_from_config(cfg)

    vctx = VariationalRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=cfg.random_seed,
        pre_quantum_input=pre_q_input,
    )
    stage = run_variational_stage(vctx)
    algo_meta = stage.algo_meta_must_include_algorithm(cfg.quantum.algorithm)
    angles = stage.angles
    energy_pre = float(stage.energy)

    profile.mark("variational_done")
    _emit("variational_done")

    _pipeline_log.info(
        "pipeline variational_done experiment_id=%s algorithm=%s E_var_au=%.10f",
        cfg.experiment_id,
        q.algorithm,
        float(energy_pre),
    )

    out: dict[str, Any] = {
        "repro": repro,
        "scf_energy": float(rhf.e_tot),
        "energy_after_variational": float(energy_pre),
        "angles": angles.tolist() if isinstance(angles, np.ndarray) else list(angles),
        **algo_meta,
    }
    out["pre_quantum_input"] = pre_q_input.as_summary_dict()
    if classical_benchmarks is not None:
        out["classical_benchmarks"] = classical_benchmarks
        out["classical_benchmark_summary"] = _classical_benchmark_summary(classical_benchmarks)
    if embedding_input_payload is not None:
        out["embedding_input_system"] = embedding_input_payload
    out["energy_components"] = energy_components
    if rdm_bundle_meta is not None:
        out["rdm_bundle_meta"] = rdm_bundle_meta
    if rdm_correction_report is not None:
        out["rdm_correction"] = rdm_correction_report
    if rdm_correction_readiness is not None:
        out["rdm_correction_readiness"] = rdm_correction_readiness
    out["hamiltonian_meta"] = dict(qh.meta)
    _apply_embedding_workflow_stage(
        cfg,
        out=out,
        qh=qh,
        exe=exe,
        embedding_input_payload=embedding_input_payload,
        schmidt_ctx=schmidt_ctx,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )
    excited_rs = _run_excited_stages(
        cfg,
        qh=qh,
        exe=exe,
        angles=angles,
        energy_pre=float(energy_pre),
        out=out,
        profile=profile,
        emit=_emit,
    )

    return _run_protocol_and_finalize_stage(
        cfg,
        out=out,
        qh=qh,
        angles=angles,
        excited_rs=excited_rs,
        bspec=bspec,
        exe=exe,
        bundle=bundle,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )


def _protocol_for_job(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    *,
    bspec: Any,
    exe: Any,
    bundle: Any,
) -> PauliAveragingProtocol:
    q = cfg.quantum
    pmsv = None
    if cfg.mitigation.pmsv_enabled:
        pmsv = PMSVConfig(
            stabilizers=list(cfg.mitigation.pmsv_stabilizers),
            retention_rate=float(cfg.mitigation.pmsv_retention_rate),
            report_extension=str(cfg.mitigation.pmsv_report_extension),
            extra=dict(cfg.mitigation.pmsv_extra),
        )
    return PauliAveragingProtocol(
        hamiltonian=qh.operator,
        n_qubits=qh.n_qubits,
        backend=bspec,
        pass_bundle=bundle,
        pmsv=pmsv,
        zne_scales=[float(s) for s in cfg.mitigation.zne_scales]
        if cfg.mitigation.zne_enabled
        else None,
        zne_mode=cfg.mitigation.zne_mode,
        measurement_grouping=q.pauli_grouping,
        run_sampled=q.run_sampled_pauli_protocol,
        run_qiskit_shots=q.run_qiskit_shots_pauli_protocol,
        record_histograms=q.record_pauli_measurement_histograms,
        executor=exe,
        nexus_analog=cfg.nexus_analog,
        pauli_support_max_terms=q.pauli_support_max_terms,
    )


def run_pipeline_from_config(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
) -> dict[str, Any]:
    """Sync pipeline plus optional job enqueue (pickled :class:`PauliAveragingProtocol`)."""
    p = Path(cfg_path)
    cfg = load_experiment_config(p)
    qh_lane: list[QubitHamiltonian] = []
    sync = run_pipeline_sync(cfg, cfg_path=p, hamiltonian_out=qh_lane, run_context=run_context)

    if job_db is None or not cfg.quantum.use_pauli_protocol:
        return sync

    qh = qh_lane[0]
    angles = np.asarray(sync["angles"], dtype=float)
    bspec2 = backend_spec_from_config(cfg)
    exe2 = executor_from_spec(bspec2)
    bundle2 = compiler_pass_bundle_from_config(cfg)
    proto = _protocol_for_job(cfg, qh, bspec=bspec2, exe=exe2, bundle=bundle2)
    proto.build(angles, hea_depth=cfg.quantum.vqe_depth)
    proto.compile()
    blob = proto.dumps()
    ph = hashlib.sha256(blob).hexdigest()[:24]
    store = SqliteJobStore(job_db)
    handle = proto.launch(store)
    sync["job"] = {"job_id": handle.job_id, "protocol_hash": ph, "store": str(job_db)}
    if not enqueue_only:
        PauliAveragingProtocol.process_job(store, handle.job_id)
        sync["job_result"] = store.result(handle.job_id)
    _attach_run_summary(sync, cfg)
    return sync
