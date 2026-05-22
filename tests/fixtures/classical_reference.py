"""Test helpers for classical mean-field references (prefer over deprecated PySCFDriver)."""

from __future__ import annotations

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.reference_factory import (
    classical_mean_field_reference_from_config,
    pyscf_rhf_result_from_config,
)
from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult
from qchem_stack.config import ExperimentConfig

__all__ = [
    "classical_reference_from_config",
    "pyscf_rhf_from_config",
]


def classical_reference_from_config(cfg: ExperimentConfig) -> ClassicalMeanFieldReference:
    return classical_mean_field_reference_from_config(cfg)


def pyscf_rhf_from_config(cfg: ExperimentConfig) -> PySCFRHFResult:
    return pyscf_rhf_result_from_config(cfg)
