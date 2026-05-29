"""UCCGD and QCC variational ansatz smoke tests on H2 sto-3g."""

from __future__ import annotations

import math

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.h2_yaml import H2_STO3G_FCI_ENERGY
from tests.helpers.paths import configs_path


@pytest.mark.parametrize(
    "config_rel",
    ["example_h2_uccgd.yaml", "example_h2_qcc.yaml"],
)
def test_uccgd_qcc_yaml_energy_window(config_rel: str) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    e = float(out["energy_after_variational"])
    assert e < -0.5
    assert e >= H2_STO3G_FCI_ENERGY - 0.05
    meta = (out.get("algorithm_report") or {}).get("meta") or {}
    ansatz = meta.get("variational_ansatz") or cfg.quantum.variational.ansatz
    assert ansatz in ("uccgd", "qcc")
    assert math.isfinite(e)


def test_scbk_hea_pipeline_runs() -> None:
    p = configs_path("example_h2_scbk_hea.yaml")
    if not p.is_file():
        pytest.skip("example_h2_scbk_hea.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    snap = out["repro"]["parity_snapshot"]
    assert snap["hamiltonian_meta"]["fermion_to_qubit_map"] == "symmetry_conserving_bravyi_kitaev"
    assert math.isfinite(float(out["energy_after_variational"]))
