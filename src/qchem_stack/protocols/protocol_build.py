"""BUILD/COMPILE stages for :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.backends.compile_passes import apply_pass_bundle
from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_measure_expand import (
    build_synthesized_pauli_shot_circuit,
    deserialize_basis_key,
    hea_operations,
)
from qchem_stack.backends.spec import CircuitIR
from qchem_stack.protocols.protocol_phase import ProtocolPhase

if TYPE_CHECKING:
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def build_logical_circuits(
    proto: PauliAveragingProtocol, angles: np.ndarray, hea_depth: int = 1
) -> None:
    proto._phase = ProtocolPhase.BUILD
    proto.angles = np.asarray(angles, dtype=float)
    proto.hea_depth = hea_depth
    proto._measurement_plan = build_measurement_plan(
        proto.hamiltonian, proto.n_qubits, grouping=proto.measurement_grouping
    )
    circuits: list[CircuitIR] = []
    for meta in proto._measurement_plan.to_circuit_metas():
        n_terms = int(meta.get("n_terms", 0))
        qs = list(meta.get("support_qubits", []))
        bk = deserialize_basis_key(meta.get("basis_key"))
        if n_terms == 0:
            circuits.append(
                CircuitIR(
                    n_qubits=proto.n_qubits,
                    operations=hea_operations(proto.n_qubits, hea_depth, proto.angles),
                    boxes=["HEA"],
                )
            )
        elif bk is not None:
            circuits.append(
                build_synthesized_pauli_shot_circuit(
                    proto.n_qubits,
                    hea_depth,
                    proto.angles,
                    basis_key=bk,
                    support_qubits=qs,
                )
            )
        else:
            ops = hea_operations(proto.n_qubits, hea_depth, proto.angles)
            ops.append({"name": "JOINT_PAULI_MEASURE", "qubits": qs, "params": dict(meta)})
            circuits.append(
                CircuitIR(
                    n_qubits=proto.n_qubits, operations=ops, boxes=["HEA", "JointPauliMeasure"]
                )
            )
    proto._logical_circuits = circuits


def compile_circuits(proto: PauliAveragingProtocol) -> None:
    proto._phase = ProtocolPhase.COMPILE
    pre = proto.pass_bundle.preoptimize_passes + proto.pass_bundle.compiler_passes
    proto._compiled = [apply_pass_bundle(c, pre) for c in proto._logical_circuits]
