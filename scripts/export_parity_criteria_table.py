#!/usr/bin/env python3
"""Emit a JSON/YAML-friendly dict for competitor Methods parity (Quantinuum §7 style).

Reads experiment YAML and optionally merges keys from a pipeline results JSON
(``run_pipeline_sync`` / ``run_pipeline_from_config`` output saved with json.dump).

Usage::

    python scripts/export_parity_criteria_table.py configs/example_h2.yaml
    python scripts/export_parity_criteria_table.py configs/example_h2.yaml --results out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qchem_stack.config import compiler_bundle_signature_from_config, load_experiment_config
from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
from qchem_stack.integrations.resource_estimation_preview import build_resource_estimation_preview_v1
from qchem_stack.orchestration.pipeline import build_excited_resource_summary_for_export
from qchem_stack.protocols.computable import computables_export_dict
from qchem_stack.protocols.inquanto_contract import (
    PARITY_EXPORT_V2_STABLE_KEYS,
    classify_pauli_expectation_path,
    inquanto_gap_categories,
    protocol_expectation_semantics_public,
)


def _table_from_config(
    cfg_path: Path,
    *,
    protocol_counts: dict | None = None,
) -> dict:
    cfg = load_experiment_config(cfg_path)
    out = {
        "parity_export_schema_version": "2",
        "source_config": str(cfg_path),
        "experiment_id": cfg.experiment_id,
        "molecule": cfg.molecule.model_dump(),
        "scf_method": cfg.scf.method,
        "active_space": cfg.active_space.model_dump(),
        "fermion_to_qubit_map": cfg.active_space.fermion_qubit_mapping,
        "pauli_grouping": cfg.quantum.pauli_grouping,
        "quantum_algorithm": cfg.quantum.algorithm,
        "variational_ansatz": cfg.quantum.variational_ansatz,
        "uccsd_trotter_steps": cfg.quantum.uccsd_trotter_steps,
        "pauli_support_max_terms": cfg.quantum.pauli_support_max_terms,
        "use_pauli_protocol": cfg.quantum.use_pauli_protocol,
        "vqe_depth": cfg.quantum.vqe_depth,
        "vqe_maxiter": cfg.quantum.vqe_maxiter,
        "adapt_max_iter": cfg.quantum.adapt_max_iter,
        "iqeb_max_rounds": cfg.quantum.iqeb_max_rounds,
        "shots_per_circuit": cfg.backend.shots_per_circuit,
        "backend_provider": cfg.backend.provider,
        "target_energy_stderr": cfg.backend.target_energy_stderr,
        "run_sampled_pauli_protocol": cfg.quantum.run_sampled_pauli_protocol,
        "run_qiskit_shots_pauli_protocol": cfg.quantum.run_qiskit_shots_pauli_protocol,
        "pauli_protocol_expectation_path": classify_pauli_expectation_path(cfg.quantum),
        "protocol_expectation_semantics_v1": protocol_expectation_semantics_public(),
        "qpe_demo_track_after_variational": cfg.quantum.qpe_demo_track_after_variational,
        "qpe_pipeline_integration": cfg.quantum.qpe_pipeline_integration,
        "record_pauli_measurement_histograms": cfg.quantum.record_pauli_measurement_histograms,
        "computable_abstract": computables_export_dict(cfg, protocol_counts=protocol_counts),
        "excited_resource_from_config": build_excited_resource_summary_for_export(cfg),
        "inquanto_gap_categories": inquanto_gap_categories(),
        "vqd_after_variational": cfg.quantum.vqd_after_variational,
        "vqd_n_states": cfg.quantum.vqd_n_states,
        "vqd_penalty_weight": cfg.quantum.vqd_penalty_weight,
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
        "mitigation_execution_class": cfg.mitigation.execution_class,
        "mitigation_pmsv_enabled": cfg.mitigation.pmsv_enabled,
        "mitigation_pmsv_stabilizers": list(cfg.mitigation.pmsv_stabilizers),
        "mitigation_pmsv_retention_rate": cfg.mitigation.pmsv_retention_rate,
        "mitigation_pmsv_report_extension": cfg.mitigation.pmsv_report_extension,
        "mitigation_pmsv_extra": cfg.mitigation.pmsv_extra,
        "mitigation_zne_enabled": cfg.mitigation.zne_enabled,
        "mitigation_zne_mode": cfg.mitigation.zne_mode,
        "mitigation_zne_scales": list(cfg.mitigation.zne_scales),
        "embedding": cfg.embedding.model_dump(),
        "embedding_mode": cfg.embedding.mode,
        "parity_integrations_dmet_stub_one_shot_ledger": cfg.parity_integrations.dmet_stub_one_shot_ledger,
        "chemistry_extended": cfg.chemistry_extended.model_dump(),
        "nexus_analog": cfg.nexus_analog.model_dump(),
        "nexus_cloud": cfg.nexus_cloud.model_dump(),
        "tensornet_expectation_stub": cfg.quantum.tensornet_expectation_stub,
        "tensornet_contraction_engine": cfg.quantum.tensornet_contraction_engine,
        "iqeb_implementation_path": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
        "compiler_native_twoq": cfg.compiler.native_twoq,
        "compiler_optimization_level": cfg.compiler.optimization_level,
        "compiler_preoptimize_passes": list(cfg.compiler.preoptimize_passes),
        "compiler_passes_yaml": list(cfg.compiler.compiler_passes),
        "compiler_bundle_signature": compiler_bundle_signature_from_config(cfg),
        "methods_resource_preview_v1": {
            "schema": "methods_resource_preview_v1",
            "qpe_pipeline_integration": cfg.quantum.qpe_pipeline_integration,
            "qpe_demo_track_after_variational": cfg.quantum.qpe_demo_track_after_variational,
            "use_pauli_protocol": cfg.quantum.use_pauli_protocol,
            "parity_integrations_tket_first_circuit_stats": cfg.parity_integrations.tket_first_circuit_stats,
        },
    }
    if cfg.parity_integrations.resource_estimation_preview:
        out["resource_estimation_preview_v1"] = build_resource_estimation_preview_v1(cfg=cfg)
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
                    "dmet_uniform_multifragment_toy_yaml",
                    "dmet_stub_one_shot_ledger_yaml",
                    "dmet_fragment_solve_present",
                    "dmet_fragment_solve_schema",
                    "variational_ansatz_yaml",
                    "uccsd_n_parameters",
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
            out["methods_resource_unified_v1"] = build_methods_resource_unified_v1(data)
            if isinstance(rsum, dict) and rsum.get("qpe_demo_track_ran"):
                out["qpe_demo_track_ran_from_run_summary"] = True
            if isinstance(rsum, dict):
                if rsum.get("vqd_three_protocol_present") is not None:
                    out["vqd_three_protocol_present_from_run_summary"] = rsum["vqd_three_protocol_present"]
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
                        out["sceom_shots_per_matrix_element_from_run"] = sm["shots_per_matrix_element"]
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
