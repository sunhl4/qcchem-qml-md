"""Sample-based quantum chemistry algorithms (SQD family; peer to VQE).

Source survey: ``docs/基于采样的量子化学计算报告.pdf`` (IBM sampling / QCSC line).
"""

from __future__ import annotations

from qchem_stack.contracts.schema_ids import ALGORITHM_SQD_REPORT_V1
from qchem_stack.quantum.algorithms.sqd.core import (
    VARIANT_TO_CLASS,
    AdaptQSCI,
    CBS,
    EWFTrimSQD,
    HIVQE,
    QBESQD,
    QSCI,
    QSEQSCI,
    SKQD,
    SQD,
    SQDAFQMC,
    SqDRIFT,
    sqd_algorithm_report_v1,
)
from qchem_stack.quantum.algorithms.sqd.types import (
    ALL_SQD_ALGORITHM_IDS,
    CUSTOMER_SQD_ALGORITHM_IDS,
    EXPERIMENTAL_SQD_ALGORITHM_IDS,
    MAX_SQD_QUBITS,
    SqdConfig,
    SqdResult,
)

__all__ = [
    "ALGORITHM_SQD_REPORT_V1",
    "ALL_SQD_ALGORITHM_IDS",
    "CUSTOMER_SQD_ALGORITHM_IDS",
    "EXPERIMENTAL_SQD_ALGORITHM_IDS",
    "MAX_SQD_QUBITS",
    "VARIANT_TO_CLASS",
    "AdaptQSCI",
    "CBS",
    "EWFTrimSQD",
    "HIVQE",
    "QBESQD",
    "QSCI",
    "QSEQSCI",
    "SKQD",
    "SQD",
    "SQDAFQMC",
    "SqDRIFT",
    "SqdConfig",
    "SqdResult",
    "sqd_algorithm_report_v1",
]
