# QPE / QEC demo track (L1 open analog)

This package implements a **documentation-aligned**, **non–vendor-binary** analog of InQuanto’s QPE / Bayesian-QPE **naming and repro hooks** (see [与InQuanto能力差距与实施计划 — 附录 D](../../docs/与InQuanto能力差距与实施计划.md) **序 C7 / C14** and [inquanto_public_parity_matrix.md](../../docs/inquanto_public_parity_matrix.md) §2).

## Public entry points

| Symbol | Role |
|--------|------|
| `BayesianQPEStub` (`bayesian_stub.py`) | **AlgorithmBayesianQPE** / Phayes-shaped **toy** MAP phase on a grid (not Phayes). |
| `kitaev_qpe_energy_estimate` (`kitaev.py`) | Dense / Kitaev-style phase-energy helper for demos. |
| `FaultTolerantDemoAdapter` (`adapter.py`) | Light adapter boundary toward heavier QEC stacks (optional). |

## Repro / parity keys (pipeline)

When `quantum.qpe_demo_track_after_variational: true` **or** `quantum.qpe_pipeline_integration: true`:

Implementation lives in `pipeline_track.py` (`qpe_demo_track_payload`), shared with `scripts/run_qpe_track_demo.py`. Register width is **`quantum.qpe_demo_track_n_bits`** (default **4**, minimum **2**); the main pipeline passes it into `qpe_demo_track_payload`.

- **`out["qpe_demo_track"]`**: merged demo blob (Kitaev-style block + optional `bayesian_phase_map_toy` from the stub).
- **`repro.run_summary.qpe_demo_track_ran`**: boolean flag for Methods tables.

Packaged YAML: `configs/example_h2_qpe_track.yaml` (Pauli-on chain); **`configs/example_h2_qpe_track_parity_integrations.yaml`** (same + `parity_integrations` / TKET probe for `methods_resource_unified_v1`); **`configs/qpe_dual_track_demo.yaml`** (variational-only + integration flag). Export merge keys include `qpe_demo_track_from_run`, `qpe_demo_track_ran_from_run_summary` (see `scripts/export_parity_criteria_table.py`).

## Tests

- `tests/test_l1_phase_c_iqeb_bayesian.py` — `BayesianQPEStub.estimate` smoke.
- Orchestration / QPE track: `tests/test_orchestration_pipeline.py`, `scripts/run_qpe_track_demo.py`.

**Status**: `partial` vs closed-source InQuanto — L1 naming + JSON only, not numerical parity with vendor stacks.

## P1 演示轨 vs P2 深度（边界）

- **P1（已验收）**：`qpe_demo_track` + `run_summary.qpe_demo_track_ran` + `export_parity_criteria_table` 的 `qpe_*_from_run` / `methods_resource_unified_v1`（见上 YAML 表）；可选 TKET 探针见 `example_h2_qpe_track_parity_integrations.yaml`。  
- **P2（进行中）**：超出 demo 的 **resource estimation** 可选叙事见 export 顶键 **`resource_estimation_preview_v1`**（`parity_integrations.resource_estimation_preview: true` 时）；**不**宣称云计价或闭源资源估计 L0。双月周历见 [与InQuanto能力差距与实施计划 — 附录 A](../../docs/与InQuanto能力差距与实施计划.md) 内 `### 8.`。
