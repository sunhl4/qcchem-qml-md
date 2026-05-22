from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.integrals.pyscf_onebody import (
    one_electron_operator_fermion_from_rhf,
    one_electron_operator_pauli_from_rhf,
)
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def test_one_electron_operator_fermion_and_pauli_hcore() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = pyscf_rhf_from_config(cfg)
    fop = one_electron_operator_fermion_from_rhf(rhf, "hcore")
    assert hasattr(fop, "terms")
    assert len(fop.terms) > 0
    qop = one_electron_operator_pauli_from_rhf(rhf, "hcore")
    assert hasattr(qop, "terms")


def test_one_electron_operator_vector_shapes() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = pyscf_rhf_from_config(cfg)
    r_ops = one_electron_operator_fermion_from_rhf(rhf, "r")
    dm_ops = one_electron_operator_fermion_from_rhf(rhf, "dm")
    rr_ops = one_electron_operator_fermion_from_rhf(rhf, "rr")
    assert isinstance(r_ops, list) and len(r_ops) == 3
    assert isinstance(dm_ops, list) and len(dm_ops) == 3
    assert isinstance(rr_ops, list) and len(rr_ops) == 9
