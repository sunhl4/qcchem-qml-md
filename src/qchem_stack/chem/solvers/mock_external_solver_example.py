"""Runnable example backend adapter for third-party chemistry software.

This module is intentionally simple: it returns deterministic mock SCF outputs
so users can copy the pattern and replace only the backend-specific sections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.config.active_space_helpers import resolve_n_electrons, resolve_n_orbitals

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


@dataclass
class MockExternalIntegralSolver:
    """Example ChemIntegralSolver implementation for onboarding and demos."""

    _cfg: ExperimentConfig

    @property
    def capabilities(self) -> SolverCapabilities:
        # TODO[1]: replace backend_id and capability flags for your real backend.
        return SolverCapabilities(
            backend_id="mock_external",
            supports_molecular_scf=True,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> MockExternalIntegralSolver:
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        # TODO[2]: replace this block with your backend SCF call and parse output.
        m = self._cfg.molecule
        n_orb = max(1, resolve_n_orbitals(self._cfg.active_space))
        # Deterministic, finite placeholders: replace with real backend SCF values.
        e_tot = -0.5 * float(len(m.symbols)) - 0.01 * float(abs(m.charge))
        occ = min(n_orb, max(1, resolve_n_electrons(self._cfg.active_space) // 2))
        vals = np.linspace(-1.0, 0.5, n_orb, dtype=float)
        vals[:occ] -= 0.25
        return MolecularMeanFieldResult(
            mf=wrap_mean_field_like(
                backend_tag="mock_external",
                raw_mf={
                    "backend": "mock_external",
                    "symbols": list(m.symbols),
                    "basis": str(m.basis),
                },
                e_tot=float(e_tot),
                mo_energy=vals,
            ),
            e_tot=float(e_tot),
            mo_energy=vals,
            driver_meta={
                "classical_bridge_backend": "mock_external",
                "adapter_example": True,
                "n_orbitals": int(n_orb),
            },
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("MockExternalIntegralSolver does not implement periodic SCF.")

    def get_integrals(self, *args: object, **kwargs: object) -> dict[str, object]:
        # TODO[3]: implement AO/MO integral export when enabling active-space Hamiltonian path.
        raise NotImplementedError(
            "MockExternalIntegralSolver.get_integrals is a template hook; wire your backend integrals here."
        )

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, object]:
        raise NotImplementedError(
            "MockExternalIntegralSolver.build_embedding_input_system is a template hook."
        )


def register_mock_external_solver() -> None:
    """Register demo backend id ``mock_external`` into solver registry.

    TODO[1]-adjacent: if you rename backend_id, keep this registration key aligned
    with your YAML ``scf.driver`` value.
    """
    from qchem_stack.chem.solvers.registry import register_solver

    register_solver(
        "mock_external", MockExternalIntegralSolver.from_experiment_config, overwrite=True
    )
