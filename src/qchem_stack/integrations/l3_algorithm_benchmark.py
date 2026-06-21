"""Representative pipeline metrics for publication-style tables (optional L3 / CI gate).

``L3_PYTEST_YAMLS`` is the slim set for ``pytest -m l3`` (`QCHEM_RUN_L3=1`); ``DEFAULT_BENCHMARK_YAMLS`` adds
baseline H2 VQE, default IQEB, and QPE dual-track for paper-style ``l3_algorithm_benchmark_report.py`` defaults.

**Increment rules (maintainers)**

- **``L3_PYTEST_YAMLS``**: keep each entry **PySCF-runnable** and **CI-sized** (small molecules); prefer one config per
  distinct algorithm/pool story (baseline VQE, ADAPT pools + YAML aliases, IQEB pools + aliases, excited smoke).
  Update ``tests/test_l3_benchmark_smoke.py`` expectations only via tuple length / schema — no hard-coded counts in docs;
  refresh narrative docs that cite “当前 N 条”.
- **``DEFAULT_BENCHMARK_YAMLS``**: superset for ``scripts/l3_algorithm_benchmark_report.py`` paper tables; may include
  configs **not** in ``L3_PYTEST_YAMLS`` if they add Methods breadth without exploding runtime (review in PR).
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Protocol

from qchem_stack.config import load_experiment_config
from qchem_stack.config.quantum_helpers import (
    resolve_adapt_pool_id,
    resolve_iqeb_pool_id,
    resolve_variational_algorithm,
)
from qchem_stack.contracts.schema_ids import (
    ALGORITHM_BENCHMARK_BUNDLE_V1,
    MERGED_EXPERIMENT_BENCHMARK_V1,
)

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.config import ExperimentConfig


class PipelineSyncRunner(Protocol):
    def __call__(
        self,
        cfg: ExperimentConfig,
        *,
        cfg_path: Path | None = ...,
    ) -> dict[str, object]: ...


DEFAULT_BENCHMARK_YAMLS: tuple[str, ...] = (
    "configs/example_h2.yaml",
    "configs/example_h2_adapt_singles_pool.yaml",
    "configs/example_h2_adapt_doubles_pool.yaml",
    "configs/example_h2_adapt_uccsd_jw_alias.yaml",
    "configs/example_h2_iqeb.yaml",
    "configs/example_h2_iqeb_fermionic_doubles_pool.yaml",
    "configs/example_h2_iqeb_qubit_excitation_alias.yaml",
    "configs/example_h2_excited_smoke.yaml",
    "configs/example_h2_vqd_uccsd.yaml",
    "configs/example_h2_vqd_uccsd_three_computable.yaml",
    "configs/example_h2_uccsd_pauli_protocol.yaml",
    "configs/example_h2_uccsd_qse_pauli_qiskit.yaml",
    "configs/example_h2_uccsd_bk.yaml",
    "configs/example_h2_projection_trace.yaml",
    "configs/example_h2_uccgd.yaml",
    "configs/example_h2_qcc.yaml",
    "configs/example_h2_scbk_hea.yaml",
    "configs/example_h2_sa_vqe.yaml",
    "configs/example_h2_vqd_deflation_circuit.yaml",
    "configs/qpe_dual_track_demo.yaml",
)

L3_PYTEST_YAMLS: tuple[str, ...] = (
    "configs/example_h2.yaml",
    "configs/example_h2_adapt_singles_pool.yaml",
    "configs/example_h2_adapt_doubles_pool.yaml",
    "configs/example_h2_adapt_uccsd_jw_alias.yaml",
    "configs/example_h2_iqeb_fermionic_doubles_pool.yaml",
    "configs/example_h2_iqeb_qubit_excitation_alias.yaml",
    "configs/example_h2_excited_smoke.yaml",
)


def algorithm_benchmark_bundle_v1(
    *,
    repo_root: Path,
    config_rels: list[str],
    run_sync: PipelineSyncRunner | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel in config_rels:
        p = repo_root / rel
        if not p.is_file():
            continue
        if run_sync is None:
            msg = (
                "algorithm_benchmark_bundle_v1 requires run_sync= when config files exist; "
                "inject run_pipeline_sync from scripts or tests."
            )
            raise TypeError(msg)
        t0 = time.perf_counter()
        cfg = load_experiment_config(p)
        exp_id = cfg.experiment_id
        out = run_sync(cfg, cfg_path=p)
        wall_ms = (time.perf_counter() - t0) * 1000.0
        out_row: dict[str, Any] = out if isinstance(out, dict) else dict(out)
        rs = out_row.get("repro", {})
        rs = rs if isinstance(rs, dict) else {}
        run_summary = rs.get("run_summary") or {}
        run_summary = run_summary if isinstance(run_summary, dict) else {}
        nfev_val = out_row.get("nfev")
        nfev = int(nfev_val) if isinstance(nfev_val, int) else None
        row: dict[str, Any] = {
            "experiment_id": exp_id,
            "config_rel": rel,
            "quantum_algorithm_yaml": resolve_variational_algorithm(cfg),
            "adapt_pool_id_yaml": resolve_adapt_pool_id(cfg),
            "iqeb_pool_id_yaml": resolve_iqeb_pool_id(cfg),
            "scf_energy_au": out_row.get("scf_energy"),
            "energy_after_variational_au": out_row.get("energy_after_variational"),
            "nfev": nfev,
            "adapt_total_gradient_evals": run_summary.get("adapt_total_gradient_evals"),
            "wall_time_ms": float(wall_ms),
            "stages_completed_tail": list((run_summary.get("stages_completed") or [])[-5:]),
        }
        rows.append(row)
    return {"schema": ALGORITHM_BENCHMARK_BUNDLE_V1, "rows": rows}


def merged_experiment_benchmark_v1(bundle: dict[str, Any]) -> dict[str, Any]:
    rows_raw = bundle.get("rows")
    rows: list[dict[str, Any]] = (
        [r for r in rows_raw if isinstance(r, dict)] if isinstance(rows_raw, list) else []
    )
    walls = [float(r["wall_time_ms"]) for r in rows if r.get("wall_time_ms") is not None]

    algo_walls: dict[str, list[float]] = {}
    for r in rows:
        algo = r.get("quantum_algorithm_yaml")
        key = algo if isinstance(algo, str) else ""
        wm = r.get("wall_time_ms")
        if wm is None:
            continue
        algo_walls.setdefault(key, []).append(float(wm))

    by_algo: list[dict[str, Any]] = []
    for key in sorted(algo_walls.keys()):
        gw = algo_walls[key]
        by_algo.append(
            {
                "quantum_algorithm_yaml": key or None,
                "n_configs": len(gw),
                "total_wall_time_ms": float(sum(gw)),
                "mean_wall_time_ms": float(sum(gw) / len(gw)) if gw else None,
            }
        )

    return {
        "schema": MERGED_EXPERIMENT_BENCHMARK_V1,
        "n_configs": len(rows),
        "total_wall_time_ms": float(sum(walls)) if walls else None,
        "mean_wall_time_ms": float(sum(walls) / len(walls)) if walls else None,
        "by_quantum_algorithm_yaml": by_algo,
    }
