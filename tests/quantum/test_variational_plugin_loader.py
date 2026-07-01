"""Focused coverage for variational_plugins.loader edge paths."""

from __future__ import annotations

import pytest

from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.variational_plugins.loader import (
    load_variational_runner_from_factory,
    validate_factory_import_path,
)


def test_validate_factory_import_path_rejects_empty_parts() -> None:
    with pytest.raises(ValueError, match="Invalid algorithm_factory"):
        validate_factory_import_path(":fn")
    with pytest.raises(ValueError, match="Invalid algorithm_factory"):
        validate_factory_import_path("mod:")


def test_load_factory_rejects_missing_attribute() -> None:
    with pytest.raises(PipelineError, match="attribute not found"):
        load_variational_runner_from_factory(
            "qchem_stack.quantum.variational_plugins.loader:__not_an_attr__"
        )


def test_load_factory_rejects_external_module_by_default() -> None:
    with pytest.raises(PipelineError, match="outside the default allowlist"):
        load_variational_runner_from_factory("json:loads")


def test_load_factory_allows_external_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from qchem_stack.quantum.variational_plugins import loader as loader_mod

    monkeypatch.setenv("QCHEM_QUANTUM_ALGORITHM_FACTORY_ALLOW_EXTERNAL", "1")
    loader_mod._assert_factory_module_allowed("json")
    runner = load_variational_runner_from_factory(
        "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
    )
    assert callable(runner)


def test_load_factory_class_plugin_run_variational() -> None:
    runner = load_variational_runner_from_factory(
        "qchem_stack.quantum.variational_plugins.examples.echo_runner:EchoVariationalPlugin"
    )
    assert callable(runner)


def test_load_factory_direct_runner_one_arg() -> None:
    runner = load_variational_runner_from_factory(
        "qchem_stack.quantum.variational_plugins.examples.echo_runner:run_echo_variational"
    )
    assert callable(runner)


def test_load_factory_non_callable_raises() -> None:
    with pytest.raises(PipelineError, match="expected class or callable"):
        load_variational_runner_from_factory(
            "qchem_stack.quantum.variational_plugins.loader:_FACTORY_ALLOW_EXTERNAL_ENV"
        )


def test_load_factory_class_without_run_variational_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QCHEM_QUANTUM_ALGORITHM_FACTORY_ALLOW_EXTERNAL", "1")
    with pytest.raises(PipelineError, match="run_variational"):
        load_variational_runner_from_factory("builtins:object")


def test_load_factory_factory_returning_bad_object_raises() -> None:
    spec = "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"

    def _bad_factory() -> str:
        return "not_a_runner"

    import qchem_stack.quantum.variational_plugins.examples.echo_runner as mod

    original = mod.echo_runner_factory
    mod.echo_runner_factory = _bad_factory  # type: ignore[assignment]
    try:
        with pytest.raises(PipelineError, match="factory must return"):
            load_variational_runner_from_factory(spec)
    finally:
        mod.echo_runner_factory = original


def test_load_factory_class_needs_zero_arg_constructor() -> None:
    with pytest.raises(PipelineError, match="zero arguments"):
        load_variational_runner_from_factory(
            "qchem_stack.quantum.variational_plugins.spec:VariationalRunContext"
        )
