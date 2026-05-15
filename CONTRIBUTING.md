# Contributing to qchem-stack

**对标与工程母稿（三份 + 契约矩阵）**：[竞争定位](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) · [工程记忆](docs/工程记忆_Quantinuum对标与数据流技术文档.md) · [差距与实施计划](docs/与InQuanto能力差距与实施计划.md)（含 **附录 A–F**：P2 / Y1 / L1 / B→J / P1 审计 / 不排期项）· [parity 矩阵](docs/inquanto_public_parity_matrix.md)。**详细技术契约**：`docs/技术文档_*.md`、`mitigation_PMSV_ZNE_Qermit_mapping.md`、`launch_retrieve_nexus_analog.md`。

## Local Python environment (hard-pinned)

This repository pins local command execution to:

- `/home/sunhl/projects/qchem_qml_md/.venv/bin/python`

Use `./scripts/venv-run ...` for local lint/test/script commands.

## 维护角色（原 `docs/MAINTAINERS.md`）

| 角色 | 职责 |
|------|------|
| **Parity / 契约维护** | 矩阵与 `inquanto_contract` / `inquanto_gap_categories` 同源；公开站改版时执行差距登记（见 [与InQuanto能力差距与实施计划.md §5](docs/与InQuanto能力差距与实施计划.md)）。 |
| **度量与台账** | 月度更新 [与InQuanto… — 附录 B](docs/与InQuanto能力差距与实施计划.md) §3；主表 yes/partial/n/a 可用 `python scripts/count_parity_matrix_main_tables.py` 对照手填。 |
| **签字合并 gate** | 合并前：`ruff check src/qchem_stack tests scripts examples`、`ruff format --check`（同上路径）、`pytest`、`python scripts/check_parity_export_sample.py`；在 [附录 C](docs/与InQuanto能力差距与实施计划.md) 末行可写明 **实名 + 日期**。 |

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

GitHub Actions runs these in the dedicated **`lint` job** (Python 3.12); **`test`** (matrix 3.10–3.12) and **`docs-site`** both **`needs: lint`**.

Optional [pre-commit](https://pre-commit.com) hooks (same paths as CI). The **`pre-commit` CLI ships with `pip install -e ".[dev]"`**:

```bash
./scripts/venv-run pre-commit install
# one-off full tree (like CI scope; runs ruff + ruff-format hooks):
./scripts/venv-run pre-commit run --all-files
```

Uses `.pre-commit-config.yaml` at the repo root.

## Tests

From the repo root:

```bash
./scripts/venv-run pytest tests -q --tb=short
```

Optional heavier chemistry smoke (multi-fragment DMET exact, etc.):

```bash
./scripts/venv-run pytest -m slow tests/test_dmet_fragment_exact.py -q --tb=short
```

Targeted markers (see `pyproject.toml`): `-m l1_excited`, `-m l1_md_ml`, `-m l3`. CI **`lint`** job runs **`ruff check`** + **`ruff format --check`** before the **`test`** matrix installs the package.

**Molecular Hamiltonian parity (PySCF ↔ OpenFermion, Tangelo recipe)**：`tests/test_integral_openfermion_tangelo_recipe.py` 校验 CAS 活性空间积分经 `transpose(0,2,3,1)` 与 `InteractionOperator` 半因子后，H₂(sto-3g) 的 **JW 固定粒子数扇区基态 = PySCF FCI**，并与手工 Tangelo 公式得到的 `QubitOperator` 稠密矩阵一致。若本机可 `import tangelo`（部分 Python 版本上 PyPI 包构建可能失败），同文件中的可选用例会与 `SecondQuantizedMolecule` 的 JW 哈密顿量做矩阵对比。

### CI markers (PR 必跑)

`.github/workflows/ci.yml` 在完整 `pytest tests` 之后还会跑 **`pytest -m l1_excited`** 与 **`pytest -m l1_md_ml`**（非「仅本地可选」）。激发态/VQD/QSE/SCEOM 等回归以 `l1_excited` 为准；`md_bridge` 与 MD/ML 契约以 `l1_md_ml` 为准（长板字段与 `repro` 对齐清单见 [与InQuanto能力差距与实施计划 — 附录 B §6](docs/与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 表末行）。

**Parity / `computables_rich`（可选 repro）**：`parity_integrations.include_computables_rich_in_repro: true` 时的 workflow-preview 对齐见 `tests/test_workflow_preview_repro_alignment.py`；FastAPI 侧 `POST /v1/meta/workflow-preview` 烟测见 `tests/test_api_runs.py`（需 `pip install -e ".[api]"`，CI 已装）。

## PySCF boundary coding rule

For PySCF-related refactors, keep module boundaries stable:

- Put active-space, one-body, and Lowdin matrix transformations in `src/qchem_stack/chem/integrals/`.
- Put AO/Lowdin view dataclasses in `src/qchem_stack/chem/systems/`.
- Keep `src/qchem_stack/chem/drivers/pyscf_driver.py` focused on compatibility facade and workflow orchestration.

If you add new helper logic, prefer the new modules first and keep legacy import paths compatible where practical.

## Parity export / golden fixture

Config-only Methods alignment (no PySCF run):

```bash
./scripts/venv-run python scripts/export_parity_criteria_table.py configs/example_h2.yaml
./scripts/venv-run python scripts/check_parity_export_sample.py
```

After intentional contract changes to `inquanto_gap_categories()`, **`PARITY_EXPORT_V2_STABLE_KEYS`**, or export columns (e.g. **`geometry_source`**), regenerate `tests/fixtures/parity_export_example_h2_config_only.json` from `configs/example_h2.yaml` and normalize `source_config` to `configs/example_h2.yaml` if the exporter emits OS-specific separators.

新增「判据表导出」相关 `configs/*.yaml` 时，请同步扩展 `scripts/check_parity_export_sample.py` 中的 `SAMPLE_CONFIGS_REL`（见 [与InQuanto能力差距与实施计划 — 附录 E](docs/与InQuanto能力差距与实施计划.md) 原 §5 队列项 12）。

### 算符池与 L3 基准（ADAPT / IQEB）

- **新池 id 或 YAML 别名**：除 `quantum/operator_pool_registry.py`、`config.py` 中 `adapt_pool_id` / `iqeb_pool_id` Literal 外，按需更新 `tests/test_operator_pool_registry_export.py`、`tests/test_methods_resource_unified_export.py`、`docs/inquanto_public_parity_matrix.md` 与 [算法面广度索引](docs/算法面广度_InQuanto_Tangelo对照索引.md)。若增加**代表运行配置**，同步 `scripts/check_parity_export_sample.py`、`tests/test_export_parity_golden.py` 参数表，并评估是否加入 `integrations/l3_algorithm_benchmark.py` 的 `L3_PYTEST_YAMLS` / `DEFAULT_BENCHMARK_YAMLS`。HTTP **`GET /v1/meta/capability-surface`** 与 `capability_surface_v1` 顶层键同源（含 **`object_map`**、**`gaps`**、**`mitigation_execution_model`**、**`open_stack_differentiators`**、**`tangelo_public_mapping_alias_surface_v1`**、**`operator_pool_registry_export_v1`**、**`algorithm_registry_export_v1`**、**`variational_registry_export_v1`**），与 `tests/test_api_runs.py::test_capability_surface_matches_inquanto_contract` 对拍。
- **可选重型门禁**：`QCHEM_RUN_L3=1 ./scripts/venv-run pytest -m l3`（`tests/test_l3_benchmark_smoke.py`）。

## Dependabot（依赖与 Actions）

[`.github/dependabot.yml`](.github/dependabot.yml) 会定期开 PR：**GitHub Actions**（仓库根，按周、同批合并）、**pip / `pyproject.toml`**（按月）、**`docs-site` npm**（按周）。合并前仍按本页 **Lint / Tests / parity** 自检。

## Smoke orchestration

Requires PySCF (`pip install qchem-stack[chem]`):

```bash
./scripts/venv-run python scripts/smoke_pipeline.py
./scripts/venv-run python scripts/smoke_pipeline.py --iqeb
./scripts/venv-run python scripts/smoke_pipeline.py --projection-trace
```

## Examples / tutorials

See `examples/` and `python examples/run_all_smoke.py` (best-effort; skips steps when PySCF or optional extras are missing).

**User-facing docs** (**Docusaurus** under `docusaurus-site/`，`npm start`，路由示例 `/guide/onboarding-three-paths`）：镜像源码 [`docusaurus-site/docs/guide/onboarding-three-paths.md`](docusaurus-site/docs/guide/onboarding-three-paths.md)。可选 **VitePress** 副本仍在 `docs-site/`（部分脚本与旧链接）。

教程交叉引用：[UCCSD Trotter + export](docusaurus-site/docs/tutorial/uccsd-trotter-export.md)、[ZNE × Qiskit repro](docusaurus-site/docs/tutorial/zne-qiskit-repro.md)、[Projection embedding deep dive](docusaurus-site/docs/tutorial/projection-embedding-deep-dive.md)。若新增 `configs/*.yaml` 且沿用既有 CI，仍在 `docs-site/` 下运行 `npm run sync:configs-table`，保持 [configs-packaged-list](docs-site/docs/product/configs-packaged-list.md) 同步。

**新用户三条路径**（P2-W7）：同上优先走 **Docusaurus** `onboarding-three-paths`。MD/ML 与 `repro` 字段冻结见 [工程记忆 §16](docs/工程记忆_Quantinuum对标与数据流技术文档.md)。P2 双月周历见 [与InQuanto能力差距与实施计划 — 附录 A](docs/与InQuanto能力差距与实施计划.md) 内 `### 8.`。
