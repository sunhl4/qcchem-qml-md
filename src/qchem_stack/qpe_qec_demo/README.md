# QPE / QEC demo track (L1 open analog)

This package implements a **documentation-aligned**, **non–vendor-binary** analog of InQuanto’s QPE / Bayesian-QPE **naming and repro hooks** (see [InQuanto_B_J_逐项闭合计划.md](../../docs/InQuanto_B_J_逐项闭合计划.md) **序 C7 / C14** and [inquanto_public_parity_matrix.md](../../docs/inquanto_public_parity_matrix.md) §2).

## Public entry points

| Symbol | Role |
|--------|------|
| `BayesianQPEStub` (`bayesian_stub.py`) | **AlgorithmBayesianQPE** / Phayes-shaped **toy** MAP phase on a grid (not Phayes). |
| `kitaev_qpe_energy_estimate` (`kitaev.py`) | Dense / Kitaev-style phase-energy helper for demos. |
| `FaultTolerantDemoAdapter` (`adapter.py`) | Light adapter boundary toward heavier QEC stacks (optional). |

## Repro / parity keys (pipeline)

When `quantum.qpe_demo_track_after_variational: true`:

- **`out["qpe_demo_track"]`**: merged demo blob (Kitaev-style block + optional `bayesian_phase_map_toy` from the stub).
- **`repro.run_summary.qpe_demo_track_ran`**: boolean flag for Methods tables.

Packaged YAML: `configs/example_h2_qpe_track.yaml`. Export merge keys include `qpe_demo_track_from_run`, `qpe_demo_track_ran_from_run_summary` (see `scripts/export_parity_criteria_table.py`).

## Tests

- `tests/test_l1_phase_c_iqeb_bayesian.py` — `BayesianQPEStub.estimate` smoke.
- Orchestration / QPE track: `tests/test_orchestration_pipeline.py`, `scripts/run_qpe_track_demo.py`.

**Status**: `partial` vs closed-source InQuanto — L1 naming + JSON only, not numerical parity with vendor stacks.
