from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qchem_stack.chem.solvers.adapter_contract import validate_solver_adapter_contract
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities


@dataclass
class _GoodSolver:
    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(backend_id="dummy", supports_molecular_scf=True)

    def set_physical_data(self, cfg: Any) -> None:
        del cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        del periodic
        return MolecularMeanFieldResult(
            mf={"dummy": True},
            e_tot=-1.0,
            mo_energy=np.array([-0.5, 0.2], dtype=float),
            driver_meta={},
        )

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=False)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        del args, kwargs
        return {}


@dataclass
class _BadSolver:
    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(backend_id="", supports_molecular_scf=True)

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        del periodic
        return MolecularMeanFieldResult(
            mf={},
            e_tot=float("nan"),
            mo_energy=np.array([], dtype=float),
            driver_meta={},
        )


def test_validate_solver_adapter_contract_ok() -> None:
    rep = validate_solver_adapter_contract(_GoodSolver(), run_mean_field=True)
    assert rep.ok
    assert rep.backend_id == "dummy"
    assert rep.errors == []


def test_validate_solver_adapter_contract_catches_invalid_outputs() -> None:
    rep = validate_solver_adapter_contract(_BadSolver(), run_mean_field=True)
    assert not rep.ok
    assert any("backend_id" in e for e in rep.errors)
    assert any("must be finite" in e for e in rep.errors)
    assert any("must not be empty" in e for e in rep.errors)
