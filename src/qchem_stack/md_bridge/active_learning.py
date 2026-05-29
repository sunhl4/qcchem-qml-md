"""MD-bridge active-learning helpers (discrete pool + mock labeling for tests)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame
from qchem_stack.ml.active_learning import ActiveLearningLoop, max_std_proxy

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class MockLabelingSpec:
    """Deterministic energies for multi-round MD loop tests (Hartree)."""

    base_energy_hartree: float = -1.12
    per_extra_delta_hartree: float = 0.03


def mock_labeling_result(
    atomic_numbers: Sequence[int],
    base_positions_bohr: Sequence[Sequence[float]],
    extra_coordinates_bohr: Sequence[Sequence[Sequence[float]]],
    *,
    spec: MockLabelingSpec | None = None,
):
    """Build a labeling result without running the qchem pipeline."""
    from qchem_stack.md_bridge.qchem_labeler import LabelingResult

    s = spec or MockLabelingSpec()
    base_fr = QMFrame(
        atomic_numbers=list(atomic_numbers),
        positions_bohr=[list(map(float, row)) for row in base_positions_bohr],
        energy_hartree=float(s.base_energy_hartree),
        forces_hartree_bohr=[],
        method_tag="mock_labeler",
    )
    frames = [base_fr]
    for i, geom in enumerate(extra_coordinates_bohr):
        frames.append(
            QMFrame(
                atomic_numbers=list(atomic_numbers),
                positions_bohr=[list(map(float, row)) for row in geom],
                energy_hartree=float(s.base_energy_hartree + (i + 1) * s.per_extra_delta_hartree),
                forces_hartree_bohr=[],
                method_tag="mock_labeler",
            )
        )
    return LabelingResult(
        dataset=QMEFDataset(frames=frames, provenance_yaml="mock_labeler: true\n"),
        failures=[],
        epistemic_bound="mock_labeler",
        primary_repro_config_sha256_prefix="mock000000000000",
    )


__all__ = [
    "ActiveLearningLoop",
    "MockLabelingSpec",
    "max_std_proxy",
    "mock_labeling_result",
]
