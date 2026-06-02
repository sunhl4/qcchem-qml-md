"""
Property-based tests for configuration serialization roundtrip.

Uses Hypothesis to verify that:
1. Finite floats survive JSON roundtrip
2. YAML keys survive serialization
3. Configuration values remain lossless through serialization
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps

# Strategy for finite floats (excluding NaN, inf, -inf)
finite_floats = st.floats(allow_nan=False, allow_infinity=False, width=64)

# Strategy for valid YAML keys (strings that don't contain problematic characters)
yaml_keys = st.text(
    alphabet=st.characters(
        blacklist_categories=["Cs", "Cn"],  # Exclude surrogates and unassigned
        blacklist_characters=["\x00", "\n", "\r"],  # Exclude null, newlines
    ),
    min_size=1,
    max_size=100,
)


@composite
def repro_dict_strategy(draw):
    """Generate random repro dictionaries with JSON-serializable values."""
    num_keys = draw(st.integers(min_value=1, max_value=10))
    keys = draw(st.lists(yaml_keys, min_size=num_keys, max_size=num_keys, unique=True))

    result = {}
    for key in keys:
        value_type = draw(st.sampled_from(["float", "int", "str", "list", "nested"]))

        if value_type == "float":
            result[key] = draw(finite_floats)
        elif value_type == "int":
            result[key] = draw(st.integers(min_value=-1e9, max_value=1e9))
        elif value_type == "str":
            result[key] = draw(st.text(min_size=0, max_size=200))
        elif value_type == "list":
            list_len = draw(st.integers(min_value=0, max_value=5))
            result[key] = [draw(finite_floats) for _ in range(list_len)]
        else:  # nested
            nested_key = draw(yaml_keys)
            result[key] = {nested_key: draw(finite_floats)}

    return result


@given(finite_floats)
def test_finite_float_json_roundtrip(value: float):
    """Verify finite floats survive JSON roundtrip without loss."""
    # Skip very large/small values that might lose precision
    assume(abs(value) < 1e308 and (abs(value) > 1e-308 or value == 0.0))

    repro = {"test_value": value}
    safe = repro_dict_for_strict_json(repro)
    json_str = json.dumps(safe, allow_nan=False)
    restored = json.loads(json_str)

    # Check that the value survived roundtrip
    restored_value = restored["test_value"]

    # For very small values near zero, allow some tolerance
    if abs(value) < 1e-15:
        assert abs(restored_value - value) < 1e-15 or restored_value == value
    else:
        # For normal values, check relative precision
        if value != 0:
            relative_error = abs((restored_value - value) / value)
            assert relative_error < 1e-10, f"Relative error {relative_error} too large"
        else:
            assert restored_value == 0.0


@given(yaml_keys)
def test_yaml_key_survives_serialization(key: str):
    """Verify YAML keys survive JSON serialization."""
    assume(len(key.strip()) > 0)  # Skip whitespace-only keys

    repro = {key: "test_value"}
    safe = repro_dict_for_strict_json(repro)
    json_str = json.dumps(safe, ensure_ascii=False)
    restored = json.loads(json_str)

    # The key should survive roundtrip (possibly converted to string)
    assert str(key) in restored or key in restored


@given(repro_dict_strategy())
def test_repro_dict_roundtrip(repro: dict):
    """Verify repro dictionaries survive JSON roundtrip."""
    repro_dict_for_strict_json(repro)
    json_str = repro_json_dumps(repro)
    restored = json.loads(json_str)

    # Check structure is preserved
    def check_structure(orig, rest, path="$"):
        if isinstance(orig, dict):
            assert isinstance(rest, dict), f"Dict at {path} became {type(rest)}"
            for key in orig:
                assert str(key) in rest, f"Key {key} missing at {path}"
                check_structure(orig[key], rest[str(key)], f"{path}.{key}")
        elif isinstance(orig, list):
            assert isinstance(rest, list), f"List at {path} became {type(rest)}"
            assert len(orig) == len(rest), f"List length mismatch at {path}"
            for i, (o, r) in enumerate(zip(orig, rest, strict=True)):
                check_structure(o, r, f"{path}[{i}]")
        elif isinstance(orig, float):
            # Allow small floating point differences
            if abs(orig) < 1e-15:
                assert abs(rest - orig) < 1e-15 or rest == orig
            elif orig != 0:
                relative_error = abs((rest - orig) / orig)
                assert relative_error < 1e-10, f"Float precision loss at {path}"
        elif isinstance(orig, (int, str, bool)):
            assert orig == rest, f"Value mismatch at {path}: {orig} != {rest}"
        # None should remain None
        elif orig is None:
            assert rest is None, f"None became {rest} at {path}"

    check_structure(repro, restored)


def test_repro_rejects_non_finite_float():
    """Verify that non-finite floats are rejected."""
    from qchem_stack.exceptions import ReproExportError

    # Test NaN
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"bad": float("nan")})

    # Test positive infinity
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"bad": float("inf")})

    # Test negative infinity
    with pytest.raises(ReproExportError, match="non-finite"):
        repro_dict_for_strict_json({"bad": float("-inf")})


def test_repro_handles_numpy_types():
    """Verify numpy types are converted correctly."""
    import numpy as np

    repro = {
        "array": np.array([1.0, 2.0, 3.0]),
        "scalar": np.float64(42.5),
        "int": np.int32(100),
    }

    repro_dict_for_strict_json(repro)
    json_str = repro_json_dumps(repro)
    restored = json.loads(json_str)

    assert restored["array"] == [1.0, 2.0, 3.0]
    assert restored["scalar"] == 42.5
    assert restored["int"] == 100


def test_repro_handles_path_objects():
    """Verify Path objects are converted to strings."""
    repro = {
        "config_path": Path("/path/to/config.yaml"),
        "data_dir": Path("relative/path"),
    }

    repro_dict_for_strict_json(repro)
    json_str = repro_json_dumps(repro)
    restored = json.loads(json_str)

    assert restored["config_path"] == "/path/to/config.yaml"
    assert restored["data_dir"] == "relative/path"


def test_repro_detects_cycles():
    """Verify circular references are detected."""
    from qchem_stack.exceptions import ReproExportError

    # Create a cycle
    repro = {"key": "value"}
    repro["self"] = repro

    with pytest.raises(ReproExportError, match="cycle"):
        repro_dict_for_strict_json(repro)
