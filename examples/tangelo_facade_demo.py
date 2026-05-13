"""Notebook-friendly bridge: load packaged YAML as :class:`~qchem_stack.config.ExperimentConfig`.

Tangelo users often pass nested dicts into ``VQESolver``; this repository keeps **validated YAML**
(Pydantic ``ExperimentConfig``) as the single source of truth. Use this module to jump from tutorial
names to a loaded config without introducing unchecked dict trees.

See ``examples/README.md`` and ``docs/P2_W5_algorithm_registry_alignment.md`` §5.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from qchem_stack.config import ExperimentConfig, load_experiment_config

_ROOT = Path(__file__).resolve().parents[1]

PackagedExampleName = Literal["h2_vqe", "h2_uccsd", "h2_qpe_track_parity", "h2_pec_stub"]

_PACKAGED: dict[PackagedExampleName, Path] = {
    "h2_vqe": _ROOT / "configs" / "example_h2.yaml",
    "h2_uccsd": _ROOT / "configs" / "example_h2_uccsd.yaml",
    "h2_qpe_track_parity": _ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml",
    "h2_pec_stub": _ROOT / "configs" / "example_h2_pec_literature_stub.yaml",
}


def packaged_example_names() -> tuple[PackagedExampleName, ...]:
    """Stable tuple of curated names (for tests / notebooks)."""
    return tuple(_PACKAGED.keys())


def packaged_config_path(name: PackagedExampleName = "h2_vqe") -> Path:
    """Return absolute path to a packaged experiment YAML."""
    return _PACKAGED[name]


def load_packaged_example(name: PackagedExampleName = "h2_vqe") -> ExperimentConfig:
    """Load ``ExperimentConfig`` from a curated packaged YAML under ``configs/``."""
    return load_experiment_config(packaged_config_path(name))


if __name__ == "__main__":
    cfg = load_packaged_example()
    print(cfg.experiment_id)
