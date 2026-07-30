---
title: chem · Schmidt 生产管线
description: schmidt_production_pipeline_v1：闭壳层 RHF 杂质积分、浴轨道与约束。
---

# chem · Schmidt 生产管线

本页聚焦杂质积分与审计契约 `schmidt_production_pipeline_v1`。DMET 循环与 YAML 编排见 [embedding-dmet](./embedding-dmet)。

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| Schmidt / 纠缠浴 | 与 DMET 浴轨道同一谱系（Knizia & Chan 等） |
| 杂质模型 | 片段 AO 空间 ⊕ 环境密度诱导的浴 |

目标：给定闭壳层 RHF 与片段原子，构造**正交杂质轨道**上的空间积分 $(E_0, h_1, h_2)$，供 FCI / 映射 / 量子求解。本栈硬限制：**仅 RHF/RKS 参考**；ROHF/UHF 抛 `SchmidtProductionError`。

---

## 2. 理论思想

1. 从全局 AO 密度 $D$ 与重叠 $S$ 出发。  
2. 片段原子定义片段 AO 子空间；环境块 $(D_e, S_e)$ 的广义特征问题给出候选浴。  
3. 取领先浴轨道，并与片段空间做 $S$-正交化，得 $C_{\mathrm{imp}}$。  
4. 杂质度量应满足

$$
C_{\mathrm{imp}}^{T} S\, C_{\mathrm{imp}} \approx I
$$

（容差 `SCHMIDT_ORTHONORMALITY_TOLERANCE`）。  
5. Fock 变换给出 $h_1$；`impurity_eri_chemist` 给出 $h_2$。

电子数在杂质空间上计数，可选 FCI 参考与化学势二分。

---

## 3. 本栈实现

核心模块：`chem/embedding/schmidt_production.py`。

| API | 作用 |
|-----|------|
| `build_schmidt_impurity_integrals(rhf, *, fragment_atom_indices, n_bath_orbitals, ...)` | → `SchmidtImpurityModel` |
| `SchmidtImpurityModel` | `constant`、`h1`、`h2`、`C_imp_ao`、电子计数 |
| `fci_impurity_spatial_ground` / `fci_fragment_ground_state` | FCI 参考 |
| `bisection_mu_for_fragment_electron_count` | $\mu$ 二分 |

管线装配：`pre_quantum_schmidt.py` 的 `schmidt_hamiltonian_and_context`。  
模型 / ERI：`schmidt_production_model.py`、`impurity_eri.py`。

**Schema IDs**

- `schmidt_impurity_integrals_v1`  
- `schmidt_production_pipeline_v1`  
- `schmidt_fci_fragment_v1`

### 硬约束

- 参考类 **RHF 或 RKS only**  
- `scf.method='RHF'` 在 `schmidt_hamiltonian_and_context` 强制  
- `n_bath_orbitals \gt 0`；片段与环境 AO 集均非空  
- 杂质空间轨道数 $n_{\mathrm{imp}}$ 不超过 `max_impurity_spatial_orbitals`（默认 14）  
- **`active_space_yaml_ignored_for_qh: true`**：YAML CAS 尺寸对主 `qh` 仅账本意义  

---

## 4. YAML 参数表

Schmidt 字段嵌在 DMET 块（见 [DMET](./embedding-dmet)）：

```yaml
embedding:
  mode: dmet
  dmet:
    hamiltonian_source: schmidt_atomic_production
    schmidt:
      fragment_atom_indices: [0, 1]
      n_bath_spatial: 2
      max_impurity_spatial_orbitals: 14
      run_mu_bisection: false
      attach_fci_reference: true
      fci_reference_max_spatial_orbitals: 8
      dmet_max_cycles: 1
      dmet_mixing_alpha: 0.35
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `fragment_atom_indices` | `[]` | 片段原子 |
| `n_bath_spatial` | `2` | 浴轨道数 |
| `max_impurity_spatial_orbitals` | `14` | 杂质帽 |
| `attach_fci_reference` | `true` | 附 FCI 能量（尺寸受限） |
| `run_mu_bisection` | `false` | 片段电子数化学势 |

路径：`resolve_pre_quantum_path` → `schmidt_atomic_production`。

---

## 5. Python 调用

```python
import qchem_stack.chem.embedding.schmidt_production as sp
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path

cfg = load_experiment_config("configs/example_h2_dimer_dmet_self_consistent.yaml")
print(resolve_pre_quantum_path(cfg))
print(hasattr(sp, "build_schmidt_impurity_integrals"))
```

端到端：

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_dimer_dmet_self_consistent.yaml")
# 检查 pre_quantum meta / audit 中的 schmidt_production_pipeline_v1 字段
```

---

## 6. 验证命令

```bash
pytest tests/integrations/test_schmidt_embedding_production.py \
  tests/chem/test_embedding.py -q

python -c "import qchem_stack.chem.embedding.schmidt_production as sp; print('ok', sp.__name__)"
```

期望打印 `ok ...`。

---

## 7. 调参建议

| 症状 | 建议 |
|------|------|
| `SchmidtProductionError` / 方法不符 | 改用闭壳层 `RHF`；勿用 UHF/ROHF |
| 杂质超帽 | 减片段原子或 `n_bath_spatial` |
| 正交性告警 | 检查几何 / 基组；环境 AO 是否为空 |
| CAS YAML「无效」 | 预期行为：主 `qh` 来自杂质，不来自 `active_space.cas` |
| 只要积分烟雾 | `dmet_max_cycles: 1`、`attach_fci_reference: true` |

---

## 8. 相关

- [DMET](./embedding-dmet) · [嵌入总览](./embedding) · [双线路](./dual-ingress)  
- 仓库：`docs/说明_embedding配置.md`  
- 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
