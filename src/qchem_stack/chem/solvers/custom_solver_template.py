"""Template for user-provided classical chemistry backend adapters.

Copy this module, replace ``backend_id``, and implement ``compute_mean_field`` /
``get_integrals`` against your external chemistry software.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.config import ExperimentConfig


class CustomExternalIntegralSolver:
    """Minimal adapter template implementing the ChemIntegralSolver shape.

    This class is intentionally conservative: it validates config binding and
    raises ``NotImplementedError`` for backend-specific execution hooks.
    """

    def __init__(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="custom_external_template",
            supports_molecular_scf=False,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> CustomExternalIntegralSolver:
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
        raise NotImplementedError(
            "CustomExternalIntegralSolver.run_molecular_mean_field is a template. "
            "Populate this using your backend's SCF result and return MolecularMeanFieldResult."
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.run_periodic_mean_field is a template. "
            "Set supports_pbc_scf=True only after implementing this method."
        )

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.get_integrals is a template hook for MO/AO integrals."
        )


def build_stub_mean_field_result(*, n_mo: int = 1) -> MolecularMeanFieldResult:
    """Tiny helper for template prototyping/tests before real backend wiring."""
    n = max(1, int(n_mo))
    return MolecularMeanFieldResult(
        mf={"template": "replace_with_backend_handle"},
        e_tot=0.0,
        mo_energy=np.zeros(n, dtype=float),
        driver_meta={"adapter_template_stub": True},
    )
