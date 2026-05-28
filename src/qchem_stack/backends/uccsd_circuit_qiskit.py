"""Qiskit export for UCCSD prep circuits (same wire map as HEA: logical q → physical n-1-q)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.backends._bit_utils import bit_reverse_index

if TYPE_CHECKING:
    from qchem_stack.backends.spec import CircuitIR
    from qchem_stack.quantum.algorithms.uccsd_circuit import UCCSDCircuitContext


def _wire(n_qubits: int, q: int) -> int:
    return n_qubits - 1 - q


def _permute_unitary_for_qiskit(u: np.ndarray, n_qubits: int) -> np.ndarray:
    """Map a unitary on logical tensor axes to Qiskit ``unitary(..., qubits=range(n)[::-1])``."""
    dim = 2**n_qubits
    mat = np.asarray(u, dtype=np.complex128)
    if mat.shape != (dim, dim):
        raise ValueError(f"expected ({dim}, {dim}) unitary, got {mat.shape}")
    r = np.zeros((dim, dim), dtype=np.complex128)
    for i in range(dim):
        r[bit_reverse_index(i, n_qubits), i] = 1.0
    return r @ mat @ r


def _amplitudes_openfermion_to_qiskit(amps: np.ndarray, n_qubits: int) -> np.ndarray:
    """Reorder statevector amplitudes for ``QuantumCircuit.initialize`` wire map ``w(q)=n-1-q``."""
    src = np.asarray(amps, dtype=np.complex128).ravel()
    out = np.zeros_like(src)
    for i, amp in enumerate(src):
        out[bit_reverse_index(i, n_qubits)] = amp
    return out


def circuit_ir_to_qiskit(ir: CircuitIR) -> Any:
    """Build a Qiskit ``QuantumCircuit`` from CircuitIR (HEA + UCCSD + Pauli basis ops)."""
    from qiskit import QuantumCircuit

    n = int(ir.n_qubits)
    has_measure = any(str(op.get("name", "")) == "MEASURE" for op in ir.operations)
    qc = QuantumCircuit(n, 1 if has_measure else 0)
    for op in ir.operations:
        name = str(op.get("name", ""))
        qs = [int(q) for q in op.get("qubits", [])]
        p = op.get("params") or {}
        if name == "INIT_STATEVECTOR":
            amps = _amplitudes_openfermion_to_qiskit(
                np.asarray(p["amplitudes"], dtype=np.complex128),
                n,
            )
            qc.initialize(list(amps), [_wire(n, q) for q in range(n)])
        elif name == "UNITARY":
            mat = _permute_unitary_for_qiskit(np.asarray(p["matrix"], dtype=np.complex128), n)
            qc.unitary(mat, [_wire(n, q) for q in range(n)])
        elif name == "RY":
            qc.ry(float(p["theta"]), _wire(n, qs[0]))
        elif name == "RX":
            qc.rx(float(p["theta"]), _wire(n, qs[0]))
        elif name == "RZ":
            qc.rz(float(p["theta"]), _wire(n, qs[0]))
        elif name == "PAULI_ROTATION":
            from qiskit.circuit.library import PauliEvolutionGate
            from qiskit.quantum_info import Pauli

            ps = str(p["pauli_string"])
            phi = float(p["phi"])
            gate = PauliEvolutionGate(Pauli(ps[::-1]), time=phi / 2.0)
            qc.append(gate, [_wire(n, q) for q in range(n)])
        elif name in ("CX", "CNOT"):
            qc.cx(_wire(n, qs[0]), _wire(n, qs[1]))
        elif name == "H":
            qc.h(_wire(n, qs[0]))
        elif name == "SDG":
            qc.sdg(_wire(n, qs[0]))
        elif name == "S":
            qc.s(_wire(n, qs[0]))
        elif name == "X":
            qc.x(_wire(n, qs[0]))
        elif name == "SX":
            qc.sx(_wire(n, qs[0]))
        elif name == "SXDG":
            qc.sxdg(_wire(n, qs[0]))
        elif name == "MEASURE":
            cbit = 0 if qc.num_clbits else None
            if cbit is None:
                continue
            qc.measure(_wire(n, qs[0]), cbit)
        elif name in ("CSWAP", "FREDKIN"):
            qc.cswap(_wire(n, qs[0]), _wire(n, qs[1]), _wire(n, qs[2]))
        elif name == "SWAP_TEST_SKETCH":
            anc = _wire(n, qs[0])
            sys_qs = [_wire(n, q) for q in qs[1:]]
            qc.h(anc)
            for q in sys_qs:
                qc.cswap(anc, q, q)
        elif name == "JOINT_PAULI_MEASURE":
            continue
        else:
            raise ValueError(f"unsupported CircuitIR op for qiskit export: {name!r}")
    return qc


def uccsd_circuit_qiskit(
    n_qubits: int,
    angles: np.ndarray,
    ctx: UCCSDCircuitContext,
) -> Any:
    from qchem_stack.quantum.algorithms.uccsd_circuit import uccsd_circuit_ir

    ir = uccsd_circuit_ir(np.asarray(angles, dtype=float), ctx, n_qubits=n_qubits)
    return circuit_ir_to_qiskit(ir)


def statevector_from_circuit_ir(ir: CircuitIR) -> np.ndarray:
    """Exact statevector via Qiskit (used for UCCSD parity tests)."""
    from qiskit.quantum_info import Statevector

    qc = circuit_ir_to_qiskit(ir)
    return np.asarray(Statevector.from_instruction(qc).data, dtype=np.complex128).ravel()
