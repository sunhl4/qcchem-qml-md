from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.chem.pre_quantum_builder_registry import (
    list_pre_quantum_branch_builders,
    register_pre_quantum_branch_builder,
)
from qchem_stack.chem.pre_quantum_path import PreQuantumPath
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference


def test_pre_quantum_default_builder_registry_lists_all_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_precomputed_bundle.yaml"
    cfg = load_experiment_config(cfg_path)
    rhf = run_scf_reference(cfg)
    build_pre_quantum_input_with_context(cfg, rhf, cfg_path=cfg_path)
    assert set(list_pre_quantum_branch_builders()) == {
        path.value for path in PreQuantumPath
    }


def test_pre_quantum_builder_registry_requires_explicit_override() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_precomputed_bundle.yaml"
    cfg = load_experiment_config(cfg_path)
    rhf = run_scf_reference(cfg)
    build_pre_quantum_input_with_context(cfg, rhf, cfg_path=cfg_path)

    def _dummy_builder(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise NotImplementedError

    with pytest.raises(ValueError, match="already registered"):
        register_pre_quantum_branch_builder(PreQuantumPath.PRECOMPUTED_BUNDLE, _dummy_builder)
