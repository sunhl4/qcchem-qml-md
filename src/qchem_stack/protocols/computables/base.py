"""Shared runtime context for Computable evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.protocols.ansatz_prep import AnsatzPrepSpec


@dataclass
class EvaluationContext:
    """Inputs shared across computables in a ProtocolList batch."""

    angles: np.ndarray
    ansatz_prep: AnsatzPrepSpec | None = None
    rng: np.random.Generator | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    name: str
    value: float | complex | dict[str, Any]
    meta: dict[str, Any] = field(default_factory=dict)


class ComputableRuntime(Protocol):
    name: str

    def evaluate(self, ctx: EvaluationContext) -> EvaluationResult: ...
