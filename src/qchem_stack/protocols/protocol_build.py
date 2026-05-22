"""BUILD/COMPILE stages for :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.backends.compile_passes import apply_pass_bundle
from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_measure_expand import (
    build_synthesized_pauli_shot_circuit,
    deserialize_basis_key,
)
from qchem_stack.backends.spec import CircuitIR
from qchem_stack.protocols.ansatz_prep import AnsatzPrepSpec, build_prep_operations, prep_box_label
from qchem_stack.protocols.protocol_phase import ProtocolPhase

if TYPE_CHECKING:
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def build_logical_circuits(
    proto: PauliAveragingProtocol,
    angles: np.ndarray,
    hea_depth: int = 1,
    *,
    ansatz_prep: AnsatzPrepSpec | None = None,
) -> None:
    proto._phase = ProtocolPhase.BUILD
    proto.angles = np.asarray(angles, dtype=float)
    if ansatz_prep is not None:
        proto.ansatz_prep = ansatz_prep
    elif proto.ansatz_prep is None:
        proto.ansatz_prep = AnsatzPrepSpec.hea(
            n_qubits=proto.n_qubits,
            angles=proto.angles,
            depth=hea_depth,
        )
    else:
        proto.ansatz_prep.angles = proto.angles
    proto.hea_depth = hea_depth if proto.ansatz_prep.kind == "hea" else proto.hea_depth
    prep_ops = build_prep_operations(proto.ansatz_prep)
    prep_box = prep_box_label(proto.ansatz_prep)
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
                    operations=list(prep_ops),
                    boxes=[prep_box],
                )
            )
        elif bk is not None:
            circuits.append(
                build_synthesized_pauli_shot_circuit(
                    proto.n_qubits,
                    prep_ops,
                    basis_key=bk,
                    support_qubits=qs,
                    prep_box=prep_box,
                )
            )
        else:
            ops = list(prep_ops)
            ops.append({"name": "JOINT_PAULI_MEASURE", "qubits": qs, "params": dict(meta)})
            circuits.append(
                CircuitIR(
                    n_qubits=proto.n_qubits,
                    operations=ops,
                    boxes=[prep_box, "JointPauliMeasure"],
                )
            )
    proto._logical_circuits = circuits


def compile_circuits(proto: PauliAveragingProtocol) -> None:
    proto._phase = ProtocolPhase.COMPILE
    pre = proto.pass_bundle.preoptimize_passes + proto.pass_bundle.compiler_passes
    proto._compiled = [apply_pass_bundle(c, pre) for c in proto._logical_circuits]
