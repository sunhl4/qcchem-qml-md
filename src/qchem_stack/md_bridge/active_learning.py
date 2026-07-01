"""MD-bridge active-learning helpers (discrete pool + mock labeling for tests)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import numpy as np

from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame
from qchem_stack.quantum.algorithms.tolerances import RIDGE_REGULARIZATION

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


@dataclass
class ActiveLearningLoop:
    """Pick next geometry index by max predicted uncertainty (toy on discrete pool)."""

    pool_features: np.ndarray
    acquisition: Callable[[np.ndarray, SurrogateEnergyModel], int]

    def next_index(self, model: SurrogateEnergyModel) -> int:
        return int(self.acquisition(self.pool_features, model))


@dataclass
class SurrogateEnergyModel:
    """Ridge-style linear surrogate on scalar features (test / API stub only)."""

    weights: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray, lam: float = RIDGE_REGULARIZATION) -> None:
        x = np.c_[np.ones(len(X)), X]
        d = x.shape[1]
        self.weights = np.linalg.solve(x.T @ x + lam * np.eye(d), x.T @ y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            from qchem_stack.exceptions import MDBridgeError

            raise MDBridgeError("call fit first")
        x = np.c_[np.ones(len(X)), X]
        return cast("np.ndarray", x @ self.weights)


def max_std_proxy(X: np.ndarray, model: SurrogateEnergyModel) -> int:
    """Use deviation from mean prediction as exploration proxy."""
    preds = model.predict(X)
    return int(np.argmax(np.abs(preds - preds.mean())))


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
    "SurrogateEnergyModel",
    "max_std_proxy",
    "mock_labeling_result",
]
