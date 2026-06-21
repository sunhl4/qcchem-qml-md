"""RDMBundle v2 lineage tags and :class:`QuantumRDMInput` protocol."""

from __future__ import annotations

import numpy as np
import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.kernels.rdm_corrections import rdm_bundle_from_mean_field
from qchem_stack.chem.rdm_bundle import QuantumRDMInput, RDMBundle
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def test_rdm_bundle_requires_lineage_tags() -> None:
    dm = np.eye(2)
    with pytest.raises(ValueError, match="rdm_basis"):
        RDMBundle(rdm1_spatial=dm, rdm_basis="", rdm_source="x", spin_model="restricted")
    with pytest.raises(ValueError, match="square"):
        RDMBundle(rdm1_spatial=dm[:1], rdm_basis="a", rdm_source="b", spin_model="restricted")


def test_rdm_bundle_metadata_syncs_canonical_fields() -> None:
    dm = np.eye(2)
    b = RDMBundle(
        rdm1_spatial=dm,
        rdm_basis="spatial_ao_test",
        rdm_source="unit_test_source",
        spin_model="restricted",
        metadata={"custom": True},
    )
    assert b.metadata["schema"] == "rdm_bundle_v2"
    assert b.metadata["custom"] is True
    assert b.metadata["rdm_basis"] == "spatial_ao_test"
    assert b.metadata["source"] == "unit_test_source"
    assert b.metadata["spin_model"] == "restricted"


def test_rdm_bundle_from_mean_field_matches_protocol() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    bundle = rdm_bundle_from_mean_field(ref)
    assert isinstance(bundle, QuantumRDMInput)
    assert bundle.rdm_basis == "spatial_ao_pyscf"
    assert bundle.rdm_source == "pyscf_scf_rdm1"
    assert bundle.spin_model == "restricted"
    assert bundle.metadata["schema"] == "rdm_bundle_v2"
