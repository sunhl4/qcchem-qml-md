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

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
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
from qchem_stack.contracts.schema_ids import EMBEDDING_INPUT_SYSTEM_V1

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
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

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="psi4",
            supports_molecular_scf=True,
            supports_pbc_scf=True,
            supports_pbc_k_mesh=False,
            supports_rhf=True,
            supports_rohf=True,
            supports_uhf=True,
            supports_implicit_solvent_ddcosmo=True,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=True,
            supports_projection_fragment_mulliken_hamiltonian=False,
            supports_schmidt_atomic_hamiltonian=False,
            supports_embedding_input_ao_lowdin=False,
            supports_casscf_orbital_audit=False,
            supports_avas_active_space_projection=False,
            supports_rdm_correction_hooks=False,
            supports_rdm_nevpt2_casci=False,
            supports_get_integrals=False,
            capability_notes={
                "avas_active_space_projection": "PySCF mcscf.avas on imported MO coefficients.",
                "rdm_nevpt2_casci": "PySCF mrpt.NEVPT on shadow CASCI built from Psi4 MO.",
                "pbc_k_mesh": "Gamma-only (all mesh entries must be 1).",
            },
        )

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        validate_cfg_driver_and_method(cfg)
        self._cfg = cfg
        self._system = molecular_system_from_config(cfg)
        self._method = str(cfg.scf.method).upper()
        self.chemistry_extended = cfg.chemistry_extended

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
            meta = dict(reference.driver_meta)
            meta["integral_representation"] = "ao"
            meta["ao_reference_kind"] = "psi4_wavefunction"
            return {
                "schema": EMBEDDING_INPUT_SYSTEM_V1,
                "representation": "ao",
                "has_run_hf": True,
                "e_tot": float(reference.e_tot),
                "driver_meta": meta,
                "epistemic_bound": "Psi4 wavefunction AO wrapper for embedding workflows.",
            }

        s = ao.overlap_ao()
        evals, evecs = np.linalg.eigh(s)
        if np.min(evals) <= 1e-12:
            raise ValueError("AO overlap matrix is near singular; cannot build Lowdin basis.")
        c_low = np.asarray(evecs @ np.diag(evals**-0.5) @ evecs.T, dtype=float)
        hcore = ao.hcore_ao()
        h1_low = np.einsum("pi,pq,qj->ij", c_low, hcore, c_low, optimize=True)
        dm_ao = ao.make_rdm1_ao()
        c_inv = np.linalg.inv(c_low)
        dm_low = np.asarray(c_inv @ dm_ao @ c_inv.T, dtype=float)
        meta = dict(reference.driver_meta)
        meta["integral_representation"] = "lowdin_orth_ao"
        meta["lowdin_basis_transform"] = "s^-1/2"
        return {
            "schema": EMBEDDING_INPUT_SYSTEM_V1,
            "representation": "lowdin_orth_ao",
            "n_spatial_orbitals": int(h1_low.shape[0]),
            "rdm1_trace": float(np.trace(dm_low)),
            "constant": float(ao.energy_nuc_au()),
            "driver_meta": meta,
            "epistemic_bound": "Lowdin AO tensors from Psi4 MintsHelper overlap/core.",
        }

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
