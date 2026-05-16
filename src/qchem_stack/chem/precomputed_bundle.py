"""Load precomputed classical-to-quantum bundle files.

The bundle schema is designed for the "offline classical, online quantum" lane:
users can run classical chemistry elsewhere, save a stable JSON payload, then
feed it into this stack without rerunning classical SCF.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    hamiltonian_fingerprint_from_qubit_operator,
)
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.contracts.schema_ids import (
    CLASSICAL_REFERENCE_BUNDLE_V1,
    PRECOMPUTED_MANIFEST_SCHEMA_V1,
    PRE_QUANTUM_INPUT_SCHEMA_V1,
)


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
    block = data.get("classical_reference")
    if not isinstance(block, dict):
        raise ValueError("bundle.classical_reference must be an object.")
    try:
        e_tot = float(block["e_tot"])
    except Exception as exc:  # noqa: BLE001
        raise ValueError("bundle.classical_reference.e_tot must be numeric.") from exc
    mo_raw = block.get("mo_energy")
    if not isinstance(mo_raw, list) or not mo_raw:
        raise ValueError("bundle.classical_reference.mo_energy must be a non-empty list.")
    mo_energy = np.asarray(mo_raw, dtype=float)
    driver_meta_raw = block.get("driver_meta")
    if driver_meta_raw is not None and not isinstance(driver_meta_raw, dict):
        raise ValueError("bundle.classical_reference.driver_meta must be an object when present.")
    driver_meta = dict(driver_meta_raw or {})
    driver_meta.setdefault("upstream_classical_software_tag", "precomputed")
    driver_meta.setdefault("driver_family", "precomputed")
    driver_meta["precomputed_bundle_schema"] = CLASSICAL_REFERENCE_BUNDLE_V1
    driver_meta["precomputed_bundle_path"] = str(path)
    return MolecularMeanFieldResult(
        mf={
            "backend": "precomputed",
            "bundle_path": str(path),
            "bundle_schema": CLASSICAL_REFERENCE_BUNDLE_V1,
        },
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
    pqi = data.get("pre_quantum_input")
    if not isinstance(pqi, dict):
        raise ValueError("bundle.pre_quantum_input must be an object.")
    schema = str(pqi.get("schema") or "")
    if schema and schema != PRE_QUANTUM_INPUT_SCHEMA_V1:
        raise ValueError(
            "bundle.pre_quantum_input.schema must be "
            f"{PRE_QUANTUM_INPUT_SCHEMA_V1!r} when provided (got {schema!r})."
        )
    qh = pqi.get("qubit_hamiltonian")
    if not isinstance(qh, dict):
        raise ValueError("bundle.pre_quantum_input.qubit_hamiltonian must be an object.")
    try:
        n_qubits = int(qh["n_qubits"])
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            "bundle.pre_quantum_input.qubit_hamiltonian.n_qubits must be an integer."
        ) from exc
    if n_qubits < 1:
        raise ValueError("bundle.pre_quantum_input.qubit_hamiltonian.n_qubits must be >= 1.")
    rows = qh.get("terms")
    if not isinstance(rows, list) or not rows:
        raise ValueError(
            "bundle.pre_quantum_input.qubit_hamiltonian.terms must be a non-empty list."
        )
    op = QubitOperator()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"terms[{idx}] must be an object.")
        label = str(row.get("label") or "")
        if not label:
            raise ValueError(f"terms[{idx}].label must be non-empty.")
        try:
            coeff = float(row["coeff"])
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"terms[{idx}].coeff must be numeric.") from exc
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
    raw = data.get("manifest")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("bundle.manifest must be an object when present.")
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
        n_orb = int(raw["n_active_orbitals"])
        if n_orb < 1:
            raise ValueError("bundle.manifest.n_active_orbitals must be >= 1.")
        out["n_active_orbitals"] = n_orb
    if "n_active_electrons" in raw and raw["n_active_electrons"] is not None:
        n_ele = int(raw["n_active_electrons"])
        if n_ele < 1:
            raise ValueError("bundle.manifest.n_active_electrons must be >= 1.")
        out["n_active_electrons"] = n_ele
    if "fermion_qubit_mapping" in raw and raw["fermion_qubit_mapping"] is not None:
        map_name = str(raw["fermion_qubit_mapping"]).strip().lower()
        if not map_name:
            raise ValueError(
                "bundle.manifest.fermion_qubit_mapping must be non-empty when present."
            )
        out["fermion_qubit_mapping"] = map_name
    if "n_qubits" in raw and raw["n_qubits"] is not None:
        nq = int(raw["n_qubits"])
        if nq < 1:
            raise ValueError("bundle.manifest.n_qubits must be >= 1.")
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
        pairs: list[tuple[int, str]] = []
        for tok in parts:
            m = _INDEXED_LABEL_TOKEN.match(tok)
            if m is None:
                raise ValueError(f"invalid indexed Pauli token: {tok!r}")
            pauli = m.group(1)
            idx = int(m.group(2))
            if idx < 0 or idx >= n_qubits:
                raise ValueError(f"Pauli index out of bounds for n_qubits={n_qubits}: {idx}")
            pairs.append((idx, pauli))
        return tuple(sorted(set(pairs), key=lambda x: x[0]))
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
