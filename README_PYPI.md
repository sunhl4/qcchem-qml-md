# qchem-stack

**Stable 1.1** open orchestration for quantum chemistry: YAML pipelines, strict
`repro` JSON, Methods-style parity export, and optional MD bridge.

Non-goals (no commercial cloud parity): see the repository
`docs/product/non_goals.md`.

## Quick start

```bash
pip install "qchem-stack[chem,quantum]"
qchem-run --scenario minimal_vqe --json-summary
```

Example YAML configs ship under `share/qchem-stack/configs` in the wheel. Override
with `QCHEM_STACK_CONFIGS_DIR` or clone the repository for the full `configs/` tree.

```python
from qchem_stack.sdk import load_experiment_config, run_pipeline_from_config
from qchem_stack.config.config_paths import default_configs_dir

cfg_path = default_configs_dir() / "example_h2.yaml"
out = run_pipeline_from_config(cfg_path)
print(out["scf_energy"], out.get("energy_pauli_protocol"))
```

Pick a starter YAML by scenario:

```bash
qchem-run --list-scenarios
qchem-run --scenario minimal_vqe
```

## Install profiles (pip extras)

| Profile | Command | Use when |
|---------|---------|----------|
| **core** | `pip install qchem-stack` | Config models, repro export, bundled scenario YAMLs |
| **chemistry** | `pip install "qchem-stack[chem]"` | PySCF classical chemistry |
| **quantum** | `pip install "qchem-stack[chem,quantum]"` | PySCF + Qiskit pipeline runs |
| **maintainer** | `pip install -e ".[dev]"` from checkout | Full CI parity, all 105+ YAMLs, scripts |

Optional extras:

| Extra | Command | Use when |
|-------|---------|----------|
| **api** | `pip install "qchem-stack[api]"` | FastAPI job server |
| **uqc** | `pip install "qchem-stack[uqc]"` + `pip install -e packages/qchem-stack-uqc` | UQC cloud backend plugin |
| **pytket** | `pip install "qchem-stack[pytket]"` | TKET compile metrics probe |
| **qmlff** | sibling QML-FF editable + `pip install "qchem-stack[qmlff]"` | JAX-MD active-learning loop (not on PyPI) |

## Stable SDK facade

```python
from qchem_stack.sdk import (
    load_experiment_config,
    run_pipeline_from_config,
    workflow_preview_payload,
    repro_json_dumps,
    list_scenarios_text,
)
from qchem_stack.config.config_paths import default_configs_dir

preview = workflow_preview_payload(
    load_experiment_config(default_configs_dir() / "example_h2.yaml")
)
```

CLI: `qchem-run`, `qchem-export-parity`.

## Documentation

- Docs site: https://sunhl4.github.io/qcchem-qml-md/
- Repository guides: https://github.com/sunhl4/qcchem-qml-md/tree/main/docs
- Onboarding (three paths): `docusaurus-site/docs/tutorial/tutorial-index-three-paths.md`
- Release process: `docs/engineering/pypi_release.md`
- Contributor quick start: `docs/QUICKSTART_CONTRIBUTORS.md`

## HTTP API (optional)

```bash
pip install "qchem-stack[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## License

Apache-2.0
