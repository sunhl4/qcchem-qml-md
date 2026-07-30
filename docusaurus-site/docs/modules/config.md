---
title: config 模块
description: ExperimentConfig schema_version 2、加载/转储/校验、顶层块与迁移。
---

# config 模块

`qchem_stack.config` 将实验 YAML 变为类型化的 `ExperimentConfig`，是管线各阶段的唯一配置入口。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| 契约层 | 约束分子、SCF、活性空间、量子算法、后端与缓解的合法组合 |
| 选型 | [化学与嵌入](/guide/chemistry-and-embedding) · [配置目录](/reference/configs-catalog) |
| 工程约定 | 仓库 `docs/config_校验分层约定.md` |

配置层本身不做量子求解；它定义后续哈密顿量与算法的**契约空间**。

---

## 2. 理论

$$
\mathrm{cfg}: \mathcal{Y}_{\mathrm{YAML}} \rightarrow \mathrm{ExperimentConfig}
$$

校验分层：

1. **Schema** — Pydantic 字段类型与嵌套模型  
2. **跨字段** — `EXPERIMENT_CROSS_VALIDATORS`（算法×映射×嵌入等）  
3. **运行前** — `validate_experiment_for_run`（含 capability 门闩）  

`schema_version` **必须为** `"2"`（`SCHEMA_VERSION_CURRENT`）。非 `"2"` 的扁平旧 YAML 在加载时拒绝或先经迁移。

---

## 3. 实现

| API | 路径 | 行为 |
|-----|------|------|
| `load_experiment_config(path, *, strict_top_level_keys=False)` | `config/io.py` | 读 YAML → 版本检测 → 可选迁移 → `from_yaml_dict` |
| `dump_experiment_config(cfg)` | `config/io.py` | `model_dump(mode="json")` → `yaml.safe_dump` |
| `ExperimentConfig.from_yaml_dict(...)` | `config/experiment.py` | 预处理 + Pydantic + 交叉校验 |
| `validate_experiment_for_run(spec, *, caps)` | `config/_experiment_validation.py` | 完整运行门闩 |
| `validate_pre_quantum_contract(...)` | 同上 | 仅 pre-quantum 子集 |
| `migrate_config` / `migrate_config_file` | `config/migrations.py` | 顺序幂等迁移 |
| `resolve_pre_quantum_path(cfg)` | `config/_pre_quantum_path.py` | 选择哈密顿构建路径枚举 |

**迁移表**

| 类 | from → to | 说明 |
|----|-----------|------|
| `MigrationV1ToV2` | `1` → `2` | 扁平键 → 嵌套；写入 `schema_version: "2"` |
| `MigrationV3ToV2` | `3` → `2` | 展开 `scenario` + `overrides`（`compile_scenario_v3`） |

**`strict_top_level_keys`**：为 `True` 时，未知顶层键抛 `ConfigurationError`（须放入 `extra`）；默认未知顶层键并入 `extra`。

**`resolve_pre_quantum_path`** 返回 `PreQuantumPath`：

- `scf.driver == "precomputed"` → `precomputed_bundle`  
- `embedding.mode == PLUGIN` → `embedding_plugin`  
- Schmidt 生产路径 → `schmidt_atomic_production`  
- projection Mulliken → `projection_fragment_mulliken_mo`  
- 否则 → `canonical_active_space_integral_pack`  

公开再导出：`config/__init__.py`；`chem.pre_quantum_path` 为 shim。

---

## 4. YAML 顶层块

| 顶层键 | 作用 |
|--------|------|
| `schema_version` | **必须** `"2"` |
| `experiment_id` / `random_seed` | 实验标识与随机种子 |
| `molecule` | 几何、电荷、自旋 |
| `scf` | 驱动与收敛 |
| `active_space` | 电子/轨道、费米子映射 |
| `quantum` | 算法、ansatz、VQE、`pauli`、`tensornet` |
| `backend` | provider / shots |
| `mitigation` | ZNE / PMSV / stubs |
| `embedding` | Schmidt / DMET / projection / plugin |
| `compiler` | 编译 pass 束 |
| `chemistry_extended` | 扩展化学选项 |
| `nexus_analog` / `nexus_cloud` | Nexus 面 |
| `parity_integrations` | 对标探针开关 |
| `md_ml_export` | MD/ML QMEF 附着 |
| `gqe` | **顶层** GQE 块（不是 `quantum.algorithm`） |
| `extra` | 未知顶层键的落脚点 |

最小骨架：

```yaml
schema_version: "2"
molecule:
  name: H2
  charge: 0
  multiplicity: 1
scf:
  driver: pyscf
  basis: sto-3g
active_space:
  n_electrons: 2
  n_orbitals: 2
  fermion_qubit_mapping: jordan_wigner
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
backend:
  provider: statevector
```

---

## 5. Python

```python
from qchem_stack.config import (
    ExperimentConfig,
    load_experiment_config,
    dump_experiment_config,
    validate_experiment_for_run,
    resolve_pre_quantum_path,
)
from qchem_stack.sdk import load_experiment_config as sdk_load

cfg = load_experiment_config("configs/example_h2.yaml")
validate_experiment_for_run(cfg)
path = resolve_pre_quantum_path(cfg)
yaml_text = dump_experiment_config(cfg)
```

SDK：

```python
from qchem_stack.sdk import ExperimentConfig, load_experiment_config, run_pipeline_from_config
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.config import load_experiment_config, validate_experiment_for_run, resolve_pre_quantum_path; c=load_experiment_config('configs/example_h2.yaml'); validate_experiment_for_run(c); print(c.schema_version, resolve_pre_quantum_path(c).value)"
```

期望：退出码 `0`；打印 `2` 与某 `PreQuantumPath` 值（如 `canonical_active_space_integral_pack`）。

严格顶层键：

```bash
python3 -c "from qchem_stack.config import load_experiment_config; load_experiment_config('configs/example_h2.yaml', strict_top_level_keys=True); print('ok')"
```

---

## 7. 调优建议

- 新配置一律写 `schema_version: "2"`；旧扁平文件先 `migrate_config_file`。  
- CI / 生产加载用 `strict_top_level_keys=True`，避免拼写错误落入 `extra`。  
- 改嵌入或 `scf.driver` 后先看 `resolve_pre_quantum_path`，确认哈密顿路径符合预期。  
- 全字段索引：仓库 `docs/reference/config_field_index.md`。

---

## 8. 相关

- [chem](./chem/) · [orchestration](./orchestration) · [quantum](./quantum/)  
- [integrations](./integrations)（`gqe:` 顶层块） · [contracts](./contracts)
