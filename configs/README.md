# Config 示例目录（`configs/`）

本目录包含 **118** 个顶层 YAML 文件，另加 profiles / scenarios：

| 类别 | 数量 | CI 门控 |
|------|------|---------|
| **ExperimentConfig**（`schema_version: 2` + `molecule`） | **107** | `python scripts/check_parity_export_sample.py` 自动发现并跑 config-only parity export |
| **MdValidationLoopConfig**（`max_rounds` + `force_field_backend`） | **11** | 同上脚本末尾校验 YAML 可加载 |
| **合计（顶层）** | **118** | 无手工维护的抽样子集 |
| `configs/profiles/` | **3** | 配置档位 |
| `configs/scenarios/` | **8** | `qchem-run --list-scenarios` |

复制 [`_template.yaml`](_template.yaml) 并按需修改字段。新增 experiment YAML 会自动纳入 CI，**无需**再编辑 `SAMPLE_CONFIGS_REL`。

## 完整文件名列表（自动生成）

运行 `python scripts/generate_configs_catalog.py` 更新：

- [`docs/generated/configs_catalog_snippet.md`](../docs/generated/configs_catalog_snippet.md)
- [`docusaurus-site/docs/reference/configs-catalog-body.md`](../docusaurus-site/docs/reference/configs-catalog-body.md)

CI 对两份生成物做 `git diff --exit-code` 校验。本 README 仅保留分类说明，不再手工维护逐文件枚举。

## 文档站入口

- [配置目录页](../docusaurus-site/docs/reference/configs-catalog.md)
- [配置字段参考](../docusaurus-site/docs/reference/config-fields/index.md)
