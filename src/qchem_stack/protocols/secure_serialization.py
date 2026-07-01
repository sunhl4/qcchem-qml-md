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


def _get_hmac_key() -> bytes:
    """Get HMAC key from environment variable.

    Raises:
        ConfigurationError: If QCHEM_PROTOCOL_HMAC_KEY is not set.
    """
    key_str = os.environ.get("QCHEM_PROTOCOL_HMAC_KEY")
    if not key_str:
        from qchem_stack.exceptions import ConfigurationError

        raise ConfigurationError(
            "QCHEM_PROTOCOL_HMAC_KEY environment variable is required for protocol serialization. "
            "Set this to a 32+ byte random key for production use."
        )
    return key_str.encode("utf-8")


def secure_dumps(obj: Any) -> bytes:
    """Serialize object with pickle and add HMAC signature.

    Format: [32-byte HMAC signature][pickle data]

    Args:
        obj: Object to serialize

    Returns:
        Bytes containing HMAC signature followed by pickle data
    """
    data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
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


def _finalize_loaded(obj: Any, expected_type: type | None) -> Any:
    if expected_type is not None and not isinstance(obj, expected_type):
        raise TypeError(
            f"Deserialized object is {type(obj).__name__}, expected {expected_type.__name__}"
        )
    return obj


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

    valid, payload = _hmac_signature_valid(data)
    if not valid:
        raise ValueError("Invalid HMAC signature - data may have been tampered with")

    return _finalize_loaded(pickle.loads(payload), expected_type)


def _protocol_blob_v2_enabled() -> bool:
    raw = os.environ.get("QCHEM_PROTOCOL_BLOB_V2", "1")
    return str(raw).lower() not in {"0", "false", "no", "off"}


def _signed_payload(data: bytes) -> bytes:
    key = _get_hmac_key()
    signature = hmac.new(key, data, hashlib.sha256).digest()
    return signature + data


def secure_dumps_protocol(proto: PauliAveragingProtocol) -> bytes:
    """Serialize PauliAveragingProtocol with HMAC signature (pickle v1 or JSON v2)."""
    if _protocol_blob_v2_enabled():
        from qchem_stack.protocols.protocol_v2_document import protocol_v2_dumps

        return _signed_payload(protocol_v2_dumps(proto))
    return secure_dumps(proto)


def _legacy_pickle_allowed() -> bool:
    return os.environ.get("QCHEM_ALLOW_LEGACY_PICKLE", "").lower() in {"1", "true", "yes", "on"}


def secure_loads_protocol(data: bytes) -> PauliAveragingProtocol:
    """Deserialize PauliAveragingProtocol (HMAC JSON v2 or signed pickle v1)."""
    from qchem_stack.exceptions import JobPayloadError
    from qchem_stack.protocols.protocol import PauliAveragingProtocol
    from qchem_stack.protocols.protocol_v2_document import (
        is_protocol_v2_json_payload,
        protocol_v2_loads,
    )

    if len(data) >= 32:
        valid, payload = _hmac_signature_valid(data)
        if valid and is_protocol_v2_json_payload(payload):
            return protocol_v2_loads(payload)

    if is_protocol_v2_json_payload(data):
        return protocol_v2_loads(data)

    if data[:1] == b"\x80":
        if not _legacy_pickle_allowed():
            raise JobPayloadError(
                "Legacy unsigned pickle protocol blobs are disabled by default. "
                "Set QCHEM_ALLOW_LEGACY_PICKLE=1 only during one-time migration, "
                "then re-save jobs as HMAC-signed JSON v2."
            )
        warnings.warn(
            "Loading unsigned legacy pickle protocol blob; migrate with "
            "scripts/migrate_job_protocol_blobs.py and unset QCHEM_ALLOW_LEGACY_PICKLE.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cast(
            "PauliAveragingProtocol",
            _finalize_loaded(pickle.loads(data), PauliAveragingProtocol),
        )

    return cast("PauliAveragingProtocol", secure_loads(data, expected_type=PauliAveragingProtocol))
