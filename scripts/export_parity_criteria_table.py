#!/usr/bin/env python3
"""Emit a JSON/YAML-friendly dict for product Methods parity.

Reads experiment YAML and optionally merges keys from a pipeline results JSON
(``run_pipeline_sync`` / ``run_pipeline_from_config`` output saved with json.dump).

Stable top-level keys used by CI (subset: ``parity_export_schema_version``, ``experiment_id``,
``geometry_source``, ``computable_abstract``, ``embedding``, …) are enumerated in
``qchem_stack.protocols.product_contract.PARITY_EXPORT_V3_STABLE_KEYS``; keep them in sync
when extending this exporter.

Usage::

    python scripts/export_parity_criteria_table.py configs/example_h2.yaml
    python scripts/export_parity_criteria_table.py configs/example_h2.yaml --results out.json
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from qchem_stack.chem.bridges.facade import molecular_system_from_experiment
from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics
from qchem_stack.chem.fermion_mapping_registry import DOCUMENTED_FERMION_QUBIT_MAPPINGS
from qchem_stack.chem.solvers.registry import create_solver, registered_solver_ids
from qchem_stack.config import compiler_bundle_signature_from_config, load_experiment_config
from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
from qchem_stack.integrations.resource_estimation_preview import (
    build_resource_estimation_preview_v1,
)
from qchem_stack.integrations.workflow_preview import (
    workflow_preview_qpe_track_slice_v1,
    workflow_preview_variational_execution_slice_v1,
    workflow_preview_vqs_track_slice_v1,
)
from qchem_stack.md_bridge import QMFrame
from qchem_stack.orchestration.pipeline import build_excited_resource_summary_for_export
from qchem_stack.protocols.computable import computables_export_dict
from qchem_stack.protocols.product_contract import (
    classify_pauli_expectation_path,
    product_gap_categories,
    protocol_expectation_semantics_public,
)
from qchem_stack.quantum.algorithm_registry import ALGORITHM_REGISTRY
from qchem_stack.quantum.ansatz_registry import ANSATZ_REGISTRY
from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1
from qchem_stack.quantum.variational_plugins.registry import variational_registry_export


def _table_from_config(
    cfg_path: Path,
    *,
    protocol_counts: dict | None = None,
) -> dict:
    cfg = load_experiment_config(cfg_path)
    solver = create_solver(cfg)
    _ms = molecular_system_from_experiment(cfg)
    geometry_source = str((_ms.meta or {}).get("geometry_source") or "cartesian")
    out = {
        "parity_export_schema_version": "3",
        "source_config": str(cfg_path),
        "experiment_id": cfg.experiment_id,
        "geometry_source": geometry_source,
        "molecule": cfg.molecule.model_dump(),
        "scf_method": cfg.scf.method,
        "scf_driver": cfg.scf.driver,
        "registered_solvers": sorted(registered_solver_ids()),
        "solver_capabilities_snapshot": dataclasses.asdict(solver.capabilities),
        "active_space": cfg.active_space.model_dump(),
        "fermion_to_qubit_map": cfg.active_space.mapping.fermion_qubit,
        "pauli_grouping": cfg.quantum.pauli.grouping,
        "quantum_algorithm": cfg.quantum.algorithm,
        "quantum_algorithm_factory": cfg.quantum.algorithm_factory,
        "variational_ansatz": cfg.quantum.variational.ansatz,
        "uccsd_trotter_steps": cfg.quantum.variational.uccsd_trotter_steps,
        "pauli_support_max_terms": cfg.quantum.pauli.support_max_terms,
        "use_pauli_protocol": cfg.quantum.pauli.use_protocol,
        "vqe_depth": cfg.quantum.vqe.depth,
        "vqe_maxiter": cfg.quantum.vqe.maxiter,
        "adapt_max_iter": cfg.quantum.adapt.max_iter,
        "iqeb_max_rounds": cfg.quantum.iqeb.max_rounds,
        "shots_per_circuit": cfg.backend.shots_per_circuit,
        "backend_provider": cfg.backend.provider,
        "target_energy_stderr": cfg.backend.target_energy_stderr,
        "run_sampled_pauli_protocol": cfg.quantum.pauli.run_sampled,
        "run_qiskit_shots_pauli_protocol": cfg.quantum.pauli.run_qiskit_shots,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(cfg.quantum),
        "protocol_expectation_semantics_v1": protocol_expectation_semantics_public(),
        "qpe_demo_track_after_variational": cfg.quantum.demos.qpe.track_after_variational,
        "qpe_pipeline_integration": cfg.quantum.demos.qpe.pipeline_integration,
        "qpe_demo_track_n_bits": cfg.quantum.demos.qpe.demo_track_n_bits,
        "vqs_track_after_variational": cfg.quantum.demos.vqs.track_after_variational,
        "vqs_pipeline_integration": cfg.quantum.demos.vqs.pipeline_integration,
        "vqs_mode": cfg.quantum.demos.vqs.mode,
        "vqs_n_times": cfg.quantum.demos.vqs.n_times,
        "vqs_dt": cfg.quantum.demos.vqs.dt,
        "record_pauli_measurement_histograms": cfg.quantum.pauli.record_histograms,
        "computable_abstract": computables_export_dict(cfg, protocol_counts=protocol_counts),
        "excited_resource_from_config": build_excited_resource_summary_for_export(cfg),
        "capability_gap_categories": product_gap_categories(),
        "vqd_after_variational": cfg.quantum.excited.vqd.after_variational,
        "vqd_n_states": cfg.quantum.excited.vqd.n_states,
        "vqd_penalty_weight": cfg.quantum.excited.vqd.penalty_weight,
        "vqd_shots_objective": cfg.quantum.excited.vqd.shots_objective,
        "vqd_shots_overlap": cfg.quantum.excited.vqd.shots_overlap,
        "vqd_shots_weight": cfg.quantum.excited.vqd.shots_weight,
        "qse_after_variational": cfg.quantum.excited.qse.after_variational,
        "qse_subspace_dim": cfg.quantum.excited.qse.subspace_dim,
        "qse_max_basis": cfg.quantum.excited.qse.max_basis,
        "qse_shot_mode": cfg.quantum.excited.qse.shot_mode,
        "qse_shots_per_matrix_element": cfg.quantum.excited.qse.shots_per_matrix_element,
        "qse_shots_per_ij_term": cfg.quantum.excited.qse.shots_per_ij_term,
        "sceom_after_variational": cfg.quantum.excited.sceom.after_variational,
        "sceom_subspace_dim": cfg.quantum.excited.sceom.subspace_dim,
        "sceom_shots_per_matrix_element": cfg.quantum.excited.sceom.shots_per_matrix_element,
        "mitigation_execution_class": cfg.mitigation.execution_class,
        "mitigation_pmsv_enabled": cfg.mitigation.pmsv.enabled,
        "mitigation_pmsv_stabilizers": list(cfg.mitigation.pmsv.stabilizers),
        "mitigation_pmsv_retention_rate": cfg.mitigation.pmsv.retention_rate,
        "mitigation_pmsv_report_extension": cfg.mitigation.pmsv.report_extension,
        "mitigation_pmsv_extra": cfg.mitigation.pmsv.extra,
        "mitigation_zne_enabled": cfg.mitigation.zne.enabled,
        "mitigation_zne_mode": cfg.mitigation.zne.mode,
        "mitigation_zne_scales": list(cfg.mitigation.zne.scales),
        "embedding": cfg.embedding.model_dump(),
        "pre_quantum_semantics_from_config": pre_quantum_hamiltonian_semantics(cfg),
        "embedding_mode": cfg.embedding.mode,
        "embedding_input_representation": cfg.embedding.embedding_input_representation,
        "parity_integrations_dmet_stub_one_shot_ledger": cfg.parity_integrations.dmet_stub_one_shot_ledger,
        "chemistry_extended": cfg.chemistry_extended.model_dump(),
        "classical_benchmark_enabled": cfg.chemistry_extended.benchmarks.enabled,
        "rdm_correction_method": cfg.chemistry_extended.post_hf.rdm_correction_method,
        "nexus_analog": cfg.nexus_analog.model_dump(),
        "nexus_cloud": cfg.nexus_cloud.model_dump(),
        "tensornet_expectation_stub": cfg.quantum.tensornet.expectation_stub,
        "tensornet_contraction_engine": cfg.quantum.tensornet.contraction_engine,
        "iqeb_implementation_path": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
        "compiler_native_twoq": cfg.compiler.native_twoq,
        "compiler_optimization_level": cfg.compiler.optimization_level,
        "compiler_preoptimize_passes": list(cfg.compiler.preoptimize_passes),
        "compiler_passes_yaml": list(cfg.compiler.compiler_passes),
        "compiler_bundle_signature": compiler_bundle_signature_from_config(cfg),
        "methods_resource_preview_v1": {
            "schema": "methods_resource_preview_v1",
            "qpe_pipeline_integration": cfg.quantum.demos.qpe.pipeline_integration,
            "qpe_demo_track_after_variational": cfg.quantum.demos.qpe.track_after_variational,
            "qpe_demo_track_n_bits": cfg.quantum.demos.qpe.demo_track_n_bits,
            "use_pauli_protocol": cfg.quantum.pauli.use_protocol,
            "parity_integrations_tket_first_circuit_stats": cfg.parity_integrations.tket_first_circuit_stats,
            "vqs_track_after_variational": cfg.quantum.demos.vqs.track_after_variational,
            "vqs_pipeline_integration": cfg.quantum.demos.vqs.pipeline_integration,
        },
    }
    ve = workflow_preview_variational_execution_slice_v1(cfg)
    if ve is not None:
        out["workflow_preview_variational_execution_v1"] = ve
    vqx = workflow_preview_vqs_track_slice_v1(cfg)
    if vqx is not None:
        out["workflow_preview_vqs_track_v1"] = vqx
    qpex = workflow_preview_qpe_track_slice_v1(cfg)
    if qpex is not None:
        out["workflow_preview_qpe_track_v1"] = qpex
    if cfg.parity_integrations.resource_estimation_preview:
        out["resource_estimation_preview_v1"] = build_resource_estimation_preview_v1(cfg=cfg)
        out["algorithm_registry_alignment_v1"] = {
            "schema": "algorithm_registry_alignment_v1",
            "algorithm_registry_ids": sorted(ALGORITHM_REGISTRY.keys()),
            "variational_registry_export_v1": variational_registry_export(),
            "operator_pool_registry_export_v1": operator_pool_registry_export_v1(),
            "ansatz_registry_ids": sorted(ANSATZ_REGISTRY.keys()),
            "documented_fermion_qubit_mappings": list(DOCUMENTED_FERMION_QUBIT_MAPPINGS),
        }
        out["md_ml_repro_freeze_fields_v1"] = {
            "schema": "md_ml_repro_freeze_fields_v1",
            "qmframe_fields": sorted(QMFrame.model_fields.keys()),
        }
    return out


def _truncate_pauli_support_for_export(out: dict, *, max_pauli: int | None) -> None:
    if max_pauli is None or max_pauli < 0:
        return
    key = "hamiltonian_pauli_strings_mirror_protocol_counts"
    xs = out.get(key)
    if isinstance(xs, list) and len(xs) > max_pauli:
        out[key] = xs[:max_pauli]
        out["hamiltonian_pauli_strings_truncated"] = True
        out["hamiltonian_pauli_strings_omitted_count"] = len(xs) - max_pauli


def main() -> None:
    ap = argparse.ArgumentParser(description="Export parity / falsifiability table fields.")
    ap.add_argument("config", type=Path, help="Experiment YAML path")
    ap.add_argument("--results", type=Path, default=None, help="Optional JSON with pipeline output")
    ap.add_argument(
        "--max-pauli-export",
        type=int,
        default=None,
        metavar="N",
        help="If set with --results, cap exported hamiltonian_pauli_strings mirror list length",
    )
    args = ap.parse_args()
    proto_pc: dict | None = None
    if args.results and args.results.is_file():
        data0 = json.loads(args.results.read_text(encoding="utf-8"))
        if isinstance(data0, dict):
            pc0 = data0.get("protocol_counts")
            if isinstance(pc0, dict):
                proto_pc = pc0
    out = _table_from_config(args.config, protocol_counts=proto_pc)
    if args.results and args.results.is_file():
        data = json.loads(args.results.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            repro = data.get("repro") if isinstance(data.get("repro"), dict) else {}
            out["parity_snapshot_from_run"] = repro.get("parity_snapshot")
            rsum = repro.get("run_summary")
            out["run_summary_from_repro"] = rsum
            out["scf_energy_from_run"] = data.get("scf_energy")
            out["energy_after_variational_from_run"] = data.get("energy_after_variational")
            out["energy_pauli_protocol_from_run"] = data.get("energy_pauli_protocol")
            jr = data.get("job_result")
            if isinstance(jr, dict):
                out["job_async_expectation_from_run"] = jr.get("expectation")
                out["job_async_energy_stderr_from_run"] = jr.get("energy_stderr")
            rsg = data.get("resource_summary")
            out["resource_summary_from_run"] = rsg
            if isinstance(rsg, dict):
                out["sum_shots_total_with_excited_upper_bound_from_run"] = rsg.get(
                    "sum_shots_total_with_excited_upper_bound"
                )
                out["excited_shots_upper_bound_from_run"] = rsg.get("excited_shots_upper_bound")
                out["excited_shot_accounting_from_run"] = rsg.get("excited_shot_accounting")
            out["protocol_expectation_source"] = None
            pc = data.get("protocol_counts")
            if isinstance(pc, dict):
                out["protocol_expectation_source"] = pc.get("expectation_source")
                out["protocol_energy_stderr_model"] = pc.get("energy_stderr_model")
                if isinstance(pc.get("pmsv_report"), dict):
                    out["protocol_pmsv_report_from_run"] = pc.get("pmsv_report")
                hp = pc.get("hamiltonian_pauli_strings")
                if isinstance(hp, list):
                    out["hamiltonian_pauli_strings_mirror_protocol_counts"] = list(hp)
                if pc.get("n_hamiltonian_pauli_terms") is not None:
                    out["n_hamiltonian_pauli_terms_from_run"] = pc.get("n_hamiltonian_pauli_terms")
                if pc.get("pauli_group_ids") is not None:
                    out["pauli_group_ids_from_run"] = pc.get("pauli_group_ids")
            hm = data.get("hamiltonian_meta")
            if isinstance(hm, dict) and hm.get("hamiltonian_fingerprint") is not None:
                out["hamiltonian_fingerprint_from_run"] = hm.get("hamiltonian_fingerprint")
            pqi = data.get("pre_quantum_input")
            if isinstance(pqi, dict):
                out["pre_quantum_input_from_run"] = {
                    k: pqi[k]
                    for k in (
                        "schema",
                        "source",
                        "backend_tag",
                        "integral_source",
                        "fermion_to_qubit_map",
                        "hamiltonian_fingerprint",
                        "reference_energy_au",
                        "scf_energy_au",
                        "n_active_orbitals",
                        "n_active_electrons",
                        "hamiltonian_branch",
                        "hamiltonian_fixed_before_variational",
                        "post_variational_embedding_audit_only",
                    )
                    if k in pqi and pqi[k] is not None
                }
            pbc = data.get("pre_quantum_build_cache")
            if isinstance(pbc, dict):
                out["pre_quantum_build_cache_from_run"] = dict(pbc)
            cb = data.get("classical_benchmarks")
            if isinstance(cb, dict):
                out["classical_benchmarks_from_run"] = cb
            cbs = data.get("classical_benchmark_summary")
            if isinstance(cbs, dict):
                out["classical_benchmark_summary_from_run"] = cbs
            rcorr = data.get("rdm_correction")
            if isinstance(rcorr, dict):
                out["rdm_correction_from_run"] = rcorr
            rr_read = data.get("rdm_correction_readiness")
            if isinstance(rr_read, dict):
                out["rdm_correction_readiness_from_run"] = rr_read
            ecmp = data.get("energy_components")
            if isinstance(ecmp, dict):
                out["energy_components_from_run"] = ecmp
            out["excited_resource_summary_from_run"] = data.get("excited_resource_summary")
            if isinstance(rsum, dict):
                for key in (
                    "n_pauli_terms",
                    "n_pauli_groups",
                    "n_circuits",
                    "n_qubits",
                    "energy_pauli_protocol",
                    "async_job_id",
                    "protocol_hash_prefix",
                    "protocol_total_shots_budget",
                    "protocol_n_measurement_circuits",
                    "protocol_shots_per_circuit_effective",
                    "protocol_energy_stderr",
                    "job_async_expectation",
                    "job_async_energy_stderr",
                    "job_async_total_shots_budget",
                    "vqd_n_states_yaml",
                    "vqd_n_energies_recorded",
                    "vqd_deflation_levels_completed",
                    "vqd_channels_count",
                    "vqd_shots_objective_yaml",
                    "vqd_shots_overlap_yaml",
                    "vqd_shots_weight_yaml",
                    "qse_subspace_dim_yaml",
                    "qse_max_basis_yaml",
                    "qse_basis_dimension_K",
                    "qse_n_excitation_energies",
                    "qse_n_transition_tasks",
                    "qse_total_shots_upper_bound",
                    "sceom_subspace_dim_yaml",
                    "sceom_n_energies_recorded",
                    "sceom_active_generator_count",
                    "sceom_matrix_construction",
                    "dmet_embedding_active",
                    "dmet_hamiltonian_source_yaml",
                    "dmet_fragment_count",
                    "decomposition_primary_fragment_id",
                    "decomposition_fragment_count",
                    "decomposition_total_pauli_terms",
                    "mitigation_zne_mode_yaml",
                    "mitigation_zne_scales_yaml",
                    "dmet_uniform_multifragment_toy_yaml",
                    "dmet_stub_one_shot_ledger_yaml",
                    "dmet_fragment_solve_present",
                    "dmet_fragment_solve_schema",
                    "protocol_zne_mode",
                    "variational_ansatz_yaml",
                    "uccsd_n_parameters",
                    "classical_benchmarks_present",
                    "classical_benchmarks_schema",
                    "classical_bench_hf_status",
                    "classical_bench_hf_energy_au",
                    "classical_bench_mp2_status",
                    "classical_bench_mp2_energy_au",
                    "classical_bench_ccsd_status",
                    "classical_bench_ccsd_energy_au",
                    "classical_bench_casci_status",
                    "classical_bench_casci_energy_au",
                    "classical_benchmark_summary_present",
                    "classical_benchmark_summary_schema",
                    "classical_benchmark_recommended_baseline_method",
                    "classical_benchmark_recommended_baseline_energy_au",
                    "classical_benchmark_best_method",
                    "classical_benchmark_best_energy_au",
                    "classical_benchmark_delta_best_vs_hf_au",
                    "embedding_input_representation_yaml",
                    "embedding_input_system_schema",
                    "energy_components_present",
                    "energy_components_schema",
                    "energy_components_mean_field_total_au",
                    "energy_components_nuclear_repulsion_au",
                    "rdm_correction_present",
                    "rdm_correction_schema",
                    "rdm_correction_method",
                    "rdm_correction_status",
                    "rdm_correction_energy_au",
                    "rdm_correction_readiness_present",
                    "rdm_correction_readiness_schema",
                    "rdm_correction_readiness_requested_method",
                    "rdm_correction_readiness_rdm1_source",
                    "rdm_correction_readiness_reference_wavefunction",
                    "rdm_correction_readiness_kernel_class",
                    "rdm_correction_readiness_nevpt2_pyscf_status",
                    "pre_quantum_source",
                    "pre_quantum_backend_tag",
                    "pre_quantum_hamiltonian_branch",
                    "hamiltonian_fingerprint",
                    "hamiltonian_fixed_before_variational",
                    "pre_quantum_pack_builds",
                    "pre_quantum_pack_hits",
                ):
                    if key in rsum and rsum[key] is not None:
                        out[f"{key}_mirror_run_summary"] = rsum[key]
            out["computable_abstract"] = computables_export_dict(
                load_experiment_config(args.config),
                protocol_counts=pc if isinstance(pc, dict) else None,
            )
            ew = data.get("embedding_workflow")
            if isinstance(ew, dict):
                out["embedding_workflow_from_run"] = ew
            if isinstance(data.get("adapt_meta"), dict):
                out["adapt_meta_from_run"] = data["adapt_meta"]
            apool = data.get("adapt_pool")
            if isinstance(apool, list):
                out["adapt_pool_from_run"] = apool
            if isinstance(data.get("iqeb_meta"), dict):
                out["iqeb_meta_from_run"] = data["iqeb_meta"]
            isp = data.get("iqeb_selected_pauli_strings")
            if isinstance(isp, list):
                out["iqeb_selected_pauli_strings_from_run"] = isp
            qdt = data.get("qpe_demo_track")
            if isinstance(qdt, dict):
                out["qpe_demo_track_from_run"] = {
                    "schema": qdt.get("schema"),
                    "has_kitaev": qdt.get("kitaev_ground_energy_dense") is not None,
                    "has_bayesian_stub": qdt.get("bayesian_phase_map_toy") is not None,
                }
            vtr = data.get("vqs_track")
            if isinstance(vtr, dict):
                out["vqs_track_from_run"] = {
                    "schema": vtr.get("schema"),
                    "has_energy_observable": bool(vtr.get("energy_observable")),
                    "vqs_mode_from_run": vtr.get("vqs_mode"),
                }
            out["methods_resource_unified_v1"] = build_methods_resource_unified_v1(data)
            if isinstance(rsum, dict) and rsum.get("qpe_demo_track_ran"):
                out["qpe_demo_track_ran_from_run_summary"] = True
            if isinstance(rsum, dict) and rsum.get("vqs_track_ran"):
                out["vqs_track_ran_from_run_summary"] = True
            if isinstance(rsum, dict):
                if rsum.get("vqd_three_protocol_present") is not None:
                    out["vqd_three_protocol_present_from_run_summary"] = rsum[
                        "vqd_three_protocol_present"
                    ]
                if rsum.get("qse_shot_mode") is not None:
                    out["qse_shot_mode_from_run_summary"] = rsum["qse_shot_mode"]
                if rsum.get("sceom_shot_noise_model") is not None:
                    out["sceom_shot_noise_model_from_run_summary"] = rsum["sceom_shot_noise_model"]
            psnap = repro.get("parity_snapshot")
            if isinstance(psnap, dict):
                for k in (
                    "tensornet_engine_resolved",
                    "tensornet_fallback_reason",
                    "variational_ansatz",
                    "uccsd_n_parameters",
                ):
                    if psnap.get(k) is not None:
                        out[f"{k}_from_parity_snapshot"] = psnap[k]
                ogr = psnap.get("open_gap_closure_reference")
                if isinstance(ogr, dict) and ogr.get("schema") is not None:
                    out["open_gap_closure_reference_schema_from_run"] = ogr.get("schema")
                ph = psnap.get("pre_quantum_handoff_v1")
                if isinstance(ph, dict):
                    out["pre_quantum_handoff_v1_from_parity_snapshot"] = dict(ph)
                pbc = psnap.get("pre_quantum_build_cache_v1")
                if isinstance(pbc, dict):
                    out["pre_quantum_build_cache_v1_from_parity_snapshot"] = dict(pbc)
            vqd_block = data.get("vqd")
            if isinstance(vqd_block, dict):
                vmeta = vqd_block.get("meta")
                if isinstance(vmeta, dict):
                    ch = vmeta.get("vqd_channels")
                    if isinstance(ch, list):
                        out["vqd_three_protocol_present_from_run"] = any(
                            isinstance(c, dict) and "three_protocol" in c for c in ch
                        )
            qse_block = data.get("qse")
            if isinstance(qse_block, dict):
                qm = qse_block.get("meta")
                if isinstance(qm, dict) and qm.get("qse_shot_mode") is not None:
                    out["qse_shot_mode_from_run_meta"] = qm.get("qse_shot_mode")
            sceom_block = data.get("sceom")
            if isinstance(sceom_block, dict):
                sm = sceom_block.get("meta")
                if isinstance(sm, dict):
                    out["sceom_shot_noise_model_from_run"] = sm.get("shot_noise_model")
                    if sm.get("shots_per_matrix_element") is not None:
                        out["sceom_shots_per_matrix_element_from_run"] = sm[
                            "shots_per_matrix_element"
                        ]
    cfg_final = load_experiment_config(args.config)
    if cfg_final.parity_integrations.resource_estimation_preview:
        pdata: dict | None = None
        if args.results and args.results.is_file():
            raw = json.loads(args.results.read_text(encoding="utf-8"))
            pdata = raw if isinstance(raw, dict) else None
        out["resource_estimation_preview_v1"] = build_resource_estimation_preview_v1(
            cfg=cfg_final, pipeline_row=pdata
        )
    _truncate_pauli_support_for_export(out, max_pauli=args.max_pauli_export)
    json.dump(out, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
