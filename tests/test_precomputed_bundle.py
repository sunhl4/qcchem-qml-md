from __future__ import annotations

import json
from pathlib import Path

import pytest

from qchem_stack.chem.precomputed_bundle import (
    CLASSICAL_REFERENCE_BUNDLE_V1,
    load_bundle_dict,
    molecular_mean_field_result_from_bundle,
    parse_precomputed_manifest,
    qubit_hamiltonian_from_bundle,
)


def _write_bundle(path: Path) -> None:
    payload = {
        "schema": CLASSICAL_REFERENCE_BUNDLE_V1,
        "classical_reference": {
            "e_tot": -1.0,
            "mo_energy": [-0.5, 0.2],
            "driver_meta": {"upstream_classical_software_tag": "dataset_demo"},
        },
        "pre_quantum_input": {
            "schema": "pre_quantum_input_v1",
            "qubit_hamiltonian": {
                "n_qubits": 2,
                "terms": [
                    {"label": "II", "coeff": -0.5},
                    {"label": "ZZ", "coeff": 0.25},
                ],
            },
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_bundle_dict_accepts_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    path, data = load_bundle_dict(str(root / "configs" / "precomputed_classical_reference_h2.json"))
    assert path.name == "precomputed_classical_reference_h2.json"
    assert data["schema"] == CLASSICAL_REFERENCE_BUNDLE_V1


def test_molecular_mean_field_result_from_bundle(tmp_path: Path) -> None:
    p = tmp_path / "bundle.json"
    _write_bundle(p)
    out = molecular_mean_field_result_from_bundle(str(p))
    assert out.e_tot == pytest.approx(-1.0)
    assert out.mo_energy.shape == (2,)
    assert out.driver_meta["driver_family"] == "precomputed"


def test_qubit_hamiltonian_from_bundle_indexed_labels(tmp_path: Path) -> None:
    p = tmp_path / "bundle_indexed.json"
    payload = {
        "schema": CLASSICAL_REFERENCE_BUNDLE_V1,
        "classical_reference": {
            "e_tot": -1.0,
            "mo_energy": [-0.5, 0.2],
        },
        "pre_quantum_input": {
            "qubit_hamiltonian": {
                "n_qubits": 2,
                "terms": [
                    {"label": "I", "coeff": -1.0},
                    {"label": "Z0 Z1", "coeff": 0.5},
                ],
            },
        },
    }
    p.write_text(json.dumps(payload), encoding="utf-8")
    qh = qubit_hamiltonian_from_bundle(str(p))
    assert qh.n_qubits == 2
    assert len(qh.operator.terms) == 2
    assert qh.meta["integral_source"] == CLASSICAL_REFERENCE_BUNDLE_V1
    assert qh.meta["integral_openfermion_bridge"] == "precomputed_pauli_terms_v1"
    assert len(qh.meta["hamiltonian_fingerprint"]) == 32


def test_parse_precomputed_manifest_validates_fields(tmp_path: Path) -> None:
    p = tmp_path / "bundle_with_manifest.json"
    payload = {
        "schema": CLASSICAL_REFERENCE_BUNDLE_V1,
        "manifest": {
            "schema": "precomputed_manifest_v1",
            "n_active_orbitals": 2,
            "n_active_electrons": 2,
            "fermion_qubit_mapping": "jordan_wigner",
            "n_qubits": 2,
            "molecule_symbols": ["H", "H"],
        },
        "classical_reference": {
            "e_tot": -1.0,
            "mo_energy": [-0.5, 0.2],
        },
        "pre_quantum_input": {
            "qubit_hamiltonian": {
                "n_qubits": 2,
                "terms": [
                    {"label": "I", "coeff": -1.0},
                ],
            },
        },
    }
    p.write_text(json.dumps(payload), encoding="utf-8")
    _, data = load_bundle_dict(str(p))
    manifest = parse_precomputed_manifest(data)
    assert manifest is not None
    assert manifest["n_active_orbitals"] == 2
    assert manifest["fermion_qubit_mapping"] == "jordan_wigner"


def test_qubit_hamiltonian_from_bundle_copies_manifest_mapping(tmp_path: Path) -> None:
    p = tmp_path / "bundle_with_mapping.json"
    payload = {
        "schema": CLASSICAL_REFERENCE_BUNDLE_V1,
        "manifest": {
            "schema": "precomputed_manifest_v1",
            "fermion_qubit_mapping": "bravyi_kitaev",
        },
        "classical_reference": {
            "e_tot": -1.0,
            "mo_energy": [-0.5, 0.2],
        },
        "pre_quantum_input": {
            "qubit_hamiltonian": {
                "n_qubits": 2,
                "terms": [{"label": "ZI", "coeff": 1.0}],
            },
        },
    }
    p.write_text(json.dumps(payload), encoding="utf-8")

    qh = qubit_hamiltonian_from_bundle(str(p))

    assert qh.meta["fermion_to_qubit_map"] == "bravyi_kitaev"
    assert len(qh.meta["hamiltonian_fingerprint"]) == 32
