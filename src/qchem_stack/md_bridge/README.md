# `qchem_stack.md_bridge`

MD/ML active-learning and QMEF (quantum mechanics energy fingerprint) integration.

## Install tiers (pick one)

| Tier | Install | MD loop backend |
|------|---------|-----------------|
| **core** | `pip install -e .` | Not available (import `md_bridge` only for types) |
| **classical_h2** | `pip install -e ".[dev]"` (no QML-FF) | `force_field_backend: classical_h2` in YAML — full CI path |
| **full qmlff** | editable **QML-FF** sibling + `pip install -e ".[qmlff]"` | `qmlff` / `qnn` presets in `configs/example_h2_qmlff_md.yaml` |

Without QML-FF, use `configs/example_h4_classical_md_stub.yaml` or `example_h2_classical_md.yaml` for MD validation demos.

## Capabilities

- **QMEFDataset** — attach pipeline energies/trajectories for downstream ML (`md_bridge/contracts.py`)
- **MD validation loop** — multi-round force-field refinement (`md_validation_loop.py`, `md_loop_rounds.py`)
- **QML-FF / JAX-MD** — optional sibling install (`pip install -e /path/to/QML-FF` + `pip install qchem-stack[qmlff]`)

## Example configs

| Config | Schema |
|--------|--------|
| `configs/example_h2_qmlff_md.yaml` | MdValidationLoopConfig |
| `configs/example_h2_uqc_mock_md_ml.yaml` | ExperimentConfig + MD/ML |
| `configs/example_h2_md_ml_trajectory_full_pipeline.yaml` | ExperimentConfig |

## Entry points

- `run_md_validation_loop` — `md_bridge/md_validation_loop.py`
- `run_jaxmd_trajectory` — `md_bridge/qmlff_md.py`
- HTTP façade — `md_bridge/http_surface.py` (when `qchem-stack[api]` installed)

Former `qchem_stack.ml` stub was removed; use this package only.
