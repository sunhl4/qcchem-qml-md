"""Tests for UpCCGSD, pUCCD, staggered pools, and P4 ansatz extensions."""

from __future__ import annotations

import math

import pytest

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.quantum.operator_pool_registry import (
    build_registered_operator_pool,
    resolve_operator_pool_id,
)
from tests.helpers.h2_yaml import H2_STO3G_FCI_ENERGY
from tests.helpers.paths import configs_path


@pytest.mark.parametrize(
    "config_rel",
    ["example_h2_upccgsd.yaml", "example_h2_puccd.yaml"],
)
def test_upccgsd_puccd_yaml_energy_window(config_rel: str) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    e = float(out["energy_after_variational"])
    assert e < -0.5
    assert e >= H2_STO3G_FCI_ENERGY - 0.15
    assert math.isfinite(e)


def test_staggered_pool_registered_and_non_empty() -> None:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

    qh = QubitHamiltonian(
        operator=QubitOperator((), 0.0),
        n_qubits=4,
        fermion_space=FermionSpace(4, 2),
    )
    canonical = resolve_operator_pool_id("fermionic_singles_doubles_staggered")
    assert canonical == "fermionic_singles_doubles_staggered"
    pool = build_registered_operator_pool(canonical, qh)
    assert len(pool) >= 2
