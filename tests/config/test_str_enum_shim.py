"""Python 3.10-compatible StrEnum shim."""

from __future__ import annotations

from qchem_stack.config._str_enum import StrEnum
from qchem_stack.config.embedding_enums import EmbeddingMode


def test_str_enum_shim_embedding_mode() -> None:
    assert EmbeddingMode.NONE == "none"
    assert issubclass(EmbeddingMode, StrEnum)
