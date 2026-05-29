"""
Grouped Pauli measurements on UQC cloud (HEA + basis rotation + measure per group).

Mirrors :mod:`qchem_stack.backends.qiskit_pauli_shots` but submits static OpenQASM 3.0
circuits via ``uqc_client.UQC.submit_task``.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_measure_expand import deserialize_basis_key
from qchem_stack.backends.pauli_shot_sim import _pauli_eigenvalue_on_comp_bit
from qchem_stack.backends.qiskit_executor import hea_circuit_qiskit
from qchem_stack.backends.qiskit_pauli_shots import (
    _append_pauli_basis_to_qiskit,
    _basis_key_for_term,
)
from qchem_stack.backends.uqc_transpiler import transpile_to_uqc_native

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec

logger = logging.getLogger(__name__)


def _round_uqc_shots(shots: int) -> int:
    s = max(100, min(1000, int(shots)))
    return ((s + 99) // 100) * 100


def _histogram_to_comp_probabilities(hist_data: list[list], n_qubits: int) -> dict[int, float]:
    """ARTIQ histogram index → computational-basis probability (OpenFermion index)."""
    idx_to_v: dict[int, int] = {}
    for entry in hist_data:
        idx, count = int(entry[0]), int(entry[1])
        idx_to_v[idx] = idx_to_v.get(idx, 0) + count
    total = int(sum(idx_to_v.values())) or 1
    return {k: v / total for k, v in idx_to_v.items()}


def _group_expectation_from_comp_probs(
    coeffs: list[tuple[tuple, float]],
    p_comp: dict[int, float],
    n_qubits: int,
    basis_key: tuple[tuple[int, str], ...] | None,
) -> float:
    ev = 0.0
    for bidx, p in p_comp.items():
        vshot = 0.0
        for t, c in coeffs:
            bk = basis_key if basis_key is not None else _basis_key_for_term(t)
            vshot += c * _pauli_eigenvalue_on_comp_bit(t, bidx, n_qubits, bk)
        ev += p * float(vshot)
    return ev


def _build_uqc_measurement_circuit(
    n_qubits: int,
    hea_depth: int,
    angles: np.ndarray,
    basis_key: tuple[tuple[int, str], ...],
) -> Any:

    qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))
    _append_pauli_basis_to_qiskit(qc, basis_key, n_qubits)
    qc.barrier()
    qc.measure_all()
    return qc


def _submit_uqc_circuit(
    client: Any,
    qc: Any,
    *,
    target: str,
    shots: int,
    opt_level: int,
    max_wait: float,
    poll_interval: float,
) -> dict[int, float]:
    from qiskit.qasm3 import dumps

    qc_t = transpile_to_uqc_native(qc, optimization_level=opt_level)
    qasm3_str = dumps(qc_t)
    try:
        from uqc_client import ensure_static_qasm

        ensure_static_qasm(qasm3_str)
    except ImportError:
        pass
    except Exception as e:
        from qchem_stack.exceptions import PipelineError

        raise PipelineError(f"Circuit failed UQC static validation: {e}") from e

    shots = _round_uqc_shots(shots)
    task_id = client.submit_task(convert_qprog=qasm3_str, target=target, shots=shots)
    if task_id is None:
        raise RuntimeError("UQC submit_task returned None")

    elapsed = 0.0
    while elapsed < max_wait:
        status = client.get_task_status(task_id)
        if status == "SUCCESS":
            break
        if status == "FAILURE":
            raise RuntimeError(f"UQC task {task_id} failed")
        time.sleep(poll_interval)
        elapsed += poll_interval
    else:
        raise TimeoutError(f"UQC task {task_id} timed out after {max_wait}s")

    raw = client.get_task_result(task_id)
    if raw is None:
        raise RuntimeError(f"UQC task {task_id} returned no results")
    hist = raw[0]["datasets"]["computational_basis_histogram"]
    return _histogram_to_comp_probabilities(hist, qc_t.num_qubits)


def energy_estimate_grouped_uqc_shots(
    hamiltonian: QubitOperator,
    n_qubits: int,
    hea_depth: int,
    angles: np.ndarray,
    shots_per_circuit: int,
    client: Any,
    spec: BackendSpec,
) -> float:
    """⟨H⟩ from tensor-product Pauli groups, one UQC job per commuting measurement basis."""
    meta = spec.meta or {}
    grouping = meta.get("uqc_pauli_grouping", "tensor_product")
    plan = build_measurement_plan(hamiltonian, n_qubits, grouping=grouping)
    terms_dict = {k: float(np.real(v)) for k, v in dict(hamiltonian.terms).items()}
    ident = float(terms_dict.get((), 0.0))
    metas = plan.to_circuit_metas()

    target = str(meta.get("uqc_target", "iontrap-sim"))
    opt_level = int(meta.get("uqc_transpile_opt_level", spec.uqc_transpile_opt_level))
    max_wait = float(meta.get("uqc_timeout_s", 600.0))
    poll_interval = float(meta.get("uqc_poll_interval_s", 2.0))
    angles = np.asarray(angles, dtype=float).ravel()

    total = ident
    n_groups = max(1, len(plan.groups))
    shots_group = _round_uqc_shots(max(100, shots_per_circuit // n_groups))

    for gid, g in enumerate(plan.groups):
        cmeta = metas[gid] if gid < len(metas) else {}
        bk = deserialize_basis_key(cmeta.get("basis_key"))
        coeffs = [(t, float(terms_dict[t])) for t in g if t in terms_dict]
        if not coeffs:
            continue

        if bk is None:
            for t, c in coeffs:
                bk1 = _basis_key_for_term(t)
                qc = _build_uqc_measurement_circuit(n_qubits, hea_depth, angles, bk1)
                p_comp = _submit_uqc_circuit(
                    client,
                    qc,
                    target=target,
                    shots=shots_group,
                    opt_level=opt_level,
                    max_wait=max_wait,
                    poll_interval=poll_interval,
                )
                total += _group_expectation_from_comp_probs([(t, c)], p_comp, n_qubits, bk1)
            continue

        qc = _build_uqc_measurement_circuit(n_qubits, hea_depth, angles, bk)
        p_comp = _submit_uqc_circuit(
            client,
            qc,
            target=target,
            shots=shots_group,
            opt_level=opt_level,
            max_wait=max_wait,
            poll_interval=poll_interval,
        )
        total += _group_expectation_from_comp_probs(coeffs, p_comp, n_qubits, bk)

    logger.debug(
        "UQC grouped Pauli energy=%.8f (%s groups, %s shots/group)",
        total,
        len(plan.groups),
        shots_group,
    )
    return float(np.real(total))
