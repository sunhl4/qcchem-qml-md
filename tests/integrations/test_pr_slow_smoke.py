"""PR slow smoke: precomputed pipeline → strict repro export (no PySCF)."""

from __future__ import annotations

import pytest

from qchem_stack.orchestration.pipeline import run_pipeline_from_config
from qchem_stack.repro.export import repro_json_dumps
from tests.helpers.paths import configs_path

pytestmark = pytest.mark.slow


def test_precomputed_pipeline_repro_export_roundtrip() -> None:
    cfg = configs_path("example_h2_precomputed_bundle.yaml")
    if not cfg.is_file():
        pytest.skip("precomputed fixture config missing")
    out = run_pipeline_from_config(str(cfg))
    repro = out.get("repro")
    assert isinstance(repro, dict)
    dumped = repro_json_dumps(repro)
    assert "hamiltonian_fingerprint" in dumped or "run_context" in dumped
