"""Read-only helpers for :class:`~qchem_stack.config.chemistry_extended.ChemistryExtendedSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chemistry_extended import ChemistryExtendedSpec


def solvent_model(spec: ChemistryExtendedSpec) -> str:
    return str(spec.solvent.model)


def pbc_cell_vectors_bohr(spec: ChemistryExtendedSpec):
    return spec.pbc.cell_vectors_bohr


def pbc_kpoint_mesh(spec: ChemistryExtendedSpec) -> list[int]:
    return list(spec.pbc.kpoint_mesh)


def avas_ao_labels(spec: ChemistryExtendedSpec) -> list[str]:
    return list(spec.avas.ao_labels)


def avas_threshold(spec: ChemistryExtendedSpec) -> float:
    return float(spec.avas.threshold)


def avas_minao(spec: ChemistryExtendedSpec) -> str:
    return str(spec.avas.minao)


def avas_with_iao(spec: ChemistryExtendedSpec) -> bool:
    return bool(spec.avas.with_iao)


def avas_openshell_option(spec: ChemistryExtendedSpec) -> int:
    return int(spec.avas.openshell_option)


def avas_canonicalize(spec: ChemistryExtendedSpec) -> bool:
    return bool(spec.avas.canonicalize)


def avas_ncore(spec: ChemistryExtendedSpec) -> int:
    return int(spec.avas.ncore)


def integral_crosscheck(spec: ChemistryExtendedSpec) -> str:
    return str(spec.post_hf.integral_crosscheck)


def classical_benchmark_enabled(spec: ChemistryExtendedSpec) -> bool:
    return bool(spec.benchmarks.enabled)
