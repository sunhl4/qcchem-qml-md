"""Unit tests for md_bridge.from_pipeline_extract (mock PipelineOut, no full pipeline)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.from_pipeline_extract import (
    as_out_dict,
    config_sha_prefix,
    energy_hartree_from_pipeline_out,
    normalize_coords,
    protocol_hash_prefix,
)


def test_normalize_coords_casts_to_float() -> None:
    assert normalize_coords([[0, 0, 0], [0, 0, 1.4]]) == [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]


def test_as_out_dict_accepts_plain_dict() -> None:
    out = {"scf_energy": -1.0}
    assert as_out_dict(out) is out


def test_protocol_hash_prefix_from_parity_snapshot() -> None:
    out = {
        "repro": {
            "parity_snapshot": {"compiler_bundle_signature": "abc123def456"},
            "config_sha256_prefix": "deadbeef",
        }
    }
    assert protocol_hash_prefix(out) == "abc123def456"
    assert config_sha_prefix(out) == "deadbeef"


def test_protocol_hash_prefix_missing_repro() -> None:
    assert protocol_hash_prefix({}) == ""
    assert config_sha_prefix({}) == ""


def test_energy_hartree_variational_default() -> None:
    from qchem_stack.config import ExperimentConfig

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    out = {"energy_after_variational": -0.5}
    assert energy_hartree_from_pipeline_out(cfg, out) == -0.5


def test_energy_hartree_scf_reference() -> None:
    from qchem_stack.config import ExperimentConfig, MdMlExportSpec

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
            "md_ml_export": MdMlExportSpec(energy_reference="scf").model_dump(),
        }
    )
    out = {"scf_energy": -1.1, "energy_after_variational": -0.5}
    assert energy_hartree_from_pipeline_out(cfg, out) == -1.1


def test_energy_hartree_missing_variational_raises() -> None:
    from qchem_stack.config import ExperimentConfig

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    with pytest.raises(PipelineError, match="energy_after_variational"):
        energy_hartree_from_pipeline_out(cfg, {})


def test_active_space_digest_stable() -> None:
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.md_bridge.from_pipeline_extract import active_space_digest

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    d1 = active_space_digest(cfg)
    d2 = active_space_digest(cfg)
    assert len(d1) == 16
    assert d1 == d2


def test_energy_hartree_pauli_protocol() -> None:
    from qchem_stack.config import ExperimentConfig, MdMlExportSpec

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
            "md_ml_export": MdMlExportSpec(energy_reference="pauli_protocol").model_dump(),
        }
    )
    out = {"energy_pauli_protocol": -0.42}
    assert energy_hartree_from_pipeline_out(cfg, out) == -0.42


def test_as_pyscf_rhf_rejects_non_pyscf_backend() -> None:
    from unittest.mock import MagicMock

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.md_bridge.from_pipeline_extract import as_pyscf_rhf

    ref = MagicMock(spec=ClassicalMeanFieldReference)
    ref.backend_tag.return_value = "psi4"
    with pytest.raises(PipelineError, match="PySCF-backed"):
        as_pyscf_rhf(ref)


def test_is_periodic_rhf_from_driver_meta() -> None:
    from qchem_stack.md_bridge.from_pipeline_extract import is_periodic_rhf

    rhf = MagicMock()
    rhf.driver_meta = {"pbc": True}
    rhf.mf.mol = MagicMock()
    type(rhf.mf.mol).__name__ = "Mole"
    assert is_periodic_rhf(rhf) is True
