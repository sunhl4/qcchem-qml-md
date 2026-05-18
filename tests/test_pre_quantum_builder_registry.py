from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.chem.pre_quantum_builder_registry import (
    PreQuantumBuildRequest,
    get_pre_quantum_branch_builder,
    list_pre_quantum_branch_builders,
    register_pre_quantum_branch_builder,
)
from qchem_stack.chem.pre_quantum_path import PreQuantumPath
from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import PreQuantumCapabilityError
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

    def _dummy_builder(_req: PreQuantumBuildRequest):
        raise NotImplementedError

    with pytest.raises(PreQuantumCapabilityError, match="already registered"):
        register_pre_quantum_branch_builder(PreQuantumPath.PRECOMPUTED_BUNDLE, _dummy_builder)


def test_pre_quantum_builder_registry_override_is_effective() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    rhf = run_scf_reference(cfg)
    build_pre_quantum_input_with_context(cfg, rhf, cfg_path=cfg_path)

    path = PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK
    original = get_pre_quantum_branch_builder(path)

    calls = {"n": 0}

    def _wrapper(req: PreQuantumBuildRequest):
        calls["n"] += 1
        return original(req)

    register_pre_quantum_branch_builder(path, _wrapper, allow_override=True)
    try:
        build_pre_quantum_input_with_context(cfg, rhf, cfg_path=cfg_path)
        assert calls["n"] == 1
    finally:
        register_pre_quantum_branch_builder(path, original, allow_override=True)
