"""Standard ``driver_meta`` fields for multi-backend classical chemistry."""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.kernels.catalog import (
    KERNEL_AVAS_PROJECTION,
    KERNEL_CASCI_ACTIVE_INTEGRALS,
    KERNEL_MEAN_FIELD_SCF,
    KERNEL_NEVPT2_CASCI,
    KernelBinding,
    kernel_binding,
)

DRIVER_META_SCHEMA_VERSION = 1


def merge_integration_driver_meta(
    base: dict[str, Any] | None,
    *,
    backend_tag: str,
    driver_family: str | None = None,
    kernel_bindings: list[KernelBinding] | None = None,
    epistemic_bound: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge canonical multi-backend bookkeeping into solver ``driver_meta``."""
    out = dict(base or {})
    out["driver_meta_schema_version"] = DRIVER_META_SCHEMA_VERSION
    out["upstream_classical_software_tag"] = str(backend_tag)
    out.setdefault("driver_family", driver_family or str(backend_tag))
    if kernel_bindings:
        append_kernel_bindings(out, kernel_bindings)
    if epistemic_bound:
        out["epistemic_bound"] = str(epistemic_bound)
    if extra:
        out.update(extra)
    return out


def append_kernel_bindings(
    meta: dict[str, Any],
    bindings: list[KernelBinding],
) -> None:
    """Append kernel rows; later entries with the same ``kernel_id`` replace earlier ones."""
    rows: list[dict[str, Any]] = list(meta.get("kernel_bindings") or [])
    index = {str(r.get("kernel_id")): i for i, r in enumerate(rows) if r.get("kernel_id")}
    for kb in bindings:
        row = kb.as_dict()
        kid = str(row.get("kernel_id"))
        if kid in index:
            rows[index[kid]] = row
        else:
            index[kid] = len(rows)
            rows.append(row)
    meta["kernel_bindings"] = rows


def binding_mean_field_scf(
    provider: str,
    implementation_id: str,
    *,
    native: bool,
) -> KernelBinding:
    return kernel_binding(
        KERNEL_MEAN_FIELD_SCF,
        provider=provider,
        implementation_id=implementation_id,
        native=native,
    )


def binding_casci_active_integrals(
    provider: str,
    implementation_id: str,
    *,
    native: bool,
) -> KernelBinding:
    return kernel_binding(
        KERNEL_CASCI_ACTIVE_INTEGRALS,
        provider=provider,
        implementation_id=implementation_id,
        native=native,
    )


def binding_avas_projection(
    provider: str,
    implementation_id: str,
    *,
    native: bool,
) -> KernelBinding:
    return kernel_binding(
        KERNEL_AVAS_PROJECTION,
        provider=provider,
        implementation_id=implementation_id,
        native=native,
    )


def binding_nevpt2_casci(
    provider: str,
    implementation_id: str,
    *,
    native: bool,
) -> KernelBinding:
    return kernel_binding(
        KERNEL_NEVPT2_CASCI,
        provider=provider,
        implementation_id=implementation_id,
        native=native,
    )


def record_casci_active_integrals_binding(
    reference_meta: dict[str, Any],
    pack: Any,
) -> None:
    """Record ``casci_active_integrals`` from canonical pack provenance (post-cache safe)."""
    prov = getattr(pack, "provenance", None) or {}
    if not isinstance(prov, dict):
        prov = {}
    tag = str(
        prov.get("classical_backend")
        or reference_meta.get("upstream_classical_software_tag")
        or "unknown"
    )
    impl = str(
        prov.get("casci_implementation_id")
        or getattr(getattr(pack, "compact", None), "storage_schema", None)
        or f"{tag}_casci_v1"
    )
    append_kernel_bindings(
        reference_meta,
        [binding_casci_active_integrals(tag, impl, native=True)],
    )


def merge_rdm_correction_bindings_into_reference(
    reference_meta: dict[str, Any],
    correction_report: dict[str, Any],
) -> None:
    """Copy NEVPT2 kernel metadata from an RDM correction report into reference ``driver_meta``."""
    impl = correction_report.get("kernel_class")
    for key in ("nevpt2", "pyscf_nevpt2", "psi4_nevpt2"):
        block = correction_report.get(key)
        if not isinstance(block, dict) or block.get("status") != "ok":
            continue
        provider = "pyscf" if key.startswith("pyscf") else str(key).split("_", 1)[0]
        append_kernel_bindings(
            reference_meta,
            [
                binding_nevpt2_casci(
                    provider,
                    str(block.get("implementation_id") or impl or "nevpt2_casci"),
                    native=provider == reference_meta.get("upstream_classical_software_tag"),
                )
            ],
        )
        break
