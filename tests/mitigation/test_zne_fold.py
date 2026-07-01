"""Unit tests for ZNE circuit folding helpers."""

from __future__ import annotations

import pytest

from qchem_stack.mitigation.zne_fold import fold_gates_local, fold_unitary_circuit, zne_scale_energy


class _MiniGate:
    def __init__(self, name: str) -> None:
        self.name = name

    def inverse(self) -> _MiniGate:
        return _MiniGate(f"{self.name}_inv")


class _MiniCircuit:
    def __init__(self, label: str = "U") -> None:
        self.label = label
        self.data: list[_MiniGate] = [_MiniGate("G")]

    def copy(self) -> _MiniCircuit:
        c = _MiniCircuit(self.label)
        c.data = list(self.data)
        return c

    def inverse(self) -> _MiniCircuit:
        return _MiniCircuit(f"{self.label}_dag")

    def compose(self, other: _MiniCircuit) -> _MiniCircuit:
        out = _MiniCircuit(f"{self.label}*{other.label}")
        out.data = list(self.data)
        return out


def test_zne_scale_energy_stub() -> None:
    assert zne_scale_energy(1.0, 1.0) == pytest.approx(1.0)
    assert zne_scale_energy(1.0, 3.0) == pytest.approx(1.02)


def test_fold_unitary_circuit_zero_folds() -> None:
    c = _MiniCircuit()
    assert fold_unitary_circuit(c, 0) is c


def test_fold_unitary_circuit_negative_folds_raises() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        fold_unitary_circuit(_MiniCircuit(), -1)


def test_fold_gates_local_identity_scale() -> None:
    c = _MiniCircuit()
    out = fold_gates_local(c, 1.0)
    assert out.data == c.data


def test_fold_gates_local_invalid_scale() -> None:
    with pytest.raises(ValueError, match=">= 1"):
        fold_gates_local(_MiniCircuit(), 0.5)
