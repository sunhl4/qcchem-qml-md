from __future__ import annotations

import hashlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ExperimentConfig, dump_experiment_config


def package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("numpy", "scipy", "openfermion", "pandas"):
        try:
            mod = __import__(name)
            out[name] = str(getattr(mod, "__version__", "?"))
        except Exception:  # noqa: BLE001
            out[name] = "not_imported"
    try:
        import yaml as yaml_mod

        out["yaml"] = str(getattr(yaml_mod, "__version__", "?"))
    except Exception:  # noqa: BLE001
        out["yaml"] = "not_imported"
    try:
        import pyscf

        out["pyscf"] = str(getattr(pyscf, "__version__", "?"))
    except Exception:  # noqa: BLE001
        out["pyscf"] = "not_imported"
    return out


def classical_software_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("pyscf", "psi4"):
        try:
            mod = __import__(name)
            out[name] = str(getattr(mod, "__version__", "?"))
        except Exception:  # noqa: BLE001
            out[name] = "not_imported"
    return out


def collect_repro_metadata_impl(
    cfg: ExperimentConfig,
    *,
    parity_snapshot_fn: Callable[[ExperimentConfig, QubitHamiltonian | None], dict[str, Any]],
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    """Hashes and versions for job/publication reproducibility."""
    from qchem_stack.integrations.workflow_preview import (
        workflow_preview_payload,
        workflow_preview_qpe_track_slice_v1,
        workflow_preview_variational_execution_slice_v1,
        workflow_preview_vqs_track_slice_v1,
    )

    raw_yaml = dump_experiment_config(cfg)
    h = hashlib.sha256(raw_yaml.encode("utf-8")).hexdigest()[:16]
    classical_versions = classical_software_versions()
    repro: dict[str, Any] = {
        "experiment_id": cfg.experiment_id,
        "random_seed": cfg.random_seed,
        "config_sha256_prefix": h,
        "config_path": str(cfg_path) if cfg_path else None,
        "python": sys.version.split()[0],
        "packages": package_versions(),
        "classical_software_versions": classical_versions,
        "pyscf_version": classical_versions.get("pyscf", "not_imported"),
        "embedding_config": cfg.embedding.model_dump(mode="json"),
        "chemistry_extended_config": cfg.chemistry_extended.model_dump(mode="json"),
        "nexus_analog_config": cfg.nexus_analog.model_dump(mode="json"),
        "nexus_cloud_config": cfg.nexus_cloud.model_dump(mode="json"),
        "parity_snapshot": parity_snapshot_fn(cfg, qh),
        "workflow_preview_v1": workflow_preview_payload(
            cfg,
            include_computables_rich=cfg.parity_integrations.include_computables_rich_in_repro,
        ),
    }
    ve_slice = workflow_preview_variational_execution_slice_v1(cfg)
    if ve_slice is not None:
        repro["workflow_preview_variational_execution_v1"] = ve_slice
    vqs_slice = workflow_preview_vqs_track_slice_v1(cfg)
    if vqs_slice is not None:
        repro["workflow_preview_vqs_track_v1"] = vqs_slice
    qpe_slice = workflow_preview_qpe_track_slice_v1(cfg)
    if qpe_slice is not None:
        repro["workflow_preview_qpe_track_v1"] = qpe_slice
    return repro
