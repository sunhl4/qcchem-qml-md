"""Tests for per-run pre-quantum integral pack cache keys."""

from __future__ import annotations

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.run_build_cache import pack_cache_key
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ExperimentConfig


def _minimal_cfg() -> ExperimentConfig:
    return ExperimentConfig.model_validate(
        {
            "experiment_id": "cache_key_test",
            "molecule": {
                "symbols": ["H"],
                "coordinates": [[0, 0, 0]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "manual",
                "manual": {"n_orbitals": 1, "n_electrons": 1},
                "mapping": {"fermion_qubit": "jordan_wigner"},
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "quantum": {"algorithm": "vqe"},
            "backend": {"provider": "statevector"},
        }
    )


def _minimal_ref(*, meta_extra: dict | None = None) -> ClassicalMeanFieldReference:
    ms = MolecularSystem(
        symbols=["H"],
        coordinates_bohr=np.zeros((1, 3)),
        charge=0,
        multiplicity=1,
        basis="sto-3g",
    )
    mo = np.array([-0.5], dtype=float)
    meta = {"backend": "test", "note": "stable"}
    if meta_extra:
        meta.update(meta_extra)
    return ClassicalMeanFieldReference(
        mf=wrap_mean_field_like(
            backend_tag="test",
            raw_mf={},
            e_tot=-0.5,
            mo_energy=mo,
        ),
        e_tot=-0.5,
        mo_energy=mo,
        molecular_system=ms,
        driver_meta=meta,
    )


def test_pack_cache_key_stable_for_same_reference() -> None:
    cfg = _minimal_cfg()
    ref = _minimal_ref()
    k1 = pack_cache_key(cfg, ref)
    k2 = pack_cache_key(cfg, ref)
    assert k1 == k2
    assert len(k1) == 24


def test_pack_cache_key_changes_with_energy() -> None:
    cfg = _minimal_cfg()
    ref_a = _minimal_ref()
    ref_b = _minimal_ref()
    ref_b.e_tot = -0.6
    assert pack_cache_key(cfg, ref_a) != pack_cache_key(cfg, ref_b)


def test_driver_meta_digest_handles_numpy_scalar() -> None:
    cfg = _minimal_cfg()
    ref = _minimal_ref(meta_extra={"step": np.int64(3)})
    pack_cache_key(cfg, ref)
