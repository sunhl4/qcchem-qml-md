"""
Strict JSON conversion for ``out['repro']`` (and nested snapshots).

Enterprise exports should not rely on ``json.dumps(..., default=str)``, which hides type bugs.
Use :func:`repro_json_dumps` or :func:`repro_dict_for_strict_json` before persistence or HTTP APIs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from qchem_stack.exceptions import ReproExportError

try:
    import numpy as _np
except ImportError:  # pragma: no cover - optional dependency
    _np = None  # type: ignore[assignment]

_NP_GENERIC_TYPE = _np.generic if _np is not None else ()
_NP_ARRAY_TYPE = _np.ndarray if _np is not None else ()


def repro_dict_for_strict_json(repro: dict[str, Any], *, _path: str = "$") -> dict[str, Any]:
    """
    Return a deep structure using only JSON-native types.

    Raises
    ------
    ReproExportError
        On unsupported types, non-finite floats, or cyclic structures.
    """
    seen: set[int] = set()
    out = _to_json_serializable(repro, path=_path, _seen=seen)
    if not isinstance(out, dict):
        raise ReproExportError("top-level repro must serialize to a JSON object")
    return out


def repro_json_dumps(
    repro: dict[str, Any],
    *,
    indent: int | None = None,
    ensure_ascii: bool = False,
) -> str:
    """Stable UTF-8 JSON text with no NaN/Infinity (RFC-compliant ``allow_nan=False``)."""
    safe = repro_dict_for_strict_json(repro)
    return json.dumps(
        safe, indent=indent, ensure_ascii=ensure_ascii, allow_nan=False, sort_keys=False
    )


def _to_json_serializable(obj: Any, *, path: str, _seen: set[int]) -> Any:
    if isinstance(obj, dict):
        oid = id(obj)
        if oid in _seen:
            raise ReproExportError(f"repro contains a cycle at {path}")
        _seen.add(oid)
        try:
            return {
                str(k): _to_json_serializable(v, path=f"{path}.{k}", _seen=_seen)
                for k, v in obj.items()
            }
        finally:
            _seen.discard(oid)

    if isinstance(obj, (list, tuple)):
        oid = id(obj)
        if oid in _seen:
            raise ReproExportError(f"repro contains a cycle at {path}")
        _seen.add(oid)
        try:
            return [
                _to_json_serializable(v, path=f"{path}[{i}]", _seen=_seen)
                for i, v in enumerate(obj)
            ]
        finally:
            _seen.discard(oid)

    if obj is None or isinstance(obj, str):
        return obj
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ReproExportError(f"non-finite float at {path}")
        return float(obj)
    if isinstance(obj, Path):
        return str(obj)

    if _np is not None:
        if isinstance(obj, _NP_GENERIC_TYPE):
            return _to_json_serializable(obj.item(), path=path, _seen=_seen)
        if isinstance(obj, _NP_ARRAY_TYPE):
            return _to_json_serializable(obj.tolist(), path=path, _seen=_seen)

    raise ReproExportError(f"unsupported type {type(obj).__name__} at {path}")
