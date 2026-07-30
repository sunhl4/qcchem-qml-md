"""Quantum algorithm classes — lazy exports via :func:`__getattr__`."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "AlgorithmBase",
    "AlgorithmLifecycle",
    "AlgorithmReport",
    "VQE",
    "FermionicAdaptVQE",
    "IQEBVQE",
    "IQCCVQE",
    "VQD",
    "QSE",
    "AlgorithmDeterministicQPE",
    "AlgorithmKitaevQPE",
    "AlgorithmInfoTheoryQPE",
    "AlgorithmVQS",
    "AlgorithmMcLachlanRealTime",
    "AlgorithmMcLachlanImagTime",
    "SCEOMResult",
    "run_sceom_reference_subspace",
]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "AlgorithmBase": ("qchem_stack.quantum.algorithms.base", "AlgorithmBase"),
    "AlgorithmLifecycle": ("qchem_stack.quantum.algorithms.base", "AlgorithmLifecycle"),
    "AlgorithmReport": ("qchem_stack.quantum.algorithms.base", "AlgorithmReport"),
    "VQE": ("qchem_stack.quantum.algorithms.vqe", "VQE"),
    "FermionicAdaptVQE": ("qchem_stack.quantum.algorithms.adapt", "FermionicAdaptVQE"),
    "IQEBVQE": ("qchem_stack.quantum.algorithms.iqeb", "IQEBVQE"),
    "IQCCVQE": ("qchem_stack.quantum.algorithms.iqcc", "IQCCVQE"),
    "VQD": ("qchem_stack.quantum.algorithms.excited", "VQD"),
    "QSE": ("qchem_stack.quantum.algorithms.excited", "QSE"),
    "AlgorithmDeterministicQPE": (
        "qchem_stack.quantum.algorithms.qpe",
        "AlgorithmDeterministicQPE",
    ),
    "AlgorithmKitaevQPE": ("qchem_stack.quantum.algorithms.qpe", "AlgorithmKitaevQPE"),
    "AlgorithmInfoTheoryQPE": (
        "qchem_stack.quantum.algorithms.qpe",
        "AlgorithmInfoTheoryQPE",
    ),
    "AlgorithmVQS": ("qchem_stack.quantum.algorithms.vqs", "AlgorithmVQS"),
    "AlgorithmMcLachlanRealTime": (
        "qchem_stack.quantum.algorithms.vqs",
        "AlgorithmMcLachlanRealTime",
    ),
    "AlgorithmMcLachlanImagTime": (
        "qchem_stack.quantum.algorithms.vqs",
        "AlgorithmMcLachlanImagTime",
    ),
    "SCEOMResult": ("qchem_stack.quantum.algorithms.sceom", "SCEOMResult"),
    "run_sceom_reference_subspace": (
        "qchem_stack.quantum.algorithms.sceom",
        "run_sceom_reference_subspace",
    ),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod_name, attr_name = _LAZY_EXPORTS[name]
    module = importlib.import_module(mod_name)
    obj = getattr(module, attr_name)
    globals()[name] = obj
    return obj


def __dir__() -> list[str]:
    return sorted(__all__)
