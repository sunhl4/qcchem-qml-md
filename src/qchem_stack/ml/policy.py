from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qchem_stack.backends.spec import CompilerPassBundle


@dataclass
class MLPolicy:
    """Inject ML decisions into allowed strategy space (compiler passes / shots multiplier)."""

    extra_compiler_passes: list[str] = field(default_factory=list)
    shots_multiplier: float = 1.0

    def adjust_bundle(self, bundle: CompilerPassBundle) -> CompilerPassBundle:
        return CompilerPassBundle(
            optimization_level=bundle.optimization_level,
            preoptimize_passes=list(bundle.preoptimize_passes) + list(self.extra_compiler_passes),
            compiler_passes=list(bundle.compiler_passes),
        )

    def adjust_shots(self, base: int) -> int:
        return max(1, int(base * self.shots_multiplier))
