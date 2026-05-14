"""MD/ML attachment controls for exporting QMEF-compatible repro snapshots."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MdMlExportSpec(BaseModel):
    """Optional snapshot of :mod:`~qchem_stack.md_bridge` training schema onto ``repro``."""

    attach_single_frame_to_repro: bool = False
    """When ``True``, attach ``repro.qmef_ml_attachment_v1`` after the pipeline completes."""
    energy_reference: Literal["variational", "scf", "pauli_protocol"] = "variational"
    """
    Primary-frame total energy in Hartree: post-VQE ``energy_after_variational``, mean-field ``scf_energy``, or
    ``energy_pauli_protocol`` (requires ``quantum.use_pauli_protocol: true`` and a completed Pauli stage).
    Extra trajectory frames use nested pipeline energies only when ``trajectory_theory_level: full_pipeline``;
    HF-only extras always record mean-field ``e_tot``.
    """
    include_hf_nuclear_gradient: bool = False
    """
    Attempt PySCF analytic HF forces (:math:`-\\partial E/\\partial R`) in Hartree/Bohr for molecular clusters.
    Ignored on periodic / PBC drivers or when gradients raise.
    """
    extra_coordinates_bohr: list[list[list[float]]] = Field(default_factory=list)
    """
    Additional nuclear geometries (each ``n_atom × 3`` Bohr, same atom order as ``molecule.symbols``).

    Evaluated according to ``trajectory_theory_level`` after the primary pipeline finishes.
    """
    trajectory_theory_level: Literal["hf_scf", "full_pipeline"] = "hf_scf"
    """
    ``hf_scf``: PySCF mean-field energy (+ optional HF gradient) per extra geometry only.

    ``full_pipeline``: nested :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync` per geometry
    (QMEF attachment disabled on nested runs to avoid recursion).
    """
