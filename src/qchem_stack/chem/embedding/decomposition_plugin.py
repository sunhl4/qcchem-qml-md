"""Optional decomposition / embedding plugin boundary (toy JSON integrals).

See ``embedding.mode == \"plugin\"`` and ``configs/example_decomposition_plugin_toy.yaml``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ExperimentConfig


@runtime_checkable
class DecompositionPlugin(Protocol):
    """Load fragment payloads from disk or external stores."""

    def load_fragments(self, cfg: ExperimentConfig, *, cfg_path: Path | None = None) -> dict[str, Any]: ...


class UniformFragmentGuessPlugin:
    """Reads ``decomposition_plugin_toy_v1`` JSON and builds the primary fragment Hamiltonian."""

    def load_fragments(self, cfg: ExperimentConfig, *, cfg_path: Path | None = None) -> dict[str, Any]:
        _ = cfg_path
        raw_path = cfg.embedding.decomposition_plugin_json_path
        if not raw_path:
            raise ValueError("embedding.decomposition_plugin_json_path is required for plugin mode")
        path = Path(raw_path)
        if not path.is_file() and cfg_path is not None:
            alt = cfg_path.parent / raw_path
            if alt.is_file():
                path = alt
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != "decomposition_plugin_toy_v1":
            raise ValueError("unsupported decomposition JSON schema")
        return dict(data["fragments"])


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
    emb = cfg.embedding
    name = (emb.decomposition_plugin or "").strip()
    if name != "uniform_fragment_guess":
        raise ValueError(f"unknown embedding.decomposition_plugin: {name!r}")
    raw_path = emb.decomposition_plugin_json_path
    if not raw_path:
        raise ValueError("embedding.decomposition_plugin_json_path required")
    path = Path(raw_path)
    if not path.is_file() and cfg_path is not None:
        alt = cfg_path.parent / raw_path
        if alt.is_file():
            path = alt
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "decomposition_plugin_toy_v1":
        raise ValueError("unsupported decomposition JSON schema")
    primary = str(data.get("primary_fragment_id") or "")
    frags = data.get("fragments") or {}
    if primary not in frags:
        raise ValueError("primary_fragment_id missing from fragments map")
    block = frags[primary]
    n_qubits = int(block["n_qubits"])
    mapping = str(block.get("fermion_qubit_mapping") or "jordan_wigner")
    op = QubitOperator()
    for row in block.get("pauli_coefficients") or []:
        coeff = float(row["coeff"])
        label = str(row["label"])
        op += coeff * _pauli_label_to_operator(label, n_qubits)
    meta = {
        "integral_source": "decomposition_plugin_toy_v1",
        "fermion_to_qubit_map": mapping,
        "decomposition_plugin": name,
        "decomposition_plugin_json": str(path),
    }
    return QubitHamiltonian(operator=op, n_qubits=n_qubits, meta=meta, fermion_space=None)
