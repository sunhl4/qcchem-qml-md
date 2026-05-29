"""Smoke tests for protocol_counts TypedDict helpers and build_cache re-exports."""

from __future__ import annotations


def test_empty_protocol_counts() -> None:
    from qchem_stack.protocols.protocol_counts import empty_protocol_counts

    assert empty_protocol_counts() == {}


def test_protocol_counts_typed_dict_keys_importable() -> None:
    from qchem_stack.protocols.protocol_counts import (
        ProtocolCountsCore,
        ProtocolCountsPauliSupport,
        ProtocolCountsPmsv,
        ProtocolCountsZne,
    )

    core: ProtocolCountsCore = {"expectation": -1.0, "expectation_source": "test"}
    assert core["expectation"] == -1.0
    zne: ProtocolCountsZne = {"zne_mode": "linear"}
    pmsv: ProtocolCountsPmsv = {"kept_shots": 100}
    pauli: ProtocolCountsPauliSupport = {"n_hamiltonian_pauli_terms": 3}
    assert zne["zne_mode"] == "linear"
    assert pmsv["kept_shots"] == 100
    assert pauli["n_hamiltonian_pauli_terms"] == 3


def test_build_cache_reexport_matches_canonical() -> None:
    from qchem_stack.chem.bridges import run_build_cache as canonical
    from qchem_stack.orchestration import build_cache as shim

    assert shim.RunBuildCache is canonical.RunBuildCache
    assert shim.pack_cache_key is canonical.pack_cache_key
