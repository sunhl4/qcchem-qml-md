"""Unified classical-to-quantum handoff object.

All chemistry backends should be normalized to this object before quantum
algorithms run, so downstream modules avoid backend-specific branching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.contracts.schema_ids import PRE_QUANTUM_INPUT_SCHEMA_V1


def pre_quantum_meta_from_hamiltonian(
    *,
    source: str,
    qubit_hamiltonian: QubitHamiltonian,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stable branch metadata copied alongside the canonical handoff object."""
    hmeta = dict(qubit_hamiltonian.meta)
    out: dict[str, Any] = {
        "source": str(source),
        "n_qubits": int(qubit_hamiltonian.n_qubits),
        "integral_source": hmeta.get("integral_source"),
        "fermion_to_qubit_map": hmeta.get("fermion_to_qubit_map"),
        "hamiltonian_fingerprint": hmeta.get("hamiltonian_fingerprint"),
    }
    for key in (
        "integral_openfermion_bridge",
        "hamiltonian_fingerprint_truncated",
        "jordan_wigner_coeff_atol",
    ):
        if key in hmeta:
            out[key] = hmeta[key]
    if extra:
        out.update(extra)
    return out


@dataclass(frozen=True)
class PreQuantumInput:
    """Canonical payload consumed by quantum orchestration/runtime layers."""

    classical_reference: ClassicalMeanFieldReference
    qubit_hamiltonian: QubitHamiltonian
    canonical_active_space_integral_pack: CanonicalActiveSpaceIntegralPack | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def schema(self) -> str:
        return PRE_QUANTUM_INPUT_SCHEMA_V1

    def as_summary_dict(self) -> dict[str, Any]:
        pack = self.canonical_active_space_integral_pack
        hmeta = dict(self.qubit_hamiltonian.meta)
        source = str(self.meta.get("source") or "")
        hamiltonian_summary: dict[str, Any] = {
            "n_qubits": int(self.qubit_hamiltonian.n_qubits),
            "integral_source": hmeta.get("integral_source"),
            "fermion_to_qubit_map": hmeta.get("fermion_to_qubit_map"),
            "hamiltonian_fingerprint": hmeta.get("hamiltonian_fingerprint"),
        }
        for key in (
            "integral_openfermion_bridge",
            "jw_build",
            "n_active_orbitals",
            "n_active_electrons",
            "hamiltonian_fingerprint_truncated",
            "jordan_wigner_coeff_atol",
        ):
            if key in hmeta:
                hamiltonian_summary[key] = hmeta[key]
        summary: dict[str, Any] = {
            "schema": self.schema,
            "source": source,
            "backend_tag": self.classical_reference.backend_tag(),
            "n_qubits": int(self.qubit_hamiltonian.n_qubits),
            "integral_source": hamiltonian_summary.get("integral_source"),
            "fermion_to_qubit_map": hamiltonian_summary.get("fermion_to_qubit_map"),
            "hamiltonian_fingerprint": hamiltonian_summary.get("hamiltonian_fingerprint"),
            "hamiltonian_summary": hamiltonian_summary,
            "hamiltonian_meta": hmeta,
            "meta": dict(self.meta),
            "has_canonical_active_space_integral_pack": pack is not None,
        }
        if pack is not None:
            summary["canonical_active_space_integral_pack"] = {
                "schema": pack.schema,
                "provenance": dict(pack.provenance),
                "n_active_orbitals": int(pack.compact.n_active_orbitals),
                "n_active_electrons": int(pack.compact.n_active_electrons),
                "compact_storage_schema": pack.compact.storage_schema,
            }
        return summary
