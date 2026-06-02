"""Per-run cache for expensive pre-quantum integral builds (chem layer)."""

from __future__ import annotations

import hashlib
import json
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.config.active_space_helpers import resolve_n_electrons, resolve_n_orbitals
from qchem_stack.contracts.schema_ids import RUN_BUILD_CACHE_V1
from qchem_stack.repro.export import repro_dict_for_strict_json

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
    safe = repro_dict_for_strict_json(data, _path="driver_meta")
    canonical = json.dumps(
        safe, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
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
        n_active_orbitals if n_active_orbitals is not None else resolve_n_orbitals(cfg.active_space)
    )
    ne = int(
        n_active_electrons
        if n_active_electrons is not None
        else resolve_n_electrons(cfg.active_space)
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
    pack_spills: int = 0
    spill_dir: Path | None = field(default=None)

    def __post_init__(self) -> None:
        if self.spill_dir is None:
            raw = __import__("os").environ.get("QCHEM_RUN_BUILD_CACHE_SPILL_DIR", "").strip()
            if raw:
                self.spill_dir = Path(raw)
                self.spill_dir.mkdir(parents=True, exist_ok=True)

    def _spill_path(self, key: str) -> Path | None:
        if self.spill_dir is None:
            return None
        return self.spill_dir / f"{key}.pkl"

    def _load_spilled(self, key: str) -> CanonicalActiveSpaceIntegralPack | None:
        path = self._spill_path(key)
        if path is None or not path.is_file():
            return None
        with path.open("rb") as fh:
            return pickle.load(fh)

    def _spill_pack(self, key: str, pack: CanonicalActiveSpaceIntegralPack) -> None:
        path = self._spill_path(key)
        if path is None:
            return
        with path.open("wb") as fh:
            pickle.dump(pack, fh, protocol=pickle.HIGHEST_PROTOCOL)
        self.pack_spills += 1

    def get_or_build_pack(
        self,
        key: str,
        builder: Callable[[], CanonicalActiveSpaceIntegralPack],
    ) -> CanonicalActiveSpaceIntegralPack:
        if key in self.packs:
            self.pack_hits += 1
            return self.packs[key]
        spilled = self._load_spilled(key)
        if spilled is not None:
            self.packs[key] = spilled
            self.pack_hits += 1
            return spilled
        pack = builder()
        max_packs = int(__import__("os").environ.get("QCHEM_RUN_BUILD_CACHE_MAX_PACKS", "0") or "0")
        if max_packs > 0 and len(self.packs) >= max_packs:
            oldest_key = next(iter(self.packs))
            self._spill_pack(oldest_key, self.packs.pop(oldest_key))
        self.packs[key] = pack
        self.pack_builds += 1
        return pack

    def stats_dict(self) -> dict[str, Any]:
        return {
            "schema": RUN_BUILD_CACHE_V1,
            "pack_count": len(self.packs),
            "pack_hits": int(self.pack_hits),
            "pack_builds": int(self.pack_builds),
            "pack_spills": int(self.pack_spills),
            "spill_dir": str(self.spill_dir) if self.spill_dir else None,
        }
