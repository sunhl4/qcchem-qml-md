# Contributing to qchem-stack

**New contributors:** start with the English quick start — [`docs/QUICKSTART_CONTRIBUTORS.md`](docs/QUICKSTART_CONTRIBUTORS.md) (YAML → pipeline → `repro` keys).

**对标与工程母稿（三份 + 契约矩阵）**：[竞争定位](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) · [工程记忆](docs/工程记忆_Quantinuum对标与数据流技术文档.md) · [差距与实施计划](docs/public_parity_matrix.md)（含 **附录 A–F**：P2 / Y1 / L1 / B→J / P1 审计 / 不排期项）· [parity 矩阵](docs/public_parity_matrix.md)。**详细技术契约**：`docs/技术文档_*.md`、`mitigation_PMSV_ZNE_Qermit_mapping.md`、`launch_retrieve_nexus_analog.md`。

## Local Python environment (default)

**Recommended first-time setup:**

```bash
./scripts/bootstrap_dev.sh
export QCHEM_STACK_PYTHON="$(pwd)/.venv/bin/python"
./scripts/venv-run pytest tests -q --tb=short -m "not slow and not perf"
# PR merge gate (skip docusaurus):
./scripts/release_precheck.sh --quick
```

Note: `.[dev]` no longer pulls `uqc` by default. For UQC experimental: `pip install -e ".[dev-uqc]"`.

[`scripts/venv-run`](scripts/venv-run) runs commands with **`QCHEM_STACK_PYTHON`** when set, otherwise **`.venv/bin/python`** if present, else `python3` on `PATH`:

```bash
export QCHEM_STACK_PYTHON=/path/to/python   # optional override
./scripts/venv-run pytest tests -q --tb=short
```

## 维护角色（原 `docs/MAINTAINERS.md`）

| 角色 | 职责 |
|------|------|
| **契约 / capability 导出** | 产品与 HTTP 控制台同源模块 **`qchem_stack.protocols.product_contract`**（ gap 列表、capability_map、parity export 的稳定键常量等）；workflow 预览 **`qchem_stack.integrations.workflow_preview`**。布局见 [Product contracts and workflow-preview](#product-contracts-and-workflow-preview-stable-imports)。矩阵与路线图仍按需维护（见 [public_parity_matrix.md §5](docs/public_parity_matrix.md)）。 |
| **度量与台账** | 月度更新 [与Vendor platform… — 附录 B](docs/public_parity_matrix.md) §3；主表 yes/partial/n/a 可用 `python scripts/count_parity_matrix_main_tables.py` 对照手填。 |
| **签字合并 gate** | 合并前：`ruff check` / `ruff format --check` / `pytest` / `check_parity_export_sample` / `check_comparative_execution_backlog`；或一键：**`QCHEM_STACK_PYTHON=python ./scripts/release_precheck.sh`**（PR 可用 **`--quick`** 跳过 Docusaurus / nbmake，见 [`scripts/README.md`](scripts/README.md)）；CI **`security-audit`** 对 `dev` 与 **`chem,api`** 安装面运行 `pip-audit`（见 [`pip-audit.toml`](pip-audit.toml) allowlist）；在 [附录 C](docs/public_parity_matrix.md) 末行可写明 **实名 + 日期**。 |

### 发版前

1. `QCHEM_STACK_PYTHON=python ./scripts/release_precheck.sh`（pytest + coverage + pyright + pip-audit + contract-docs 同步）
2. Minor releases (1.1.x): complete [`docs/engineering/v1_1_acceptance.md`](docs/engineering/v1_1_acceptance.md); integrators read [`docs/engineering/migration_v1_0_to_v1_1.md`](docs/engineering/migration_v1_0_to_v1_1.md)
3. Patch releases on 1.0.x: [`docs/engineering/v1_0_acceptance.md`](docs/engineering/v1_0_acceptance.md) + [`docs/engineering/migration_v0_8_to_v1_0.md`](docs/engineering/migration_v0_8_to_v1_0.md)
3. Optional full gate: `QCHEM_RELEASE_FULL=1 ./scripts/release_precheck.sh`（L3 benchmarks when PySCF installed）
4. `python scripts/generate_configs_catalog.py` 并提交 `docs/generated/configs_catalog_snippet.md` 与 `docusaurus-site/docs/reference/configs-catalog-body.md`
5. 大改动建议拆 PR：**docs** / **orchestration** / **tests** / **ci** 分开发，便于 review 与 bisect

## Lint

From the repo root (hard-pinned local venv runner):

```bash
./scripts/venv-run ruff check src/qchem_stack tests scripts examples
./scripts/venv-run ruff format --check src/qchem_stack tests scripts examples
```

To apply the formatter locally (when `format --check` fails):

```bash
./scripts/venv-run ruff format src/qchem_stack tests scripts examples
```

GitHub Actions runs these in the dedicated **`lint` job** (Python 3.12); **`test`** (matrix 3.10–3.12) and **`docusaurus`** (documentation build) both **`needs: lint`**.

Optional [pre-commit](https://pre-commit.com) hooks (same paths as CI). The **`pre-commit` CLI ships with `pip install -e ".[dev]"`**:

```bash
./scripts/venv-run pre-commit install
# one-off full tree (like CI scope; runs ruff + ruff-format hooks):
./scripts/venv-run pre-commit run --all-files
```

Uses `.pre-commit-config.yaml` at the repo root.

## Nightly / L3 benchmarks

Optional deep algorithm benchmarks (seven representative configs):

```bash
QCHEM_RUN_L3=1 pytest -m l3 -q --tb=short
python scripts/l3_algorithm_benchmark_report.py --output /tmp/l3_benchmark.json
```

CI runs this in the **`test-nightly`** job (see `.github/workflows/nightly.yml`, invoked from `ci.yml` on schedule).

## Install profiles (pip extras)

| Goal | Install | Notes |
|------|---------|--------|
| Core CI / unit tests | `pip install -e ".[dev]"` | No PySCF: `python scripts/smoke_pipeline.py --precomputed-only` |
| Classical chemistry | `pip install -e ".[chem]"` | PySCF smoke: `scripts/smoke_pipeline.py` |
| Qiskit Pauli shots | `pip install -e ".[quantum]"` | `scripts/smoke_pipeline.py --qiskit-shots` |
| HTTP API | `pip install -e ".[api]"` | Set `QCHEM_STACK_API_KEY` in production |
| MD/ML full chain | editable sibling **QML-FF** + `pip install -e ".[qmlff]"` | Without QML-FF use `force_field_backend: classical_h2` in MD loop YAML |

**Onboarding (three paths):** [docusaurus-site/docs/guide/onboarding-three-paths.md](docusaurus-site/docs/guide/onboarding-three-paths.md) · [tutorial index](docusaurus-site/docs/tutorial/tutorial-index-three-paths.md).

## Tests

From the repo root:

```bash
./scripts/venv-run pytest tests -q --tb=short
```

Optional heavier chemistry smoke (multi-fragment DMET exact, etc.):

```bash
./scripts/venv-run pytest -m slow tests/chem/test_dmet_fragment_exact.py -q --tb=short
```

Targeted markers (see `pyproject.toml`): `-m l1_excited`, `-m l1_md_ml`, `-m l3`. CI **`lint`** job runs **`ruff check`** + **`ruff format --check`** before the **`test`** matrix installs the package.

**Molecular Hamiltonian parity (PySCF ↔ OpenFermion, Tangelo recipe)**：`tests/chem/test_integral_openfermion_tangelo_recipe.py` 校验 CAS 活性空间积分经 `transpose(0,2,3,1)` 与 `InteractionOperator` 半因子后，H₂(sto-3g) 的 **JW 固定粒子数扇区基态 = PySCF FCI**，并与手工 Tangelo 公式得到的 `QubitOperator` 稠密矩阵一致。若本机可 `import tangelo`（部分 Python 版本上 PyPI 包构建可能失败），同文件中的可选用例会与 `SecondQuantizedMolecule` 的 JW 哈密顿量做矩阵对比。

### CI markers (PR 必跑)

主矩阵命令为 **`pytest tests -m "not slow and not perf"`**（见 `.github/workflows/test.yml`）。Python **3.12** 另跑 **`pytest -m l1_md_ml -k "not jax"`**（`tests/md_bridge` + `tests/integrations`）。激发态/VQD/QSE/SCEOM 回归以 `l1_excited` 为准；完整 jax-md / qmlff 重路径仍在 **nightly** `test-md-bridge-l1`（`pytest -m l1_md_ml` 全量）。

**Lint job** 另跑 `python scripts/check_comparative_execution_backlog.py`（与上文「签字合并 gate」一致）。

### Test pyramid

| Tier | When | Command |
|------|------|---------|
| **PR (required)** | Every push/PR | `pytest tests -m "not slow and not perf"` |
| **PR extras (3.12)** | CI only | smoke scripts, `check_parity_export_sample.py`, API tests |
| **Nightly** | schedule / `[nightly]` | `pytest -m "slow or perf"`; `QCHEM_RUN_L3=1 pytest -m l3` |
| **Local optional** | Before release | `pytest -m psi4`, `pytest -m l1_md_ml`, `pytest -m uqc_mock`; DMET exact: `pytest -m slow tests/chem/test_dmet_fragment_exact.py` |

Markers: `slow`, `perf`, `l3`, `l1_excited`, `l1_md_ml`, `pyscf`, `psi4`, `uqc_mock` — see `pyproject.toml`.

**Parity / `computables_rich`（可选 repro）**：`parity_integrations.include_computables_rich_in_repro: true` 时的 workflow-preview 对齐见 `tests/repro/test_workflow_preview_repro_alignment.py`；FastAPI 侧 `POST /v1/meta/workflow-preview` 烟测见 `tests/api/test_api_runs.py`（需 `pip install -e ".[api]"`，CI 已装）。

## Config module style (nested schema)

All new or refactored YAML fields in `src/qchem_stack/config/` must follow [`docs/config_校验分层约定.md`](docs/config_校验分层约定.md): nested sub-blocks, `extra="forbid"`, YAML path = Python path, validation split across `_{section}_validation.py` and `_experiment_validation.py`. Reference implementations: `embedding*.py`, `quantum*.py`. PRs that change public YAML shape must update the matching `docs/说明_*.md` and config tests.

## Code style optimization (P0–P4)

Milestone tracker: [`docs/internal/STYLE_OPTIMIZATION_ROADMAP.md`](docs/internal/STYLE_OPTIMIZATION_ROADMAP.md). Before large refactors, capture baseline:

```bash
./scripts/venv-run python scripts/code_health_baseline.py
# optional JSON artifact:
./scripts/venv-run python scripts/code_health_baseline.py --write docs/internal/code_health_baseline.json
```

Style PRs should attach baseline diff (files >400 lines, `dict[str, Any]` hotspots). Optional local checks after P3/P4 land:

```bash
./scripts/venv-run pyright src/qchem_stack
./scripts/venv-run ruff check src/qchem_stack --select TCH
```

CI runs hard gates: `typecheck-config` (config, repro, exceptions) and `typecheck-stack` (full `src/qchem_stack`).

## PySCF boundary coding rule

For PySCF-related refactors, keep module boundaries stable:

- Put active-space, one-body, and Lowdin matrix transformations in `src/qchem_stack/chem/integrals/`.
- Put AO/Lowdin view dataclasses in `src/qchem_stack/chem/systems/`.
- Keep `src/qchem_stack/chem/drivers/pyscf_driver.py` focused on compatibility facade and workflow orchestration.

If you add new helper logic, prefer the new modules first and keep legacy import paths compatible where practical.

## Adding repro / parity_snapshot fields

When you add or rename keys that appear in **`repro`**, **`repro.parity_snapshot`**, or **`repro.run_summary`**, work through this checklist before merging:

1. **Orchestration** — set the value in [`src/qchem_stack/orchestration/repro_summary.py`](src/qchem_stack/orchestration/repro_summary.py) and/or [`repro_snapshot.py`](src/qchem_stack/orchestration/repro_snapshot.py) (or the stage that owns the key; see [`docs/engineering/pipeline_stage_ownership.md`](docs/engineering/pipeline_stage_ownership.md)).
2. **Export stable keys** — if the field must appear in config-only parity export, add it to **`PARITY_EXPORT_V3_STABLE_KEYS`** in [`src/qchem_stack/protocols/product_contract.py`](src/qchem_stack/protocols/product_contract.py).
3. **Export scripts** — extend [`scripts/export_parity_criteria_table.py`](scripts/export_parity_criteria_table.py) and ensure [`scripts/check_parity_export_sample.py`](scripts/check_parity_export_sample.py) still passes (auto-discovers `configs/*.yaml`).
4. **Tests** — add or extend a focused test (pattern: [`tests/repro/test_workflow_preview_repro_alignment.py`](tests/repro/test_workflow_preview_repro_alignment.py)); for export-only keys, refresh [`tests/fixtures/parity_export_example_h2_config_only.json`](tests/fixtures/parity_export_example_h2_config_only.json) when intentional.
5. **Docs** — if user-visible, note the key in [`docs/ENGINEERING_ARCHITECTURE.md`](docs/ENGINEERING_ARCHITECTURE.md) or the relevant contract doc; run doc sync scripts if the key affects generated tables.

## Product contracts and workflow-preview (stable imports)

- **Capability gaps / product surface literals** live in **`src/qchem_stack/protocols/product_contract.py`** (`product_gap_categories`, `PRODUCT_CAPABILITY_MAP`, `PARITY_EXPORT_V3_STABLE_KEYS`, mitigation / differentiation bundles, expectation-path helpers). HTTP **`GET /v1/meta/capability-surface`** MUST stay aligned via `tests/api/test_api_runs.py::test_capability_surface_matches_product_contract`.
- **Workflow preview payload** (`protocol_stages_preview_v1`, **`computable_graph_v2`**, `workflow_preview_payload`, slim summaries): **`src/qchem_stack/integrations/workflow_preview.py`** (HTTP `POST /v1/meta/workflow-preview`, pipeline repro sidecars when enabled).

Spot-check:

```bash
./scripts/venv-run python -c "from qchem_stack.protocols.product_contract import product_gap_categories, PARITY_EXPORT_V3_STABLE_KEYS; print(len(product_gap_categories()), len(PARITY_EXPORT_V3_STABLE_KEYS))"
./scripts/venv-run python -c "from qchem_stack.integrations.workflow_preview import computable_graph_v2; print('computable_graph_v2', callable(computable_graph_v2))"
```

**Docusaurus 主站镜像（中文）**：源码 `docusaurus-site/docs/reference/parity-contract-import-paths.md` — 本地 `cd docusaurus-site && npm start` 后路径 **`/reference/parity-contract-import-paths`**。

## Parity export / golden fixture

Config-only Methods alignment (no PySCF run):

```bash
./scripts/venv-run python scripts/export_parity_criteria_table.py configs/example_h2.yaml
./scripts/venv-run python scripts/check_parity_export_sample.py
```

After intentional contract changes to **`product_gap_categories()`**, **`PARITY_EXPORT_V3_STABLE_KEYS`** (see `qchem_stack.protocols.product_contract`), or export columns (e.g. **`geometry_source`**), regenerate `tests/fixtures/parity_export_example_h2_config_only.json` from `configs/example_h2.yaml` and normalize `source_config` to `configs/example_h2.yaml` if the exporter emits OS-specific separators.

新增「判据表导出」相关 `configs/*.yaml`（ExperimentConfig 形态）时，**无需**再手工维护 `SAMPLE_CONFIGS_REL`：`scripts/check_parity_export_sample.py` 会自动发现 `configs/*.yaml` 中全部 experiment 配置并跑 config-only export 门控。MdValidationLoop 形态的 YAML 由同脚本末尾的 `MdValidationLoopConfig.from_yaml` 校验。

### 算符池与 L3 基准（ADAPT / IQEB）

- **新池 id 或 YAML 别名**：除 `quantum/operator_pool_registry.py`、`config.py` 中 `adapt_pool_id` / `iqeb_pool_id` Literal 外，按需更新 `tests/quantum/test_operator_pool_registry_export.py`、`docs/public_parity_matrix.md` 与 [算法面广度索引](docs/算法面广度_Vendor platform_Tangelo对照索引.md)。若增加**代表运行配置**，同步 `scripts/check_parity_export_sample.py`、`tests/repro/test_export_parity_golden.py` 参数表，并评估是否加入 `integrations/l3_algorithm_benchmark.py` 的 `L3_PYTEST_YAMLS` / `DEFAULT_BENCHMARK_YAMLS`。HTTP **`GET /v1/meta/capability-surface`** 返回 **`schema: capability_surface_v2`**（参见 `src/qchem_stack/api/app.py`），与 **`tests/api/test_api_runs.py::test_capability_surface_matches_product_contract`** 同源对拍。
- **可选重型门禁**：`QCHEM_RUN_L3=1 ./scripts/venv-run pytest -m l3`（`tests/integrations/test_l3_benchmark_smoke.py`）。

## Dependabot（依赖与 Actions）

[`.github/dependabot.yml`](.github/dependabot.yml) 会定期开 PR：**GitHub Actions**（仓库根，按周、同批合并）、**pip / `pyproject.toml`**（按月）、**`docusaurus-site` npm**（按周）。合并前仍按本页 **Lint / Tests / parity** 自检。

## Pre-quantum stack（维护清单）

经典 → `PreQuantumInput` → 量子变分的主路径。改下列区域时，请同步对应测试与文档。

| 区域 | 模块 / 文档 | 合并前自检 |
|------|-------------|------------|
| **配置门禁** | `config/_experiment_validation.py`，`validate_pre_quantum_contract` | `pytest tests/config/test_config_pre_quantum_combos.py tests/chem/test_validate_pre_quantum_contract.py -q` |
| **公开构建 API** | `chem/pre_quantum_build.build_pre_quantum_input`；勿再教用户直接用 `molecular_hamiltonian_from_classical_reference` | `pytest tests/chem/test_build_pre_quantum_input_api.py -q` |
| **装配（chem）** | `chem/pre_quantum_build.py`（`build_pre_quantum_input` / `build_pre_quantum_input_with_context`），分支见 `chem/pre_quantum_path.py` | `pytest tests/chem/test_build_pre_quantum_input_api.py -q` |
| **管线阶段（编排）** | `stage_execution.build_pre_quantum_stage`（precomputed / live 分叉与计时） | `pytest tests/orchestration/test_orchestration_pipeline.py tests/chem/test_pre_quantum_input_contract.py -q` |
| **单次 run 缓存** | `chem/bridges/run_build_cache.py` → `out["pre_quantum_build_cache"]` | `pytest tests/chem/test_run_build_cache.py -q` |
| **分支解析** | `chem/pre_quantum_path.py`（与 `hamiltonian_semantics` / 校验共用） | `pytest tests/chem/test_pre_quantum_path.py -q` |
| **嵌入语义** | `chem/embedding/hamiltonian_semantics.py`；`parity_snapshot.pre_quantum_handoff_v1` | `pytest tests/chem/test_embedding_hamiltonian_semantics.py -q` |
| **活性空间 exporter** | `chem/integrals/*_active_space_exporter.py`，`canonical_integral_pack` | `pytest tests/chem/test_canonical_integral_pack.py -q` |
| **Psi4（可选）** | `chem/integrals/psi4_active_space.py`；CI job `test-psi4` | `pytest -m psi4 -q`（本机需 `pip install psi4`） |
| **YAML 组合表** | `docs/pre_quantum_yaml_matrix.md` | 新增/禁止组合时更新矩阵 + 负例测试 |
| **Parity 导出** | `pre_quantum_semantics_from_config` ∈ `PARITY_EXPORT_V3_STABLE_KEYS` | `pytest tests/repro/test_export_pre_quantum_semantics.py`；`python scripts/check_parity_export_sample.py` |

推荐端到端样例：`configs/example_h2.yaml`（PySCF canonical）、`configs/example_h2_precomputed_bundle.yaml`（离线）、`configs/example_h2_psi4_rhf_sto3g.yaml`（Psi4）、`configs/example_h4_schmidt_multifragment.yaml`（Schmidt，`-m slow`）。

## Smoke orchestration

PySCF paths (`pip install qchem-stack[chem]`):

```bash
./scripts/venv-run python scripts/smoke_pipeline.py
./scripts/venv-run python scripts/smoke_pipeline.py --iqeb
./scripts/venv-run python scripts/smoke_pipeline.py --projection-trace
```

**Pre-quantum 离线 lane**（无需 PySCF，读 `precomputed_classical_reference_h2.json`）：

```bash
./scripts/venv-run python scripts/smoke_pipeline.py --precomputed-only
```

## Solver / backend plugin checklist (~10 min)

Reference implementation: [`examples/solver_plugin_entrypoint_demo/`](examples/solver_plugin_entrypoint_demo/README.md).

| Step | Action | Verify |
|------|--------|--------|
| 1 | `pip install -e ./examples/solver_plugin_entrypoint_demo` | `"entrypoint_demo" in registered_solver_ids()` |
| 2 | Scaffold or copy solver module | `python scripts/create_solver_adapter_scaffold.py my_backend --output ...` |
| 3 | Register `[project.entry-points."qchem_stack.solvers"]` in plugin `pyproject.toml` | No import warning on `import qchem_stack` |
| 4 | Set `scf.driver: my_backend` in a YAML | `run_pipeline_from_config("configs/example_h2.yaml")` succeeds |
| 5 | Declare accurate `SolverCapabilities` | `python scripts/check_solver_adapter_contract.py` when CAS integrals are required |
| 6 | Open PR with README snippet + test or smoke note | CI `lint` + `test` green |

Variational or shot backends use `BackendSpec` / backend registry — not the SCF entry-point group above.

## Release checklist (v0.3.0+)

1. Bump `[project].version` in `pyproject.toml` and `CHANGELOG.md`.
2. Align `src/qchem_stack/api/app.py` OpenAPI version with package version.
3. Run merge gates: ruff, pytest, `check_parity_export_sample.py`, `check_comparative_execution_backlog.py`.
4. See [`docs/engineering/api_stability_policy.md`](docs/engineering/api_stability_policy.md).

## Examples / tutorials

See `examples/` and `python examples/run_all_smoke.py` (best-effort; skips steps when PySCF or optional extras are missing).

**User-facing docs**（**Docusaurus**，目录 `docusaurus-site/`，`npm start`，路由示例 `/guide/onboarding-three-paths`）：源码 [`docusaurus-site/docs/guide/onboarding-three-paths.md`](docusaurus-site/docs/guide/onboarding-three-paths.md)。

教程交叉引用：[UCCSD Trotter + export](docusaurus-site/docs/tutorial/uccsd-trotter-export.md)、[ZNE × Qiskit repro](docusaurus-site/docs/tutorial/zne-qiskit-repro.md)、[Projection embedding deep dive](docusaurus-site/docs/tutorial/projection-embedding-deep-dive.md)。新增或重命名 `configs/*.yaml` 时，请在对应教程 / 产品页（`docusaurus-site/docs/`）与 `docs/public_parity_matrix.md` 中按需补链。

**新用户三条路径**（P2-W7）：同上优先走 **Docusaurus** `onboarding-three-paths`。MD/ML 与 `repro` 字段冻结见 [工程记忆 §16](docs/工程记忆_Quantinuum对标与数据流技术文档.md)。P2 双月周历见 [与Vendor platform能力差距与实施计划 — 附录 A](docs/public_parity_matrix.md) 内 `### 8.`。
