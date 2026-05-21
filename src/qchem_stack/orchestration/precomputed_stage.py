from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.precomputed_bundle import resolve_bundle_path
from qchem_stack.chem.precomputed_pre_quantum import (
    precomputed_config_fingerprint,
    precomputed_config_fingerprint_payload,
    precomputed_pre_quantum_input,
    validate_precomputed_manifest_against_config,
)

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.config import ExperimentConfig

__all__ = [
    "is_precomputed_driver",
    "normalize_precomputed_bundle_path",
    "precomputed_config_fingerprint",
    "precomputed_config_fingerprint_payload",
    "validate_precomputed_manifest_against_config",
    "precomputed_pre_quantum_input",
]


def is_precomputed_driver(cfg: ExperimentConfig) -> bool:
    return str(cfg.scf.driver).strip().lower() == "precomputed"


def normalize_precomputed_bundle_path(
    cfg: ExperimentConfig, *, cfg_path: Path | None
) -> ExperimentConfig:
    if not is_precomputed_driver(cfg):
        return cfg
    raw = str(cfg.scf.precomputed.bundle_path or "").strip()
    if not raw:
        return cfg
    resolved = resolve_bundle_path(raw, cfg_path=cfg_path)
    return cfg.model_copy(
        update={
            "scf": cfg.scf.model_copy(
                update={
                    "precomputed": cfg.scf.precomputed.model_copy(
                        update={"bundle_path": str(resolved)}
                    )
                }
            )
        }
    )
