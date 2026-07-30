"""Strict repro JSON export (no NaN, no silent str coercion)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qchem_stack.exceptions import ReproExportError
from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps


def test_repro_json_round_trip_plain() -> None:
    r = {"a": 1, "b": [2, 3], "c": {"d": "x"}, "ok": True, "n": None}
    text = repro_json_dumps(r)
    assert json.loads(text) == r


def test_repro_json_dumps_indent_and_ensure_ascii() -> None:
    text = repro_json_dumps({"msg": "café", "v": 1}, indent=2, ensure_ascii=True)
    assert '"msg"' in text
    assert "\\u" in text
    assert json.loads(text) == {"msg": "café", "v": 1}


def test_repro_dict_bool_tuple_and_path() -> None:
    out = repro_dict_for_strict_json(
        {
            "flag": False,
            "pair": (1, "x"),
            "p": Path("/tmp/x"),
        }
    )
    assert out == {"flag": False, "pair": [1, "x"], "p": "/tmp/x"}


def test_repro_rejects_nan() -> None:
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"x": float("nan")})


@pytest.mark.parametrize("bad", [float("inf"), float("-inf")])
def test_repro_rejects_infinity(bad: float) -> None:
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"x": bad})


def test_repro_rejects_cycle() -> None:
    d: dict = {"a": 1}
    d["self"] = d
    with pytest.raises(ReproExportError, match="cycle"):
        repro_dict_for_strict_json(d)


def test_repro_rejects_list_cycle() -> None:
    lst: list = [1]
    lst.append(lst)
    with pytest.raises(ReproExportError, match="cycle"):
        repro_dict_for_strict_json({"items": lst})


def test_repro_numpy_scalar_if_available() -> None:
    np = pytest.importorskip("numpy")
    # float64 subclasses float and is handled by the finite-float branch
    out = repro_dict_for_strict_json({"q": np.float64(1.5)})
    assert out["q"] == 1.5
    # datetime64 is np.generic but not a Python float/int — exercises .item() path
    with pytest.raises(ReproExportError, match="unsupported"):
        repro_dict_for_strict_json({"t": np.datetime64("2020-01-01")})


def test_repro_numpy_array_if_available() -> None:
    np = pytest.importorskip("numpy")
    out = repro_dict_for_strict_json({"arr": np.array([1.0, 2.0])})
    assert out["arr"] == [1.0, 2.0]


def test_repro_unsupported_type() -> None:
    class Opaque:
        pass

    with pytest.raises(ReproExportError, match="unsupported"):
        repro_dict_for_strict_json({"x": Opaque()})


def test_repro_rejects_non_object_top_level() -> None:
    with pytest.raises(ReproExportError, match="top-level repro must serialize"):
        repro_dict_for_strict_json([])  # type: ignore[arg-type]
