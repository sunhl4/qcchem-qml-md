"""Pre-quantum branch selection — re-exports from config for backward compatibility.

The canonical definitions live in :mod:`qchem_stack.config._pre_quantum_path`
to keep the config module free of runtime chem imports.
"""

from __future__ import annotations

from qchem_stack.config._pre_quantum_path import (
    PreQuantumPath,
    list_pre_quantum_path_sources,
    list_pre_quantum_paths,
    pre_quantum_path_source,
    resolve_pre_quantum_path,
)

__all__ = [
    "PreQuantumPath",
    "list_pre_quantum_paths",
    "list_pre_quantum_path_sources",
    "pre_quantum_path_source",
    "resolve_pre_quantum_path",
]
