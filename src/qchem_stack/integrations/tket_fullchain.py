"""
TKET-oriented **compile closing** path: ``CircuitIR`` → pytket circuit → resource stats.

Logical compilation stays boxed until lowering; we expose a single hook that fails soft when pytket is absent.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import (
    TKET_CLOSURE_LAYER_V1,
    TKET_PEEPHOLE_OPTIMIZE_V1,
    TKET_STATS_ATTEMPT_V1,
)

if TYPE_CHECKING:
    from qchem_stack.backends.spec import CircuitIR


class TketCompileMode(str, Enum):
    """How aggressively to involve pytket (open stack)."""

    OFF = "off"
    """Only :mod:`qchem_stack.backends.compile_passes` on ``CircuitIR``."""
    STATS = "stats"
    """Translate IR → pytket → depth / 2Q / gate count (no backend rebase)."""
    FULL = "full"
    """Run local pytket ``FullPeepholeOptimise`` when available (no device ``Backend`` rebase)."""


def describe_tket_closure_layer() -> dict[str, Any]:
    """Machine-readable summary for parity docs / dashboards."""
    return {
        "schema": TKET_CLOSURE_LAYER_V1,
        "bridge_module": "qchem_stack.backends.pytket_bridge",
        "modes": [m.value for m in TketCompileMode],
        "note": "FULL mode refers to optional local peephole optimise (see circuit_ir_tket_peephole_optimize_stats_or_none); ion-trap vendor passes still external.",
    }


def circuit_ir_to_tket_stats_or_none(ir: CircuitIR) -> dict[str, Any] | None:
    """
    If pytket is installed, return ``pytket_circuit_stats`` plus conversion warnings.

    Returns ``None`` if pytket is not importable (no exception).
    """
    try:
        from qchem_stack.backends.pytket_bridge import circuit_ir_to_pytket, pytket_circuit_stats
    except ImportError:
        return None
    try:
        circ, warnings = circuit_ir_to_pytket(ir)
        stats = pytket_circuit_stats(circ)
    except Exception as e:  # noqa: BLE001
        return {
            "schema": TKET_STATS_ATTEMPT_V1,
            "ok": False,
            "error": str(e)[:500],
        }
    return {
        "schema": TKET_STATS_ATTEMPT_V1,
        "ok": True,
        "pytket_stats": stats,
        "bridge_warnings": warnings,
    }


def circuit_ir_tket_peephole_optimize_stats_or_none(ir: CircuitIR) -> dict[str, Any] | None:
    """
    Apply ``FullPeepholeOptimise`` to a bridged circuit and return before/after gate/depth stats.

    Returns ``None`` if pytket is missing; does not raise.
    """
    try:
        from pytket.passes import FullPeepholeOptimise

        from qchem_stack.backends.pytket_bridge import circuit_ir_to_pytket, pytket_circuit_stats
    except ImportError:
        return None
    try:
        circ, warnings = circuit_ir_to_pytket(ir)
        before = pytket_circuit_stats(circ)
        opt = circ.copy()
        FullPeepholeOptimise().apply(opt)
        after = pytket_circuit_stats(opt)
    except Exception as e:  # noqa: BLE001
        return {
            "schema": TKET_PEEPHOLE_OPTIMIZE_V1,
            "ok": False,
            "error": str(e)[:500],
        }
    return {
        "schema": TKET_PEEPHOLE_OPTIMIZE_V1,
        "ok": True,
        "before": before,
        "after": after,
        "bridge_warnings": warnings,
    }
