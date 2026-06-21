"""Stable QMFrame field names for export (protocols layer; no md_bridge import)."""

from __future__ import annotations

QMFRAME_FIELD_NAMES_V1: tuple[str, ...] = (
    "active_space_hash",
    "atomic_numbers",
    "backend_noise_tag",
    "box",
    "charge",
    "energy_hartree",
    "forces_hartree_bohr",
    "method_tag",
    "multiplicity",
    "positions_bohr",
    "protocol_hash",
    "repro_config_sha256_prefix",
)


def qmframe_field_names_v1() -> list[str]:
    """Sorted QMFrame field names for md_ml_repro_freeze_fields export."""
    return sorted(QMFRAME_FIELD_NAMES_V1)


__all__ = ["QMFRAME_FIELD_NAMES_V1", "qmframe_field_names_v1"]
