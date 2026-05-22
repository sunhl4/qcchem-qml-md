"""PySCF :class:`~qchem_stack.chem.solvers.base.ChemIntegralSolver` implementation.

Responsibility map — implementation lives in sibling modules:

| Module | Scope |
|--------|--------|
| ``pyscf_solver_common`` | ``require_pyscf``, version probe |
| ``pyscf_solver_setup`` | Molecule, SCF controls, driver meta |
| ``pyscf_solver_mf`` | Mean-field (molecular + PBC) |
| ``pyscf_solver_integrals`` | CASCI active-space integrals |
| ``pyscf_solver`` (this file) | Class facade, capabilities, embedding export |
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.chem.bridges.embedding_input import (
    build_ao_embedding_payload,
    build_lowdin_embedding_payload,
)
from qchem_stack.chem.integration.presets import capabilities_pyscf_production
from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment
from qchem_stack.chem.pyscf_typing import as_pyscf_mf
from qchem_stack.chem.solvers.pyscf_solver_common import pyscf_version_or_unknown, require_pyscf
from qchem_stack.chem.solvers.pyscf_solver_integrals import get_active_space_integrals
from qchem_stack.chem.solvers.pyscf_solver_mf import (
    build_molecular_mf_without_kernel,
    execute_molecular_mean_field,
    execute_periodic_mean_field,
    idle_molecular_driver_meta,
)
from qchem_stack.config.scf_helpers import (
    resolve_scf_chkfile,
    resolve_scf_density_fit,
    resolve_scf_density_fit_auxbasis,
    resolve_scf_diis_space_dimension,
    resolve_scf_init_guess,
    resolve_scf_level_shift,
    resolve_scf_max_cycle,
    resolve_scf_use_newton,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
    from qchem_stack.chem.system import MolecularSystem
    from qchem_stack.config import ChemistryExtendedSpec, ExperimentConfig

__all__ = [
    "PySCFIntegralSolver",
    "require_pyscf",
    "pyscf_version_or_unknown",
]


class PySCFIntegralSolver:
    """PySCF implementation of :class:`~qchem_stack.chem.solvers.base.ChemIntegralSolver`."""

    def __init__(
        self,
        system: MolecularSystem,
        method: Literal["RHF", "ROHF", "UHF"],
        chemistry_extended: ChemistryExtendedSpec,
        *,
        scf_max_cycle: int | None = None,
        chkfile: str | None = None,
        init_guess: str | None = None,
        level_shift: float | None = None,
        use_newton: bool = False,
        diis_space_dimension: int | None = None,
        density_fit: bool = False,
        density_fit_auxbasis: str | None = None,
    ) -> None:
        self.system = system
        self.method = method
        self.chemistry_extended = chemistry_extended
        self.scf_max_cycle = scf_max_cycle
        self.chkfile = chkfile
        self.init_guess = init_guess
        self.level_shift = level_shift
        self.use_newton = use_newton
        self.diis_space_dimension = diis_space_dimension
        self.density_fit = density_fit
        self.density_fit_auxbasis = density_fit_auxbasis

    @property
    def capabilities(self) -> SolverCapabilities:
        return capabilities_pyscf_production()

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> PySCFIntegralSolver:
        sys = molecular_system_from_experiment(cfg)
        scf = cfg.scf
        inst = cls(
            sys,
            method=scf.method,
            chemistry_extended=cfg.chemistry_extended,
            scf_max_cycle=resolve_scf_max_cycle(scf),
            chkfile=resolve_scf_chkfile(scf),
            init_guess=resolve_scf_init_guess(scf),
            level_shift=resolve_scf_level_shift(scf),
            use_newton=resolve_scf_use_newton(scf),
            diis_space_dimension=resolve_scf_diis_space_dimension(scf),
            density_fit=resolve_scf_density_fit(scf),
            density_fit_auxbasis=resolve_scf_density_fit_auxbasis(scf),
        )
        inst.set_physical_data(cfg)
        return inst

    def build_molecular_mf_without_kernel(self) -> Any:
        return build_molecular_mf_without_kernel(self)

    def idle_molecular_driver_meta(self) -> dict[str, Any]:
        return idle_molecular_driver_meta(self)

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        if str(cfg.scf.driver).strip().lower() != "pyscf":
            raise ValueError(
                "PySCFIntegralSolver.set_physical_data requires cfg.scf.driver='pyscf' "
                f"(got {cfg.scf.driver!r})."
            )
        self.system = molecular_system_from_experiment(cfg)
        scf = cfg.scf
        self.method = scf.method
        self.chemistry_extended = cfg.chemistry_extended
        self.scf_max_cycle = resolve_scf_max_cycle(scf)
        self.chkfile = resolve_scf_chkfile(scf)
        self.init_guess = resolve_scf_init_guess(scf)
        self.level_shift = resolve_scf_level_shift(scf)
        self.use_newton = resolve_scf_use_newton(scf)
        self.diis_space_dimension = resolve_scf_diis_space_dimension(scf)
        self.density_fit = resolve_scf_density_fit(scf)
        self.density_fit_auxbasis = resolve_scf_density_fit_auxbasis(scf)

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return get_active_space_integrals(self, *args, **kwargs)

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        return execute_periodic_mean_field(self) if periodic else execute_molecular_mean_field(self)

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=False)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=True)

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]:
        if self.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise ValueError(
                "embedding_input_representation=ao/lowdin_orth_ao is currently molecular-only (non-PBC)."
            )
        rep = str(representation).strip().lower()
        if rep not in ("ao", "lowdin_orth_ao"):
            raise ValueError(f"Unsupported embedding input representation: {representation!r}")
        if reference.backend_tag() != "pyscf":
            raise ValueError(
                "PySCFIntegralSolver.build_embedding_input_system requires a PySCF classical reference."
            )
        mf = as_pyscf_mf(reference.mf)
        if rep == "ao":
            return build_ao_embedding_payload(
                e_tot=float(reference.e_tot),
                driver_meta=reference.driver_meta,
                ao_reference_kind="scf_object",
                epistemic_bound=(
                    "AO wrapper keeps SCF object for fragment builders; "
                    "no full vendor AO driver parity claim."
                ),
            )

        return build_lowdin_embedding_payload(
            overlap=np.asarray(mf.get_ovlp(), dtype=float),
            hcore=np.asarray(mf.get_hcore(), dtype=float),
            rdm1_ao=mf.make_rdm1(),
            energy_nuc=float(mf.mol.energy_nuc()),
            driver_meta=reference.driver_meta,
            epistemic_bound=(
                "Lowdin AO tensors are provided for open embedding workflows "
                "(not a closed-source embedding product clone)."
            ),
        )
