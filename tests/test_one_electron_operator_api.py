from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.config import load_experiment_config


def test_one_electron_operator_fermion_and_pauli_hcore() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    fop = drv.compute_one_electron_operator_fermion("hcore")
    assert hasattr(fop, "terms")
    assert len(fop.terms) > 0
    qop = drv.compute_one_electron_operator_pauli("hcore")
    assert hasattr(qop, "terms")


def test_one_electron_operator_vector_shapes() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    r_ops = drv.compute_one_electron_operator_fermion("r")
    dm_ops = drv.compute_one_electron_operator_fermion("dm")
    rr_ops = drv.compute_one_electron_operator_fermion("rr")
    assert isinstance(r_ops, list) and len(r_ops) == 3
    assert isinstance(dm_ops, list) and len(dm_ops) == 3
    assert isinstance(rr_ops, list) and len(rr_ops) == 9
