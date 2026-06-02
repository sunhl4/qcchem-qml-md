"""Chem module shared helpers introduced during Phase 1–3 refactors."""

from __future__ import annotations

import numpy as np

from qchem_stack.chem.bridges.lowdin import build_lowdin_tensors, coalesce_spin_summed_rdm1
from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment
from qchem_stack.chem.solvers._active_space_common import resolve_active_space_spec
from qchem_stack.config import ExperimentConfig
from tests.helpers.h2_yaml import h2_yaml_dict


def test_resolve_active_space_spec_aliases() -> None:
    ncas, nelec = resolve_active_space_spec({"ncas": 2, "nelecas": 4})
    assert ncas == 2
    assert nelec == 4
    ncas2, nelec2 = resolve_active_space_spec({"n_active_orbitals": 3, "n_active_electrons": 6})
    assert ncas2 == 3
    assert nelec2 == 6


def test_molecular_system_from_experiment_geometry_source() -> None:
    cfg = ExperimentConfig.from_yaml_dict(
        h2_yaml_dict(
            experiment_id="chem_shared_helpers",
            quantum={
                "algorithm": "vqe",
                "vqe": {"depth": 1, "maxiter": 5},
                "pauli": {"use_protocol": False},
            },
        )
    )
    ms = molecular_system_from_experiment(cfg)
    assert ms.meta["geometry_source"] == "cartesian"
    assert ms.symbols == ["H", "H"]


def test_build_lowdin_tensors_identity_overlap() -> None:
    s = np.eye(2)
    h = np.array([[1.0, 0.2], [0.2, 2.0]])
    d = np.array([[1.0, 0.0], [0.0, 0.0]])
    lowdin = build_lowdin_tensors(s, h, d)
    assert np.allclose(lowdin.h1_low, h)
    assert np.allclose(lowdin.dm_low, d)


def test_coalesce_spin_summed_rdm1() -> None:
    a = np.eye(2)
    b = np.zeros((2, 2))
    out = coalesce_spin_summed_rdm1((a, b))
    assert np.allclose(out, a)
