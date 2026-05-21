"""Optional decomposition / embedding plugin boundary (JSON fragment payloads).

See ``embedding.mode == \"plugin\"`` and ``configs/example_decomposition_plugin_toy.yaml``.

Schemas:

- ``decomposition_plugin_toy_v1``: Pauli-string fragments only.
- ``decomposition_plugin_contract_v1``: toy Pauli fragments plus optional per-fragment
  ``fragment_energy_terms`` stubs (open-stack ledger hooks inspired by decomposition narratives in
  research packages such as Tangelo — **not** a closed embedding energy accountant).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    hamiltonian_fingerprint_from_qubit_operator,
)
from qchem_stack.config.embedding_helpers import require_plugin

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig

_DECOMPOSITION_PLUGIN_SCHEMAS = frozenset(
    {"decomposition_plugin_toy_v1", "decomposition_plugin_contract_v1"}
)


class DecompositionPlugin(Protocol):
    """Load fragment payloads from disk or external stores."""

    def load_fragments(
        self, cfg: ExperimentConfig, *, cfg_path: Path | None = None
    ) -> dict[str, Any]: ...


class UniformFragmentGuessPlugin:
    """Reads ``embedding.plugin.json_path`` JSON and builds the primary fragment Hamiltonian."""

    def load_fragments(
        self, cfg: ExperimentConfig, *, cfg_path: Path | None = None
    ) -> dict[str, Any]:
        _, data = _resolve_decomposition_plugin_payload(cfg, cfg_path=cfg_path)
        return dict(data["fragments"])


def _resolve_decomposition_plugin_payload(
    cfg: ExperimentConfig, *, cfg_path: Path | None = None
) -> tuple[Path, dict[str, Any]]:
    raw_path = require_plugin(cfg.embedding).plugin.json_path
    if not raw_path:
        raise ValueError("embedding.plugin.json_path required")
    path = Path(raw_path)
    if not path.is_file() and cfg_path is not None:
        alt = cfg_path.parent / raw_path
        if alt.is_file():
            path = alt
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema")
    if schema not in _DECOMPOSITION_PLUGIN_SCHEMAS:
        raise ValueError(f"unsupported decomposition JSON schema: {schema!r}")
    frags = data.get("fragments")
    if not isinstance(frags, dict) or not frags:
        raise ValueError("decomposition plugin payload requires non-empty fragments map")
    for fid, block in frags.items():
        _validate_fragment_block(str(fid), block)
    primary = str(data.get("primary_fragment_id") or "")
    if primary not in frags:
        raise ValueError("primary_fragment_id missing from fragments map")
    return path, data


def _validate_fragment_block(fid: str, block: Any) -> None:
    if not isinstance(block, dict):
        raise ValueError(f"fragment {fid!r} must be an object")
    ft = block.get("fragment_energy_terms")
    if ft is not None and not isinstance(ft, dict):
        raise ValueError(f"fragment {fid!r} fragment_energy_terms must be an object when present")
    if "n_qubits" not in block:
        raise ValueError(f"fragment {fid!r} missing required key n_qubits")
    try:
        n_qubits = int(block["n_qubits"])
    except (TypeError, ValueError) as e:
        raise ValueError(f"fragment {fid!r} n_qubits must be an integer") from e
    if n_qubits < 1:
        raise ValueError(f"fragment {fid!r} n_qubits must be >= 1")
    rows = block.get("pauli_coefficients")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"fragment {fid!r} pauli_coefficients must be a non-empty list")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"fragment {fid!r} pauli_coefficients[{i}] must be an object")
        if "label" not in row or "coeff" not in row:
            raise ValueError(
                f"fragment {fid!r} pauli_coefficients[{i}] requires keys 'label' and 'coeff'"
            )
        try:
            _ = float(row["coeff"])
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"fragment {fid!r} pauli_coefficients[{i}].coeff must be numeric"
            ) from e
        label = str(row["label"])
        _pauli_label_to_operator(label, n_qubits)


def _fragment_pauli_term_counts(fragments: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fid, block in fragments.items():
        rows = block.get("pauli_coefficients") if isinstance(block, dict) else None
        counts[str(fid)] = len(rows) if isinstance(rows, list) else 0
    return counts


def _pauli_label_to_operator(label: str, n_qubits: int) -> QubitOperator:
    s = label.strip().upper()
    if len(s) != n_qubits:
        raise ValueError(f"pauli label length {len(s)} != n_qubits {n_qubits}")
    tup: list[tuple[int, str]] = []
    for i, ch in enumerate(s):
        if ch == "I":
            continue
        if ch not in ("X", "Y", "Z"):
            raise ValueError(f"invalid pauli character {ch!r}")
        tup.append((i, ch))
    return QubitOperator(tuple(tup), 1.0)


def qubit_hamiltonian_from_decomposition_plugin(
    cfg: ExperimentConfig, *, cfg_path: Path | None = None
) -> QubitHamiltonian:
    plugin = require_plugin(cfg.embedding).plugin
    name = (plugin.name or "").strip()
    if name != "uniform_fragment_guess":
        raise ValueError(f"unknown embedding.plugin.name: {name!r}")
    path, data = _resolve_decomposition_plugin_payload(cfg, cfg_path=cfg_path)
    schema_tag = str(data.get("schema") or "")
    primary = str(data.get("primary_fragment_id") or "")
    frags = data.get("fragments") or {}
    term_counts = _fragment_pauli_term_counts(frags)
    ledger_summary: dict[str, dict[str, Any]] = {}
    for fid, b in frags.items():
        if isinstance(b, dict):
            ft = b.get("fragment_energy_terms")
            if isinstance(ft, dict):
                ledger_summary[str(fid)] = ft
    block = frags[primary]
    n_qubits = int(block["n_qubits"])
    mapping = str(block.get("fermion_qubit_mapping") or "jordan_wigner")
    op = QubitOperator()
    for row in block.get("pauli_coefficients") or []:
        coeff = float(row["coeff"])
        label = str(row["label"])
        op += coeff * _pauli_label_to_operator(label, n_qubits)
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(op)
    meta = {
        "integral_source": schema_tag,
        "integral_openfermion_bridge": "decomposition_plugin_pauli_terms_v1",
        "fermion_to_qubit_map": mapping,
        "hamiltonian_fingerprint": fp,
        "decomposition_plugin": name,
        "decomposition_plugin_json": str(path),
        "decomposition_plugin_schema": schema_tag,
        "decomposition_primary_fragment_id": primary,
        "decomposition_fragment_count": len(frags),
        "decomposition_fragment_ids": sorted(str(k) for k in frags),
        "decomposition_fragment_pauli_term_counts": term_counts,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if ledger_summary:
        meta["decomposition_fragment_energy_terms_v1"] = ledger_summary
    return QubitHamiltonian(operator=op, n_qubits=n_qubits, meta=meta, fermion_space=None)
