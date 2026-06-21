from __future__ import annotations

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.chem.classical_benchmarks import (
    ClassicalBenchmarkContext,
    run_classical_post_hf_benchmarks,
)
from qchem_stack.chem.classical_benchmarks.schema import CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import classical_reference_from_config


def _h2_cfg_yaml() -> str:
    return """
schema_version: "2"
experiment_id: h2_bench
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
"""


def test_classical_benchmarks_payload_shape(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    ref = classical_reference_from_config(cfg)
    ctx = ClassicalBenchmarkContext(
        mean_field_reference=ref,
        reference_scf_method=str(cfg.scf.method),
        n_active_orbitals=2,
        n_active_electrons=2,
    )
    res = run_classical_post_hf_benchmarks(cfg, ctx)
    assert res.get("schema") == CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1
    assert res.get("backend_id") == "pyscf"
    for k in ("hf", "mp2", "ccsd", "casci"):
        assert isinstance(res.get(k), dict)
        assert "status" in res[k]
        assert "value" in res[k]
        assert "reason" in res[k]
    assert res["hf"]["status"] == "ok"


def test_classical_benchmarks_casci_unavailable_without_active_space(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    ctx = ClassicalBenchmarkContext(
        mean_field_reference=None,
        reference_scf_method=str(cfg.scf.method),
    )
    res = run_classical_post_hf_benchmarks(cfg, ctx)
    assert res["casci"]["status"] == "unavailable"
