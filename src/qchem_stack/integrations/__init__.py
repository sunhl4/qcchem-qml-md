"""
Closed-gap **extension layer** toward documented public-contract parity (not binary parity).

See ``docs/工程记忆_Quantinuum对标与数据流技术文档.md`` §0 for epistemic bounds (L0–L3).
"""

from __future__ import annotations

from qchem_stack.integrations.dmet_self_consistent import (
    DMETBathState,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
    OneShotEmbeddingDriver,
)
from qchem_stack.integrations.nexus_optional import probe_qnexus_installation
from qchem_stack.integrations.qermit_reference import qermit_capability_matrix
from qchem_stack.integrations.tensornet_closure import tensornet_closure_strategy
from qchem_stack.integrations.tket_fullchain import (
    TketCompileMode,
    circuit_ir_to_tket_stats_or_none,
    describe_tket_closure_layer,
)
from qchem_stack.integrations.ucc_reference import (
    ChemicallyAwareUCCPolicy,
    IdentityRegrouping,
    build_spin_uccsd_fermion_generators,
    count_uccsd_excitations,
)

__all__ = [
    "ChemicallyAwareUCCPolicy",
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "IdentityRegrouping",
    "OneShotEmbeddingDriver",
    "TketCompileMode",
    "build_spin_uccsd_fermion_generators",
    "circuit_ir_to_tket_stats_or_none",
    "count_uccsd_excitations",
    "describe_tket_closure_layer",
    "probe_qnexus_installation",
    "qermit_capability_matrix",
    "tensornet_closure_strategy",
]
