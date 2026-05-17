"""Precomputed bundle helpers for unified pre-quantum assembly."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_input import PreQuantumInput, build_pre_quantum_meta
from qchem_stack.chem.pre_quantum_path import PreQuantumPath, pre_quantum_path_source
from qchem_stack.chem.precomputed_bundle import (
    load_bundle_dict,
    parse_precomputed_manifest,
    qubit_hamiltonian_from_bundle_payload,
)
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError


def _manifest_mismatch(field: str, detail: str) -> PipelineError:
    return PipelineError(f"precomputed manifest mismatch: {field} {detail}")


def _compare_manifest_scalar(
    *,
    manifest: dict[str, Any],
    field: str,
    expected: Any,
    normalize: Any,
    rhs_message: str,
) -> None:
    if field not in manifest:
        return
    observed = normalize(manifest[field])
    exp = normalize(expected)
    if observed != exp:
        lhs = f"{observed!r} " if isinstance(observed, str) else f"{observed} "
        raise _manifest_mismatch(field, lhs + rhs_message)


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
    required_fields = (
        "n_active_orbitals",
        "n_active_electrons",
        "fermion_qubit_mapping",
        "n_qubits",
        "molecule_symbols",
        "config_fingerprint",
    )
    missing = tuple(field for field in required_fields if field not in manifest)
    if missing:
        raise _manifest_mismatch(
            "required_fields",
            (
                "missing required manifest fields for strict precomputed validation: "
                f"{list(missing)}."
            ),
        )

    scalar_checks: tuple[tuple[str, Any, Any, str], ...] = (
        (
            "n_active_orbitals",
            cfg.active_space.n_active_orbitals,
            int,
            f"!= cfg.active_space.n_active_orbitals {cfg.active_space.n_active_orbitals}.",
        ),
        (
            "n_active_electrons",
            cfg.active_space.n_active_electrons,
            int,
            f"!= cfg.active_space.n_active_electrons {cfg.active_space.n_active_electrons}.",
        ),
        (
            "fermion_qubit_mapping",
            cfg.active_space.fermion_qubit_mapping,
            str,
            f"!= {cfg.active_space.fermion_qubit_mapping!r}.",
        ),
    )
    for field, expected, normalize, rhs in scalar_checks:
        _compare_manifest_scalar(
            manifest=manifest,
            field=field,
            expected=expected,
            normalize=normalize,
            rhs_message=rhs,
        )

    if "n_qubits" in manifest:
        pqi = bundle_data.get("pre_quantum_input") or {}
        qh = pqi.get("qubit_hamiltonian") if isinstance(pqi, dict) else None
        observed_nq = int((qh or {}).get("n_qubits", -1)) if isinstance(qh, dict) else -1
        if int(manifest["n_qubits"]) != observed_nq:
            raise _manifest_mismatch(
                "n_qubits",
                (
                    f"{manifest['n_qubits']} != bundle pre_quantum_input.qubit_hamiltonian.n_qubits "
                    f"{observed_nq}."
                ),
            )
    if "molecule_symbols" in manifest:
        cfg_symbols = [str(x) for x in cfg.molecule.symbols]
        if list(manifest["molecule_symbols"]) != cfg_symbols:
            raise _manifest_mismatch(
                "molecule_symbols",
                f"{manifest['molecule_symbols']!r} != cfg.molecule.symbols {cfg_symbols!r}.",
            )
    if "config_fingerprint" in manifest:
        observed = str(manifest["config_fingerprint"])
        expected = precomputed_config_fingerprint(cfg)
        if observed != expected:
            raise _manifest_mismatch("config_fingerprint", f"{observed!r} != expected {expected!r}.")


def precomputed_pre_quantum_input(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
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
        classical_reference=reference,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=None,
        meta=build_pre_quantum_meta(
            cfg,
            source=pre_quantum_path_source(PreQuantumPath.PRECOMPUTED_BUNDLE),
            qubit_hamiltonian=qh,
            extra={"precomputed_bundle_path": str(path)},
        ),
    )
