from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd


@dataclass
class BackendSpec:
    """Execution target: use ``provider`` to choose API (statevector / Qiskit / IonStack)."""

    name: str
    provider: Literal["statevector", "qiskit", "ionstack"] = "statevector"
    # When target_energy_stderr is None, this is the nominal per-circuit shot count (and stderr input).
    shots_per_circuit: int = 1024
    # If set, recommended_shots_per_circuit is used for stderr bookkeeping (classical bound).
    target_energy_stderr: float | None = None
    supports_mid_circuit_measure: bool = False
    native_twoq: str = "CX"
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    ionstack_endpoint: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompilerPassBundle:
    optimization_level: int = 1
    preoptimize_passes: list[str] = field(default_factory=list)
    compiler_passes: list[str] = field(default_factory=list)


@dataclass
class CircuitIR:
    """Logical circuit: list of operations ``{name, qubits, params?, box?}``."""

    n_qubits: int
    operations: list[dict[str, Any]] = field(default_factory=list)
    boxes: list[str] = field(default_factory=list)


def _twoq_gate_count(ops: list[dict[str, Any]], native: str) -> int:
    c = 0
    for op in ops:
        n = op.get("name", "")
        if n in ("CX", "CNOT", "ZZ", "ZZPhase", "MS", "CP"):
            c += 1
        elif n == "PAULI_ROTATION":
            from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import (
                pauli_rotation_elementary_ops,
            )

            p = op.get("params") or {}
            c += _twoq_gate_count(
                pauli_rotation_elementary_ops(str(p["pauli_string"]), float(p["phi"])),
                native,
            )
    return c


def _depth_estimate(ops: list[dict[str, Any]], n_qubits: int) -> int:
    if not ops:
        return 0
    layers = [0] * n_qubits
    depth = 0
    for op in ops:
        qs = list(op.get("qubits", []))
        if not qs:
            continue
        t = max(layers[q] for q in qs) + 1
        for q in qs:
            layers[q] = t
        depth = max(depth, t)
    return depth


def circuit_resource_row(
    cid: str,
    circ: CircuitIR,
    shots: int,
    backend: BackendSpec,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    n2 = _twoq_gate_count(circ.operations, backend.native_twoq)
    row: dict[str, Any] = {
        "circuit_id": cid,
        "n_qubits": circ.n_qubits,
        "depth": _depth_estimate(circ.operations, circ.n_qubits),
        "twoq_count": n2,
        "native_twoq": backend.native_twoq,
        "shots": shots,
        "total_shots": shots,
    }
    if extra:
        row.update(extra)
    return row


def dataframe_circuit_shot(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Resource summary table aligned with workflow-export conventions."""
    return pd.DataFrame(rows)


def summarize_circuit_shot_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-circuit rows (semantic analogue to summing a ``dataframe_circuit_shot`` block)."""
    if not rows:
        return {"n_circuits": 0, "sum_shots": 0, "max_depth": 0, "sum_twoq": 0}
    df = pd.DataFrame(rows)
    shots_col = "total_shots" if "total_shots" in df.columns else "shots"
    sshots = int(df[shots_col].sum()) if shots_col in df.columns else 0
    return {
        "n_circuits": len(rows),
        "sum_shots": sshots,
        "max_depth": int(df["depth"].max()) if "depth" in df.columns else 0,
        "sum_twoq": int(df["twoq_count"].sum()) if "twoq_count" in df.columns else 0,
        "n_qubits": int(df["n_qubits"].iloc[0]) if "n_qubits" in df.columns and len(df) else 0,
    }
