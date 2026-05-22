"""Thin L3 dispatch helpers (record bindings + delegate to active_space / integrations)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.active_space.backend_hooks import apply_avas_to_reference
from qchem_stack.chem.integration.meta_schema import (
    append_kernel_bindings,
    binding_mean_field_scf,
)
from qchem_stack.chem.kernels.catalog import KERNEL_MEAN_FIELD_SCF
from qchem_stack.chem.kernels.rdm_corrections import run_nevpt2_casci_correction

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def record_mean_field_binding(
    meta: dict[str, Any],
    backend_tag: str,
    implementation_id: str,
    *,
    native: bool,
) -> None:
    """Append or replace the ``mean_field_scf`` row in ``driver_meta``."""
    append_kernel_bindings(
        meta,
        [binding_mean_field_scf(str(backend_tag), str(implementation_id), native=native)],
    )


def ensure_mean_field_binding(
    meta: dict[str, Any],
    backend_tag: str,
    implementation_id: str,
    *,
    native: bool,
) -> None:
    """Record mean-field binding only when no ``mean_field_scf`` row exists yet."""
    kids = {
        str(r.get("kernel_id")) for r in (meta.get("kernel_bindings") or []) if isinstance(r, dict)
    }
    if KERNEL_MEAN_FIELD_SCF not in kids:
        record_mean_field_binding(meta, backend_tag, implementation_id, native=native)


def run_avas(cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None:
    """AVAS projection (binding recorded in ``avas_projection.apply_avas_projection``)."""
    apply_avas_to_reference(cfg, reference)


def run_nevpt2_casci(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    ncas: int,
    nelec: int,
) -> dict[str, Any]:
    """NEVPT2/CASCI correction with bindings merged into ``reference.driver_meta`` by caller."""
    report = run_nevpt2_casci_correction(reference, ncas, nelec, cfg=cfg)
    return dict(report)
