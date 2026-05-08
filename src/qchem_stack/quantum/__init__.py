"""Quantum algorithms and utilities.

Public re-exports were removed from this ``__init__`` to prevent import cycles
(``chem`` ↔ ``config`` ↔ ``quantum``). Import concrete modules explicitly, e.g.
``from qchem_stack.quantum.algorithms.vqe import VQE``.
"""

__all__: list[str] = []
