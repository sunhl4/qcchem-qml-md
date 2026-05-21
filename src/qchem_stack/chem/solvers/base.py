from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.chem.bridges.mean_field_like import MeanFieldLike
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


@dataclass(frozen=True)
class SolverCapabilities:
    """Static capability flags for classical chemistry backends.

    Each ``supports_*`` answers whether the **pipeline may attempt** a YAML path,
    not whether the feature is implemented natively inside the driver executable.
    Delegated implementations (e.g. Psi4 SCF + PySCF AVAS kernel) should still set
    the flag when wired, and record ``driver_meta.kernel_bindings`` with
    ``native=False``. See ``docs/execution/multi_backend_integration_philosophy.md``.
    """

    backend_id: str
    supports_molecular_scf: bool = True
    supports_pbc_scf: bool = False
    supports_pbc_k_mesh: bool = False
    """True when Monkhorst–Pack meshes with any entry > 1 are supported for PBC SCF."""
    capability_notes: dict[str, str] = field(default_factory=dict)
    """Human-readable notes for ``supports_*`` flags (delegation, epistemic bounds)."""
    supports_rhf: bool = True
    supports_rohf: bool = True
    supports_uhf: bool = True
    supports_implicit_solvent_ddcosmo: bool = False
    supports_qmmm: bool = False
    supports_restricted_active_space_qubit_hamiltonian: bool = False
    """True when the backend supplies MO active-space integrals for the restricted CASCI-style qubit Hamiltonian path."""
    supports_projection_fragment_mulliken_hamiltonian: bool = False
    """True when ``embedding.projection.quantum_hamiltonian='fragment_mulliken_mo'`` is implemented."""
    supports_schmidt_atomic_hamiltonian: bool = False
    """True when ``embedding.dmet.hamiltonian_source='schmidt_atomic_production'`` is implemented."""
    supports_embedding_input_ao_lowdin: bool = False
    """True when ``embedding_input_representation`` in ``{ao, lowdin_orth_ao}`` is implemented."""
    supports_casscf_orbital_audit: bool = False
    """True when ``chemistry_extended.casscf_orbital_optimization_audit`` hook is implemented."""
    supports_avas_active_space_projection: bool = False
    """PySCF example: AVAS orbital projection / active-space resizing (``active_space.strategy='avas'``)."""
    supports_rdm_correction_hooks: bool = False
    """True when ``rdm_bundle_from_mean_field`` style extraction is implemented for this backend."""
    supports_rdm_nevpt2_casci: bool = False
    """True when backend-specific ``pyscf_nevpt2_casci``-class correction hook is available."""
    supports_get_integrals: bool = False
    """True when :meth:`ChemIntegralSolver.get_integrals` is implemented for this backend."""


@dataclass
class MolecularMeanFieldResult:
    """Converged (or prepared) mean-field container used by drivers and pipeline."""

    mf: MeanFieldLike
    e_tot: float
    mo_energy: np.ndarray
    driver_meta: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ChemIntegralSolver(Protocol):
    """Classical integral / Hartree–Fock backend aligned with Tangelo ``IntegralSolver`` *shape*.

    Tangelo-oriented mapping (conceptual, not a fork):

    - **set_physical_data**: bind geometry / basis / charge / SCF options from :class:`ExperimentConfig`.
    - **compute_mean_field**: primary SCF entry; ``periodic=False`` molecule, ``periodic=True`` crystal.
    - **get_integrals**: optional hook for AO/MO integrals (M2+; may raise ``NotImplementedError``).

    Compatibility: :meth:`run_molecular_mean_field` / :meth:`run_periodic_mean_field` stay as thin
    wrappers around :meth:`compute_mean_field`.
    """

    @property
    def capabilities(self) -> SolverCapabilities: ...

    def set_physical_data(self, cfg: ExperimentConfig) -> None: ...

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult: ...

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult: ...

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult: ...

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]: ...
