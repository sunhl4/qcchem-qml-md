"""L1 phase D (序 17): Projection embedding config surface."""

from __future__ import annotations

from qchem_stack.chem.embedding.projection import ProjectionEmbeddingConfig


def test_projection_embedding_config_defaults() -> None:
    p = ProjectionEmbeddingConfig()
    assert p.low_level == "HF"
    assert p.high_level == "CAS"
    assert p.threshold == 1e-8
