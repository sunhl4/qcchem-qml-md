"""Optional bridge to the QML-FF (Quantum ML force field + JAX-MD) project.

This module is **additive** and does **not** alter any existing ``md_bridge`` surface.
All ``qmlff`` / ``jax_md`` imports are deferred to function bodies so the rest of
``qchem_stack`` remains usable without those packages installed.

Two equally valid install layouts are supported:

* ``pip install -e /path/to/QML-FF`` (editable install of the sibling repo)
* ``PYTHONPATH=/path/to/QML-FF`` (manual import path)

Units convention at the boundary
--------------------------------
* qchem_stack internals: **Hartree, Bohr, Hartree/Bohr** (matches :class:`QMFrame`).
* QML-FF / JAX-MD internals: **eV, Å, eV/Å, ps, K, amu**.

Conversion is centralised here so callers can stay in their native units.
"""

from __future__ import annotations

from qchem_stack.md_bridge.qmlff_builders import (
    ForceFieldBackend,
    QmlffModelHandle,
    atomic_number_to_symbol,
    build_force_field_handle,
    build_qmlff_model_angle,
    build_qmlff_model_from_preset,
    build_qmlff_model_quantum_ff,
    build_qmp_h2_model,
    symbol_to_atomic_number,
)
from qchem_stack.md_bridge.qmlff_io import (
    qmlff_handle_to_qmef_frame,
    trajectory_to_extxyz,
)
from qchem_stack.md_bridge.qmlff_md import (
    JaxMdTrajectory,
    predict_energy_forces_hartree,
    run_jaxmd_trajectory,
    select_geometries_from_trajectory,
)
from qchem_stack.md_bridge.qmlff_training import (
    train_force_field_on_qmef,
    train_qmlff_on_qmef,
)

__all__ = [
    "ForceFieldBackend",
    "QmlffModelHandle",
    "JaxMdTrajectory",
    "build_force_field_handle",
    "build_qmlff_model_from_preset",
    "build_qmlff_model_quantum_ff",
    "build_qmlff_model_angle",
    "build_qmp_h2_model",
    "train_force_field_on_qmef",
    "train_qmlff_on_qmef",
    "predict_energy_forces_hartree",
    "run_jaxmd_trajectory",
    "select_geometries_from_trajectory",
    "trajectory_to_extxyz",
    "qmlff_handle_to_qmef_frame",
    "atomic_number_to_symbol",
    "symbol_to_atomic_number",
]
