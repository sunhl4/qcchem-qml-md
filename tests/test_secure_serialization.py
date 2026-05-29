"""HMAC protocol serialization and legacy pickle compatibility."""

from __future__ import annotations

import pickle
import warnings

import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.protocols.secure_serialization import (
    secure_dumps,
    secure_loads,
    secure_loads_protocol,
)


def _minimal_protocol() -> PauliAveragingProtocol:
    h = QubitOperator((), 0.1)
    return PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=10),
    )


def test_secure_roundtrip_signed_blob() -> None:
    proto = _minimal_protocol()
    blob = secure_dumps(proto)
    loaded = secure_loads_protocol(blob)
    assert isinstance(loaded, PauliAveragingProtocol)
    assert loaded.n_qubits == proto.n_qubits


def test_legacy_unsigned_pickle_still_loads() -> None:
    proto = _minimal_protocol()
    legacy = pickle.dumps(proto)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        loaded = secure_loads_protocol(legacy)
    assert isinstance(loaded, PauliAveragingProtocol)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_tampered_signed_blob_rejected() -> None:
    proto = _minimal_protocol()
    blob = bytearray(secure_dumps(proto))
    blob[-1] ^= 0xFF
    with pytest.raises(ValueError, match="Invalid HMAC signature"):
        secure_loads(bytes(blob))


def test_secure_loads_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        secure_loads(b"not-a-pickle")
