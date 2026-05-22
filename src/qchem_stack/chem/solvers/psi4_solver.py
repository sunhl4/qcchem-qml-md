"""Psi4 backend adapter aligned with :class:`PySCFIntegralSolver` capability surface.

Responsibility map — implementation lives in sibling modules:

| Module | Scope |
|--------|--------|
| ``psi4_solver_common`` | Version probe |
| ``psi4_solver_setup`` | Geometry, SCF options, driver meta |
| ``psi4_solver_mf`` | Mean-field (molecular + PBC) |
| ``psi4_solver_integrals`` | CASCI active-space integrals |
| ``psi4_solver`` (this file) | Class facade, capabilities, embedding export |
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.embedding_input import (
    build_ao_embedding_payload,
    build_lowdin_embedding_payload,
)
from qchem_stack.chem.integration.presets import capabilities_psi4_production
from qchem_stack.chem.solvers.psi4_solver_common import psi4_version_or_unknown
from qchem_stack.chem.solvers.psi4_solver_integrals import get_active_space_integrals
from qchem_stack.chem.solvers.psi4_solver_mf import (
    execute_molecular_mean_field,
    execute_periodic_mean_field,
    psi4_hf_total_energy_au,
)
from qchem_stack.chem.solvers.psi4_solver_setup import (
    molecular_system_from_config,
    validate_cfg_driver_and_method,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
    from qchem_stack.config import ExperimentConfig

__all__ = [
    "Psi4IntegralSolver",
    "psi4_hf_total_energy_au",
    "psi4_version_or_unknown",
]


class Psi4IntegralSolver:
    """Psi4-backed classical solver adapter (RHF/ROHF/UHF molecular + PBC smoke)."""

    def __init__(self, cfg: ExperimentConfig) -> None:
        validate_cfg_driver_and_method(cfg)
        self._cfg = cfg
        self._system = molecular_system_from_config(cfg)
        self._method = str(cfg.scf.method).upper()
        self.chemistry_extended = cfg.chemistry_extended
        self._last_molecular_mf_result: MolecularMeanFieldResult | None = None

    @property
    def capabilities(self) -> SolverCapabilities:
        return capabilities_psi4_production()

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        validate_cfg_driver_and_method(cfg)
        self._cfg = cfg
        self._system = molecular_system_from_config(cfg)
        self._method = str(cfg.scf.method).upper()
        self.chemistry_extended = cfg.chemistry_extended
        self._last_molecular_mf_result = None

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return get_active_space_integrals(self, *args, **kwargs)

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]:
        if self.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise ValueError(
                "embedding_input_representation=ao/lowdin_orth_ao is molecular-only (non-PBC)."
            )
        if reference.backend_tag() != "psi4":
            raise ValueError(
                "Psi4IntegralSolver.build_embedding_input_system requires backend_tag='psi4'."
            )
        rep = str(representation).strip().lower()
        if rep not in ("ao", "lowdin_orth_ao"):
            raise ValueError(f"Unsupported embedding input representation: {representation!r}")

        ao = reference.ao_basis_view()
        if rep == "ao":
            return build_ao_embedding_payload(
                e_tot=float(reference.e_tot),
                driver_meta=reference.driver_meta,
                ao_reference_kind="psi4_wavefunction",
                epistemic_bound="Psi4 wavefunction AO wrapper for embedding workflows.",
            )

        return build_lowdin_embedding_payload(
            overlap=ao.overlap_ao(),
            hcore=ao.hcore_ao(),
            rdm1_ao=ao.make_rdm1_ao(),
            energy_nuc=float(ao.energy_nuc_au()),
            driver_meta=reference.driver_meta,
            epistemic_bound="Lowdin AO tensors from Psi4 MintsHelper overlap/core.",
        )

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return execute_periodic_mean_field(self)
        return execute_molecular_mean_field(self)

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> Psi4IntegralSolver:
        validate_cfg_driver_and_method(cfg)
        return cls(cfg)

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=False)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=True)
