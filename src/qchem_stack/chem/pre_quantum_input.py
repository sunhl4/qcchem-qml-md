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

PRE_QUANTUM_INPUT_SCHEMA_V1 = "pre_quantum_input_v1"


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
        summary: dict[str, Any] = {
            "schema": self.schema,
            "backend_tag": self.classical_reference.backend_tag(),
            "n_qubits": int(self.qubit_hamiltonian.n_qubits),
            "hamiltonian_meta": dict(self.qubit_hamiltonian.meta),
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
