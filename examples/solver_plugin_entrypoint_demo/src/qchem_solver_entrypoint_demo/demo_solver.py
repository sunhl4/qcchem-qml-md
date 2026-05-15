from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.config import ExperimentConfig


@dataclass
class EntrypointDemoIntegralSolver:
    """Tiny external solver used to demonstrate entry-point based registration."""

    _cfg: ExperimentConfig

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> EntrypointDemoIntegralSolver:
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="entrypoint_demo",
            supports_molecular_scf=True,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
        )

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        n_orb = max(1, int(self._cfg.active_space.n_active_orbitals))
        n_occ = min(n_orb, max(1, int(self._cfg.active_space.n_active_electrons // 2)))
        mo_energy = np.linspace(-1.2, 0.4, n_orb, dtype=float)
        mo_energy[:n_occ] -= 0.1
        return MolecularMeanFieldResult(
            mf={
                "backend": "entrypoint_demo",
                "symbols": list(self._cfg.molecule.symbols),
                "basis": str(self._cfg.molecule.basis),
            },
            e_tot=float(-0.2 * len(self._cfg.molecule.symbols)),
            mo_energy=mo_energy,
            driver_meta={
                "classical_bridge_backend": "entrypoint_demo",
                "entrypoint_plugin_demo": True,
            },
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("EntrypointDemoIntegralSolver does not implement periodic SCF.")

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("EntrypointDemoIntegralSolver.get_integrals not implemented.")
