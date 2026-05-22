"""Unified classical-to-quantum handoff object.

All chemistry backends should be normalized to this object before quantum
algorithms run, so downstream modules avoid backend-specific branching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import PRE_QUANTUM_INPUT_SCHEMA_V1

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

# Keys copied from ``QubitHamiltonian.meta`` into branch-stable handoff meta / summaries.
HAMILTONIAN_META_BRANCH_KEYS: tuple[str, ...] = (
    "integral_source",
    "fermion_to_qubit_map",
    "hamiltonian_fingerprint",
    "integral_openfermion_bridge",
    "hamiltonian_fingerprint_truncated",
    "jordan_wigner_coeff_atol",
)

HAMILTONIAN_META_SUMMARY_EXTRA_KEYS: tuple[str, ...] = (
    "jw_build",
    "n_active_orbitals",
    "n_active_electrons",
)

HAMILTONIAN_SEMANTICS_KEYS: tuple[str, ...] = (
    "hamiltonian_branch",
    "hamiltonian_fixed_before_variational",
    "post_variational_embedding_audit_only",
)


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
    }
    for key in HAMILTONIAN_META_BRANCH_KEYS:
        if key in hmeta:
            out[key] = hmeta[key]
    if extra:
        out.update(extra)
    return out


def build_pre_quantum_meta(
    cfg: Any,
    *,
    source: str,
    qubit_hamiltonian: QubitHamiltonian,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Hamiltonian branch meta plus parity semantics (all ingress paths)."""
    from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics

    meta = pre_quantum_meta_from_hamiltonian(
        source=source,
        qubit_hamiltonian=qubit_hamiltonian,
        extra=extra,
    )
    meta.update(pre_quantum_hamiltonian_semantics(cfg))
    return meta


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

    @property
    def hamiltonian(self) -> QubitHamiltonian:
        return self.qubit_hamiltonian

    def as_summary_dict(self) -> dict[str, Any]:
        pack = self.canonical_active_space_integral_pack
        hmeta = dict(self.qubit_hamiltonian.meta)
        source = str(self.meta.get("source") or "")
        hamiltonian_summary: dict[str, Any] = {
            "n_qubits": int(self.qubit_hamiltonian.n_qubits),
        }
        for key in HAMILTONIAN_META_BRANCH_KEYS + HAMILTONIAN_META_SUMMARY_EXTRA_KEYS:
            if key in hmeta:
                hamiltonian_summary[key] = hmeta[key]
        na = hmeta.get("n_active_orbitals")
        ne = hmeta.get("n_active_electrons")
        if pack is not None:
            na = int(pack.compact.n_active_orbitals)
            ne = int(pack.compact.n_active_electrons)
        summary: dict[str, Any] = {
            "schema": self.schema,
            "source": source,
            "backend_tag": self.classical_reference.backend_tag(),
            "n_qubits": int(self.qubit_hamiltonian.n_qubits),
            "reference_energy_au": float(self.classical_reference.e_tot),
            "scf_energy_au": float(self.classical_reference.e_tot),
            "n_active_orbitals": na,
            "n_active_electrons": ne,
            "hamiltonian_summary": hamiltonian_summary,
            "hamiltonian_meta": hmeta,
            "meta": dict(self.meta),
            "has_canonical_active_space_integral_pack": pack is not None,
        }
        for key in HAMILTONIAN_META_BRANCH_KEYS:
            summary[key] = hamiltonian_summary.get(key)
        for key in HAMILTONIAN_SEMANTICS_KEYS:
            if key in self.meta:
                summary[key] = self.meta[key]
        dm = dict(self.classical_reference.driver_meta or {})
        bindings = dm.get("kernel_bindings")
        if bindings:
            summary["classical_kernel_bindings"] = list(bindings)
        bound = dm.get("epistemic_bound")
        if bound:
            text = str(bound)
            summary["classical_epistemic_bound"] = text[:512] + ("…" if len(text) > 512 else "")
        if pack is not None:
            summary["canonical_active_space_integral_pack"] = {
                "schema": pack.schema,
                "provenance": dict(pack.provenance),
                "n_active_orbitals": int(pack.compact.n_active_orbitals),
                "n_active_electrons": int(pack.compact.n_active_electrons),
                "compact_storage_schema": pack.compact.storage_schema,
            }
        return summary
