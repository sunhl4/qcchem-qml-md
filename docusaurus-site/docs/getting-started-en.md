---
title: Getting started (English bridge)
description: Short English install and smoke path; links to Chinese docs and repo onboarding.
keywords:
  - getting started
  - install
  - English
---

# Getting started (English bridge)

:::note English notes (not a full locale)
This site’s default locale is **zh-Hans**. This page is an English **bridge only**, not a complete bilingual documentation set. For deep algorithms and modules, follow the Chinese pages linked below or the repo English onboarding docs.
:::

**qchem-stack** orchestrates quantum-chemistry workflows from YAML: chemistry → program construction → backend execution → `repro` export.

This page is a short English bridge. Deep docs on this site are primarily Chinese; use the links below.

---

## Install

```bash
pip install "qchem-stack[chem,quantum]"
```

| Extra | Purpose |
|-------|---------|
| *(core)* | Precomputed pipeline, strict repro |
| `chem` | PySCF |
| `quantum` | Qiskit / Aer |
| `api` | FastAPI job service |
| `gqe` | GPT-QE (JAX) |

Full matrix: [Install profiles](/reference/install-profiles).

Without PySCF (repo tree):

```bash
python3 scripts/smoke_pipeline.py --precomputed-only
```

---

## Smoke

```bash
qchem-run --scenario minimal_vqe
# or
python3 scripts/smoke_pipeline.py
```

```python
from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps

out = run_pipeline_from_config("configs/example_h2.yaml")
print(repro_json_dumps(out["repro"]))
```

---

## Chinese deep docs (this site)

| Goal | Link |
|------|------|
| Full Chinese getting started | [开始使用](/getting-started) |
| 15-minute tutorial | [Quickstart](/tutorial/quickstart) |
| Module handbook | [Modules](/modules/) |
| FAQ | [FAQ](/faq/) |
| Config fields | [Config fields](/reference/config-fields/) |
| Integrator API surface | [API surface](/reference/api-surface) |

---

## Repo English onboarding (GitHub)

- [ONBOARDING_BY_ROLE_en.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/ONBOARDING_BY_ROLE_en.md)
- [QUICKSTART_HTTP_API_en.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/QUICKSTART_HTTP_API_en.md)
