from __future__ import annotations

import json

import pytest

from qchem_stack.config import load_experiment_config


def test_density_fit_auxbasis_requires_density_fit(tmp_path) -> None:
    p = tmp_path / "bad_density_fit.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_density_fit
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
  density_fit_auxbasis: weigend
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="density_fit_auxbasis requires scf.density_fit"):
        load_experiment_config(p)


def test_molecule_coordinates_and_zmatrix_mutually_exclusive(tmp_path) -> None:
    p = tmp_path / "bad_geom.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_bad_geom
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  zmatrix: |
    H
    H 1 0.74
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        load_experiment_config(p)


def test_precomputed_driver_requires_bundle_path(tmp_path) -> None:
    p = tmp_path / "bad_precomputed_missing_path.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_precomputed_missing_path
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: precomputed
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="requires scf.precomputed_bundle_path"):
        load_experiment_config(p)


def test_precomputed_bundle_path_forbidden_for_non_precomputed_driver(tmp_path) -> None:
    p = tmp_path / "bad_precomputed_path_on_live_driver.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_precomputed_forbidden
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
  precomputed_bundle_path: configs/precomputed_classical_reference_h2.json
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="only valid when scf.driver='precomputed'"):
        load_experiment_config(p)


def test_precomputed_bundle_path_resolves_relative_to_yaml_dir(tmp_path) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text(
        json.dumps(
            {
                "schema": "classical_reference_bundle_v1",
                "classical_reference": {"e_tot": -1.0, "mo_energy": [-0.5, 0.2]},
                "pre_quantum_input": {
                    "qubit_hamiltonian": {
                        "n_qubits": 2,
                        "terms": [{"label": "II", "coeff": -0.5}],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    p = tmp_path / "ok_precomputed_relative.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_precomputed_relative
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: precomputed
  method: RHF
  precomputed_bundle_path: bundle.json
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(p)
    assert cfg.scf.precomputed_bundle_path == str(bundle.resolve())
