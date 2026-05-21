"""Per-run cache for expensive pre-quantum integral builds (chem layer)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.contracts.schema_ids import RUN_BUILD_CACHE_V1

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def _array_digest(arr: np.ndarray) -> str:
    payload = np.ascontiguousarray(arr)
    return hashlib.sha256(payload.view(np.uint8).tobytes()).hexdigest()[:24]


def _driver_meta_digest(ref: ClassicalMeanFieldReference) -> str:
    data = dict(ref.driver_meta or {})
    for key in ("kernel_bindings", "integral_crosscheck_casci_v1"):
        data.pop(key, None)
    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _molecule_digest(ref: ClassicalMeanFieldReference) -> str:
    ms = ref.molecular_system
    symbols = [str(x) for x in ms.symbols]
    coords = np.asarray(ms.coordinates_bohr, dtype=float)
    payload = {
        "symbols": symbols,
        "coords_sha": _array_digest(coords),
        "charge": int(ms.charge),
        "multiplicity": int(ms.multiplicity),
        "basis": str(ms.basis),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _mf_checksum(ref: ClassicalMeanFieldReference) -> str:
    e = float(ref.e_tot)
    mo = np.asarray(ref.mo_energy, dtype=float)
    tag = ref.backend_tag()
    raw = (
        f"{tag}|{e:.12f}|mo_shape={tuple(int(x) for x in mo.shape)}|"
        f"mo_sha={_array_digest(mo)}|driver_meta_sha={_driver_meta_digest(ref)}|"
        f"molecule_sha={_molecule_digest(ref)}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _resolved_active_space_counts(
    cfg: ExperimentConfig,
    *,
    n_active_orbitals: int | None,
    n_active_electrons: int | None,
) -> tuple[int, int]:
    na = int(
        n_active_orbitals if n_active_orbitals is not None else cfg.active_space.cas.n_orbitals
    )
    ne = int(
        n_active_electrons if n_active_electrons is not None else cfg.active_space.cas.n_electrons
    )
    return na, ne


def _pack_cache_key_material(
    cfg: ExperimentConfig,
    ref: ClassicalMeanFieldReference,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> str:
    return (
        f"{cfg.experiment_id}|{cfg.scf.driver}|{cfg.scf.method}|"
        f"{n_active_orbitals}|{n_active_electrons}|"
        f"{cfg.active_space.mapping.fermion_qubit}|{_mf_checksum(ref)}"
    )


def pack_cache_key(
    cfg: ExperimentConfig,
    ref: ClassicalMeanFieldReference,
    *,
    n_active_orbitals: int | None = None,
    n_active_electrons: int | None = None,
) -> str:
    na, ne = _resolved_active_space_counts(
        cfg,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
    )
    raw = _pack_cache_key_material(
        cfg,
        ref,
        n_active_orbitals=na,
        n_active_electrons=ne,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


@dataclass
class RunBuildCache:
    """Caches canonical integral packs within a single pipeline invocation."""

    packs: dict[str, CanonicalActiveSpaceIntegralPack] = field(default_factory=dict)
    pack_hits: int = 0
    pack_builds: int = 0

    def get_or_build_pack(
        self,
        key: str,
        builder: Callable[[], CanonicalActiveSpaceIntegralPack],
    ) -> CanonicalActiveSpaceIntegralPack:
        if key in self.packs:
            self.pack_hits += 1
            return self.packs[key]
        pack = builder()
        self.packs[key] = pack
        self.pack_builds += 1
        return pack

    def stats_dict(self) -> dict[str, Any]:
        return {
            "schema": RUN_BUILD_CACHE_V1,
            "pack_count": len(self.packs),
            "pack_hits": int(self.pack_hits),
            "pack_builds": int(self.pack_builds),
        }
