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
    """Legacy unsigned pickles require explicit opt-in via environment variable."""
    import os

    proto = _minimal_protocol()
    legacy = pickle.dumps(proto)

    # Without env var, should be rejected
    with pytest.raises(ValueError, match="disabled by default"):
        secure_loads_protocol(legacy)

    # With env var set, should load with deprecation warning
    os.environ["QCHEM_ALLOW_LEGACY_PICKLE"] = "1"
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            loaded = secure_loads_protocol(legacy)
        assert isinstance(loaded, PauliAveragingProtocol)
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    finally:
        del os.environ["QCHEM_ALLOW_LEGACY_PICKLE"]


def test_tampered_signed_blob_rejected() -> None:
    proto = _minimal_protocol()
    blob = bytearray(secure_dumps(proto))
    blob[-1] ^= 0xFF
    with pytest.raises(ValueError, match="Invalid HMAC signature"):
        secure_loads(bytes(blob))


def test_secure_loads_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        secure_loads(b"not-a-pickle")


def test_secure_loads_protocol_rejects_non_allowlisted_pickle() -> None:
    import os

    os.environ["QCHEM_ALLOW_LEGACY_PICKLE"] = "1"
    try:
        legacy = pickle.dumps({"not": "a protocol"})
        with pytest.raises(TypeError, match="PauliAveragingProtocol"):
            secure_loads_protocol(legacy)
    finally:
        del os.environ["QCHEM_ALLOW_LEGACY_PICKLE"]


def test_secure_v2_roundtrip_when_env_enabled() -> None:
    import os

    proto = _minimal_protocol()
    os.environ["QCHEM_PROTOCOL_BLOB_V2"] = "1"
    try:
        blob = secure_dumps(proto)
        loaded = secure_loads_protocol(blob)
        assert loaded.n_qubits == proto.n_qubits
    finally:
        del os.environ["QCHEM_PROTOCOL_BLOB_V2"]


def test_missing_hmac_key_raises_configuration_error() -> None:
    """P0-2: secure_dumps/loads must fail-secure when QCHEM_PROTOCOL_HMAC_KEY is unset."""
    import os

    saved = os.environ.pop("QCHEM_PROTOCOL_HMAC_KEY", None)
    try:
        from qchem_stack.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError, match="QCHEM_PROTOCOL_HMAC_KEY"):
            secure_dumps(_minimal_protocol())
    finally:
        if saved is not None:
            os.environ["QCHEM_PROTOCOL_HMAC_KEY"] = saved
