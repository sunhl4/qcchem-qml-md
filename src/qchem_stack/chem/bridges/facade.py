"""Single façade for classical mean-field: any registered ``ChemIntegralSolver`` → interchange shape."""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.bridges.interchange import merge_canonical_classical_bridge_headers
from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.solvers import create_solver
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ExperimentConfig


def molecular_system_from_experiment(cfg: ExperimentConfig) -> MolecularSystem:
    """Canonical :class:`~qchem_stack.chem.system.MolecularSystem` projection from YAML config."""
    m = cfg.molecule
    meta: dict[str, Any] = {}
    if getattr(m, "zmatrix", None) and str(m.zmatrix).strip():
        meta["geometry_source"] = "zmatrix"
    else:
        meta["geometry_source"] = "cartesian"
    return MolecularSystem(
        symbols=m.symbols,
        coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
        charge=m.charge,
        multiplicity=m.multiplicity,
        basis=m.basis,
        ecp=m.ecp,
        meta=meta,
    )


def classical_mean_field_via_solver_bridge(cfg: ExperimentConfig) -> MolecularMeanFieldResult:
    """
    **Unified classical SCF choke point** behind ``scf.driver``.

    Every backend adapter must converge to :class:`~qchem_stack.chem.solvers.base.MolecularMeanFieldResult`
    with ``driver_meta`` augmented by :func:`merge_canonical_classical_bridge_headers`.
    Downstream stages (embedding, CASCI folds, fermion builders) consume this interchange only.
    """
    solver = create_solver(cfg)
    solver.set_physical_data(cfg)
    pbc_on = cfg.chemistry_extended.pbc_cell_vectors_bohr is not None
    raw = solver.compute_mean_field(periodic=pbc_on)
    meta = merge_canonical_classical_bridge_headers(
        raw.driver_meta,
        upstream_software_tag=cfg.scf.driver,
        periodic_boundary_condition=pbc_on,
    )
    mf_like = wrap_mean_field_like(
        backend_tag=cfg.scf.driver,
        raw_mf=raw.mf,
        e_tot=float(raw.e_tot),
        mo_energy=np.asarray(raw.mo_energy, dtype=float),
    )
    return MolecularMeanFieldResult(
        mf=mf_like,
        e_tot=raw.e_tot,
        mo_energy=raw.mo_energy,
        driver_meta=meta,
    )


class RegistryBackedClassicalBridge:
    """Concrete :class:`~qchem_stack.chem.bridges.protocol.ClassicalChemistrySoftwareBridge` (registry path)."""

    def to_interchange_mean_field(self, cfg: ExperimentConfig) -> MolecularMeanFieldResult:
        return classical_mean_field_via_solver_bridge(cfg)
