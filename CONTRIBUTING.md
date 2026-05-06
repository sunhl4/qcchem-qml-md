# Contributing to qchem-stack

**工程文档总索引**（母稿路径、合并记录、阅读顺序）：[docs/技术文档_软件工程文档总索引.md](docs/技术文档_软件工程文档总索引.md)。

## Tests

From the repo root (with `src` on `PYTHONPATH`, or after `pip install -e ".[dev]"`):

```bash
pytest tests -q --tb=short
```

Optional heavier chemistry smoke (multi-fragment DMET exact, etc.):

```bash
pytest -m slow tests/test_dmet_fragment_exact.py -q --tb=short
```

Targeted markers (see `pyproject.toml`): `-m l1_excited`, `-m l1_md_ml`, `-m l3`.

### CI markers (PR 必跑)

`.github/workflows/ci.yml` 在完整 `pytest tests` 之后还会跑 **`pytest -m l1_excited`** 与 **`pytest -m l1_md_ml`**（非「仅本地可选」）。激发态/VQD/QSE/SCEOM 等回归以 `l1_excited` 为准；`md_bridge` 与 MD/ML 契约以 `l1_md_ml` 为准（长板字段与 `repro` 对齐清单见 [Y1_residual_partial_SLA_template.md](docs/Y1_residual_partial_SLA_template.md) 表末行）。

**Parity / `computables_rich`（可选 repro）**：`parity_integrations.include_computables_rich_in_repro: true` 时的 workflow-preview 对齐见 `tests/test_workflow_preview_repro_alignment.py`；FastAPI 侧 `POST /v1/meta/workflow-preview` 烟测见 `tests/test_api_runs.py`（需 `pip install -e ".[api]"`，CI 已装）。

## Parity export / golden fixture

Config-only Methods alignment (no PySCF run):

```bash
python scripts/export_parity_criteria_table.py configs/example_h2.yaml
python scripts/check_parity_export_sample.py
```

After intentional contract changes to `inquanto_gap_categories()` or export columns, regenerate `tests/fixtures/parity_export_example_h2_config_only.json` from `configs/example_h2.yaml` and normalize `source_config` to `configs/example_h2.yaml` if the exporter emits OS-specific separators.

新增「判据表导出」相关 `configs/*.yaml` 时，请同步扩展 `scripts/check_parity_export_sample.py` 中的 `SAMPLE_CONFIGS_REL`（见 [P1_completion_audit.md](docs/P1_completion_audit.md) §5 队列项 12）。

## Smoke orchestration

Requires PySCF (`pip install qchem-stack[chem]`):

```bash
python scripts/smoke_pipeline.py
python scripts/smoke_pipeline.py --iqeb
python scripts/smoke_pipeline.py --projection-trace
```

## Examples / tutorials

See `examples/` and `python examples/run_all_smoke.py` (best-effort; skips steps when PySCF or optional extras are missing).

**User-facing docs** (VitePress under `docs-site/`): [UCCSD Trotter + export](docs-site/docs/tutorial/uccsd-trotter-export.md), [ZNE × Qiskit repro](docs-site/docs/tutorial/zne-qiskit-repro.md), [Projection embedding deep dive](docs-site/docs/tutorial/projection-embedding-deep-dive.md). After adding `configs/*.yaml`, run `npm run sync:configs-table` from `docs-site/` so [configs-packaged-list](docs-site/docs/product/configs-packaged-list.md) stays in sync (CI may enforce this).

**新用户三条路径**（P2-W7）：入门顺序见 [onboarding-three-paths](docs-site/docs/guide/onboarding-three-paths.md)（`npm run docs:dev` 在 `docs-site/` 下打开路由 `/guide/onboarding-three-paths`）。MD/ML 与 `repro` 字段冻结见 [md_bridge_repro_freeze_list.md](docs/md_bridge_repro_freeze_list.md)。P2 双月周历见 [P2_详细实施计划.md](docs/P2_详细实施计划.md) §8。
