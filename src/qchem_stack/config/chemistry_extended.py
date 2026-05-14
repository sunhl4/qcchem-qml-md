"""Extended chemistry driver knobs for PBC, AVAS, and post-HF add-ons."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from ._chemistry_extended_validation import validate_pbc_mesh_and_cell


class ChemistryExtendedSpec(BaseModel):
    """Extended driver surface (InQuanto-adjacent names; PySCF where implemented)."""

    solvent_model: Literal["none", "ddcosmo"] = "none"
    """``ddcosmo``: wrap SCF with :class:`pyscf.solvent.ddCOSMO` before ``kernel``."""
    ddcosmo_epsilon: float = 78.3553
    """Solvent dielectric (default water) for ddCOSMO."""
    pbc_cell_vectors_bohr: list[list[float]] | None = None
    """3×3 lattice row vectors in Bohr for :mod:`pyscf.pbc` (``PySCFDriver.run_pbc_rhf``)."""
    pbc_kpoint_mesh: list[int] = Field(default_factory=lambda: [1, 1, 1])
    """Monkhorst–Pack mesh ``[nx,ny,nz]``; all ``1`` → Γ-only :class:`pyscf.pbc.scf.hf.RHF`, else :class:`pyscf.pbc.scf.khf.KRHF` with that mesh."""
    pbc_active_space_kpoint_index: int = 0
    """Which k-point in ``KRHF`` MO list to use for CASCI / active-space integrals (Γ is usually index ``0`` in PySCF ordering)."""
    casscf_orbital_optimization_audit: bool = False
    """
    Molecular RHF branch only: run PySCF :class:`pyscf.mcscf.CASSCF` for the resolved active-space
    electron/orbital counts (after optional AVAS) and record ``casscf_orbital_audit_v1`` in ``driver_meta``
    unless ``casscf_orbital_optimization_for_integrals`` alone is enabled (audit can be bundled with the same
    CASSCF call when either flag is true).
    """

    casscf_orbital_optimization_for_integrals: bool = False
    """
    When ``True`` (PySCF molecular RHF), rotate ``mf.mo_coeff`` using the optimized CASSCF orbitals **before**
    CASCI-style active extracts used for ``CanonicalActiveSpaceIntegralPack`` / JW Hamiltonians.
    Pairs naturally after ``active_space.strategy=avas`` while still respecting solver capability gates.

    Implemented as a shared single ``CASSCF`` kernel with ``casscf_orbital_optimization_audit`` so enabling
    both does **not** run CASSCF twice.
    """
    classical_benchmark_enabled: bool = False
    """
    When ``True``, pipeline attaches ``classical_benchmarks`` via
    :func:`qchem_stack.chem.classical_benchmarks.run_classical_post_hf_benchmarks`
    (HF/MP2/CCSD/CASCI status blocks; schema ``qchem_classical_post_hf_benchmarks_v1``).
    """
    classical_benchmark_backend: Literal["auto", "stub", "pyscf", "psi4"] = "auto"
    """
    Which chemistry backend executes post-HF benchmarks.

    ``auto``: use PySCF benchmarks when the mean-field reference reports ``upstream_classical_software_tag=pyscf``;
    otherwise attach a stub payload. ``pyscf`` / ``psi4`` force that registry path (``psi4`` is placeholder-only today).
    """
    rdm_correction_method: Literal["none", "stub_nevpt2", "stub_ac0", "pyscf_nevpt2_casci"] = "none"
    """
    Optional post-SCF RDM correction hook (Phase C / Phase 3).
    ``stub_*``: machine-readable reports only (zero numerical correction).
    ``pyscf_nevpt2_casci``: PySCF ``mrpt.NEVPT`` on a CASCI reference (open stack — not InQuanto L0).
    """
    avas_ao_labels: list[str] = Field(default_factory=list)
    """
    Atomic-orbital label strings interpreted by PySCF :class:`~pyscf.mcscf.avas.AVAS` **when**
    ``active_space.strategy='avas'`` (required non-empty combination — validated on :class:`ExperimentConfig`).

    When non-empty **and strategy is not** ``avas``: copied to ``driver_meta["avas_ao_labels_requested"]`` and
    ``driver_meta["avas_ao_labels_logging_only"]=true`` without changing orbitals / integrals.

    Stub intent without projection remains ``strategy=avas_stub``.
    """

    avas_threshold: float = Field(default=0.2, gt=0.0, le=1.0)
    """AVAS orbital selection threshold forwarded to PySCF."""
    avas_minao: str = Field(default="minao", min_length=1)
    """Reference minimal basis forwarded to AVAS."""
    avas_with_iao: bool = False
    avas_openshell_option: int = Field(default=2, ge=0, le=10)
    """PySCF ``avas.AVAS`` openshell option (consult PySCF docs for semantics)."""
    avas_canonicalize: bool = True
    avas_ncore: int = Field(default=0, ge=0, le=512)
    """Frozen core orbital count forwarded to AVAS."""
    pyscf_symmetry: bool | str = False
    """
    Forwarded to PySCF ``gto.M(..., symmetry=...)`` on the molecular branch (non-PBC).

    ``True`` enables automatic subgroup detection; a non-empty **string** selects an explicit subgroup label
    understood by your PySCF build.

    This can reduce **classical** integral / SCF cost when symmetry applies. The bridge to OpenFermion for the
    quantum stage still materializes **dense** active-space tensors — there is **no** drop-in equivalent to
    InQuanto ``ChemistryRestrictedIntegralOperatorCompact`` in this repository yet.
    """
    mo_coeff_transform_hook: str = ""
    """
    Optional post-SCF MO transform hook name.

    Built-ins:
    - ``reverse_mo_columns``: deterministic column reversal for smoke/tests.
    - ``identity``: explicit no-op.

    Custom hooks may be provided as ``python_module:function_name`` and must return an array with the
    same shape as ``mf.mo_coeff``.
    """
    mo_coeff_transform_kwargs: dict[str, Any] = Field(default_factory=dict)
    """Opaque kwargs passed to the selected MO transform hook."""

    @model_validator(mode="after")
    def _validate_pbc_cell_matrix(self) -> ChemistryExtendedSpec:
        validate_pbc_mesh_and_cell(self)
        return self
