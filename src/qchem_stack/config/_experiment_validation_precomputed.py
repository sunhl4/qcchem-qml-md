"""Precomputed-driver cross-field validation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from qchem_stack.exceptions import ConfigurationError

from ._driver_helpers import scf_driver_id

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


def validate_precomputed_driver_excludes_live_hooks(spec: ExperimentConfig) -> None:
    if scf_driver_id(spec.scf.driver) != "precomputed":
        return
    ce = spec.chemistry_extended
    if ce.benchmarks.enabled:
        raise ConfigurationError(
            "chemistry_extended.benchmarks.enabled is unsupported with "
            "scf.driver='precomputed' (no live post-HF backend)."
        )
    if str(ce.post_hf.rdm_correction_method).strip().lower() != "none":
        raise ConfigurationError(
            "chemistry_extended.post_hf.rdm_correction_method requires live backend hooks and is "
            "unsupported with scf.driver='precomputed'."
        )
    from qchem_stack.config.embedding_enums import EmbeddingMode
    from qchem_stack.config.embedding_helpers import is_projection_mulliken, is_schmidt_production

    emb = spec.embedding
    if emb.mode == EmbeddingMode.DMET and is_schmidt_production(emb):
        raise ConfigurationError(
            "embedding.dmet.hamiltonian_source='schmidt_atomic_production' requires "
            "supports_schmidt_atomic_hamiltonian=True; scf.driver='precomputed' is bundle-only."
        )
    if emb.mode == EmbeddingMode.PROJECTION and is_projection_mulliken(emb):
        raise ConfigurationError(
            "embedding.projection.quantum_hamiltonian='fragment_mulliken_mo' requires "
            "supports_projection_fragment_mulliken_hamiltonian=True; "
            "scf.driver='precomputed' is bundle-only."
        )


def preprocess_precomputed_bundle_path(
    data: dict[str, Any],
    *,
    base_dir: Path,
) -> None:
    """Resolve ``scf.precomputed.bundle_path`` relative to YAML location when present."""
    scf = data.get("scf")
    if not isinstance(scf, dict):
        return
    if str(scf.get("driver", "")).strip().lower() != "precomputed":
        return
    pre = scf.get("precomputed")
    if not isinstance(pre, dict):
        return
    raw = pre.get("bundle_path")
    if raw is None:
        return
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigurationError(
            "scf.precomputed.bundle_path must be a non-empty string when scf.driver='precomputed'."
        )
    p = Path(raw.strip())
    resolved = p if p.is_absolute() else (base_dir / p).resolve()
    pre["bundle_path"] = str(resolved)
