"""
Projection **workflow** labels and a small config dataclass used in L1 parity traces.

**Variational Hamiltonian (non-stub path)** when ``embedding.projection.quantum_hamiltonian`` is
``fragment_mulliken_mo``: see :mod:`qchem_stack.chem.embedding.projection_hamiltonian` — RHF
``mo_coeff``, Mulliken AO weights on fragment atoms, PySCF :class:`pyscf.mcscf.CASCI` ``get_h1eff`` /
``get_h2eff`` (same chemist ``h2`` convention as :func:`~qchem_stack.chem.integrals.pyscf_active_space.active_space_integrals`),
then Jordan–Wigner.

**References (surface / Methods wording)**: Mulliken populations and MO locality screening are standard
in electronic structure texts; the implementation stays on public PySCF APIs only.

**Epistemic boundary**: this stack does **not** implement full many-body projection embedding of the
environment wavefunction onto an active space, nor claim parity with proprietary vendor PySCF extensions.
"""

from __future__ import annotations

from dataclasses import dataclass

from qchem_stack.chem.tolerances import PROJECTION_EMBEDDING_THRESHOLD


@dataclass
class ProjectionEmbeddingConfig:
    """Lightweight projection trace parameters (paired with :class:`~qchem_stack.config.EmbeddingSpec` YAML)."""

    low_level: str = "HF"
    high_level: str = "CAS"
    threshold: float = PROJECTION_EMBEDDING_THRESHOLD
