"""Strict repro JSON export (no NaN, no silent str coercion)."""

from __future__ import annotations

import json

import pytest

from qchem_stack.exceptions import ReproExportError
from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps


def test_repro_json_round_trip_plain() -> None:
    r = {"a": 1, "b": [2, 3], "c": {"d": "x"}}
    text = repro_json_dumps(r)
    assert json.loads(text) == r


def test_repro_rejects_nan() -> None:
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"x": float("nan")})


def test_repro_rejects_cycle() -> None:
    d: dict = {"a": 1}
    d["self"] = d
    with pytest.raises(ReproExportError, match="cycle"):
        repro_dict_for_strict_json(d)


def test_repro_numpy_scalar_if_available() -> None:
    np = pytest.importorskip("numpy")
    out = repro_dict_for_strict_json({"q": np.float64(1.5)})
    assert out["q"] == 1.5


def test_repro_unsupported_type() -> None:
    class Opaque:
        pass

    with pytest.raises(ReproExportError, match="unsupported"):
        repro_dict_for_strict_json({"x": Opaque()})
