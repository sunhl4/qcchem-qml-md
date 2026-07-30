---
title: quantum 模块
description: 变分 / 自适应 / 激发态枢纽；链向 algorithms/ 深读。
---

# quantum 模块

`qchem_stack.quantum` 在固定 `QubitHamiltonian` 上运行变分、自适应与激发态算法。  
**使用者优先进入 [算法深读索引](./algorithms/)**。选型：[算法与 ansatz 菜单](/guide/algorithm-and-ansatz-menu)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| 包 | `src/qchem_stack/quantum/` |
| 阶段 | 管线 `variational`；激发态侧车 `excited` |
| 上游 | `PreQuantumInput` / `qh`（由 chem + pre_quantum 固定） |
| 下游 | protocols、backends、orchestration finalize |
| 深读 | [algorithms/](./algorithms/)（论文 / 数学 / YAML / 调用） |

本页是**包枢纽**；单算法文献见各深读页。

---

## 2. 理论

VQE 目标：

$$
E(\boldsymbol{\theta}) = \min_{\boldsymbol{\theta}} \langle \psi(\boldsymbol{\theta}) | \hat{H} | \psi(\boldsymbol{\theta}) \rangle
$$

UCCSD 示意：

$$
|\psi\rangle = e^{\hat{T}-\hat{T}^\dagger}|{\mathrm{HF}}\rangle
$$

外层 `quantum.algorithm` 与内层 `variational.ansatz` 经 `variational_plugins` 物化。  
**GQE 不是** `quantum.algorithm`：使用顶层 `gqe:` 块（见 [GQE 深读](./algorithms/gqe) · [integrations](../integrations)）。

---

## 3. 实现

| 能力 | 入口 |
|------|------|
| Ansatz 注册 | `quantum.ansatz_registry` |
| 算法注册 | `quantum.algorithm_registry` |
| 变分阶段 | `variational_plugins.registry.run_variational_stage`（由编排调用） |
| 算符池 | `operator_pool_registry`（ADAPT/IQEB/iQCC） |
| 激发态插件 | `excited_plugins` |

摘要页（短）：[ansatz-algorithms](./ansatz-algorithms) · [adapt-iqeb](./adapt-iqeb) · [excited-states](./excited-states)。

---

## 4. YAML

```yaml
schema_version: "2"
quantum:
  algorithm: vqe          # adapt | iqeb | iqcc | sa_vqe | …
  vqe:
    depth: 2
    max_iter: 80
  variational:
    ansatz: hea           # uccsd | qcc | …
  pauli:
    use_protocol: false
  tensornet:
    expectation_stub: false
    contraction_engine: stub
# GQE 在顶层，不在此：
# gqe:
#   enabled: true
```

| 线索 | 深读 |
|------|------|
| `vqe` + `hea` | [VQE/HEA](./algorithms/vqe-hea) |
| `uccsd` | [UCCSD](./algorithms/uccsd) |
| `adapt` / `iqeb` / `iqcc` | [ADAPT](./algorithms/adapt-vqe) · [IQEB](./algorithms/iqeb) · [iQCC](./algorithms/iqcc) |
| `excited.*` | [VQD](./algorithms/vqd) · [QSE](./algorithms/qse) · [SCEOM](./algorithms/sceom) |
| `quantum.pauli` | [Pauli 协议](./algorithms/pauli-protocol) |
| 顶层 `gqe:` | [GQE](./algorithms/gqe) |

---

## 5. Python

```python
from qchem_stack.quantum.ansatz_registry import (
    list_registered_ansatz_ids,
    ansatz_registry_export,
)
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
from qchem_stack.sdk import run_pipeline_from_config, load_experiment_config

print(list_registered_ansatz_ids())
print(list_registered_algorithm_ids())
cfg = load_experiment_config("configs/example_h2.yaml")
print(cfg.quantum.algorithm, cfg.quantum.variational.ansatz)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids; ids=list_registered_ansatz_ids(); assert 'hea' in ids and 'uccsd' in ids; print(len(ids))"
```

期望：正整数（注册 ansatz 数）。

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print('quantum_hub_ok', 'repro' in o)"
```

期望：`quantum_hub_ok True`。

---

## 7. 调优建议

- 先定映射与活性空间（[chem](../chem/)），再换 ansatz。  
- 自适应路径先读 [operator-pools](./algorithms/operator-pools)。  
- 上 shots 前读完 [Pauli 深读](./algorithms/pauli-protocol) 与 [mitigation](../mitigation)。  
- 自定义： [custom-plugin](./algorithms/custom-plugin)。

任务路径：[P1–P5](../reading-paths)。

---

## 8. 相关

### 深读（algorithms/）

- 基态：[vqe-hea](./algorithms/vqe-hea) · [uccsd](./algorithms/uccsd) · [adapt-vqe](./algorithms/adapt-vqe) · [iqeb](./algorithms/iqeb) · [iqcc](./algorithms/iqcc) · [qcc-paired](./algorithms/qcc-paired) · [sa-vqe](./algorithms/sa-vqe) · [uccgd](./algorithms/uccgd) · [research-ansatze](./algorithms/research-ansatze)  
- 激发态：[vqd](./algorithms/vqd) · [qse](./algorithms/qse) · [sceom](./algorithms/sceom)  
- 测量 / 其他：[pauli-protocol](./algorithms/pauli-protocol) · [qpe](./algorithms/qpe) · [vqs](./algorithms/vqs) · [gqe](./algorithms/gqe) · [custom-plugin](./algorithms/custom-plugin) · [operator-pools](./algorithms/operator-pools)

### 模块邻接

- [chem](../chem/) · [protocols](../protocols) · [backends](../backends) · [orchestration](../orchestration) · [integrations](../integrations) · [模块总览](../)
