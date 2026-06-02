"""Qiskit histogram estimates for QSE Pauli transition amplitudes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_measure_expand import basis_change_operations
from qchem_stack.backends.pauli_shot_sim import apply_pauli_tensor_basis_to_state
from qchem_stack.backends.qiskit_pauli_shots import qiskit_bitstring_to_comp_index
from qchem_stack.backends.uccsd_circuit_qiskit import _amplitudes_openfermion_to_qiskit, _wire
from qchem_stack.quantum.algorithms.tolerances import PROBABILITY_FLOOR
from qchem_stack.quantum.qse_transition import _basis_key_for_term


def estimate_transition_pauli_amplitude_qiskit_shots(
    phi_left: np.ndarray,
    phi_right: np.ndarray,
    pauli_term: tuple[tuple[int, str], ...],
    n_qubits: int,
    shots: int,
) -> complex:
    """Estimate ``<phi_l|P|phi_r>`` via Qiskit Aer histogram after basis change on ``|phi_r>``."""
    if len(pauli_term) == 0:
        return complex(np.vdot(phi_left, phi_right))
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    bk = _basis_key_for_term(pauli_term)
    psi_r = apply_pauli_tensor_basis_to_state(
        np.asarray(phi_right, dtype=complex).ravel(), bk, n_qubits
    )
    psi_l = apply_pauli_tensor_basis_to_state(
        np.asarray(phi_left, dtype=complex).ravel(), bk, n_qubits
    )
    n = int(n_qubits)
    qc = QuantumCircuit(n, n)
    amps = _amplitudes_openfermion_to_qiskit(psi_r, n)
    qc.initialize(list(amps), [_wire(n, q) for q in range(n)])
    for op in basis_change_operations(bk, n):
        name = op["name"]
        q = int(op["qubits"][0])
        if name == "H":
            qc.h(_wire(n, q))
        elif name == "SDG":
            qc.sdg(_wire(n, q))
            qc.h(_wire(n, q))
    qc.measure([_wire(n, q) for q in range(n)], list(range(n)))
    backend = AerSimulator(method="statevector")
    counts = backend.run(qc, shots=max(1, int(shots))).result().get_counts()
    acc = 0j
    total = float(sum(counts.values()))
    from qchem_stack.backends.pauli_shot_sim import _pauli_eigenvalue_on_comp_bit

    p = np.abs(psi_r) ** 2
    psum = float(np.sum(p))
    if psum < PROBABILITY_FLOOR:
        return 0j
    p = p / psum
    for bitstr, cnt in counts.items():
        b = qiskit_bitstring_to_comp_index(bitstr, n)
        pb = float(p[b])
        if pb < PROBABILITY_FLOOR:
            continue
        z = _pauli_eigenvalue_on_comp_bit(pauli_term, b, n, bk)
        acc += (cnt / total) * z * np.conj(psi_l[b]) * psi_r[b] / pb
    return acc


def expectation_grouped_qiskit_shots(
    psi: np.ndarray,
    op: QubitOperator,
    n_qubits: int,
    shots: int,
) -> float:
    """Grouped Pauli expectation ``<psi|O|psi>`` via Qiskit Aer histograms."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    from qchem_stack.backends.pauli_grouping import build_measurement_plan
    from qchem_stack.backends.pauli_shot_sim import _pauli_eigenvalue_on_comp_bit

    plan = build_measurement_plan(op, int(n_qubits), grouping="tensor_product")
    terms_dict = {k: float(np.real(v)) for k, v in dict(op.terms).items()}
    ident = float(terms_dict.get((), 0.0))
    n = int(n_qubits)
    backend = AerSimulator(method="statevector")
    group_means: list[float] = []
    for meta in plan.to_circuit_metas():
        bk = meta.get("basis_key")
        coeff_sum = float(meta.get("coeff_sum", 0.0))
        if bk is None:
            continue
        qc = QuantumCircuit(n, n)
        amps = _amplitudes_openfermion_to_qiskit(np.asarray(psi, dtype=complex).ravel(), n)
        qc.initialize(list(amps), [_wire(n, q) for q in range(n)])
        for bop in basis_change_operations(bk, n):
            name = bop["name"]
            q = int(bop["qubits"][0])
            if name == "H":
                qc.h(_wire(n, q))
            elif name == "SDG":
                qc.sdg(_wire(n, q))
                qc.h(_wire(n, q))
        qc.measure([_wire(n, q) for q in range(n)], list(range(n)))
        counts = backend.run(qc, shots=max(1, int(shots))).result().get_counts()
        total = float(sum(counts.values()))
        acc = 0.0
        for bitstr, cnt in counts.items():
            b = qiskit_bitstring_to_comp_index(bitstr, n)
            z = _pauli_eigenvalue_on_comp_bit(tuple(bk), b, n, bk)
            acc += (cnt / total) * z * coeff_sum
        group_means.append(acc)
    return float(ident + sum(group_means))
