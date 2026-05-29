"""
Release-facing product contracts and stable export registries.

This module is the public contract surface for qchem_stack itself. Competitive
alignment artifacts are intentionally kept out of the default release payloads.
"""

from __future__ import annotations

from qchem_stack.protocols.product_contract_export import (
    PARITY_EXPORT_V3_STABLE_KEYS,
    mitigation_execution_model_public,
    open_stack_differentiators_public,
    pauli_protocol_expectation_path_for_config,
    protocol_expectation_semantics_public,
)
from qchem_stack.protocols.product_contract_gaps import (
    PRODUCT_CAPABILITY_MAP,
    PRODUCT_GAP_CATEGORIES_V1,
    product_capability_map_for_docs,
    product_gap_anchor_index_v1,
    product_gap_categories,
    validate_product_gap_categories,
)
from qchem_stack.protocols.product_contract_matrix import (
    ansatz_protocol_matrix_v1,
    classify_pauli_expectation_path,
    matrix_pauli_protocol_name,
    matrix_qse_protocol_name,
    validate_ansatz_protocol_combo,
    validate_pauli_protocol_for_config,
    validate_qse_protocol_for_config,
)

__all__ = [
    "PARITY_EXPORT_V3_STABLE_KEYS",
    "PRODUCT_CAPABILITY_MAP",
    "PRODUCT_GAP_CATEGORIES_V1",
    "ansatz_protocol_matrix_v1",
    "classify_pauli_expectation_path",
    "matrix_pauli_protocol_name",
    "matrix_qse_protocol_name",
    "mitigation_execution_model_public",
    "open_stack_differentiators_public",
    "pauli_protocol_expectation_path_for_config",
    "product_capability_map_for_docs",
    "product_gap_anchor_index_v1",
    "product_gap_categories",
    "protocol_expectation_semantics_public",
    "validate_ansatz_protocol_combo",
    "validate_pauli_protocol_for_config",
    "validate_product_gap_categories",
    "validate_qse_protocol_for_config",
]
