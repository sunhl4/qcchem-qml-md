"""Versioned JSON interchange for ``PauliAveragingProtocol`` job blobs (no pickle)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypedDict, cast

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.protocols.protocol import PauliAveragingProtocol

if TYPE_CHECKING:
    from qchem_stack.config import NexusAnalogSpec
    from qchem_stack.mitigation.pmsv import PMSVConfig


PROTOCOL_BLOB_VERSION_V2 = 2


class ProtocolBlobDocumentV2(TypedDict, total=False):
    """JSON document shape for :func:`protocol_to_v2_document` / v2 job blobs."""

    protocol_blob_version: int
    hamiltonian: dict[str, Any]
    n_qubits: int
    backend_spec: dict[str, Any]
    pass_bundle: dict[str, Any]
    pmsv: dict[str, Any] | None
    zne_scales: list[float] | None
    zne_mode: str
    hea_depth: int
    angles: list[float]
    measurement_grouping: str
    run_sampled: bool
    run_qiskit_shots: bool
    record_histograms: bool
    pauli_support_max_terms: int | None
    classical_shadows_enabled: bool
    classical_shadows_budget_pairs: int
    nexus_analog: dict[str, Any] | None


def _serialize_qubit_operator(op: QubitOperator) -> dict[str, Any]:
    terms: list[dict[str, Any]] = []
    for pauli, coeff in op.terms.items():
        c = complex(coeff)
        pauli_tuple = tuple(pauli) if pauli else ()
        terms.append(
            {
                "coeff_real": c.real,
                "coeff_imag": c.imag,
                "pauli": [[int(i), str(g)] for i, g in pauli_tuple],
            }
        )
    return {"terms": terms}


def _deserialize_qubit_operator(doc: dict[str, Any]) -> QubitOperator:
    op = QubitOperator()
    for term in doc.get("terms") or []:
        pauli_list = term.get("pauli") or []
        pauli = tuple((int(i), str(g)) for i, g in pauli_list)
        coeff = complex(float(term["coeff_real"]), float(term.get("coeff_imag", 0.0)))
        op += QubitOperator(pauli, coeff)
    return op


def _backend_spec_to_dict(spec: BackendSpec) -> dict[str, Any]:
    return {
        "name": spec.name,
        "provider": spec.provider,
        "shots_per_circuit": spec.shots_per_circuit,
        "target_energy_stderr": spec.target_energy_stderr,
        "supports_mid_circuit_measure": spec.supports_mid_circuit_measure,
        "native_twoq": spec.native_twoq,
        "qiskit_mode": spec.qiskit_mode,
        "ionstack_endpoint": spec.ionstack_endpoint,
        "uqc_token": spec.uqc_token,
        "uqc_backend_name": spec.uqc_backend_name,
        "uqc_mode": spec.uqc_mode,
        "uqc_transpile_opt_level": spec.uqc_transpile_opt_level,
        "meta": dict(spec.meta),
    }


def _backend_spec_from_dict(doc: dict[str, Any]) -> BackendSpec:
    return BackendSpec(
        name=str(doc["name"]),
        provider=doc.get("provider", "statevector"),
        shots_per_circuit=int(doc.get("shots_per_circuit", 1024)),
        target_energy_stderr=doc.get("target_energy_stderr"),
        supports_mid_circuit_measure=bool(doc.get("supports_mid_circuit_measure", False)),
        native_twoq=str(doc.get("native_twoq", "CX")),
        qiskit_mode=doc.get("qiskit_mode", "statevector"),
        ionstack_endpoint=doc.get("ionstack_endpoint"),
        uqc_token=doc.get("uqc_token"),
        uqc_backend_name=doc.get("uqc_backend_name"),
        uqc_mode=doc.get("uqc_mode", "real"),
        uqc_transpile_opt_level=int(doc.get("uqc_transpile_opt_level", 2)),
        meta=dict(doc.get("meta") or {}),
    )


def _pass_bundle_to_dict(bundle: CompilerPassBundle) -> dict[str, Any]:
    return {
        "optimization_level": bundle.optimization_level,
        "preoptimize_passes": list(bundle.preoptimize_passes),
        "compiler_passes": list(bundle.compiler_passes),
    }


def _pass_bundle_from_dict(doc: dict[str, Any]) -> CompilerPassBundle:
    return CompilerPassBundle(
        optimization_level=int(doc.get("optimization_level", 1)),
        preoptimize_passes=list(doc.get("preoptimize_passes") or []),
        compiler_passes=list(doc.get("compiler_passes") or []),
    )


def _pmsv_to_dict(pmsv: PMSVConfig | None) -> dict[str, Any] | None:
    if pmsv is None:
        return None
    return {
        "stabilizers": list(pmsv.stabilizers),
        "retention_rate": float(pmsv.retention_rate),
    }


def _nexus_analog_to_dict(na: NexusAnalogSpec | None) -> dict[str, Any] | None:
    if na is None:
        return None
    return na.model_dump()


def _nexus_analog_from_dict(doc: dict[str, Any] | None) -> NexusAnalogSpec | None:
    if not doc:
        return None
    from qchem_stack.config import NexusAnalogSpec

    return NexusAnalogSpec.model_validate(doc)


def _pmsv_from_dict(doc: dict[str, Any] | None) -> PMSVConfig | None:
    if not doc:
        return None
    from qchem_stack.mitigation.pmsv import PMSVConfig

    return PMSVConfig(
        stabilizers=list(doc.get("stabilizers") or []),
        retention_rate=float(doc.get("retention_rate", 1.0)),
    )


def protocol_to_v2_document(proto: PauliAveragingProtocol) -> ProtocolBlobDocumentV2:
    """Build a JSON-serializable protocol document (schema version 2)."""
    angles = np.asarray(proto.angles, dtype=float)
    doc: ProtocolBlobDocumentV2 = {
        "protocol_blob_version": PROTOCOL_BLOB_VERSION_V2,
        "hamiltonian": _serialize_qubit_operator(proto.hamiltonian),
        "n_qubits": int(proto.n_qubits),
        "backend_spec": _backend_spec_to_dict(proto.backend),
        "pass_bundle": _pass_bundle_to_dict(proto.pass_bundle),
        "pmsv": _pmsv_to_dict(proto.pmsv),
        "zne_scales": list(proto.zne_scales) if proto.zne_scales is not None else None,
        "zne_mode": proto.zne_mode,
        "hea_depth": int(proto.hea_depth),
        "angles": angles.tolist(),
        "measurement_grouping": proto.measurement_grouping,
        "run_sampled": bool(proto.run_sampled),
        "run_qiskit_shots": bool(proto.run_qiskit_shots),
        "record_histograms": bool(proto.record_histograms),
        "pauli_support_max_terms": proto.pauli_support_max_terms,
        "classical_shadows_enabled": bool(proto.classical_shadows_enabled),
        "classical_shadows_budget_pairs": int(proto.classical_shadows_budget_pairs),
        "nexus_analog": _nexus_analog_to_dict(proto.nexus_analog),
    }
    return doc


def protocol_from_v2_document(
    doc: ProtocolBlobDocumentV2 | dict[str, Any],
) -> PauliAveragingProtocol:
    """Reconstruct ``PauliAveragingProtocol`` from a v2 JSON document."""
    if int(doc.get("protocol_blob_version", 0)) != PROTOCOL_BLOB_VERSION_V2:
        raise ValueError(
            f"expected protocol_blob_version={PROTOCOL_BLOB_VERSION_V2}, "
            f"got {doc.get('protocol_blob_version')!r}"
        )
    ham = _deserialize_qubit_operator(cast("dict[str, Any]", doc["hamiltonian"]))
    angles = np.asarray(doc.get("angles") or [0.0], dtype=float)
    return PauliAveragingProtocol(
        hamiltonian=ham,
        n_qubits=int(doc["n_qubits"]),
        backend=_backend_spec_from_dict(cast("dict[str, Any]", doc["backend_spec"])),
        pass_bundle=_pass_bundle_from_dict(cast("dict[str, Any]", doc.get("pass_bundle") or {})),
        pmsv=_pmsv_from_dict(cast("dict[str, Any] | None", doc.get("pmsv"))),
        zne_scales=list(doc["zne_scales"]) if doc.get("zne_scales") is not None else None,
        zne_mode=doc.get("zne_mode", "scalar_stub"),
        hea_depth=int(doc.get("hea_depth", 1)),
        angles=angles,
        measurement_grouping=doc.get("measurement_grouping", "tensor_product"),
        run_sampled=bool(doc.get("run_sampled", False)),
        run_qiskit_shots=bool(doc.get("run_qiskit_shots", False)),
        record_histograms=bool(doc.get("record_histograms", False)),
        pauli_support_max_terms=doc.get("pauli_support_max_terms"),
        classical_shadows_enabled=bool(doc.get("classical_shadows_enabled", False)),
        classical_shadows_budget_pairs=int(doc.get("classical_shadows_budget_pairs", 256)),
        nexus_analog=_nexus_analog_from_dict(
            cast("dict[str, Any] | None", doc.get("nexus_analog"))
        ),
    )


def protocol_v2_dumps(proto: PauliAveragingProtocol) -> bytes:
    """UTF-8 JSON bytes for a v2 protocol document."""
    return json.dumps(protocol_to_v2_document(proto), separators=(",", ":")).encode("utf-8")


def protocol_v2_loads(data: bytes) -> PauliAveragingProtocol:
    """Parse v2 JSON bytes into a protocol instance."""
    doc = json.loads(data.decode("utf-8"))
    if not isinstance(doc, dict):
        raise TypeError("protocol v2 document must be a JSON object")
    return protocol_from_v2_document(doc)


def is_protocol_v2_json_payload(payload: bytes) -> bool:
    """Heuristic: unsigned JSON object with ``protocol_blob_version`` 2."""
    stripped = payload.lstrip()
    if not stripped.startswith(b"{"):
        return False
    try:
        doc = json.loads(stripped.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return (
        isinstance(doc, dict)
        and int(doc.get("protocol_blob_version", 0)) == PROTOCOL_BLOB_VERSION_V2
    )


__all__ = [
    "PROTOCOL_BLOB_VERSION_V2",
    "ProtocolBlobDocumentV2",
    "is_protocol_v2_json_payload",
    "protocol_from_v2_document",
    "protocol_to_v2_document",
    "protocol_v2_dumps",
    "protocol_v2_loads",
]
