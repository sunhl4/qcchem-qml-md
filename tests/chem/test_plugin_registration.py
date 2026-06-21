"""Variational and excited plugin registration tests."""

from __future__ import annotations

import pytest

from qchem_stack.quantum.excited_plugins.registry import (
    get_excited_plugin_record,
    register_excited_plugin,
    unregister_excited_plugin,
)
from qchem_stack.quantum.variational_plugins.examples.echo_runner import run_echo_variational
from qchem_stack.quantum.variational_plugins.registry import (
    is_registered_variational_id,
    register_variational_plugin,
    unregister_variational_plugin,
)


def test_variational_plugin_register_unregister_roundtrip() -> None:
    pid = "___ephemeral_plugin_registration_test___"
    register_variational_plugin(
        pid,
        runner=run_echo_variational,
        summary="Ephemeral test plugin.",
        implementation="tests.test_plugin_registration",
        overwrite=True,
    )
    assert is_registered_variational_id(pid)
    unregister_variational_plugin(pid)
    assert not is_registered_variational_id(pid)


def test_excited_plugin_register_unregister_roundtrip() -> None:
    from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome

    def _runner(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
        return ExcitedStageOutcome(bundle_key="test", bundle={"ok": True})

    eid = "___ephemeral_excited_registration_test___"
    register_excited_plugin(
        eid,
        runner=_runner,
        summary="Ephemeral excited plugin.",
        implementation="tests.test_plugin_registration",
        overwrite=True,
    )
    assert get_excited_plugin_record(eid) is not None
    unregister_excited_plugin(eid)
    assert get_excited_plugin_record(eid) is None


def test_unregister_unknown_excited_raises() -> None:
    with pytest.raises(KeyError):
        unregister_excited_plugin("___no_such_excited_plugin___")
