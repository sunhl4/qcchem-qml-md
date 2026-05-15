from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.precomputed_bundle import (
    load_bundle_dict,
    parse_precomputed_manifest,
    qubit_hamiltonian_from_bundle_payload,
    resolve_bundle_path,
)
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError


def is_precomputed_driver(cfg: ExperimentConfig) -> bool:
    return str(cfg.scf.driver).strip().lower() == "precomputed"


def normalize_precomputed_bundle_path(
    cfg: ExperimentConfig, *, cfg_path: Path | None
) -> ExperimentConfig:
    if not is_precomputed_driver(cfg):
        return cfg
    raw = str(cfg.scf.precomputed_bundle_path or "").strip()
    if not raw:
        return cfg
    resolved = resolve_bundle_path(raw, cfg_path=cfg_path)
    return cfg.model_copy(
        update={"scf": cfg.scf.model_copy(update={"precomputed_bundle_path": str(resolved)})}
    )


def precomputed_config_fingerprint_payload(cfg: ExperimentConfig) -> dict[str, Any]:
    coords_bohr = np.asarray(cfg.molecule.coordinates_in_bohr(), dtype=float)
    rounded = [[round(float(x), 12) for x in row] for row in coords_bohr.tolist()]
    return {
        "schema": "precomputed_config_fingerprint_v1",
        "molecule_symbols": [str(x) for x in cfg.molecule.symbols],
        "molecule_coordinates_bohr": rounded,
        "charge": int(cfg.molecule.charge),
        "multiplicity": int(cfg.molecule.multiplicity),
        "basis": str(cfg.molecule.basis),
        "active_space": {
            "n_active_orbitals": int(cfg.active_space.n_active_orbitals),
            "n_active_electrons": int(cfg.active_space.n_active_electrons),
            "fermion_qubit_mapping": str(cfg.active_space.fermion_qubit_mapping),
        },
    }


def precomputed_config_fingerprint(cfg: ExperimentConfig) -> str:
    payload = precomputed_config_fingerprint_payload(cfg)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_precomputed_manifest_against_config(
    bundle_data: dict[str, Any], cfg: ExperimentConfig
) -> None:
    manifest = parse_precomputed_manifest(bundle_data)
    if manifest is None:
        return
    if "n_active_orbitals" in manifest and int(manifest["n_active_orbitals"]) != int(
        cfg.active_space.n_active_orbitals
    ):
        raise PipelineError(
            "precomputed manifest mismatch: n_active_orbitals "
            f"{manifest['n_active_orbitals']} != cfg.active_space.n_active_orbitals "
            f"{cfg.active_space.n_active_orbitals}."
        )
    if "n_active_electrons" in manifest and int(manifest["n_active_electrons"]) != int(
        cfg.active_space.n_active_electrons
    ):
        raise PipelineError(
            "precomputed manifest mismatch: n_active_electrons "
            f"{manifest['n_active_electrons']} != cfg.active_space.n_active_electrons "
            f"{cfg.active_space.n_active_electrons}."
        )
    if "fermion_qubit_mapping" in manifest and str(manifest["fermion_qubit_mapping"]) != str(
        cfg.active_space.fermion_qubit_mapping
    ):
        raise PipelineError(
            "precomputed manifest mismatch: fermion_qubit_mapping "
            f"{manifest['fermion_qubit_mapping']!r} != "
            f"{cfg.active_space.fermion_qubit_mapping!r}."
        )
    if "n_qubits" in manifest:
        pqi = bundle_data.get("pre_quantum_input") or {}
        qh = pqi.get("qubit_hamiltonian") if isinstance(pqi, dict) else None
        observed_nq = int((qh or {}).get("n_qubits", -1)) if isinstance(qh, dict) else -1
        if int(manifest["n_qubits"]) != observed_nq:
            raise PipelineError(
                "precomputed manifest mismatch: n_qubits "
                f"{manifest['n_qubits']} != bundle pre_quantum_input.qubit_hamiltonian.n_qubits "
                f"{observed_nq}."
            )
    if "molecule_symbols" in manifest:
        cfg_symbols = [str(x) for x in cfg.molecule.symbols]
        if list(manifest["molecule_symbols"]) != cfg_symbols:
            raise PipelineError(
                "precomputed manifest mismatch: molecule_symbols "
                f"{manifest['molecule_symbols']!r} != cfg.molecule.symbols {cfg_symbols!r}."
            )
    if "config_fingerprint" in manifest:
        observed = str(manifest["config_fingerprint"])
        expected = precomputed_config_fingerprint(cfg)
        if observed != expected:
            raise PipelineError(
                "precomputed manifest mismatch: config_fingerprint "
                f"{observed!r} != expected {expected!r}."
            )


def precomputed_pre_quantum_input(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None,
) -> PreQuantumInput:
    raw = str(cfg.scf.precomputed_bundle_path or "").strip()
    if not raw:
        raise PipelineError(
            "scf.driver='precomputed' requires scf.precomputed_bundle_path to load pre-quantum input."
        )
    path, bundle_data = load_bundle_dict(raw, cfg_path=cfg_path)
    validate_precomputed_manifest_against_config(bundle_data, cfg)
    qh = qubit_hamiltonian_from_bundle_payload(bundle_data, path=path)
    return PreQuantumInput(
        classical_reference=rhf,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=None,
        meta={"source": "precomputed_bundle"},
    )
