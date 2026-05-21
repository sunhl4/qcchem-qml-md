"""Cross-field validation helpers for :mod:`qchem_stack.config.scf`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .scf_enums import ScfDriverId
from .scf_helpers import resolve_scf_density_fit, resolve_scf_density_fit_auxbasis

if TYPE_CHECKING:
    from .scf import SCFSpec


def validate_density_fit_auxbasis_consistency(spec: SCFSpec) -> None:
    if resolve_scf_density_fit_auxbasis(spec) and not resolve_scf_density_fit(spec):
        raise ValueError("scf.density_fit_auxbasis requires scf.density_fit=true.")


def validate_precomputed_bundle_requirements(spec: SCFSpec) -> None:
    raw = spec.precomputed.bundle_path
    if raw is not None:
        raw = str(raw).strip()
    spec.precomputed.bundle_path = raw or None
    if spec.driver == ScfDriverId.PRECOMPUTED.value and not spec.precomputed.bundle_path:
        raise ValueError(
            "scf.driver='precomputed' requires scf.precomputed.bundle_path to be non-empty."
        )
    if spec.driver != ScfDriverId.PRECOMPUTED.value and spec.precomputed.bundle_path:
        raise ValueError("scf.precomputed.bundle_path is only valid when scf.driver='precomputed'.")
