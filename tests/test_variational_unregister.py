"""Runtime unregister for dynamically registered variational plug-ins."""

from __future__ import annotations

import pytest

from qchem_stack.quantum.variational_plugins.examples.echo_runner import run_echo_variational
from qchem_stack.quantum.variational_plugins.registry import (
    BUILTIN_VARIATIONAL_PLUGIN_IDS,
    is_registered_variational_id,
    register_variational_plugin,
    unregister_variational_plugin,
)


def test_unregister_builtin_is_forbidden() -> None:
    for pid in sorted(BUILTIN_VARIATIONAL_PLUGIN_IDS):
        with pytest.raises(ValueError, match="cannot unregister built-in"):
            unregister_variational_plugin(pid)


def test_unregister_unknown_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        unregister_variational_plugin("___no_such_plugin_ever___")


def test_unregister_removes_registration_and_keeps_builtin_intact() -> None:
    pid = "___ephemeral_unregister_test_plugin___"
    register_variational_plugin(
        pid,
        runner=run_echo_variational,
        summary="Ephemeral unregister test plug-in.",
        implementation="tests.test_variational_unregister",
        overwrite=True,
    )
    assert is_registered_variational_id(pid)
    unregister_variational_plugin(pid)
    assert not is_registered_variational_id(pid)
    assert sorted(BUILTIN_VARIATIONAL_PLUGIN_IDS) == sorted(
        ("adapt", "iqeb", "tetris_adapt", "vqe")
    )
