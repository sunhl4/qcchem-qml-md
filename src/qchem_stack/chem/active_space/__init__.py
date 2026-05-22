"""Active-space strategy helpers (CAS / manual / AVAS stub honesty metadata)."""

from qchem_stack.chem.active_space.mean_field_meta import (
    AVAS_AO_LABELS_LOGGING_ONLY_META_KEY,
    AVAS_AO_LABELS_REQUESTED_META_KEY,
    AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY,
    AVAS_PARTIAL_STUB_META_KEY,
    AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1,
    AVAS_STUB_SEMANTICS_META_KEY,
    annotate_mean_field_reference_active_space,
    apply_active_space_strategy_to_mean_field_meta,
    build_active_space_recipe,
)
from qchem_stack.chem.active_space.sizing import (
    classify_mean_field_spin_symmetry,
    ncas_nelec_couplet,
)

__all__ = [
    "AVAS_AO_LABELS_LOGGING_ONLY_META_KEY",
    "AVAS_AO_LABELS_REQUESTED_META_KEY",
    "AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY",
    "AVAS_PARTIAL_STUB_META_KEY",
    "AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1",
    "AVAS_STUB_SEMANTICS_META_KEY",
    "annotate_mean_field_reference_active_space",
    "apply_active_space_strategy_to_mean_field_meta",
    "build_active_space_recipe",
    "classify_mean_field_spin_symmetry",
    "ncas_nelec_couplet",
]
