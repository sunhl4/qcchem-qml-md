# Config 示例目录（`configs/`）

本目录包含 **105** 个 YAML 文件：

| 类别 | 数量 | CI 门控 |
|------|------|---------|
| **ExperimentConfig**（`schema_version: 2` + `molecule`） | **97** | `python scripts/check_parity_export_sample.py` 自动发现全部 97 个并跑 config-only parity export |
| **MdValidationLoopConfig**（`max_rounds` + `force_field_backend`） | **8** | 同上脚本末尾校验 YAML 可加载 |
| 合计 | **105** | 无手工维护的抽样子集 |

复制 [`_template.yaml`](_template.yaml) 并按需修改字段。新增 experiment YAML 会自动纳入 CI，**无需**再编辑 `SAMPLE_CONFIGS_REL`。

## 完整文件名列表（自动生成）

运行 `python scripts/generate_configs_catalog.py` 更新：

- [`docs/generated/configs_catalog_snippet.md`](../docs/generated/configs_catalog_snippet.md)
- [`docusaurus-site/docs/reference/configs-catalog-body.md`](../docusaurus-site/docs/reference/configs-catalog-body.md)

CI 对两份生成物做 `git diff --exit-code` 校验。本 README 仅保留分类说明，不再手工维护逐文件枚举。

## Experiment profiles (`configs/profiles/`)

Named overlays applied via `qchem_stack.config.experiment_profiles.apply_experiment_profile`:

| Profile | Template | Purpose |
|---------|----------|---------|
| `minimal` | [`profiles/minimal_h2.yaml`](profiles/minimal_h2.yaml) | Precomputed SCF, no Pauli protocol |
| `research` | [`profiles/research_h2.yaml`](profiles/research_h2.yaml) | Rich parity / workflow preview sidecars |
| `production` | [`profiles/production_h2.yaml`](profiles/production_h2.yaml) | Protocol-on defaults + repro preview |

Merge a profile dict onto any base experiment YAML, or load a template and edit `experiment_id` / `molecule`.

## 校验与 export

- **全量门控**：`python scripts/check_parity_export_sample.py`
- 允许的组合：[`docs/pre_quantum_yaml_matrix.md`](../docs/pre_quantum_yaml_matrix.md)
