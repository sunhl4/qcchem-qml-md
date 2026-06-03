# qchem-stack

Quantum chemistry orchestration: classical downfolding, variational protocols,
reproducible `repro` export, and optional MD bridge.

## Quick start

```bash
pip install "qchem-stack[chem,quantum]"
```

```python
from qchem_stack.sdk import load_experiment_config, run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml")
print(out["scf_energy"], out.get("energy_pauli_protocol"))
```

Pick a starter YAML by scenario:

```bash
qchem-run --list-scenarios
qchem-run configs/example_h2.yaml
```

## Install profiles (pip extras)

| Profile | Command | Use when |
|---------|---------|----------|
| **core** | `pip install qchem-stack` | Config models, repro export only |
| **chemistry** | `pip install "qchem-stack[chem]"` | PySCF classical chemistry |
| **quantum** | `pip install "qchem-stack[chem,quantum]"` | PySCF + Qiskit simulators |
| **maintainer** | `pip install "qchem-stack[dev]"` from git checkout | Full CI parity |

Optional extras:

| Extra | Command | Use when |
|-------|---------|----------|
| **api** | `pip install "qchem-stack[api]"` | FastAPI job server |
| **uqc** | `pip install "qchem-stack[uqc]"` + `pip install -e packages/qchem-stack-uqc` | UQC cloud backend plugin |
| **pytket** | `pip install "qchem-stack[pytket]"` | TKET compile metrics probe |
| **qmlff** | `pip install "qchem-stack[qmlff]"` + sibling QML-FF editable | JAX-MD active-learning loop |

## Stable SDK facade

```python
from qchem_stack.sdk import (
    load_experiment_config,
    run_pipeline_from_config,
    workflow_preview_payload,
    repro_json_dumps,
    list_scenarios_text,
)

preview = workflow_preview_payload(load_experiment_config("configs/example_h2.yaml"))
```

CLI: `qchem-run`, `qchem-export-parity`.

## Documentation

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
