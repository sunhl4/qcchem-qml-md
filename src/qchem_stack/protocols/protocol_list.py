"""Batch multiple computables with shared evaluation context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qchem_stack.protocols.computables.base import (
        ComputableRuntime,
        EvaluationContext,
    )


@dataclass
class ProtocolSpec:
    """Lightweight protocol tag for matrix enforcement."""

    name: str
    kind: str = "pauli_averaging"


@dataclass
class ProtocolList:
    items: list[tuple[ComputableRuntime, ProtocolSpec]] = field(default_factory=list)

    def run_all(self, ctx: EvaluationContext) -> dict[str, Any]:
        results: dict[str, Any] = {}
        metas: dict[str, Any] = {}
        for comp, pspec in self.items:
            out = comp.evaluate(ctx)
            results[comp.name] = out.value
            metas[comp.name] = {"protocol": pspec.name, **out.meta}
        return {"results": results, "computable_meta": metas}

    @classmethod
    def from_computables(
        cls,
        computables: list[ComputableRuntime],
        *,
        protocol_name: str = "pauli_averaging_exact",
    ) -> ProtocolList:
        pspec = ProtocolSpec(name=protocol_name, kind="pauli_averaging")
        return cls([(c, pspec) for c in computables])
