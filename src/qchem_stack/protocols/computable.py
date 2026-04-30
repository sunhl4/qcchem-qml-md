"""
Thin InQuanto-*Computable*-style descriptors (open stack).

InQuanto exposes ``Computable`` objects that bind observables to execution; here we attach
**named, serializable** summaries for Methods / parity export without a second object graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qchem_stack.config import ExperimentConfig
from qchem_stack.protocols.inquanto_contract import classify_pauli_expectation_path, pauli_protocol_expectation_path_for_config


@dataclass(frozen=True)
class ComputableRef:
    """A single high-level target (analog of a documented InQuanto computable)."""

    name: str
    """E.g. ``ground_state_energy_hea_pauli``."""
    kind: str
    """Coarse class: ``energy``, ``spectrum``, ``phase``."""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComputableSpec:
    """Typed twin of :class:`ComputableRef` for specs / rich workflow export."""

    name: str
    kind: str
    details: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_ref(r: ComputableRef) -> ComputableSpec:
        return ComputableSpec(name=r.name, kind=r.kind, details=dict(r.details))

    def to_ref(self) -> ComputableRef:
        return ComputableRef(name=self.name, kind=self.kind, details=dict(self.details))


def list_computables_for_config(cfg: ExperimentConfig) -> list[ComputableRef]:
    """List what the current YAML is configured to *evaluate* (best-effort, documentation-first)."""
    out: list[ComputableRef] = []
    q = cfg.quantum
    if q.algorithm == "vqe":
        out.append(ComputableRef("ground_state_energy", "energy", {"algorithm": "vqe", "vqe_depth": q.vqe_depth}))
    elif q.algorithm == "adapt":
        out.append(
            ComputableRef("ground_state_energy", "energy", {"algorithm": "adapt", "adapt_max_iter": q.adapt_max_iter})
        )
    else:
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm": "iqeb",
                    "iqeb_max_rounds": q.iqeb_max_rounds,
                    "vqe_depth": q.vqe_depth,
                },
            )
        )
    if q.use_pauli_protocol:
        out.append(
            ComputableRef(
                "hamiltonian_expectation_pauli_protocol",
                "energy",
                {
                    "pauli_grouping": q.pauli_grouping,
                    "pauli_protocol_expectation_path": classify_pauli_expectation_path(q),
                },
            )
        )
    if q.vqd_after_variational:
        out.append(ComputableRef("excited_energies_vqd", "spectrum", {"n_states": q.vqd_n_states}))
    if q.qse_after_variational:
        out.append(ComputableRef("excitation_energies_qse", "spectrum", {"subspace_dim": q.qse_subspace_dim}))
    if q.sceom_after_variational:
        out.append(ComputableRef("sceom_energies", "spectrum", {"subspace_dim": q.sceom_subspace_dim}))
    if q.qpe_demo_track_after_variational:
        out.append(ComputableRef("qpe_demo_track", "phase", {"hook": "qpe_qec_demo.kitaev + bayesian_stub"}))
    return out


def list_computable_specs_for_config(cfg: ExperimentConfig) -> list[ComputableSpec]:
    return [ComputableSpec.from_ref(r) for r in list_computables_for_config(cfg)]


def computables_export_dict(
    cfg: ExperimentConfig,
    protocol_counts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """JSON-friendly blob for :mod:`scripts.export_parity_criteria_table`.

    When ``protocol_counts`` is passed (e.g. from a finished pipeline run), marks that the
    Pauli support set is available for strict :func:`~qchem_stack.protocols.pauli_support.assert_evaluate_compatible` checks.
    """
    support_from = bool(
        protocol_counts is not None and protocol_counts.get("hamiltonian_pauli_strings") is not None
    )
    return {
        "schema": "qchem_computable_abstract_v2",
        "pauli_protocol_expectation_path": pauli_protocol_expectation_path_for_config(cfg),
        "evaluate_note": (
            "Strict InQuanto-style evaluate reuse (conservative): each required Pauli label must appear "
            "in hamiltonian_pauli_strings from protocol_counts; see "
            "qchem_stack.protocols.pauli_support.assert_evaluate_compatible."
        ),
        "support_set_exported_from_protocol": support_from,
        "items": [
            {"name": c.name, "kind": c.kind, "details": c.details} for c in list_computables_for_config(cfg)
        ],
    }
