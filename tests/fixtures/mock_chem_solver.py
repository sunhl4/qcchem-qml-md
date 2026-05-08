from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.solvers.registry import register_solver
from qchem_stack.config import ExperimentConfig


@dataclass
class MockChemIntegralSolver:
    cfg: ExperimentConfig

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="mockchem",
            supports_molecular_scf=True,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
            supports_projection_fragment_mulliken_hamiltonian=False,
            supports_schmidt_atomic_hamiltonian=False,
            supports_embedding_input_ao_lowdin=False,
            supports_casscf_orbital_audit=False,
            supports_avas_active_space_projection=False,
            supports_rdm_correction_hooks=False,
            supports_rdm_nevpt2_casci=False,
            supports_get_integrals=False,
        )

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self.cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            raise NotImplementedError("mockchem supports molecular branch only")
        nao = max(1, len(self.cfg.molecule.symbols))
        return MolecularMeanFieldResult(
            mf={"backend": "mockchem", "status": "stub"},
            e_tot=0.0,
            mo_energy=np.zeros(nao, dtype=float),
            driver_meta={"driver_family": "mockchem"},
        )

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=False)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=True)

    def get_integrals(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise NotImplementedError("mockchem does not implement get_integrals")


def register_mockchem_solver() -> None:
    register_solver("mockchem", MockChemIntegralSolver)
