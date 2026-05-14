from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from qchem_stack.md_bridge.schema import QMEFDataset


@dataclass
class TrainedModelArtifact:
    path: str
    metrics: dict[str, float] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


class ForceFieldTrainerProtocol(Protocol):
    def fit(self, dataset: QMEFDataset, hyperparams: dict[str, Any]) -> TrainedModelArtifact: ...

    def export_openmm(self, path: str) -> None: ...

    def export_lammps(self, path: str) -> None: ...

    def score(self, dataset_val: QMEFDataset) -> dict[str, float]: ...


class StubTorchMLIPTrainer:
    """Non-training stub: records hyperparameters and writes placeholder paths."""

    def fit(self, dataset: QMEFDataset, hyperparams: dict[str, Any]) -> TrainedModelArtifact:
        return TrainedModelArtifact(
            path="stub_model.pt",
            metrics={"rmse_energy_mHa": 0.0, "rmse_force": 0.0},
            meta=hyperparams | {"n_frames": len(dataset.frames)},
        )

    def export_openmm(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "# OpenMM torch export placeholder — integrate OpenMM-ML / NNPOps in production.\n"
            )

    def export_lammps(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# LAMMPS pair_nequip / MACE export placeholder.\n")

    def score(self, dataset_val: QMEFDataset) -> dict[str, float]:
        return {"kendall_tau": 1.0, "rmse_energy_mHa": 0.0}
