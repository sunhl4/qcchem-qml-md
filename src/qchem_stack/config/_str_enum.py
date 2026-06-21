"""StrEnum shim for Python 3.10 (stdlib StrEnum is 3.11+)."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from typing_extensions import StrEnum

__all__ = ["StrEnum"]
