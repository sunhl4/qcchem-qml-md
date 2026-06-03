"""Assemble post-variational pipeline dict and patch repro parity snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.chem.integrals.exporter_registry import list_active_space_integral_exporters
from qchem_stack.chem.pre_quantum_builder_registry import list_pre_quantum_branch_builders
from qchem_stack.contracts.schema_ids import (
    ACTIVE_SPACE_EXPORTERS_REGISTRY_V1,
    PRE_QUANTUM_BRANCH_REGISTRY_V1,
)
from qchem_stack.orchestration.repro_summary import classical_benchmark_summary

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def assemble_pipeline_result_dict(
    *,
    repro: dict[str, Any],
    rhf: Any,
    energy_pre: float,
    angles: Any,
    algo_meta: dict[str, Any],
    algorithm_report: Any,
    pre_q_input: Any,
    classical_benchmarks: dict[str, Any] | None,
    embedding_input_payload: Any,
    energy_components: Any,
    rdm_bundle_meta: dict[str, Any] | None,
    rdm_correction_report: Any,
    rdm_correction_readiness: Any,
    qh: QubitHamiltonian,
    build_cache: RunBuildCache,
) -> dict[str, Any]:
    """Assemble the post-variational result dict (pre embedding/excited/protocol stages)."""
    out: dict[str, Any] = {
        "repro": repro,
        "scf_energy": float(rhf.e_tot),
        "energy_after_variational": float(energy_pre),
        "angles": angles.tolist() if isinstance(angles, np.ndarray) else list(angles),
        **algo_meta,
    }
    if algorithm_report is not None:
        out["algorithm_report"] = algorithm_report
    out["pre_quantum_input"] = pre_q_input.as_summary_dict()
    if classical_benchmarks is not None:
        out["classical_benchmarks"] = classical_benchmarks
        out["classical_benchmark_summary"] = classical_benchmark_summary(classical_benchmarks)
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
    out["pre_quantum_build_cache"] = build_cache.stats_dict()
    return out


def patch_repro_parity_snapshot(out: dict[str, Any]) -> None:
    """Augment ``repro.parity_snapshot`` with build-cache and registry exports in place."""
    repro_ps = out.get("repro", {}).get("parity_snapshot")
    if not isinstance(repro_ps, dict):
        return
    repro_ps["pre_quantum_build_cache_v1"] = dict(out["pre_quantum_build_cache"])
    repro_ps["active_space_exporters_registry_v1"] = {
        "schema": ACTIVE_SPACE_EXPORTERS_REGISTRY_V1,
        "backend_tags": list(list_active_space_integral_exporters()),
    }
    repro_ps["pre_quantum_branch_registry_v1"] = {
        "schema": PRE_QUANTUM_BRANCH_REGISTRY_V1,
        "path_ids": list(list_pre_quantum_branch_builders()),
    }
    pqi_sum = out.get("pre_quantum_input")
    if isinstance(pqi_sum, dict):
        repro_ps["pre_quantum_handoff_v1"] = {
            k: pqi_sum[k]
            for k in (
                "source",
                "backend_tag",
                "hamiltonian_fingerprint",
                "hamiltonian_branch",
                "hamiltonian_fixed_before_variational",
                "post_variational_embedding_audit_only",
                "reference_energy_au",
                "scf_energy_au",
                "n_active_orbitals",
                "n_active_electrons",
            )
            if k in pqi_sum and pqi_sum[k] is not None
        }
