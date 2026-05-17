"""Document when embedding changes the qubit Hamiltonian vs post-variational audit only."""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.pre_quantum_path import resolve_pre_quantum_path
from qchem_stack.config import ExperimentConfig


def pre_quantum_hamiltonian_semantics(cfg: ExperimentConfig) -> dict[str, Any]:
    """Stable semantics for repro / parity (pre-quantum vs post-VQE embedding)."""
    emb = cfg.embedding
    branch = resolve_pre_quantum_path(cfg).value

    # Post-VQE ``embedding_workflow`` never replaces the variational ``qh`` in this stack.
    post_audit_only = True

    return {
        "hamiltonian_branch": branch,
        "hamiltonian_fixed_before_variational": True,
        "post_variational_embedding_audit_only": bool(post_audit_only),
        "embedding_mode": str(emb.mode),
        "dmet_hamiltonian_source": str(emb.dmet_hamiltonian_source),
    }
