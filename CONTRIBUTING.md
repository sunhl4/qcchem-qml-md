# Contributing to qchem-stack

**对标与工程母稿（三份 + 契约矩阵）**：[竞争定位](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) · [工程记忆](docs/工程记忆_Quantinuum对标与数据流技术文档.md) · [差距与实施计划](docs/public_parity_matrix.md)（含 **附录 A–F**：P2 / Y1 / L1 / B→J / P1 审计 / 不排期项）· [parity 矩阵](docs/public_parity_matrix.md)。**详细技术契约**：`docs/技术文档_*.md`、`mitigation_PMSV_ZNE_Qermit_mapping.md`、`launch_retrieve_nexus_analog.md`。

## Local Python environment (default)

[`scripts/venv-run`](scripts/venv-run) runs commands with the Python chosen by **`QCHEM_STACK_PYTHON`** (if set), otherwise the default interpreter path at the top of that script (repo default: maintainer `conda base` / workstation path). Example override:

```bash
export QCHEM_STACK_PYTHON=/path/to/python
./scripts/venv-run pytest tests -q --tb=short
```

## 维护角色（原 `docs/MAINTAINERS.md`）

| 角色 | 职责 |
|------|------|
| **契约 / capability 导出** | 产品与 HTTP 控制台同源模块 **`qchem_stack.protocols.product_contract`**（ gap 列表、capability_map、parity export 的稳定键常量等）；workflow 预览 **`qchem_stack.integrations.workflow_preview`**。布局见 [Product contracts and workflow-preview](#product-contracts-and-workflow-preview-stable-imports)。矩阵与路线图仍按需维护（见 [public_parity_matrix.md §5](docs/public_parity_matrix.md)）。 |
| **度量与台账** | 月度更新 [与Vendor platform… — 附录 B](docs/public_parity_matrix.md) §3；主表 yes/partial/n/a 可用 `python scripts/count_parity_matrix_main_tables.py` 对照手填。 |
| **签字合并 gate** | 合并前：`ruff check src/qchem_stack tests scripts examples`、`ruff format --check`（同上路径）、`pytest`、`python scripts/check_parity_export_sample.py`；在 [附录 C](docs/public_parity_matrix.md) 末行可写明 **实名 + 日期**。 |

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

`.github/workflows/ci.yml` 在完整 `pytest tests` 之后还会跑 **`pytest -m l1_excited`** 与 **`pytest -m l1_md_ml`**（非「仅本地可选」）。激发态/VQD/QSE/SCEOM 等回归以 `l1_excited` 为准；`md_bridge` 与 MD/ML 契约以 `l1_md_ml` 为准（长板字段与 `repro` 对齐清单见 [与Vendor platform能力差距与实施计划 — 附录 B §6](docs/public_parity_matrix.md#y1-residual-partial-sla-template) 表末行）。

**Parity / `computables_rich`（可选 repro）**：`parity_integrations.include_computables_rich_in_repro: true` 时的 workflow-preview 对齐见 `tests/test_workflow_preview_repro_alignment.py`；FastAPI 侧 `POST /v1/meta/workflow-preview` 烟测见 `tests/test_api_runs.py`（需 `pip install -e ".[api]"`，CI 已装）。

## PySCF boundary coding rule

For PySCF-related refactors, keep module boundaries stable:

- Put active-space, one-body, and Lowdin matrix transformations in `src/qchem_stack/chem/integrals/`.
- Put AO/Lowdin view dataclasses in `src/qchem_stack/chem/systems/`.
- Keep `src/qchem_stack/chem/drivers/pyscf_driver.py` focused on compatibility facade and workflow orchestration.

If you add new helper logic, prefer the new modules first and keep legacy import paths compatible where practical.

## Product contracts and workflow-preview (stable imports)

- **Capability gaps / product surface literals** live in **`src/qchem_stack/protocols/product_contract.py`** (`product_gap_categories`, `PRODUCT_CAPABILITY_MAP`, `PARITY_EXPORT_V3_STABLE_KEYS`, mitigation / differentiation bundles, expectation-path helpers). HTTP **`GET /v1/meta/capability-surface`** MUST stay aligned via `tests/test_api_runs.py::test_capability_surface_matches_product_contract`.
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

新增「判据表导出」相关 `configs/*.yaml` 时，请同步扩展 `scripts/check_parity_export_sample.py` 中的 `SAMPLE_CONFIGS_REL`（见 [与Vendor platform能力差距与实施计划 — 附录 E](docs/public_parity_matrix.md) 原 §5 队列项 12）。

### 算符池与 L3 基准（ADAPT / IQEB）

- **新池 id 或 YAML 别名**：除 `quantum/operator_pool_registry.py`、`config.py` 中 `adapt_pool_id` / `iqeb_pool_id` Literal 外，按需更新 `tests/test_operator_pool_registry_export.py`、`docs/public_parity_matrix.md` 与 [算法面广度索引](docs/算法面广度_Vendor platform_Tangelo对照索引.md)。若增加**代表运行配置**，同步 `scripts/check_parity_export_sample.py`、`tests/test_export_parity_golden.py` 参数表，并评估是否加入 `integrations/l3_algorithm_benchmark.py` 的 `L3_PYTEST_YAMLS` / `DEFAULT_BENCHMARK_YAMLS`。HTTP **`GET /v1/meta/capability-surface`** 返回 **`schema: capability_surface_v2`**（参见 `src/qchem_stack/api/app.py`），与 **`tests/test_api_runs.py::test_capability_surface_matches_product_contract`** 同源对拍。
- **可选重型门禁**：`QCHEM_RUN_L3=1 ./scripts/venv-run pytest -m l3`（`tests/test_l3_benchmark_smoke.py`）。

## Dependabot（依赖与 Actions）

[`.github/dependabot.yml`](.github/dependabot.yml) 会定期开 PR：**GitHub Actions**（仓库根，按周、同批合并）、**pip / `pyproject.toml`**（按月）、**`docusaurus-site` npm**（按周）。合并前仍按本页 **Lint / Tests / parity** 自检。

## Smoke orchestration

Requires PySCF (`pip install qchem-stack[chem]`):

```bash
./scripts/venv-run python scripts/smoke_pipeline.py
./scripts/venv-run python scripts/smoke_pipeline.py --iqeb
./scripts/venv-run python scripts/smoke_pipeline.py --projection-trace
```

## Examples / tutorials

See `examples/` and `python examples/run_all_smoke.py` (best-effort; skips steps when PySCF or optional extras are missing).

**User-facing docs**（**Docusaurus**，目录 `docusaurus-site/`，`npm start`，路由示例 `/guide/onboarding-three-paths`）：源码 [`docusaurus-site/docs/guide/onboarding-three-paths.md`](docusaurus-site/docs/guide/onboarding-three-paths.md)。

教程交叉引用：[UCCSD Trotter + export](docusaurus-site/docs/tutorial/uccsd-trotter-export.md)、[ZNE × Qiskit repro](docusaurus-site/docs/tutorial/zne-qiskit-repro.md)、[Projection embedding deep dive](docusaurus-site/docs/tutorial/projection-embedding-deep-dive.md)。新增或重命名 `configs/*.yaml` 时，请在对应教程 / 产品页（`docusaurus-site/docs/`）与 `docs/public_parity_matrix.md` 中按需补链。

**新用户三条路径**（P2-W7）：同上优先走 **Docusaurus** `onboarding-three-paths`。MD/ML 与 `repro` 字段冻结见 [工程记忆 §16](docs/工程记忆_Quantinuum对标与数据流技术文档.md)。P2 双月周历见 [与Vendor platform能力差距与实施计划 — 附录 A](docs/public_parity_matrix.md) 内 `### 8.`。
