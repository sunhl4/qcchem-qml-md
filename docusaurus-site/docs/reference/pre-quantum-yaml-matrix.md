---
title: Pre-quantum YAML 组合矩阵
description: driver × embedding × active_space 允许组合摘要；完整表与校验入口。
keywords:
  - pre-quantum
  - ExperimentConfig
  - validate_pre_quantum_contract
---

# Pre-quantum YAML 组合矩阵

进入量子阶段之前，`ExperimentConfig` 的 **`scf.driver` × `embedding.mode` × `active_space.strategy`** 组合受门禁约束。完整验收表与图例见仓库：

[docs/pre_quantum_yaml_matrix.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/pre_quantum_yaml_matrix.md)

规则实现：`qchem_stack.config._experiment_validation`。一次性调用：

```python
from qchem_stack.config import load_experiment_config, validate_pre_quantum_contract

cfg = load_experiment_config("configs/example_h2.yaml")
validate_pre_quantum_contract(cfg)
```

负例测试：`tests/config/test_config_pre_quantum_combos.py`。

---

## 关键禁止 / 受限组合（摘要）

| 规则 | 说明 |
|------|------|
| `precomputed` + live embedding | `embedding.mode` 为 `dmet` / `projection`（及 live Schmidt / AVAS）→ **拒绝**；bundle-only |
| `precomputed` + benchmark/RDM | `classical_benchmark_enabled` 或非 `none` 的 `rdm_correction_method` → **拒绝** |
| Schmidt 要求 RHF | `dmet.hamiltonian_source=schmidt_atomic_production` 需要 `scf.method=RHF` |
| Capability 门控 | Schmidt / Mulliken projection / AVAS 在 load 期按 `SolverCapabilities`；无 capability 的后端拒绝 live embedding |
| DMET 循环上限 | `embedding.dmet.schmidt.dmet_max_cycles` $\le$ 50（`SCHMIDT_DMET_MAX_CYCLES_LIMIT`） |
| PBC | 开启周期边界时禁止 CASSCF audit / AVAS refine |
| Plugin 路径 | `embedding.mode=plugin` 走 decomposition JSON（符号 **P**） |

允许主路径示例：`pyscf` + `none` + `cas`/`manual`/`avas`；`psi4` 对应路径需 Psi4 + capability；`precomputed` + `embedding.mode=none`。

Schema v2 嵌套：DMET 在 `embedding.dmet.*`，projection 在 `embedding.projection.*`。见 [embedding 字段](/reference/config-fields/embedding)。

---

## PreQuantumPath 分支（稳定枚举）

- `precomputed_bundle`
- `embedding_plugin`
- `schmidt_atomic_production`
- `projection_fragment_mulliken_mo`
- `canonical_active_space_integral_pack`

---

## 相关

- [config 模块](/modules/config) · [化学与嵌入](/guide/chemistry-and-embedding)
- [FAQ：bundle_path](/faq/) · [scf 字段](/reference/config-fields/scf)
