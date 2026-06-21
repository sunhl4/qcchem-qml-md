# qchem-stack

[![CI](https://github.com/sunhl4/qcchem-qml-md/actions/workflows/ci.yml/badge.svg)](https://github.com/sunhl4/qcchem-qml-md/actions/workflows/ci.yml)

Open orchestration for quantum-chemistry workloads: **chemistry → pre-quantum → quantum algorithms → protocols → jobs → `repro` export → MD/ML bridge**.

**Package:** PyPI [`qchem-stack`](https://pypi.org/project/qchem-stack/) · import `qchem_stack` · repo [`qcchem-qml-md`](https://github.com/sunhl4/qcchem-qml-md)

**Maintainers:** [CONTRIBUTING.md](CONTRIBUTING.md) · [ENGINEERING_ARCHITECTURE.md](docs/ENGINEERING_ARCHITECTURE.md) · [Onboarding by role](docs/ONBOARDING_BY_ROLE.md) · [English onboarding](docs/ONBOARDING_BY_ROLE_en.md) · [English architecture summary](docs/ENGINEERING_ARCHITECTURE_en.md)

## Get started

1. **Install:** `pip install -e ".[chem,dev]"` — [Contributor quick start](docs/QUICKSTART_CONTRIBUTORS.md)
2. **Run:** `qchem-run --scenario minimal_vqe` (recommended) or `qchem-run configs/scenarios/minimal_vqe.yaml`
3. **Tutorial:** [Docusaurus quickstart](docusaurus-site/docs/tutorial/quickstart.md)

```python
from qchem_stack.orchestration.pipeline import run_pipeline_from_config
run_pipeline_from_config("configs/scenarios/minimal_vqe.yaml")
```

Full v2 reference YAML: `configs/example_h2.yaml`.

```bash
qchem-export-parity configs/scenarios/minimal_vqe.yaml > parity_table.json
docker compose up -d   # optional API + worker on :8000
```

**Docs:** [`docs/README.md`](docs/README.md) · [parity matrix](docs/public_parity_matrix.md) · [SDK](docusaurus-site/docs/reference/python-sdk.md) · [install profiles](docs/engineering/install_profiles.md)

## Capability map

| Area | Module | Notes |
|------|--------|-------|
| Classical chemistry | `chem/` | `ChemIntegralSolver` registry; default CI path **`scf.driver=pyscf`** |
| Variational / excited | `quantum/` | VQE, ADAPT, IQEB, VQD, QSE, SCEOM — see `configs/` |
| Protocols + backends | `protocols/`, `backends/` | Pauli averaging, `BackendSpec` (statevector / qiskit / ionstack) |
| Jobs + repro | `jobs/`, `repro/` | SQLite worker, strict JSON export |
| MD / ML bridge | `md_bridge/` | `pip install -e ".[chem,md-classical]"` or `[qmlff]` for JAX-MD |

Full capability narrative: [Docusaurus product/features](docusaurus-site/docs/product/features.md).

<details>
<summary><strong>Programmatic API, HTTP, Docker, simulators</strong></summary>

```python
from pathlib import Path
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync

cfg = load_experiment_config("configs/example_h2.yaml")
out = run_pipeline_sync(cfg, cfg_path=Path("configs/example_h2.yaml"))
print(out["pre_quantum_input"]["hamiltonian_fingerprint"])
```

- **HTTP API:** `pip install qchem-stack[api]` — see [ENGINEERING_ARCHITECTURE §9](docs/ENGINEERING_ARCHITECTURE.md)
- **Methods export:** `WorkflowCoordinator` / `qchem-export-parity`
- **Pre-quantum YAML matrix:** [docs/pre_quantum_yaml_matrix.md](docs/pre_quantum_yaml_matrix.md)
- **Qiskit / shots / excited states / repro keys:** [quickstart tutorial](docusaurus-site/docs/tutorial/quickstart.md) and [pipeline stage ownership](docs/engineering/pipeline_stage_ownership.md)

</details>

<details>
<summary><strong>Deep reading (optional)</strong> — competitive positioning, long-form contracts</summary>

Historical research docs (not runtime dependencies): [docs/research/README.md](docs/research/README.md).

- [Parity matrix](docs/public_parity_matrix.md) · [HTTP contract](docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md) · [CircuitIR / TKET](docs/技术文档_CircuitIR与TKET桥接及作业契约.md)

</details>

## Layout

`chem/` · `quantum/` · `protocols/` · `backends/` · `mitigation/` · `jobs/` · `orchestration/` · `md_bridge/` · `integrations/` · `repro/`

## License

Apache-2.0
