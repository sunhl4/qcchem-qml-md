"""
Closed-gap **extension layer** toward documented public-contract parity (not binary parity).

This package is **re-export / benchmarking glue only** — not a second orchestration layer.
New end-to-end workflows belong in ``qchem_stack.orchestration``; integrations may expose
preview exports and parity helpers consumed by HTTP meta routes.

See ``docs/工程记忆_Quantinuum对标与数据流技术文档.md`` §0 for epistemic bounds (L0–L3).
"""

from __future__ import annotations

# Re-exports from moved modules for backward compatibility
from qchem_stack.chem.embedding.dmet_self_consistent import (
    DMETBathState,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
    OneShotEmbeddingDriver,
    run_dmet_bath_scf_self_consistency_v1,
)
from qchem_stack.chem.kernels.spin_ucc import (
    ChemicallyAwareUCCPolicy,
    IdentityRegrouping,
    build_spin_uccsd_fermion_generators,
    count_uccsd_excitations,
)
from qchem_stack.integrations.nexus_optional import probe_qnexus_installation
from qchem_stack.integrations.qermit_reference import qermit_capability_matrix
from qchem_stack.integrations.tensornet_closure import tensornet_closure_strategy
from qchem_stack.integrations.tket_fullchain import (
    TketCompileMode,
    circuit_ir_to_tket_stats_or_none,
    describe_tket_closure_layer,
)
from qchem_stack.protocols.workflow_preview import (
    workflow_preview_payload,
    workflow_preview_variational_execution_slice_v1,
    workflow_preview_vqs_track_slice_v1,
)
from qchem_stack.protocols.workflow_preview_graph import (
    computable_graph_v1,
    computable_graph_v2,
    protocol_stages_preview_v1,
)
from qchem_stack.quantum.l3_algorithm_benchmark import (
    DEFAULT_BENCHMARK_YAMLS,
    L3_PYTEST_YAMLS,
)
from qchem_stack.quantum.l3_algorithm_benchmark import (
    algorithm_benchmark_bundle_v1 as build_l3_algorithm_benchmark_bundle,
)

__all__ = [
    "ChemicallyAwareUCCPolicy",
    "DEFAULT_BENCHMARK_YAMLS",
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "IdentityRegrouping",
    "L3_PYTEST_YAMLS",
    "OneShotEmbeddingDriver",
    "TketCompileMode",
    "build_l3_algorithm_benchmark_bundle",
    "build_spin_uccsd_fermion_generators",
    "circuit_ir_to_tket_stats_or_none",
    "computable_graph_v1",
    "computable_graph_v2",
    "count_uccsd_excitations",
    "describe_tket_closure_layer",
    "probe_qnexus_installation",
    "protocol_stages_preview_v1",
    "qermit_capability_matrix",
    "run_dmet_bath_scf_self_consistency_v1",
    "tensornet_closure_strategy",
    "workflow_preview_payload",
    "workflow_preview_variational_execution_slice_v1",
    "workflow_preview_vqs_track_slice_v1",
]
