"""Catalog of shared kernel ids used in ``driver_meta.kernel_bindings``."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class KernelBinding:
    """One row in ``driver_meta['kernel_bindings']`` describing who ran a step."""

    kernel_id: str
    provider: str
    implementation_id: str
    native: bool
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        if out.get("note") is None:
            out.pop("note", None)
        return out


def kernel_binding(
    kernel_id: str,
    *,
    provider: str,
    implementation_id: str,
    native: bool,
    note: str | None = None,
) -> KernelBinding:
    return KernelBinding(
        kernel_id=kernel_id,
        provider=provider,
        implementation_id=implementation_id,
        native=native,
        note=note,
    )


# Stable kernel_id strings — referenced in docs and driver_meta.
KERNEL_MEAN_FIELD_SCF = "mean_field_scf"
KERNEL_CASCI_ACTIVE_INTEGRALS = "casci_active_integrals"
KERNEL_AVAS_PROJECTION = "avas_projection"
KERNEL_NEVPT2_CASCI = "nevpt2_casci"
KERNEL_QUBIT_FERMION_MAP = "qubit_fermion_map"

_KNOWN: tuple[str, ...] = (
    KERNEL_MEAN_FIELD_SCF,
    KERNEL_CASCI_ACTIVE_INTEGRALS,
    KERNEL_AVAS_PROJECTION,
    KERNEL_NEVPT2_CASCI,
    KERNEL_QUBIT_FERMION_MAP,
)


def list_known_kernels() -> list[str]:
    return list(_KNOWN)
