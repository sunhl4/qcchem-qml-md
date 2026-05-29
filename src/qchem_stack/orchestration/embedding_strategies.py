"""Embedding workflow strategy pattern implementations."""

from __future__ import annotations

from qchem_stack.orchestration.embedding_strategy_dmet import (
    DmetStrategy,
    run_dmet_fragment_solve_if_requested,
)
from qchem_stack.orchestration.embedding_strategy_none import NoneStrategy
from qchem_stack.orchestration.embedding_strategy_plugin import PluginStrategy
from qchem_stack.orchestration.embedding_strategy_projection import ProjectionStrategy
from qchem_stack.orchestration.embedding_strategy_protocol import EmbeddingStrategy

__all__ = [
    "DmetStrategy",
    "EmbeddingStrategy",
    "NoneStrategy",
    "PluginStrategy",
    "ProjectionStrategy",
    "run_dmet_fragment_solve_if_requested",
]
