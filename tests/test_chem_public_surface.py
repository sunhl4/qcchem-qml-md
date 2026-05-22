"""``qchem_stack.chem`` public ``__all__`` resolves without import cycles."""

from __future__ import annotations

import importlib

import pytest


def test_chem_public_all_importable() -> None:
    chem = importlib.import_module("qchem_stack.chem")
    missing: list[str] = []
    for name in chem.__all__:
        try:
            getattr(chem, name)
        except Exception as exc:  # noqa: BLE001 — surface contract
            missing.append(f"{name}: {exc}")
    assert not missing, "failed chem.__all__ imports:\n" + "\n".join(missing)


@pytest.mark.parametrize(
    "subpackage",
    [
        "bridges",
        "solvers",
        "integrals",
        "classical_benchmarks",
        "integration",
        "active_space",
        "embedding",
        "systems",
        "kernels",
        "drivers",
    ],
)
def test_chem_subpackage_all_importable(subpackage: str) -> None:
    mod = importlib.import_module(f"qchem_stack.chem.{subpackage}")
    if not hasattr(mod, "__all__"):
        pytest.skip(f"no __all__ on chem.{subpackage}")
    missing: list[str] = []
    for name in mod.__all__:
        try:
            getattr(mod, name)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{name}: {exc}")
    assert not missing, f"failed chem.{subpackage}.__all__ imports:\n" + "\n".join(missing)
