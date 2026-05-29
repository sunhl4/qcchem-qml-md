"""``qchem_stack.orchestration`` public ``__all__`` resolves without import cycles."""

from __future__ import annotations

import importlib


def test_orchestration_public_all_importable() -> None:
    mod = importlib.import_module("qchem_stack.orchestration")
    missing: list[str] = []
    for name in mod.__all__:
        try:
            getattr(mod, name)
        except Exception as exc:  # noqa: BLE001 — surface contract
            missing.append(f"{name}: {exc}")
    assert not missing, "failed orchestration.__all__ imports:\n" + "\n".join(missing)
