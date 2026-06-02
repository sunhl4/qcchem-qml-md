# qchem-stack

Quantum chemistry orchestration: classical downfolding, variational protocols,
reproducible `repro` export, and optional MD bridge.

## Quick start

```bash
pip install "qchem-stack[chem,quantum]"
```

```python
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml")
print(out["scf_energy"], out.get("energy_pauli_protocol"))
```

## Install profiles (pip extras)

| Profile | Command | Use when |
|---------|---------|----------|
| **core** | `pip install qchem-stack` | Config models, repro export only |
| **chemistry** | `pip install "qchem-stack[chem]"` | PySCF classical chemistry |
| **quantum** | `pip install "qchem-stack[chem,quantum]"` | PySCF + Qiskit simulators |
| **maintainer** | `pip install "qchem-stack[dev]"` from git checkout | Full CI parity |

Optional: `[api]` (FastAPI), `[uqc]` (UQC cloud), `[pytket]`.

## Documentation

- Repository guides: https://github.com/sunhl4/qcchem-qml-md/tree/main/docs
- Release process: `docs/engineering/pypi_release.md`
- Contributor quick start: `docs/QUICKSTART_CONTRIBUTORS.md`

## HTTP API (optional)

```bash
pip install "qchem-stack[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## License

Apache-2.0
