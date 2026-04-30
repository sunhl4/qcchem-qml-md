"""Placeholder for quantum-kernel or hybrid-circuit energy models distilled to MLIP."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QuantumKernelEnergyModel:
    """Reserve interface for QML energies feeding ``QMEFDataset`` augmentation."""

    note: str = "Wire kernel evaluation or small VQE snapshots into md_bridge.QMFrame builder."
