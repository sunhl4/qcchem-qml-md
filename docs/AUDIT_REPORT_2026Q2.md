# Structured Audit Report: Tests, Examples, Configs, Docs, and Root Files

**Date:** 2026-05-27
**Scope:** 194 test files, 15 example scripts, 71 YAML configs, ~189 docs files, root configuration files

---

## 1. TESTS (194 files, ~188 test modules + 3 fixtures + helpers)

### 1.1 Coverage Map by Source Module

| Source Module | Source `.py` files | Test files (approx.) | Assessment |
|---|---|---|---|
| `chem/` | 127 | ~55 | **Strong** but uneven; `chem.kernels/` and `chem.integration/` lightly covered |
| `config/` | 46 | ~15 | **Good** — nested validation, combos, molecule, embedding, quantum all covered |
| `quantum/` | 38 | ~25 | **Strong** — VQE, ADAPT, VQD, QSE, SCEOM, UCCSD, plugins, registries |
| `orchestration/` | 26 | ~8 | **Adequate** — pipeline + public surface; stage_execution internals under-tested |
| `integrations/` | 22 | ~8 | **Adequate** — closure, compat shims, workflow preview, methods |
| `protocols/` | 21 | ~10 | **Good** — computable, protocol list, jobs, parity, pauli |
| `jobs/` | 17 | ~5 | **Weak** — only store/list, retry, worker, flow, timeline; no concurrency tests |
| `backends/` | 16 | ~8 | **Good** — factory, executors, Pauli shot sim, pytket, qiskit shots |
| `md_bridge/` | 14 | ~5 | **Weak** — classical H2, QMLFF smoke, labeler, adapter imports; no multi-round loop tests |
| `api/` | 9 | ~3 | **Good** — runs, health, ml_md; but only in optional CI job |
| `mitigation/` | 6 | ~3 | **Adequate** — DAG trace, PMSV, ZNE circuit fold |
| `ml/` | 5 | ~2 | **Weak** — only one surrogate smoke test + qmef trainer |
| `qpe_qec_demo/` | 5 | ~2 | **Weak** — QPE VQS algorithms only |
| `tensornet/` | 3 | 0 (no dedicated test) | **Missing** — no `test_tensornet_stub.py` found |
| `repro/` | 3 | ~3 | **Good** — export, schema, run summary |
| `contracts/` | 3 | ~1 | **Minimal** |
| `internal_reports/` | 1 | 0 | **Missing** |

### 1.2 Test Quality Issues

**A. Inline YAML duplication (major)**

The largest issue. `test_orchestration_pipeline.py` (967 lines) contains ~15 near-identical inline YAML blocks of H2 sto-3g with only a few fields changed. Each test duplicates the full ~30-line molecule/scf/active_space/backend boilerplate. This pattern is also present (though less severe) in `test_repro_run_summary.py` (424 lines).

**Recommendation:** Extract a `_h2_base_dict()` helper (like `test_config_pre_quantum_combos.py` does with `_h2_base()`) and let each test override only the delta.

**B. Fragile exact-value assertions**

Several tests hard-code floating-point energies without clear provenance, e.g.:

- `test_orchestration_pipeline.py:767` — `e_fci_sto3g_h2 = -1.1372759436170443` (also in `render_example_plots.py:111`)
- Tests asserting `rs["n_circuits"] >= 1` and `rs["n_pauli_terms"] >= 1` — fragile if grouping algorithm changes

**C. No `conftest.py` at all**

There is zero `conftest.py` in the entire `tests/` directory. All shared state is via `tests/fixtures/` (3 Python files + 2 JSON files) and `tests/helpers/` (1 file). This means:

- No pytest fixtures (`@pytest.fixture`) for common setup (e.g., tmp YAML, PySCF skip guard, H2 config factory)
- Each test re-implements config construction
- No `autouse` fixtures for solver registry cleanup between tests (the `helpers/solver_registry_state.py` exists but must be called manually)

**D. Inconsistent skip strategies**

Three different patterns are used:

1. `pytest.importorskip("pyscf")` at module scope (correct)
2. `pytest.mark.skipif(not _have_pyscf(), ...)` (in `test_api_runs.py`)
3. `pytest.skip("configs/...yaml missing")` inside test body (in orchestration tests)
4. Module-level `pytestmark = pytest.mark.psi4` (in psi4 tests)

These should be unified.

**E. No `parametrize` on highly repetitive tests**

Tests like `test_adapt_singles_pool_yaml_runs_via_pipeline`, `test_adapt_doubles_pool_yaml_runs_via_pipeline`, `test_adapt_uccsd_jw_alias_pool_yaml_runs_via_pipeline` are identical except for the YAML path and one assertion. Should be `@pytest.mark.parametrize`.

### 1.3 Test Organization Issues

- **Flat directory**: All 188 test files live directly in `tests/` with no subdirectories. For a project with 17 source modules, grouping by area (e.g., `tests/chem/`, `tests/quantum/`, `tests/config/`) would greatly improve navigability.
- **Naming is consistent** (`test_*.py`) — good.
- **No shared base test classes** for common pipeline-run-then-assert patterns.
- **`test_integration_philosophy.py`** tests `chem.integration` internals but its name suggests a meta/philosophical doc — misleading.

### 1.4 Fixtures and Helpers Quality

- **`tests/fixtures/quantum_problem.py`** (17 lines): thin wrapper around `restricted_active_space_quantum_problem_from_config` — barely adds value over direct import.
- **`tests/fixtures/classical_reference.py`** (24 lines): similar thin wrapper.
- **`tests/fixtures/mock_chem_solver.py`** (62 lines): useful mock solver with full `SolverCapabilities` — well structured.
- **`tests/fixtures/parity_export_example_h2_config_only.json`**: golden fixture for export parity — important, well-maintained.
- **`tests/fixtures/pipeline_results_minimal_export_merge.json`**: second golden fixture.
- **`tests/helpers/solver_registry_state.py`**: provides `reset_solver_registry_state()` but no tests appear to use it via `autouse`.
- **`tests/embedding_nested.py`**: imported by orchestration tests — should be in `helpers/` or `fixtures/`.
- **No `conftest.py`**: no `tmp_path` factories, no session-scoped config loaders, no `autouse` cleanup.

---

## 2. EXAMPLES (15 files in `examples/`, plus `examples/solver_plugin_entrypoint_demo/`)

### 2.1 Documentation Quality

| Example | Docstring/Doc Quality | Runnable? |
|---|---|---|
| `tutorial_01_h2_vqe_export.py` | Short, references config | Yes (needs PySCF) |
| `tutorial_02_uccsd_pipeline.py` | Short | Yes (needs PySCF) |
| `tutorial_03_qpe_zne_paths.py` | Short | Yes (config-only without PySCF) |
| `tutorial_04_uccsd_below_scf.py` | **Best** — full docstring with caveats | Yes (needs PySCF) |
| `toy_dmrg_spin_chain.py` | **Excellent** — full educational DMRG impl | Yes (numpy/scipy only) |
| `tangelo_facade_demo.py` | Good — Tangelo bridge explanation | Yes |
| `example_open_stack_quantum_problem.py` | Moderate — references docs | Yes (needs PySCF) |
| `qmlff_md_pipeline_demo.py` | **Excellent** — full usage in docstring | Yes (needs QML-FF + jax-md) |
| `qmlff_force_field_benchmark.py` | Good usage block | Yes (needs PySCF + QMLFF) |
| `qmlff_h2_native_benchmark.py` | Good — compares native vs bridge | Yes (needs QML-FF sibling) |
| `render_example_plots.py` | Good — lists outputs | Yes (needs matplotlib + PySCF) |
| `run_all_smoke.py` | Minimal | Yes |
| `solver_plugin_entrypoint_demo/` | Separate pyproject.toml + src | Installable plugin |

### 2.2 Issues

- **`examples/README.md`** is mostly in Chinese — inconsistent with the English tutorial scripts it describes.
- **No `__init__.py` content**: `examples/__init__.py` is a single docstring line — fine but not useful for imports.
- **`run_all_smoke.py`** only runs 5 scripts (tutorials 01-04 + toy_dmrg). It does NOT smoke-test `tangelo_facade_demo.py`, `example_open_stack_quantum_problem.py`, `qmlff_*`, or `render_example_plots.py`.
- **Hard-coded paths**: `qmlff_h2_native_benchmark.py:28` hard-codes `_QMLFF_ROOT = _REPO_ROOT.parent / "QML-FF"` — fragile on different workstations.
- **No error handling in tutorials 01-03**: if pipeline fails, they silently return 0 from subprocess.

### 2.3 Missing Examples

- No example for **Schmidt DMET** end-to-end (config exists at `example_h2_psi4_schmidt_dmet.yaml` but no Python walkthrough)
- No example for **projection embedding** (configs exist but no tutorial)
- No example for **Psi4 backend** usage
- No example for **HTTP API** client usage (only server-side tests exist)
- No example for **AVAS active space** workflow
- No example for **IQEB** algorithm (config exists but no tutorial)
- No Jupyter notebooks (`.ipynb`) — all examples are `.py` scripts

---

## 3. CONFIGS (71 YAML files)

### 3.1 Naming Conventions

**Consistent pattern**: `example_{molecule}_{feature}.yaml` — good. Exceptions:

- `tutorial_chain_h2.yaml` — uses `tutorial_` prefix instead of `example_`
- `qpe_dual_track_demo.yaml` — no `example_` prefix

### 3.2 Major Inconsistency: Full-Dump vs Minimal Configs

**This is the biggest config issue.** Two distinct styles coexist:

**Style A — Full dump** (most configs, ~240 lines): Every field dumped with all defaults, including `zmatrix: null`, `ecp: null`, all `scf.pyscf.*` nulls, all `scf.psi4.*` nulls, entire `parity_integrations` block, entire `nexus_cloud` block, etc. Examples: `example_h2.yaml`, `example_h2_uccsd.yaml`, `example_h2_vqd_uccsd.yaml`, and ~60 others.

**Style B — Minimal** (a few configs, ~47-57 lines): Only meaningful fields. Examples: `example_h2_classical_md.yaml`, `example_custom_driver_template.yaml`, `example_h2_qmlff_md.yaml`.

This creates two problems:

1. **Noise**: The meaningful difference between `example_h2.yaml` and `example_h2_uccsd.yaml` is 2 fields (`variational.ansatz: uccsd` and `pauli.use_protocol: false`), but you must diff 240 lines to find it.
2. **Maintenance burden**: When a new field is added, ~65 full-dump configs need regeneration.

### 3.3 MD/ML Configs Are a Different Schema

The 5 MD configs (`example_h2_*_md.yaml`, `example_h2_qnn_native_md.yaml`) use an entirely different schema (`MdValidationLoopConfig`) — flat key-value, no `schema_version`, no `molecule` block. This is correct (they're consumed by `qmlff_md_pipeline_demo.py`, not the main pipeline), but the naming `example_h2_*.yaml` makes them look like standard experiment configs.

### 3.4 Inconsistencies Between Configs

- **`tutorial_chain_h2.yaml`** uses `scf.method: ROHF` while all other H2 configs use `RHF` — intentional (DMET path) but not documented in the config.
- **`example_h2_avas.yaml`** uses `coordinate_unit: angstrom` with bond length `0.74` while nearly all other configs use `coordinate_unit: bohr` with `1.4`. Both describe H2 but the unit inconsistency is a footgun.
- **`adapt.max_iter`** varies: 3 (singles pool), 4 (base), 5 (VQD UCCSD, doubles pool) across configs — no clear pattern.
- **`backend.shots_per_circuit`** varies: 256, 512, 1024, 2048 across configs without explanation.

### 3.5 Missing Config Examples

- No config for **H2O or larger molecule** (all H2 except H4 linear chain)
- No config demonstrating **open-shell / ROHF / UHF** chemistry (only `tutorial_chain_h2.yaml` uses ROHF)
- No config for **ddCOSMO solvent** (field exists but always `model: none`)
- No config demonstrating **classical shadows** enabled end-to-end (only `example_h2_classical_shadows_stub.yaml` with stub)
- No config for **ZNE with real mitigation** (only scalar_stub mode)
- No config demonstrating **multi-k-point PBC** (only gamma-point)

---

## 4. DOCS (~189 files across `docs/` and `docusaurus-site/`)

### 4.1 Organization

The docs are split across three locations:

| Location | Count | Language | Purpose |
|---|---|---|---|
| `docs/*.md` | ~60 top-level | Mostly Chinese | Technical contracts, config references, study notes |
| `docs/execution/` | ~30 | Mixed | Sprint calendars, weekly reports, closeout docs |
| `docs/internal/` | ~5 | English | Code health, style roadmap, config reviews |
| `docusaurus-site/docs/` | ~15 | English | User-facing tutorials, guides, references |
| `docs/assets/` | ~6 | Python scripts | Figure generation |

### 4.2 Issues

**A. Bilingual split without clear boundaries**

- Chinese docs cover: config references (`说明_*.md`), technical deep-dives (`技术文档_*.md`), learning materials (`学习路线图_*.md`, `学习笔记_*.md`), competitive analysis (`竞争定位_*.md`)
- English docs cover: architecture (`ENGINEERING_ARCHITECTURE.md`), quickstart (`QUICKSTART_CONTRIBUTORS.md`), parity matrices, execution plans
- Some docs mix languages in the same file (e.g., `README.md` has both English and Chinese sections)
- No language policy documented

**B. Execution calendar docs are voluminous and transient**

`docs/execution/` contains ~30 files of sprint calendars (`day001_day090_*.md`), weekly reports (`week_unified_chem_w01.md` through `w13`), and daily templates (`day91_template_2026Q3.md`). These are internal project management artifacts that:

- Dilute the technical docs directory
- Will become stale rapidly
- Should be in a separate location (e.g., `.github/PROJECT_NOTES/` or a private wiki)

**C. Docs that may be outdated vs. code**

- `docs/ENGINEERING_ARCHITECTURE.md` references `qchem_stack.ml` (cache, surrogate, active learning, MLPolicy) — the `ml/` module has only 5 files and minimal tests
- `docs/工作计划_第一期_2026年6月_调研与架构设计.md` — dated June 2026 (future/now); may not reflect current state
- `docs/实施清单_PhaseA_PySCF继承改造.md` and `docs/实施清单_PhaseB_PhaseC_收口.md` — implementation checklists that may be partially done
- Several docs reference `docs/P2_W5_algorithm_registry_alignment.md` which doesn't appear in the top-level listing

**D. Missing documentation**

- No **API reference** for `qchem_stack.chem` public surface (only style guide)
- No **API reference** for `qchem_stack.quantum` public surface (only style guide)
- No **migration guide** from legacy `PySCFDriver` to new `ChemIntegralSolver` path
- No **troubleshooting / FAQ** doc
- No **performance tuning** guide (e.g., when to use `density_fit`, AVAS thresholds)
- No **changelog** (CHANGELOG.md)

### 4.3 Docusaurus Site

The Docusaurus site has clean English tutorials and guides, but coverage is thin:

- Only 4 tutorials, 4 guides, 3 reference pages
- No tutorial for ADAPT, IQEB, DMET, Schmidt embedding, or Psi4 backend
- The site mirrors some `docs/*.md` content but the sync is manual

---

## 5. ROOT FILES

### 5.1 `pyproject.toml`

**Strengths:**

- Clean dependency declaration with well-separated optional extras
- Good pytest marker definitions (8 markers)
- Reasonable Ruff config with per-file ignores

**Issues:**

- `requires-python = ">=3.10"` but CI tests only 3.10-3.12 — no 3.13 testing
- `version = "0.1.0"` — still pre-1.0 despite substantial codebase
- No `readme` field (intentional per comment, but means PyPI page would be empty)
- Two script entry points point to the same function: `qchem-jobs-worker` and `qchem-pipeline-worker` both map to `qchem_stack.jobs.worker:main` — confusing
- `dev` extra includes `all` + `api` but not `examples_viz` or `qmlff`
- No `[tool.coverage]` section — no coverage configuration at all

### 5.2 CI (`.github/workflows/ci.yml`)

**Strengths:**

- Well-structured with 5 jobs: `lint`, `typecheck-config`, `typecheck-stack`, `test`, `test-psi4`, `docusaurus`
- Proper `needs: lint` dependency chain
- Extensive smoke pipeline coverage (8 different smoke modes)
- Parity export validation steps

**Issues:**

- **No coverage reporting** — no `pytest --cov` anywhere in CI
- **`test-psi4`** has `continue-on-error: true` — failures are silently ignored
- **No caching** for PySCF/Psi4 compilation (micromamba install from scratch each time)
- **Python 3.13 missing** from matrix
- **`test` job installs `[dev]` which includes `[all]` which includes `[chem,quantum,pytket,nexus]`** — so optional extras are always present in CI, meaning CI never tests the "bare install" path
- **No Windows or macOS** testing
- **Pre-quantum docs sync check** (`scripts/sync_pre_quantum_docs.py`) runs `git diff --exit-code` — fragile if auto-generated docs are slightly out of date
- **No `pytest -x`** (stop on first failure) — slow feedback loop

### 5.3 `.pre-commit-config.yaml`

Minimal: only Ruff lint + format. No type checking, no doc link checking, no YAML validation.

### 5.4 `CONTRIBUTING.md`

Comprehensive (188 lines) but heavily bilingual (Chinese section headers and tables mixed with English instructions). References ~15 other docs. The pre-quantum stack maintenance table is valuable but requires Chinese reading ability.

### 5.5 `README.md`

Very long (160 lines), dense, and serves as both product overview and technical reference. The capability map table, end-to-end orchestration example, and simulator documentation are well-organized. However:

- Mixed Chinese/English throughout
- The `repro.run_summary` documentation is an inline bullet list of ~30 keys — should be a separate reference doc
- References `../PandM/materials/learning/quantum-chem/literature/` — a path outside the repo

---

## 6. Summary of Top Priorities

1. **Tests**: Add `conftest.py` with shared fixtures; extract inline YAML boilerplate into helpers; add `parametrize` to repetitive test families; add coverage reporting to CI.
2. **Configs**: Move from full-dump YAML to minimal configs showing only non-default fields; add a `_template.yaml` with all defaults documented.
3. **Docs**: Separate execution/project-management docs from technical docs; add English API references for `chem` and `quantum` modules; add a CHANGELOG.
4. **Examples**: Add end-to-end tutorials for Schmidt DMET, projection embedding, Psi4, and HTTP API; extend `run_all_smoke.py` to cover more examples.
5. **CI**: Add `pytest --cov` with a coverage gate; add Python 3.13 to the matrix; remove `continue-on-error` from Psi4 job or make it non-blocking explicitly in a cleaner way.
