"""StrEnum shim for Python 3.10 (stdlib enum.StrEnum is 3.11+)."""

from __future__ import annotations

import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """Backport of ``enum.StrEnum`` for Python 3.10.

        Members are strings and ``str(MyEnum.X)`` returns the member's value
        (not ``"MyEnum.X"``), matching the 3.11+ stdlib behavior.
        """

        def __str__(self) -> str:  # pragma: no cover - exercised on 3.10 only
            return str(self.value)

        def _generate_next_value_(self, start, count, last_values):  # type: ignore[override]
            return (
                self.lower()
                if isinstance(self, str)
                else super()._generate_next_value_(start, count, last_values)
            )  # type: ignore[misc]


__all__ = ["StrEnum"]
