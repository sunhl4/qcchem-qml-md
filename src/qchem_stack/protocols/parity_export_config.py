"""Parity export building blocks (split from parity_criteria_export)."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics
from qchem_stack.chem.fermion_mapping_registry import DOCUMENTED_FERMION_QUBIT_MAPPINGS
from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment
from qchem_stack.chem.solvers.registry import create_solver, registered_solver_ids
from qchem_stack.config import compiler_bundle_signature_from_config, load_experiment_config
from qchem_stack.config.mitigation_helpers import mitigation_repro_core_fields
from qchem_stack.contracts.qmframe_field_names import qmframe_field_names_v1
from qchem_stack.integrations.resource_estimation_preview import (
    build_resource_estimation_preview_v1,
)
from qchem_stack.protocols.computable import computables_export_dict
from qchem_stack.protocols.excited_resource_export import build_excited_resource_summary_for_export
from qchem_stack.protocols.product_contract import (
    classify_pauli_expectation_path,
    product_gap_categories,
    protocol_expectation_semantics_public,
)
from qchem_stack.protocols.workflow_preview import (
    workflow_preview_qpe_track_slice_v1,
    workflow_preview_variational_execution_slice_v1,
    workflow_preview_vqs_track_slice_v1,
)
from qchem_stack.quantum.algorithm_registry import ALGORITHM_REGISTRY
from qchem_stack.quantum.ansatz_registry import ANSATZ_REGISTRY
from qchem_stack.quantum.excited_plugins.registry import excited_registry_export
from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1
from qchem_stack.quantum.variational_plugins.registry import variational_registry_export


def register_parity_export_solvers() -> None:
    """Register drivers needed by config-only parity export (no PySCF run)."""
    from qchem_stack.chem.solvers import register_mock_external_solver
    from qchem_stack.chem.solvers.custom_solver_template import (
        register_custom_external_template_solver,
    )

    register_custom_external_template_solver(overwrite=True)
    register_mock_external_solver()


def table_from_config(
    cfg_path: str | Path,
    *,
    protocol_counts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build parity export dict from experiment YAML only."""
    path = Path(cfg_path)
    cfg = load_experiment_config(path)
    solver = create_solver(cfg)
    _ms = molecular_system_from_experiment(cfg)
    geometry_source = str((_ms.meta or {}).get("geometry_source") or "cartesian")
    out: dict[str, Any] = {
        "parity_export_schema_version": "3",
        "source_config": str(path),
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
        "uccsd_decomposition_mode": cfg.quantum.uccsd.decomposition_mode,
        "qse_expansion_pool": cfg.quantum.excited.qse.expansion_pool,
        "vqd_optimizer_mode": cfg.quantum.excited.vqd.optimizer_mode,
        "sceom_generator_strategy": cfg.quantum.excited.sceom.generator_strategy,
        "sceom_self_consistent_rounds": cfg.quantum.excited.sceom.self_consistent_rounds,
        "mitigation_execution_class": cfg.mitigation.execution_class,
        "mitigation_pmsv_enabled": cfg.mitigation.pmsv.enabled,
        "mitigation_pmsv_stabilizers": list(cfg.mitigation.pmsv.stabilizers),
        "mitigation_pmsv_retention_rate": cfg.mitigation.pmsv.retention_rate,
        "mitigation_pmsv_report_extension": cfg.mitigation.pmsv.report_extension,
        "mitigation_pmsv_extra": cfg.mitigation.pmsv.extra,
        "mitigation_zne_enabled": cfg.mitigation.zne.enabled,
        "mitigation_zne_mode": cfg.mitigation.zne.mode,
        "mitigation_zne_scales": list(cfg.mitigation.zne.scales),
        **(
            {
                "mitigation_pec_literature_stub_v1": pec_stub,
            }
            if (
                pec_stub := mitigation_repro_core_fields(cfg).get(
                    "mitigation_pec_literature_stub_v1"
                )
            )
            is not None
            else {}
        ),
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
            "excited_registry_export_v1": excited_registry_export(),
            "operator_pool_registry_export_v1": operator_pool_registry_export_v1(),
            "ansatz_registry_ids": sorted(ANSATZ_REGISTRY.keys()),
            "documented_fermion_qubit_mappings": list(DOCUMENTED_FERMION_QUBIT_MAPPINGS),
        }
        out["md_ml_repro_freeze_fields_v1"] = {
            "schema": "md_ml_repro_freeze_fields_v1",
            "qmframe_fields": qmframe_field_names_v1(),
        }
    return out
