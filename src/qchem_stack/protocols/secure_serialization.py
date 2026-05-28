"""Secure serialization with HMAC signature verification for Protocol objects.

This module provides HMAC-signed pickle serialization to prevent arbitrary code
execution from untrusted pickle payloads.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import pickle
from typing import TYPE_CHECKING, Any

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


def secure_loads(data: bytes, expected_type: type | None = None) -> Any:
    """Deserialize object with HMAC signature verification.

    Args:
        data: Bytes containing HMAC signature followed by pickle data
        expected_type: Optional type to verify after deserialization

    Returns:
        Deserialized object

    Raises:
        ValueError: If signature is invalid or data is too short
        TypeError: If deserialized object doesn't match expected_type
    """
    if len(data) < 32:
        raise ValueError("Data too short to contain valid HMAC signature")

    signature = data[:32]
    payload = data[32:]

    # Verify HMAC signature
    key = _get_hmac_key()
    expected_signature = hmac.new(key, payload, hashlib.sha256).digest()

    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid HMAC signature - data may have been tampered with")

    obj = pickle.loads(payload)

    if expected_type is not None and not isinstance(obj, expected_type):
        raise TypeError(
            f"Deserialized object is {type(obj).__name__}, expected {expected_type.__name__}"
        )

    return obj


def secure_dumps_protocol(proto: PauliAveragingProtocol) -> bytes:
    """Serialize PauliAveragingProtocol with HMAC signature."""
    return secure_dumps(proto)


def secure_loads_protocol(data: bytes) -> PauliAveragingProtocol:
    """Deserialize PauliAveragingProtocol with HMAC signature verification."""
    from qchem_stack.protocols.protocol import PauliAveragingProtocol

    return secure_loads(data, expected_type=PauliAveragingProtocol)
