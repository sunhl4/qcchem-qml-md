"""Read-only helpers for :class:`~qchem_stack.config.md_ml_export.MdMlExportSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .md_ml_export import MdMlExportSpec


def extra_coordinates_bohr(spec: MdMlExportSpec) -> list[list[list[float]]]:
    return list(spec.trajectory.extra_coordinates_bohr)


def trajectory_theory_level(spec: MdMlExportSpec) -> str:
    return str(spec.trajectory.theory_level)
