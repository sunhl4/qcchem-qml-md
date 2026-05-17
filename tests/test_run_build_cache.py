"""RunBuildCache avoids duplicate canonical pack construction within one pipeline run."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.run_build_cache import RunBuildCache, pack_cache_key
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.scf_stage import run_scf_reference


@pytest.mark.pyscf
def test_canonical_pack_cache_hit_on_second_build() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = run_scf_reference(cfg)
    cache = RunBuildCache()
    calls = {"n": 0}
    real = CanonicalActiveSpaceIntegralPack.from_classical_reference

    def _counting(*args: object, **kwargs: object) -> CanonicalActiveSpaceIntegralPack:
        calls["n"] += 1
        return real(*args, **kwargs)

    with patch.object(CanonicalActiveSpaceIntegralPack, "from_classical_reference", _counting):
        build_pre_quantum_input_with_context(cfg, rhf, cache=cache)
        build_pre_quantum_input_with_context(cfg, rhf, cache=cache)
    assert calls["n"] == 1
    assert cache.pack_builds == 1
    assert cache.pack_hits == 1


@pytest.mark.pyscf
def test_pipeline_exposes_build_cache_stats() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    out = run_pipeline_sync(cfg, cfg_path=root / "configs" / "example_h2.yaml")
    stats = out.get("pre_quantum_build_cache") or {}
    assert stats.get("schema") == "run_build_cache_v1"
    assert int(stats.get("pack_builds", 0)) >= 1
    assert out["hamiltonian_meta"].get("scf_energy_au") == pytest.approx(float(out["scf_energy"]))


@pytest.mark.pyscf
def test_pack_cache_key_defaults_match_explicit_and_changes_with_active_space() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = run_scf_reference(cfg)

    default_key = pack_cache_key(cfg, rhf)
    explicit_key = pack_cache_key(
        cfg,
        rhf,
        n_active_orbitals=int(cfg.active_space.n_active_orbitals),
        n_active_electrons=int(cfg.active_space.n_active_electrons),
    )
    assert default_key == explicit_key

    changed_key = pack_cache_key(
        cfg,
        rhf,
        n_active_orbitals=int(cfg.active_space.n_active_orbitals) + 1,
        n_active_electrons=int(cfg.active_space.n_active_electrons),
    )
    assert changed_key != default_key


@pytest.mark.pyscf
def test_pack_cache_key_changes_with_driver_meta_and_geometry() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = run_scf_reference(cfg)
    key_ref = pack_cache_key(cfg, rhf)

    rhf_meta = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy.copy(),
        molecular_system=rhf.molecular_system,
        driver_meta={**dict(rhf.driver_meta), "custom_meta_for_cache_test": "changed"},
    )
    key_meta = pack_cache_key(cfg, rhf_meta)
    assert key_meta != key_ref

    ms = rhf.molecular_system
    ms_shift = ms.coordinates_bohr.copy()
    ms_shift[0, 0] += 1e-3
    rhf_geom = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy.copy(),
        molecular_system=type(ms)(
            symbols=list(ms.symbols),
            coordinates_bohr=ms_shift,
            charge=int(ms.charge),
            multiplicity=int(ms.multiplicity),
            basis=str(ms.basis),
            ecp=ms.ecp,
            meta=dict(ms.meta),
        ),
        driver_meta=dict(rhf.driver_meta),
    )
    key_geom = pack_cache_key(cfg, rhf_geom)
    assert key_geom != key_ref
