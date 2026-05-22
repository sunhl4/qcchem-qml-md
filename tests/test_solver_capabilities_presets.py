"""Builtin solver capabilities must match integration presets (anti-drift contract)."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

from qchem_stack.chem.integration.presets import (
    capabilities_precomputed_offline,
    capabilities_psi4_production,
    capabilities_pyscf_production,
)
from qchem_stack.chem.solvers import create_solver
from qchem_stack.config import load_experiment_config

_CAPABILITY_BOOL_FIELDS = tuple(
    f.name for f in fields(capabilities_pyscf_production()) if f.name.startswith("supports_")
)


def test_pyscf_solver_capabilities_match_preset() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "pyscf"
    assert create_solver(cfg).capabilities == capabilities_pyscf_production()


def test_psi4_solver_capabilities_match_preset() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "psi4"
    assert create_solver(cfg).capabilities == capabilities_psi4_production()


def test_precomputed_solver_capabilities_match_preset() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_precomputed_bundle.yaml")
    assert create_solver(cfg).capabilities == capabilities_precomputed_offline()


def test_pyscf_psi4_differ_only_on_pbc_k_mesh() -> None:
    pyscf = capabilities_pyscf_production()
    psi4 = capabilities_psi4_production()
    assert pyscf.backend_id == "pyscf"
    assert psi4.backend_id == "psi4"
    assert pyscf.supports_pbc_k_mesh is True
    assert psi4.supports_pbc_k_mesh is False
    for field in _CAPABILITY_BOOL_FIELDS:
        if field == "supports_pbc_k_mesh":
            continue
        assert getattr(pyscf, field) == getattr(psi4, field), f"mismatch on {field}"
