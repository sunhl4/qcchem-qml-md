"""Unit coverage for :mod:`qchem_stack.chem.active_space.mean_field_meta`."""

from __future__ import annotations

from qchem_stack.chem.active_space.mean_field_meta import (
    AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1,
    apply_active_space_strategy_to_mean_field_meta,
)


def test_avas_stub_meta_contract() -> None:
    d: dict[str, object] = {}
    apply_active_space_strategy_to_mean_field_meta(
        d,
        strategy="avas_stub",
        recipe="avas_stub:ncas=2,nelecas=2:test",
        avas_ao_labels=("Li 2s",),
    )
    assert d["active_space_strategy"] == "avas_stub"
    assert d["avas_partial_stub"] is True
    assert d["avas_atomic_projection_executed"] is False
    assert d["avas_stub_semantics"] == AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1
    assert d["avas_ao_labels_requested"] == ["Li 2s"]
    assert d["avas_ao_labels_logging_only"] is True


def test_avas_strategy_meta_pending_projection_flags() -> None:
    d: dict[str, object] = {}
    apply_active_space_strategy_to_mean_field_meta(
        d,
        strategy="avas",
        recipe="avas:test",
        avas_ao_labels=("H 1s",),
    )
    assert d["active_space_strategy"] == "avas"
    assert d["avas_atomic_projection_executed"] is False
    assert "avas_partial_stub" not in d
    assert d["avas_ao_labels_requested"] == ["H 1s"]
    assert d.get("avas_ao_labels_logging_only") is not True


def test_cas_strategy_with_labels_logs_only_no_avas_stub_keys() -> None:
    d: dict[str, object] = {"avas_partial_stub": True}
    apply_active_space_strategy_to_mean_field_meta(
        d,
        strategy="cas",
        recipe="cas:ncas=4,nelecas=4",
        avas_ao_labels=["O 2p"],
    )
    assert d["active_space_strategy"] == "cas"
    assert "avas_partial_stub" not in d
    assert "avas_atomic_projection_executed" not in d
    assert "avas_stub_semantics" not in d
    assert d["avas_ao_labels_logging_only"] is True
