"""Embedding configuration for DMET/projection workflows and plugin hooks."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ._embedding_validation import (
    validate_dmet_hamiltonian_source,
    validate_plugin_embedding_requires_fields,
    validate_projection_mulliken_requires_mode_and_indices,
)
from ._validation import strip_optional_text


class EmbeddingSpec(BaseModel):
    """Falsifiability fields for DMET / projection workflows (chemistry pre-stage)."""

    mode: Literal["none", "dmet", "projection", "plugin"] = "none"
    embedding_input_representation: Literal["mo", "ao", "lowdin_orth_ao"] = "mo"
    """
    Pre-embedding chemistry representation preference (Phase B):
    ``mo`` (default), ``ao`` (SCF object wrapper), or ``lowdin_orth_ao`` (localized orthogonal AO tensors).
    """
    n_scf_cycles_embedding: int | None = None
    """How many self-consistent embedding sweeps; ``None`` if not used."""
    classical_reference_method: str | None = None
    """E.g. ``MP2``, ``CASSCF``, ``DLPNO-CC`` — documentation / parity only in this open stack."""
    projection_low_level: str = "HF"
    """Low-level reference for ``mode=='projection'`` (L1 trace; no PySCF projection driver yet)."""
    projection_high_level: str = "CAS"
    """High-level correlation label for projection trace (documentation-only until a driver is wired)."""
    projection_threshold: float = Field(default=1e-8, gt=0)
    """Numerical threshold recorded for Methods when ``mode=='projection'``."""
    projection_quantum_hamiltonian: Literal["global_active_space", "fragment_mulliken_mo"] = (
        "global_active_space"
    )
    """
    ``global_active_space`` (default): variational ``QubitHamiltonian`` from global
    :class:`ActiveSpaceSpec` (legacy L1 trace + projection metadata only).

    ``fragment_mulliken_mo``: build active orbitals by **Mulliken fragment weights** on
    ``projection_fragment_atom_indices``, then CASCI-core integrals + JW — see
    :mod:`qchem_stack.chem.embedding.projection_hamiltonian`.
    """
    projection_fragment_atom_indices: list[int] = Field(default_factory=list)
    """Zero-based atom indices for ``projection_quantum_hamiltonian=='fragment_mulliken_mo'`` (required when set)."""
    fragment_labels: list[str] = Field(default_factory=list)
    """Fragment ids when ``mode==dmet``; empty when ``none``."""
    dmet_hamiltonian_source: Literal[
        "parity_stub", "whole_active_system", "schmidt_atomic_production"
    ] = "parity_stub"
    """
    Impurity operator source for DMET-shaped runs (open stack).

    ``parity_stub``: parity ledger uses placeholder dicts. ``whole_active_system``: reuse the global
    active-space ``QubitHamiltonian`` as the impurity (default: exactly one ``fragment_labels`` entry;
    optionally multiple labels when ``dmet_multifragment_one_shot_shared_hamiltonian`` is ``True``).
    ``schmidt_atomic_production``: **Schmidt + spectral bath** impurity Hamiltonian from SCF density
    (see ``schmidt_*`` fields); main-pipeline VQE runs on this impurity ``QubitHamiltonian``, not CASCI active space.
    """
    dmet_target_fragment_electrons: float | None = None
    """Optional DMET-style fragment electron target for μ calibration (Schmidt path when bisection enabled)."""
    schmidt_fragment_atom_indices: list[int] = Field(default_factory=list)
    """Zero-based atom indices for fragment AO seed (required for ``schmidt_atomic_production``)."""
    schmidt_n_bath_spatial: int = 2
    """Number of bath spatial orbitals from environment (D,S) spectral truncation."""
    schmidt_max_impurity_spatial_orbitals: int = 14
    """Hard cap on impurity spatial dimension (FCI / JW cost guard)."""
    schmidt_run_mu_bisection: bool = False
    """If ``True`` and ``dmet_target_fragment_electrons`` is set, bisect μ on fragment diagonal (FCI reference)."""
    schmidt_attach_fci_reference: bool = True
    """Attach small-basis FCI reference energy/1-RDM in audit when impurity spatial count ≤ cap."""
    schmidt_fci_reference_max_spatial_orbitals: int = 8
    """Skip FCI reference block above this impurity spatial size (cost guard)."""
    schmidt_dmet_max_cycles: int = Field(default=1, ge=1, le=256)
    """
    Outer Schmidt/FCI density-feedback iterations (:mod:`~qchem_stack.integrations.schmidt_dmet_self_consistent`).
    ``1`` = single-shot (SCF density only). ``>1`` = iterate bath from mixed global AO density (engineering DMET SCF).
    """
    schmidt_dmet_mixing_alpha: float = Field(default=0.35, gt=0.0, le=1.0)
    """Linear mixing of FCI impurity 1-RDM embedded in AO basis into the global density."""
    schmidt_dmet_convergence_tol: float = Field(default=1e-3, gt=0.0)
    """Stop outer iterations early when :math:`\\| \\mathrm{dm1}_{FCI} - \\gamma \\|_F` falls below this (after cycle 0)."""
    schmidt_multi_fragment_atom_groups: list[list[int]] = Field(default_factory=list)
    """
    If non-empty, **multi-fragment** Gauss–Seidel sweeps (one global ``D``, sequential fragment Schmidt+FCI updates).
    Mutually exclusive with ``schmidt_fragment_atom_indices`` (must leave the latter empty when this is set).
    """
    schmidt_multi_primary_fragment_index: int = Field(default=0, ge=0)
    """Which group in ``schmidt_multi_fragment_atom_groups`` supplies the main-pipeline ``QubitHamiltonian``."""
    schmidt_run_vqe_on_all_fragments: bool = Field(default=False)
    """
    If ``True`` and multi-fragment Schmidt is used, run an **additional** VQE on each fragment impurity
    after the embedding density loop (cost ∝ number of fragments). Default ``False`` for predictable
    production cost; enable when Methods require per-fragment variational energies.
    """
    schmidt_per_fragment_vqe_maxiter: int | None = None
    """Max VQE iterations per fragment; ``None`` means ``quantum.vqe_maxiter``. Bounded when set."""
    dmet_uniform_multifragment_toy: bool = False
    """
    If ``True`` and ``mode==dmet`` with **two or more** fragment labels, run
    :func:`~qchem_stack.integrations.dmet_multifragment_toy.run_uniform_hamiltonian_multifragment_toy`
    (each fragment sees full ``QubitHamiltonian`` — **non-physical**, wiring test only). Off by default.
    Incompatible with ``schmidt_atomic_production``.
    """
    dmet_multifragment_one_shot_shared_hamiltonian: bool = False
    """
    When ``dmet_hamiltonian_source=='whole_active_system'``, allow **multiple** ``fragment_labels`` and run
    :class:`~qchem_stack.integrations.dmet_self_consistent.OneShotEmbeddingDriver` with the **same**
    global ``QubitHamiltonian`` per fragment (demo / reproducibility only).
    """
    dmet_fragment_use_exact_solver: bool = False
    """Dense diagonalization impurity solve for small ``n_qubits`` (see ``dmet_fragment_exact_max_qubits``)."""
    dmet_fragment_exact_max_qubits: int = Field(default=14, ge=1, le=64)
    """Skip dense ED above this qubit count (fragment ledger records ``skipped``)."""
    decomposition_plugin: str = ""
    """Registered toy/plugin name when ``mode=='plugin'`` (e.g. ``uniform_fragment_guess``)."""
    decomposition_plugin_json_path: str | None = None
    """Path to fragment integral JSON (resolved relative to experiment YAML when needed)."""
    schmidt_bath_sidecar_json_path: str | None = None
    """
    Optional JSON merged into ``embedding_workflow.schmidt_bath_sidecar_v1`` when
    ``dmet_hamiltonian_source == 'schmidt_atomic_production'`` (user / Methods audit hook).
    Relative paths resolve against the directory of the experiment YAML when ``cfg_path`` is known.
    """
    oniom_layers_v1: list[dict[str, Any]] = Field(default_factory=list)
    """Toy QM/MM layer hints → ``embedding_workflow.oniom_toy_v1`` (documentation-only)."""

    @field_validator("schmidt_bath_sidecar_json_path")
    @classmethod
    def _strip_bath_sidecar(cls, v: str | None) -> str | None:
        return strip_optional_text(v)

    @field_validator("schmidt_per_fragment_vqe_maxiter")
    @classmethod
    def _schmidt_pf_vqe_maxiter_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return None
        if int(v) < 1 or int(v) > 500_000:
            raise ValueError("schmidt_per_fragment_vqe_maxiter must be in [1, 500000] when set.")
        return int(v)

    @model_validator(mode="after")
    def _dmet_hamiltonian_source_valid(self) -> EmbeddingSpec:
        validate_dmet_hamiltonian_source(self)
        return self

    @model_validator(mode="after")
    def _plugin_embedding_requires_fields(self) -> EmbeddingSpec:
        validate_plugin_embedding_requires_fields(self)
        return self

    @model_validator(mode="after")
    def _projection_mulliken_requires_mode_and_indices(self) -> EmbeddingSpec:
        validate_projection_mulliken_requires_mode_and_indices(self)
        return self
