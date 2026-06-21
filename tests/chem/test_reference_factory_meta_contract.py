"""``reference_factory`` driver_meta contract (replaces legacy PySCFDriver meta tests)."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges.reference_factory import classical_mean_field_reference_from_config
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def _required_meta_keys() -> set[str]:
    return {
        "driver_meta_schema_version",
        "driver_family",
        "scf_method",
        "integral_representation",
        "solvent_model",
        "ddcosmo_epsilon",
        "pbc",
        "pbc_kpoint_mesh",
        "pbc_active_space_kpoint_index",
        "energy_accounting_model",
        "pyscf_version",
        "scf_chkfile",
        "scf_init_guess",
        "scf_level_shift",
        "scf_use_newton",
        "scf_diis_space_dimension",
        "canonical_classical_bridge_schema",
        "canonical_classical_bridge_meta_version",
        "upstream_classical_software_tag",
        "canonical_classical_stage",
        "classical_problem_periodic_boundary_condition",
    }


def test_driver_meta_contract_molecular_rhf(tmp_path) -> None:
    cfg_path = tmp_path / "h2_mol.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: h2_mol_meta
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    r = pyscf_rhf_from_config(cfg)
    meta = r.driver_meta
    assert _required_meta_keys() <= set(meta.keys())
    assert meta["driver_meta_schema_version"] == 1
    assert meta["driver_family"] == "pyscf"
    assert meta["scf_method"] == "RHF"
    assert meta["integral_representation"] == "mo"
    assert meta["solvent_model"] == "none"
    assert meta["ddcosmo_epsilon"] is None
    assert meta["pbc"] is False
    assert meta["pbc_kpoint_mesh"] is None
    assert meta["pbc_active_space_kpoint_index"] is None
    assert meta["energy_accounting_model"] == "mf_e_tot_direct"
    assert isinstance(meta["pyscf_version"], str) and len(meta["pyscf_version"]) > 0
    assert meta["classical_problem_periodic_boundary_condition"] is False


def test_driver_meta_contract_pbc_rhf() -> None:
    cfg = load_experiment_config(configs_path("example_h2_pbc_gamma.yaml"))
    ref = classical_mean_field_reference_from_config(cfg)
    meta = ref.driver_meta
    assert _required_meta_keys() <= set(meta.keys())
    assert meta["driver_meta_schema_version"] == 1
    assert meta["driver_family"] == "pyscf"
    assert meta["scf_method"] == "RHF"
    assert meta["solvent_model"] == "none"
    assert meta["pbc"] is True
    assert meta["pbc_kpoint_mesh"] == [1, 1, 1]
    assert meta["pbc_active_space_kpoint_index"] == 0
    assert meta["energy_accounting_model"] == "mf_e_tot_direct"
    assert isinstance(meta["pyscf_version"], str) and len(meta["pyscf_version"]) > 0
    assert meta["classical_problem_periodic_boundary_condition"] is True
