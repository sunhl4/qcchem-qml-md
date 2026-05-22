"""Canonical :class:`MolecularSystem` projection from experiment YAML."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.system import MolecularSystem

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def molecular_system_from_experiment(cfg: ExperimentConfig) -> MolecularSystem:
    """
    Canonical :class:`~qchem_stack.chem.system.MolecularSystem` projection from YAML config.

    ``meta['geometry_source']`` is ``zmatrix`` when ``molecule.zmatrix`` is non-empty, else ``cartesian``;
    the same lineage is surfaced on parity exports (see ``scripts/export_parity_criteria_table.py``).
    """
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


__all__ = ["molecular_system_from_experiment"]
