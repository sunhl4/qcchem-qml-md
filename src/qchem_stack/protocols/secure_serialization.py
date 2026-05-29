"""Secure serialization with HMAC signature verification for Protocol objects.

This module provides HMAC-signed pickle serialization to prevent arbitrary code
execution from untrusted pickle payloads.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import pickle
import warnings
from typing import TYPE_CHECKING, Any, cast

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from qchem_stack.protocols.protocol import PauliAveragingProtocol

# Default HMAC key - in production, this should be set via environment variable
# QCHEM_PROTOCOL_HMAC_KEY or configured through application settings
_DEFAULT_HMAC_KEY = b"qchem-stack-protocol-serialization-key-v1"


def _get_hmac_key() -> bytes:
    """Get HMAC key from environment or use default."""
    key_str = os.environ.get("QCHEM_PROTOCOL_HMAC_KEY")
    if key_str:
        return key_str.encode("utf-8")
    return _DEFAULT_HMAC_KEY


def secure_dumps(obj: Any) -> bytes:
    """Serialize object with pickle and add HMAC signature.

    Format: [32-byte HMAC signature][pickle data]

    Args:
        obj: Object to serialize

    Returns:
        Bytes containing HMAC signature followed by pickle data
    """
    data = pickle.dumps(obj)
    key = _get_hmac_key()
    signature = hmac.new(key, data, hashlib.sha256).digest()
    return signature + data


def _hmac_signature_valid(data: bytes) -> tuple[bool, bytes]:
    """Return (valid, payload) when *data* is ``[32-byte HMAC][pickle]``."""
    if len(data) < 32:
        return False, data
    signature = data[:32]
    payload = data[32:]
    key = _get_hmac_key()
    expected_signature = hmac.new(key, payload, hashlib.sha256).digest()
    return hmac.compare_digest(signature, expected_signature), payload


def _looks_like_pickle_payload(data: bytes) -> bool:
    """Heuristic for legacy unsigned ``pickle.dumps`` blobs (pre-HMAC format)."""
    if not data:
        return False
    first = data[0:1]
    return first in {b"\x80", b"(", b"]", b"}", b"\x95", b"c"}


def _finalize_loaded(obj: Any, expected_type: type | None) -> Any:
    if expected_type is not None and not isinstance(obj, expected_type):
        raise TypeError(
            f"Deserialized object is {type(obj).__name__}, expected {expected_type.__name__}"
        )
    return obj


def secure_loads(data: bytes, expected_type: type | None = None) -> Any:
    """Deserialize object with HMAC signature verification.

    Supports legacy unsigned ``pickle.dumps`` blobs written before HMAC signing
    was introduced (e.g. existing SQLite job rows).

    Args:
        data: Bytes containing HMAC signature followed by pickle data, or legacy pickle
        expected_type: Optional type to verify after deserialization

    Returns:
        Deserialized object

    Raises:
        ValueError: If signature is invalid or data is too short / not pickle
        TypeError: If deserialized object doesn't match expected_type
    """
    if len(data) >= 32:
        valid, payload = _hmac_signature_valid(data)
        if valid:
            return _finalize_loaded(pickle.loads(payload), expected_type)

    if _looks_like_pickle_payload(data):
        warnings.warn(
            "Loading legacy unsigned protocol pickle blob; re-save via "
            "PauliAveragingProtocol.dumps() to upgrade to HMAC-signed format.",
            DeprecationWarning,
            stacklevel=2,
        )
        _log.debug("secure_loads: legacy unsigned pickle (%d bytes)", len(data))
        return _finalize_loaded(pickle.loads(data), expected_type)

    if len(data) >= 32:
        raise ValueError("Invalid HMAC signature - data may have been tampered with")

    raise ValueError("Data too short to contain valid HMAC signature or legacy pickle payload")


def secure_dumps_protocol(proto: PauliAveragingProtocol) -> bytes:
    """Serialize PauliAveragingProtocol with HMAC signature."""
    return secure_dumps(proto)


def secure_loads_protocol(data: bytes) -> PauliAveragingProtocol:
    """Deserialize PauliAveragingProtocol with HMAC signature verification."""
    from qchem_stack.protocols.protocol import PauliAveragingProtocol

    return cast("PauliAveragingProtocol", secure_loads(data, expected_type=PauliAveragingProtocol))
