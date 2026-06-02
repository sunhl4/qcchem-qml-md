"""Semantic validation for MD/ML energy reference consistency."""

from __future__ import annotations

import os
import warnings
from typing import TYPE_CHECKING, Literal

from qchem_stack.exceptions import ConfigurationError

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig

EnergyReference = Literal["variational", "scf", "pauli_protocol"]
TheoryLevel = Literal["hf_scf", "full_pipeline"]


def resolved_validation_energy_reference(
    loop_cfg: MdValidationLoopConfig,
) -> EnergyReference:
    return loop_cfg.validation_energy_reference or loop_cfg.label_energy_reference


def resolved_validation_theory_level(loop_cfg: MdValidationLoopConfig) -> TheoryLevel:
    return loop_cfg.validation_theory_level or loop_cfg.label_top_theory_level


def warn_deprecated_label_screening_theory_level(loop_cfg: MdValidationLoopConfig) -> None:
    """``label_screening_theory_level`` is legacy; |ΔE| uses validation_theory_level."""
    if loop_cfg.label_screening_theory_level != "hf_scf":
        warnings.warn(
            "label_screening_theory_level is deprecated and ignored for |ΔE| scoring; "
            "set validation_theory_level instead.",
            UserWarning,
            stacklevel=3,
        )


def warn_hf_forces_non_scf_energy(
    *,
    energy_reference: EnergyReference,
    include_hf_nuclear_gradient: bool,
) -> None:
    if include_hf_nuclear_gradient and energy_reference != "scf":
        warnings.warn(
            f"include_hf_nuclear_gradient=True attaches HF analytic forces while "
            f"energy_reference={energy_reference!r} (non-SCF energy). "
            "Forces and energies may be inconsistent.",
            UserWarning,
            stacklevel=3,
        )


def validate_loop_energy_consistency(
    loop_cfg: MdValidationLoopConfig,
    experiment_cfg: ExperimentConfig | None = None,
    *,
    strict: bool | None = None,
) -> list[str]:
    """Return human-readable issues; raise ConfigurationError when strict and non-empty."""
    if strict is None:
        strict = os.getenv("QCHEM_MD_LOOP_ENERGY_STRICT", "1").lower() not in {
            "0",
            "false",
            "no",
        }
    issues: list[str] = []

    val_ref = resolved_validation_energy_reference(loop_cfg)
    if (
        loop_cfg.validation_energy_reference is not None
        and loop_cfg.validation_energy_reference != loop_cfg.label_energy_reference
    ):
        issues.append(
            "validation_energy_reference differs from label_energy_reference; "
            "training labels and |ΔE| scoring use different energy surfaces."
        )

    val_theory = resolved_validation_theory_level(loop_cfg)
    if val_theory == "hf_scf" and val_ref != "scf":
        issues.append(
            f"validation_theory_level=hf_scf with energy_reference={val_ref!r} mixes "
            "cheap HF geometry evaluation with non-HF energy reference."
        )

    if experiment_cfg is not None and experiment_cfg.md_ml_export.attach_single_frame_to_repro:
        exp_ref = experiment_cfg.md_ml_export.energy_reference
        if exp_ref != loop_cfg.label_energy_reference:
            issues.append(
                f"experiment md_ml_export.energy_reference={exp_ref!r} != "
                f"loop label_energy_reference={loop_cfg.label_energy_reference!r}."
            )

    if strict and issues:
        raise ConfigurationError("; ".join(issues))
    return issues


def prepare_loop_config(loop_cfg: MdValidationLoopConfig) -> MdValidationLoopConfig:
    """Normalize defaults and emit deprecation warnings before the loop runs."""
    warn_deprecated_label_screening_theory_level(loop_cfg)
    warn_hf_forces_non_scf_energy(
        energy_reference=resolved_validation_energy_reference(loop_cfg),
        include_hf_nuclear_gradient=loop_cfg.include_hf_nuclear_gradient,
    )
    return loop_cfg
