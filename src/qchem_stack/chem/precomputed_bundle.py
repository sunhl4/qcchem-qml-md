"""Load precomputed classical-to-quantum bundle files.

The bundle schema is designed for the "offline classical, online quantum" lane:
users can run classical chemistry elsewhere, save a stable JSON payload, then
feed it into this stack without rerunning classical SCF.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    hamiltonian_fingerprint_from_qubit_operator,
)
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.contracts.schema_ids import (
    CLASSICAL_REFERENCE_BUNDLE_V1,
    PRE_QUANTUM_INPUT_SCHEMA_V1,
    PRECOMPUTED_MANIFEST_SCHEMA_V1,
)


def _expect_object(value: Any, message: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(message)
    return value


def _expect_non_empty_list(value: Any, message: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ValueError(message)
    return value


def _coerce_numeric(
    value: Any, message: str, converter: Callable[[Any], int | float]
) -> int | float:
    try:
        return converter(value)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(message) from exc


def _coerce_int(value: Any, message: str) -> int:
    return int(_coerce_numeric(value, message, int))


def _coerce_float(value: Any, message: str) -> float:
    return float(_coerce_numeric(value, message, float))


def _coerce_positive_int(value: Any, *, field: str) -> int:
    out = _coerce_int(value, f"{field} must be an integer.")
    if out < 1:
        raise ValueError(f"{field} must be >= 1.")
    return out


def resolve_bundle_path(raw_path: str, *, cfg_path: Path | None = None) -> Path:
    path = Path(str(raw_path).strip())
    if path.is_file():
        return path
    if cfg_path is not None:
        alt = (cfg_path.parent / path).resolve()
        if alt.is_file():
            return alt
    raise FileNotFoundError(f"precomputed bundle not found: {raw_path!r}")


def load_bundle_dict(raw_path: str, *, cfg_path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    path = resolve_bundle_path(raw_path, cfg_path=cfg_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("precomputed bundle root must be a JSON object.")
    schema = str(data.get("schema") or "")
    if schema != CLASSICAL_REFERENCE_BUNDLE_V1:
        raise ValueError(
            f"unsupported precomputed bundle schema {schema!r}; expected {CLASSICAL_REFERENCE_BUNDLE_V1!r}."
        )
    return path, data


def molecular_mean_field_result_from_bundle(
    raw_path: str,
    *,
    cfg_path: Path | None = None,
) -> MolecularMeanFieldResult:
    path, data = load_bundle_dict(raw_path, cfg_path=cfg_path)
    block = _expect_object(
        data.get("classical_reference"), "bundle.classical_reference must be an object."
    )
    e_tot = _coerce_float(block["e_tot"], "bundle.classical_reference.e_tot must be numeric.")
    mo_raw = _expect_non_empty_list(
        block.get("mo_energy"),
        "bundle.classical_reference.mo_energy must be a non-empty list.",
    )
    mo_energy = np.asarray(mo_raw, dtype=float)
    driver_meta_raw = block.get("driver_meta")
    if driver_meta_raw is not None and not isinstance(driver_meta_raw, dict):
        raise ValueError("bundle.classical_reference.driver_meta must be an object when present.")
    driver_meta = dict(driver_meta_raw or {})
    driver_meta.setdefault("upstream_classical_software_tag", "precomputed")
    driver_meta.setdefault("driver_family", "precomputed")
    driver_meta["precomputed_bundle_schema"] = CLASSICAL_REFERENCE_BUNDLE_V1
    driver_meta["precomputed_bundle_path"] = str(path)
    raw_mf = {
        "backend": "precomputed",
        "bundle_path": str(path),
        "bundle_schema": CLASSICAL_REFERENCE_BUNDLE_V1,
    }
    return MolecularMeanFieldResult(
        mf=wrap_mean_field_like(
            backend_tag="precomputed",
            raw_mf=raw_mf,
            e_tot=e_tot,
            mo_energy=mo_energy,
        ),
        e_tot=e_tot,
        mo_energy=mo_energy,
        driver_meta=driver_meta,
    )


def qubit_hamiltonian_from_bundle(
    raw_path: str,
    *,
    cfg_path: Path | None = None,
) -> QubitHamiltonian:
    path, data = load_bundle_dict(raw_path, cfg_path=cfg_path)
    return qubit_hamiltonian_from_bundle_payload(data, path=path)


def qubit_hamiltonian_from_bundle_payload(
    data: dict[str, Any],
    *,
    path: Path,
) -> QubitHamiltonian:
    pqi = _expect_object(
        data.get("pre_quantum_input"), "bundle.pre_quantum_input must be an object."
    )
    schema = str(pqi.get("schema") or "")
    if schema and schema != PRE_QUANTUM_INPUT_SCHEMA_V1:
        raise ValueError(
            "bundle.pre_quantum_input.schema must be "
            f"{PRE_QUANTUM_INPUT_SCHEMA_V1!r} when provided (got {schema!r})."
        )
    qh = _expect_object(
        pqi.get("qubit_hamiltonian"),
        "bundle.pre_quantum_input.qubit_hamiltonian must be an object.",
    )
    n_qubits = _coerce_positive_int(
        qh["n_qubits"],
        field="bundle.pre_quantum_input.qubit_hamiltonian.n_qubits",
    )
    rows = _expect_non_empty_list(
        qh.get("terms"),
        "bundle.pre_quantum_input.qubit_hamiltonian.terms must be a non-empty list.",
    )
    op = QubitOperator()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"terms[{idx}] must be an object.")
        label = str(row.get("label") or "")
        if not label:
            raise ValueError(f"terms[{idx}].label must be non-empty.")
        coeff = _coerce_float(row["coeff"], f"terms[{idx}].coeff must be numeric.")
        term = _label_to_term(label, n_qubits=n_qubits)
        op += coeff * QubitOperator(term, 1.0)
    meta = qh.get("meta")
    if meta is not None and not isinstance(meta, dict):
        raise ValueError(
            "bundle.pre_quantum_input.qubit_hamiltonian.meta must be an object when present."
        )
    qh_meta = dict(meta or {})
    qh_meta.setdefault("integral_source", CLASSICAL_REFERENCE_BUNDLE_V1)
    qh_meta.setdefault("integral_openfermion_bridge", "precomputed_pauli_terms_v1")
    manifest = parse_precomputed_manifest(data)
    if manifest is not None and "fermion_qubit_mapping" in manifest:
        qh_meta.setdefault("fermion_to_qubit_map", manifest["fermion_qubit_mapping"])
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(op)
    qh_meta.setdefault("hamiltonian_fingerprint", fp)
    if fp_trunc:
        qh_meta["hamiltonian_fingerprint_truncated"] = True
    qh_meta["precomputed_bundle_path"] = str(path)
    return QubitHamiltonian(
        operator=op,
        n_qubits=n_qubits,
        fermion_space=None,
        meta=qh_meta,
    )


def parse_precomputed_manifest(data: dict[str, Any]) -> dict[str, Any] | None:
    """Return validated optional precomputed manifest payload."""
    raw_obj = data.get("manifest")
    if raw_obj is None:
        return None
    raw = _expect_object(raw_obj, "bundle.manifest must be an object when present.")
    schema = str(raw.get("schema") or "")
    if schema and schema != PRECOMPUTED_MANIFEST_SCHEMA_V1:
        raise ValueError(
            f"bundle.manifest.schema must be {PRECOMPUTED_MANIFEST_SCHEMA_V1!r} when provided "
            f"(got {schema!r})."
        )
    out: dict[str, Any] = {"schema": PRECOMPUTED_MANIFEST_SCHEMA_V1}
    if "config_fingerprint" in raw and raw["config_fingerprint"] is not None:
        out["config_fingerprint"] = str(raw["config_fingerprint"])
    if "n_active_orbitals" in raw and raw["n_active_orbitals"] is not None:
        n_orb = _coerce_positive_int(
            raw["n_active_orbitals"], field="bundle.manifest.n_active_orbitals"
        )
        out["n_active_orbitals"] = n_orb
    if "n_active_electrons" in raw and raw["n_active_electrons"] is not None:
        n_ele = _coerce_positive_int(
            raw["n_active_electrons"], field="bundle.manifest.n_active_electrons"
        )
        out["n_active_electrons"] = n_ele
    if "fermion_qubit_mapping" in raw and raw["fermion_qubit_mapping"] is not None:
        map_name = str(raw["fermion_qubit_mapping"]).strip().lower()
        if not map_name:
            raise ValueError(
                "bundle.manifest.fermion_qubit_mapping must be non-empty when present."
            )
        out["fermion_qubit_mapping"] = map_name
    if "n_qubits" in raw and raw["n_qubits"] is not None:
        nq = _coerce_positive_int(raw["n_qubits"], field="bundle.manifest.n_qubits")
        out["n_qubits"] = nq
    if "molecule_symbols" in raw and raw["molecule_symbols"] is not None:
        symbols_raw = raw["molecule_symbols"]
        if not isinstance(symbols_raw, list) or not symbols_raw:
            raise ValueError(
                "bundle.manifest.molecule_symbols must be a non-empty list when present."
            )
        out["molecule_symbols"] = [str(x) for x in symbols_raw]
    return out


_INDEXED_LABEL_TOKEN = re.compile(r"^([XYZ])(\d+)$")


def _label_to_term(label: str, *, n_qubits: int) -> tuple[tuple[int, str], ...]:
    s = str(label).strip().upper()
    if not s:
        raise ValueError("empty Pauli label.")
    if s == "I":
        return ()
    if " " in s:
        parts = [x for x in s.split(" ") if x]
        indexed: dict[int, str] = {}
        for tok in parts:
            m = _INDEXED_LABEL_TOKEN.match(tok)
            if m is None:
                raise ValueError(f"invalid indexed Pauli token: {tok!r}")
            pauli = m.group(1)
            idx = int(m.group(2))
            if idx < 0 or idx >= n_qubits:
                raise ValueError(f"Pauli index out of bounds for n_qubits={n_qubits}: {idx}")
            prev = indexed.get(idx)
            if prev is not None and prev != pauli:
                raise ValueError(
                    f"conflicting indexed Pauli tokens at qubit {idx}: {prev!r} vs {pauli!r}."
                )
            indexed[idx] = pauli
        return tuple((idx, indexed[idx]) for idx in sorted(indexed))
    if len(s) != n_qubits:
        raise ValueError(
            f"compact Pauli label length {len(s)} must equal n_qubits={n_qubits} (label={label!r})."
        )
    out: list[tuple[int, str]] = []
    for idx, ch in enumerate(s):
        if ch == "I":
            continue
        if ch not in ("X", "Y", "Z"):
            raise ValueError(f"invalid compact Pauli character {ch!r} in label {label!r}")
        out.append((idx, ch))
    return tuple(out)
