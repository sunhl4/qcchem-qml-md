---
title: chem · 嵌入总览
description: embedding.mode 分支、PreQuantumPath 解析与分册导航。
---

# chem · 嵌入总览

本页是嵌入子系统的**导航与语义总览**。生产细节见分册：

| 模式 / 路径 | 深读 |
|-------------|------|
| DMET + Schmidt 源 | [embedding-dmet](./embedding-dmet) |
| Mulliken MO projection | [embedding-projection](./embedding-projection) |
| Schmidt 杂质积分 | [embedding-schmidt](./embedding-schmidt) |
| 离线 bundle | [dual-ingress](./dual-ingress) |

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| DMET | Knizia & Chan, Phys. Rev. Lett. **109**, 186404 (2012); Wouters et al. |
| Projection embedding | Manby / Miller 等投影嵌入族 |
| Schmidt 分解杂质 | 纠缠浴轨道构造（与 DMET 浴同源思想） |

大分子全活性空间变分不可扩展。嵌入把系统拆成杂质 / 片段 + 环境，只对小活性问题建 `QubitHamiltonian`。本栈在 **pre_quantum** 阶段选定分支，并保证：**主变分哈密顿量在变分前固定**；变分后的 embedding workflow 多为审计，不改写主 `qh`。

---

## 2. 理论思想

语义（`embedding/hamiltonian_semantics.py`）：

- `hamiltonian_fixed_before_variational = True`  
- `post_variational_embedding_audit_only = True`

即：变分插件始终优化 pre_quantum 产出的 `qh`；嵌入循环若存在，其目的是构造 / 自洽该 `qh`，而不是在 VQE 之后偷偷换算符。

---

## 3. 本栈：模式与路径解析

### 3.1 `EmbeddingMode`

`config/embedding_enums.py`：`none` | `dmet` | `projection` | `plugin`  
默认实验：`EmbeddingNone`。判别联合：`EmbeddingSpec`（`Field(discriminator="mode")`）。

### 3.2 `resolve_pre_quantum_path`

权威实现：`config/_pre_quantum_path.py`（chem 侧重导出）。

解析顺序：

1. `scf.driver == "precomputed"` → `precomputed_bundle`  
2. `embedding.mode == plugin` → `embedding_plugin`  
3. `is_schmidt_production(emb)` → `schmidt_atomic_production`  
4. `is_projection_mulliken(emb)` → `projection_fragment_mulliken_mo`  
5. 否则 → `canonical_active_space_integral_pack`

`PreQuantumPath` 字面量即上表右侧。分支构建器注册于 `pre_quantum_build` / `pre_quantum_branches.py`。

### 3.3 共享基字段

```yaml
embedding:
  mode: none
  embedding_input_representation: mo    # mo | ao | lowdin_orth_ao
  n_scf_cycles_embedding: null
  classical_reference_method: null
  oniom_layers_v1: []
```

---

## 4. YAML 速查（按模式）

| `mode` | 关键子块 | 典型触发 |
|--------|----------|----------|
| `none` | — | 全局 CAS → 标准积分包 |
| `dmet` | `embedding.dmet` (+ `schmidt`) | `hamiltonian_source: schmidt_atomic_production` |
| `projection` | `embedding.projection` | `quantum_hamiltonian: fragment_mulliken_mo` |
| `plugin` | 插件 id | 外部分解插件 |

完整字段表见各分册；配置校验：`config/_embedding_validation.py`。

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path

cfg = load_experiment_config("configs/example_h2.yaml")
print(resolve_pre_quantum_path(cfg))
# → PreQuantumPath.canonical_active_space_integral_pack（典型）

cfg_d = load_experiment_config("configs/example_h2_dimer_dmet_self_consistent.yaml")
print(cfg_d.embedding.mode, resolve_pre_quantum_path(cfg_d))
```

---

## 6. 验证命令

```bash
pytest tests/chem/test_pre_quantum_path.py \
  tests/chem/test_embedding.py \
  tests/config/test_config_embedding_yaml.py -q

python -c "from qchem_stack.config import load_experiment_config; from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path; c=load_experiment_config('configs/example_h2.yaml'); print(resolve_pre_quantum_path(c))"
```

---

## 7. 调参 / 选型

| 需求 | 选择 |
|------|------|
| 小分子全局 CAS | `mode: none` |
| 片段 + 浴自洽 | [DMET + Schmidt](./embedding-dmet) |
| 按原子 Mulliken 选 MO | [projection](./embedding-projection) |
| 只要杂质积分细节 | [Schmidt 生产管线](./embedding-schmidt) |
| 无 live SCF | [precomputed](./dual-ingress)（会短路嵌入 live 路径） |

注意：`scf.driver=precomputed` **优先**于嵌入模式，挡住 Schmidt / projection live 钩子。

---

## 8. 相关

- 分册：[DMET](./embedding-dmet) · [projection](./embedding-projection) · [Schmidt](./embedding-schmidt)  
- [双线路](./dual-ingress) · [哈密顿量](./hamiltonian) · [chem 索引](/modules/chem/)  
- 仓库：`docs/说明_embedding配置.md` · 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
