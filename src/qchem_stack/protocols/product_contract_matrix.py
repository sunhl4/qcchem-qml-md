"""Ansatz × protocol compatibility matrix and runtime validation guards."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import ANSATZ_PROTOCOL_MATRIX_V1

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig, QuantumSpec


def classify_pauli_expectation_path(q: QuantumSpec) -> str:
    """Classify how ``energy_pauli_protocol`` is produced from config intent."""
    from qchem_stack.config.quantum_helpers import classify_pauli_expectation_path_from_flags

    return classify_pauli_expectation_path_from_flags(
        use_protocol=bool(q.pauli.use_protocol),
        run_sampled=bool(q.pauli.run_sampled),
        run_qiskit_shots=bool(q.pauli.run_qiskit_shots),
    )


def ansatz_protocol_matrix_v1() -> dict[str, Any]:
    """Ansatz × protocol compatibility matrix."""
    entries: list[dict[str, Any]] = [
        {
            "ansatz": "hea",
            "protocol": "pauli_averaging_exact",
            "status": "supported",
            "prep": "hea_operations",
        },
        {
            "ansatz": "hea",
            "protocol": "pauli_averaging_sampled",
            "status": "supported",
            "prep": "hea_operations",
        },
        {
            "ansatz": "hea",
            "protocol": "pauli_averaging_qiskit",
            "status": "supported",
            "prep": "hea_operations",
        },
        {
            "ansatz": "hea",
            "protocol": "zne_circuit_scale_fold",
            "status": "supported",
            "prep": "hea_depth_fold",
        },
        {
            "ansatz": "uccsd",
            "protocol": "pauli_averaging_exact",
            "status": "supported",
            "prep": "uccsd_circuit_ir_jw",
            "mapping": "jordan_wigner",
        },
        {
            "ansatz": "uccsd",
            "protocol": "pauli_averaging_sampled",
            "status": "supported",
            "prep": "uccsd_circuit_ir_jw",
            "mapping": "jordan_wigner",
        },
        {
            "ansatz": "uccsd",
            "protocol": "pauli_averaging_qiskit",
            "status": "supported",
            "prep": "uccsd_circuit_ir_jw",
            "mapping": "jordan_wigner",
        },
        {
            "ansatz": "uccsd",
            "protocol": "zne_circuit_scale_fold",
            "status": "unsupported",
            "reason": "HEA-only depth fold; use zne.mode=scalar_stub",
        },
        {
            "ansatz": "hea",
            "protocol": "qse_pauli_transitions",
            "status": "supported",
            "basis": "hea_pauli_x_bump_legacy",
        },
        {
            "ansatz": "uccsd",
            "protocol": "qse_pauli_transitions",
            "status": "supported",
            "basis": "uccsd_fermionic_singles",
        },
        {
            "ansatz": "uccsd",
            "protocol": "qse_pauli_transitions_qiskit",
            "status": "supported",
            "basis": "uccsd_fermionic_singles_or_doubles",
        },
        {
            "ansatz": "hea",
            "protocol": "sceom_nested_commutator",
            "status": "supported",
            "prep": "hea_statevector",
        },
        {
            "ansatz": "uccsd",
            "protocol": "sceom_nested_commutator",
            "status": "supported",
            "prep": "uccsd_prepare_state",
        },
    ]
    for cluster_ansatz in ("vsqs",):
        entries.append(
            {
                "ansatz": cluster_ansatz,
                "protocol": "pauli_averaging_exact",
                "status": "unsupported",
                "reason": "VSQS uses schedule-prepared statevector; enable pauli protocol only with HEA/UCCSD prep.",
            }
        )
    for cluster_ansatz in ("uccgd", "qcc", "upccgsd", "puccd"):
        prep = "qcc_circuit_ir" if cluster_ansatz == "qcc" else "uccsd_circuit_ir_jw"
        for protocol in (
            "pauli_averaging_exact",
            "pauli_averaging_sampled",
            "pauli_averaging_qiskit",
        ):
            entries.append(
                {
                    "ansatz": cluster_ansatz,
                    "protocol": protocol,
                    "status": "supported",
                    "prep": prep,
                    "mapping": "jordan_wigner",
                }
            )
        entries.append(
            {
                "ansatz": cluster_ansatz,
                "protocol": "zne_circuit_scale_fold",
                "status": "unsupported",
                "reason": "HEA-only depth fold; use zne.mode=scalar_stub",
            }
        )
        entries.append(
            {
                "ansatz": cluster_ansatz,
                "protocol": "qse_pauli_transitions",
                "status": "supported",
                "basis": "uccsd_fermionic_singles",
            }
        )
        entries.append(
            {
                "ansatz": cluster_ansatz,
                "protocol": "qse_pauli_transitions_qiskit",
                "status": "supported",
                "basis": "uccsd_fermionic_singles_or_doubles",
            }
        )
        entries.append(
            {
                "ansatz": cluster_ansatz,
                "protocol": "sceom_nested_commutator",
                "status": "supported",
                "prep": "uccsd_prepare_state" if cluster_ansatz != "qcc" else "qcc_prepare_state",
            }
        )
    return {
        "schema": ANSATZ_PROTOCOL_MATRIX_V1,
        "doc_anchor": "docs/quantum_模块风格约定.md#8-epistemic-bounds算法实现边界",
        "entries": entries,
    }


def matrix_pauli_protocol_name(cfg: ExperimentConfig) -> str:
    """Map YAML Pauli flags to :func:`ansatz_protocol_matrix_v1` protocol ids."""
    from qchem_stack.config.quantum_helpers import (
        PAULI_PATH_EXACT,
        PAULI_PATH_QISKIT_COUNTS,
        PAULI_PATH_STATEVECTOR_SHOT_SIM,
        classify_pauli_expectation_path_for_config,
    )

    path = classify_pauli_expectation_path_for_config(cfg)
    return {
        PAULI_PATH_EXACT: "pauli_averaging_exact",
        PAULI_PATH_STATEVECTOR_SHOT_SIM: "pauli_averaging_sampled",
        PAULI_PATH_QISKIT_COUNTS: "pauli_averaging_qiskit",
    }[path]


def matrix_qse_protocol_name(shot_mode: str) -> str:
    sm = str(shot_mode).strip().lower()
    if sm == "pauli_transitions_qiskit":
        return "qse_pauli_transitions_qiskit"
    if sm in {"pauli_transitions", "gaussian_h"}:
        return "qse_pauli_transitions"
    return "qse_exact"


def validate_ansatz_protocol_combo(
    ansatz: str,
    protocol: str,
    *,
    computable_kind: str | None = None,
) -> None:
    """Runtime guard aligned with :func:`ansatz_protocol_matrix_v1` entries."""
    matrix = ansatz_protocol_matrix_v1()
    ans = str(ansatz).strip().lower()
    prot = str(protocol).strip().lower()
    for entry in matrix["entries"]:
        if entry.get("ansatz") != ans or entry.get("protocol") != prot:
            continue
        if entry.get("status") == "unsupported":
            raise ValueError(
                f"ansatz={ans!r} protocol={prot!r} unsupported: {entry.get('reason', '')}"
            )
        return
    if computable_kind in {"qse_matrices", "sceom_matrix"} and prot.startswith("pauli"):
        return
    raise ValueError(f"ansatz={ans!r} protocol={prot!r} not in ansatz_protocol_matrix_v1")


def validate_pauli_protocol_for_config(cfg: ExperimentConfig, *, ansatz: str) -> None:
    validate_ansatz_protocol_combo(str(ansatz).lower(), matrix_pauli_protocol_name(cfg))


def validate_qse_protocol_for_config(cfg: ExperimentConfig, *, ansatz: str, shot_mode: str) -> None:
    prot = matrix_qse_protocol_name(shot_mode)
    if prot == "qse_exact":
        return
    validate_ansatz_protocol_combo(
        str(ansatz).lower(),
        prot,
        computable_kind="qse_matrices",
    )
