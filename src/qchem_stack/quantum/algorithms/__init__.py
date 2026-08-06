"""Quantum algorithm classes — lazy exports via :func:`__getattr__`."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "AlgorithmBase",
    "AlgorithmLifecycle",
    "AlgorithmReport",
    "VQE",
    "GQE",
    "ConditionalGQE",
    "PersistentDPOGQE",
    "SmilesTransferGQE",
    "QSCIGQE",
    "AugerGQE",
    "GQKAE",
    "SpinGQE",
    "AdaptGQE",
    "CBS",
    "QSCI",
    "SQD",
    "QSEQSCI",
    "AdaptQSCI",
    "SKQD",
    "SqDRIFT",
    "HIVQE",
    "EWFTrimSQD",
    "QBESQD",
    "SQDAFQMC",
    "FermionicAdaptVQE",
    "IQEBVQE",
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
    "GQE": ("qchem_stack.quantum.algorithms.gqe", "GQE"),
    "ConditionalGQE": ("qchem_stack.quantum.algorithms.gqe", "ConditionalGQE"),
    "PersistentDPOGQE": ("qchem_stack.quantum.algorithms.gqe", "PersistentDPOGQE"),
    "SmilesTransferGQE": ("qchem_stack.quantum.algorithms.gqe", "SmilesTransferGQE"),
    "QSCIGQE": ("qchem_stack.quantum.algorithms.gqe", "QSCIGQE"),
    "AugerGQE": ("qchem_stack.quantum.algorithms.gqe", "AugerGQE"),
    "GQKAE": ("qchem_stack.quantum.algorithms.gqe", "GQKAE"),
    "SpinGQE": ("qchem_stack.quantum.algorithms.gqe", "SpinGQE"),
    "AdaptGQE": ("qchem_stack.quantum.algorithms.gqe", "AdaptGQE"),
    "CBS": ("qchem_stack.quantum.algorithms.sqd", "CBS"),
    "QSCI": ("qchem_stack.quantum.algorithms.sqd", "QSCI"),
    "SQD": ("qchem_stack.quantum.algorithms.sqd", "SQD"),
    "QSEQSCI": ("qchem_stack.quantum.algorithms.sqd", "QSEQSCI"),
    "AdaptQSCI": ("qchem_stack.quantum.algorithms.sqd", "AdaptQSCI"),
    "SKQD": ("qchem_stack.quantum.algorithms.sqd", "SKQD"),
    "SqDRIFT": ("qchem_stack.quantum.algorithms.sqd", "SqDRIFT"),
    "HIVQE": ("qchem_stack.quantum.algorithms.sqd", "HIVQE"),
    "EWFTrimSQD": ("qchem_stack.quantum.algorithms.sqd", "EWFTrimSQD"),
    "QBESQD": ("qchem_stack.quantum.algorithms.sqd", "QBESQD"),
    "SQDAFQMC": ("qchem_stack.quantum.algorithms.sqd", "SQDAFQMC"),
    "FermionicAdaptVQE": ("qchem_stack.quantum.algorithms.adapt", "FermionicAdaptVQE"),
    "IQEBVQE": ("qchem_stack.quantum.algorithms.iqeb", "IQEBVQE"),
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
