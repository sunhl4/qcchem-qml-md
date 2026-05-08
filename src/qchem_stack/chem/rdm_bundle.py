from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class QuantumRDMInput(Protocol):
    """Minimal contract for downstream RDM / correction kernels (implementations wrap :class:`RDMBundle`)."""

    rdm1_spatial: np.ndarray
    rdm_basis: str
    rdm_source: str
    spin_model: Literal["restricted", "unrestricted"]


SpinModelLit = Literal["restricted", "unrestricted"]


@dataclass
class RDMBundle:
    """
    Machine-readable reduced-density-matrix container.

    ``rdm_basis``, ``rdm_source``, ``spin_model`` are required lineage tags on top of numerical
    data. Canonical keys are synced into :attr:`metadata` for JSON export.
    """

    rdm1_spatial: np.ndarray
    rdm_basis: str
    rdm_source: str
    spin_model: SpinModelLit
    rdm2_spatial: np.ndarray | None = None
    rdm3_spatial: np.ndarray | None = None
    rdm4_spatial: np.ndarray | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        rdm_basis = str(self.rdm_basis).strip()
        rdm_source = str(self.rdm_source).strip()
        if not rdm_basis:
            raise ValueError("RDMBundle.rdm_basis must be a non-empty string.")
        if not rdm_source:
            raise ValueError("RDMBundle.rdm_source must be a non-empty string.")
        self.rdm_basis = rdm_basis
        self.rdm_source = rdm_source
        if self.spin_model not in ("restricted", "unrestricted"):
            raise ValueError("RDMBundle.spin_model must be 'restricted' or 'unrestricted'.")
        r1 = np.asarray(self.rdm1_spatial, dtype=float)
        if r1.ndim != 2 or r1.shape[0] != r1.shape[1]:
            raise ValueError("RDMBundle.rdm1_spatial must be a square 2D array.")
        self.rdm1_spatial = r1
        for name in ("rdm2_spatial", "rdm3_spatial", "rdm4_spatial"):
            v = getattr(self, name)
            if v is None:
                continue
            setattr(self, name, np.asarray(v, dtype=float))

        base_meta = dict(self.metadata)
        self.metadata = {
            **base_meta,
            "schema": "rdm_bundle_v2",
            "rdm_basis": self.rdm_basis,
            "rdm_source": self.rdm_source,
            "spin_model": self.spin_model,
            "source": self.rdm_source,
            "n_spatial_orbitals": int(base_meta.get("n_spatial_orbitals", r1.shape[0])),
        }
