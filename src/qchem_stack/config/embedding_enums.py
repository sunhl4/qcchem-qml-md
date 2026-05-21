"""String enums for embedding configuration (YAML-serializable)."""

from __future__ import annotations

from enum import StrEnum


class EmbeddingMode(StrEnum):
    NONE = "none"
    DMET = "dmet"
    PROJECTION = "projection"
    PLUGIN = "plugin"


class EmbeddingInputRepresentation(StrEnum):
    MO = "mo"
    AO = "ao"
    LOWDIN_ORTH_AO = "lowdin_orth_ao"


class DmetHamiltonianSource(StrEnum):
    PARITY_STUB = "parity_stub"
    WHOLE_ACTIVE_SYSTEM = "whole_active_system"
    SCHMIDT_ATOMIC_PRODUCTION = "schmidt_atomic_production"


class ProjectionQuantumHamiltonian(StrEnum):
    GLOBAL_ACTIVE_SPACE = "global_active_space"
    FRAGMENT_MULLIKEN_MO = "fragment_mulliken_mo"
