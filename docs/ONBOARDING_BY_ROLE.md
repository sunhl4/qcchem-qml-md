# Onboarding by role

Single entry for contributors and integrators. Pair with [QUICKSTART_CONTRIBUTORS.md](QUICKSTART_CONTRIBUTORS.md).

**English architecture summary:** [ENGINEERING_ARCHITECTURE_en.md](ENGINEERING_ARCHITECTURE_en.md)

## Algorithm developer

**Goal:** add or extend variational / excited-state algorithms without touching orchestration.

| Start here | Path |
|------------|------|
| Style guide | [quantum_模块风格约定.md](quantum_模块风格约定.md) |
| Algorithm modules | `src/qchem_stack/quantum/` |
| Example YAMLs | `configs/` |
| Tests | `tests/quantum/` |

**Rules:** `quantum/` must not import `orchestration` or parse YAML directly — consume `PreQuantumInput` and config models passed from orchestration.

## Integrator (SDK / HTTP / export)

**Goal:** embed qchem-stack in apps, dashboards, or Methods-style export pipelines.

| Start here | Path |
|------------|------|
| Stable SDK | `qchem_stack.sdk` — see [api_stability_policy.md](engineering/api_stability_policy.md) |
| Pipeline entry | `run_pipeline_sync`, `run_pipeline_from_config` |
| Parity export | `export_parity_table` / `scripts/export_parity_criteria_table.py` |
| HTTP API | `pip install qchem-stack[api]` — [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) §9 |
| Tests | `tests/api/`, `tests/repro/`, `tests/protocols/` |

## DevOps / maintainer

**Goal:** keep CI green, release gates, and production deployment safe.

| Start here | Path |
|------------|------|
| Architecture | [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) |
| Production checklist | [engineering/production_deployment.md](engineering/production_deployment.md) |
| Release gate | `./scripts/release_precheck.sh` |
| Test ownership | [engineering/test_ownership.md](engineering/test_ownership.md) |
| CI | `.github/workflows/ci.yml` |

**Local smoke (no PySCF):** `./scripts/venv-run python scripts/smoke_pipeline.py --precomputed-only`

**MD bridge install:** `pip install -e ".[chem]"` for classical H₂ FF + QMEF (md-classical profile, not a pip extra); `pip install -e ".[chem,qmlff]"` when using sibling QML-FF + JAX-MD.

## Historical / backlog docs

Competitive positioning and parity narratives under `docs/` (Chinese long-form) are **backlog reference**, not runtime dependencies. See [docs/README.md](README.md).
