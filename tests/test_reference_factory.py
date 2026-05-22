"""Reference factory and driver_meta helper tests."""

from __future__ import annotations

import pytest

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta, readonly_driver_meta
from qchem_stack.config import ExperimentConfig


def test_fork_driver_meta_is_mutable_copy() -> None:
    src = {"a": 1, "nested": {"b": 2}}
    view = readonly_driver_meta(src)
    fork = fork_driver_meta(view)
    fork["a"] = 99
    assert src["a"] == 1
    assert view["a"] == 1


def test_classical_mean_field_reference_from_config_h2() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.reference_factory import (
        classical_mean_field_reference_from_config,
        pyscf_rhf_result_from_config,
    )

    cfg = ExperimentConfig.from_yaml_dict(
        {
            "schema_version": "2",
            "experiment_id": "ref_factory_h2",
            "random_seed": 1,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "embedding": {"mode": "none"},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    ref = classical_mean_field_reference_from_config(cfg)
    assert ref.backend_tag() == "pyscf"
    assert ref.molecular_system.meta.get("geometry_source") == "cartesian"
    assert ref.driver_meta.get("active_space_strategy") == "cas"
    assert isinstance(ref.driver_meta.get("active_space_recipe"), str)
    rhf = pyscf_rhf_result_from_config(cfg)
    assert float(rhf.e_tot) == pytest.approx(float(ref.e_tot))
