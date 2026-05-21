"""Five-stage Pauli averaging protocol phase discriminator."""

from __future__ import annotations

from enum import Enum


class ProtocolPhase(str, Enum):
    INSTANTIATE = "instantiate"
    BUILD = "build"
    COMPILE = "compile"
    RUN = "run"
    EVALUATE = "evaluate"
