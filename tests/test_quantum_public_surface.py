"""``qchem_stack.quantum`` subpackage public surfaces resolve without import cycles."""

from __future__ import annotations

import importlib

import pytest


def test_quantum_algorithms_all_importable() -> None:
    mod = importlib.import_module("qchem_stack.quantum.algorithms")
    missing: list[str] = []
    for name in mod.__all__:
        try:
            getattr(mod, name)
        except Exception as exc:  # noqa: BLE001 — surface contract
            missing.append(f"{name}: {exc}")
    assert not missing, "failed quantum.algorithms.__all__ imports:\n" + "\n".join(missing)


@pytest.mark.parametrize(
    "symbol",
    [
        "run_variational_stage",
        "register_variational_plugin",
        "list_registered_variational_ids",
        "resolve_variational_runner",
    ],
)
def test_variational_plugins_registry_symbols_importable(symbol: str) -> None:
    mod = importlib.import_module("qchem_stack.quantum.variational_plugins.registry")
    assert hasattr(mod, symbol)
    getattr(mod, symbol)


@pytest.mark.parametrize(
    "symbol",
    [
        "build_registered_algorithm",
        "list_registered_algorithm_ids",
        "algorithm_registry_export",
    ],
)
def test_algorithm_registry_symbols_importable(symbol: str) -> None:
    mod = importlib.import_module("qchem_stack.quantum.algorithm_registry")
    assert hasattr(mod, symbol)
    getattr(mod, symbol)


@pytest.mark.parametrize(
    "symbol",
    [
        "run_excited_stages_from_context",
        "resolve_excited_plugin_ids",
        "list_registered_excited_ids",
        "register_excited_plugin",
    ],
)
def test_excited_plugins_registry_symbols_importable(symbol: str) -> None:
    mod = importlib.import_module("qchem_stack.quantum.excited_plugins.registry")
    assert hasattr(mod, symbol)
    getattr(mod, symbol)


def test_quantum_init_has_empty_all() -> None:
    mod = importlib.import_module("qchem_stack.quantum")
    assert mod.__all__ == []


@pytest.mark.parametrize(
    "module_path,symbol",
    [
        ("qchem_stack.quantum.runtime", "vqe_from_experiment_config"),
        ("qchem_stack.quantum.variational_branch", "build_uccsd_variational_model"),
        ("qchem_stack.quantum.variational_branch", "run_uccsd_vqe_from_config"),
        ("qchem_stack.quantum.ansatz_registry", "ansatz_registry_export"),
        ("qchem_stack.quantum.operator_pool_registry", "build_registered_operator_pool"),
        ("qchem_stack.quantum.statevector", "hea_state"),
    ],
)
def test_documented_quantum_entry_points_importable(module_path: str, symbol: str) -> None:
    mod = importlib.import_module(module_path)
    assert hasattr(mod, symbol)
    getattr(mod, symbol)
