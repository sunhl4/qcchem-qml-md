"""Stable classical-chemistry interchange headers (upstream QC code → qchem_stack)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta

if TYPE_CHECKING:
    from collections.abc import Mapping

# Bump when adding/removing required canonical meta keys consumed by exporters / parity.
CANONICAL_CLASSICAL_BRIDGE_META_VERSION = 1


def merge_canonical_classical_bridge_headers(
    driver_meta: Mapping[str, Any],
    *,
    upstream_software_tag: str,
    periodic_boundary_condition: bool,
) -> dict[str, Any]:
    """Merge immutable bridge bookkeeping into solver ``driver_meta`` (copies shallow)."""
    out = fork_driver_meta(driver_meta)
    out["canonical_classical_bridge_meta_version"] = int(CANONICAL_CLASSICAL_BRIDGE_META_VERSION)
    out["canonical_classical_bridge_schema"] = "qchem_classical_mean_field_bridge_v1"
    out["upstream_classical_software_tag"] = str(upstream_software_tag).strip().lower()
    out["canonical_classical_stage"] = "mean_field_completed"
    out["classical_problem_periodic_boundary_condition"] = bool(periodic_boundary_condition)
    return out
