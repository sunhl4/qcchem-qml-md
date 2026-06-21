"""Reference factory and driver_meta helper tests."""

from __future__ import annotations

import pytest

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta, readonly_driver_meta
from qchem_stack.config import ExperimentConfig
from tests.helpers.h2_yaml import h2_yaml_dict


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
        h2_yaml_dict(
            experiment_id="ref_factory_h2",
            quantum={
                "algorithm": "vqe",
                "vqe": {"depth": 1, "maxiter": 5},
                "pauli": {"use_protocol": False},
            },
        )
    )
    ref = classical_mean_field_reference_from_config(cfg)
    assert ref.backend_tag() == "pyscf"
    assert ref.molecular_system.meta.get("geometry_source") == "cartesian"
    assert ref.driver_meta.get("active_space_strategy") == "cas"
    assert isinstance(ref.driver_meta.get("active_space_recipe"), str)
    rhf = pyscf_rhf_result_from_config(cfg)
    assert float(rhf.e_tot) == pytest.approx(float(ref.e_tot))
