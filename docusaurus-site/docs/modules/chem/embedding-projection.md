---
title: chem · Projection 嵌入
description: Mulliken MO 片段投影哈密顿量：理论、YAML、审计与边界。
---

# chem · Projection 嵌入

本页覆盖 `embedding.mode: projection` 且 `quantum_hamiltonian: fragment_mulliken_mo` 的生产路径。

相关：[嵌入总览](./embedding) · [哈密顿量](./hamiltonian) · [Solver 能力位](./solvers)。

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| Projection embedding 族 | Manby, Miller 等；DFT-in-DFT / wavefunction-in-DFT 投影 |
| Mulliken 布居 | Mulliken, J. Chem. Phys. **23**, 1833 (1955) |

目标：按**原子片段**从全局 MO 中选出活性轨道子集，在该子空间上建量子哈密顿量，而不是把整个分子塞进 CAS。本栈路径是 **Mulliken 权重排序 + CASCI 风格空间积分**，审计中明确：**不是**完整多体环境波函数投影嵌入。

---

## 2. 理论思想

对原子集合 $A$，Mulliken 型 AO 权重把每个 MO $i$ 的片段权重 $w_i$ 排序；取排名靠前的轨道作为活性空间，其余作冻结 / 虚空。  
在选定 MO 系数 $C_{\mathrm{act}}$ 上抽取空间积分 $h_{pq}$、$g_{pqrs}$，再映射为 $\hat{H}_{\mathrm{qubit}}$。

认识论边界（写入 audit）：环境相关不通过完整投影算符进入杂质哈密顿量；结果用于管线验证与片段启发式，而非声称工业级投影嵌入等价物。

---

## 3. 本栈实现

### 3.1 触发

- `embedding.mode: projection`  
- `embedding.projection.quantum_hamiltonian: fragment_mulliken_mo`  
- `fragment_atom_indices` 非空  
- → `PreQuantumPath.projection_fragment_mulliken_mo`

默认 `quantum_hamiltonian: global_active_space` **不会**走 Mulliken 片段路径。

### 3.2 算法步骤

实现：`embedding/projection_hamiltonian.py`、`embedding/ao_fragment.py`。

1. `mulliken_mo_populations_on_atoms` → 片段权重  
2. `select_active_mo_indices` → 活性 MO  
3. 按 CASCI `ncore` 冻结；置换 MO：`frozen | active | rest`  
4. `casci_spatial_integrals_on_mo_coeff` → chemist $h_1$、$h_2$  
5. `qubit_hamiltonian_from_spatial_chemist_integrals` + 用户映射  

审计 schema：`projection_mulliken_mo_audit_v1`。  
工作流标签：`ProjectionEmbeddingConfig`（`embedding/projection.py`）。

### 3.3 约束

- `scf.method` 必须为 `RHF`  
- `n_active_electrons` 为偶数；`ncas` 不超过 $n_{\mathrm{mo}}$  
- Solver 需 `supports_projection_fragment_mulliken_hamiltonian`  
- `precomputed` 驱动不可走 live 路径  

---

## 4. YAML 参数表

```yaml
embedding:
  mode: projection
  projection:
    low_level: HF
    high_level: CAS
    threshold: null                 # 默认 PROJECTION_EMBEDDING_THRESHOLD
    quantum_hamiltonian: fragment_mulliken_mo   # 或 global_active_space
    fragment_atom_indices: [0]      # fragment_mulliken_mo 必需
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `low_level` / `high_level` | `HF` / `CAS` | 工作流标签 |
| `threshold` | 容差常量 | 选择 / 数值阈值 |
| `quantum_hamiltonian` | `global_active_space` | 设为 `fragment_mulliken_mo` 才触发 |
| `fragment_atom_indices` | `[]` | 片段原子下标 |

示例：`configs/example_h2_projection_trace.yaml`。

活性空间尺寸仍由 `active_space.cas`（或策略解析结果）约束电子 / 轨道数。

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path
from qchem_stack.sdk import run_pipeline_from_config

cfg = load_experiment_config("configs/example_h2_projection_trace.yaml")
assert cfg.embedding.mode == "projection"
print(resolve_pre_quantum_path(cfg))

out = run_pipeline_from_config("configs/example_h2_projection_trace.yaml")
pq = out["pre_quantum_input"]
print(pq.get("hamiltonian_fingerprint", "")[:24])
```

库函数级（高级）：

```python
# from qchem_stack.chem.embedding.projection_hamiltonian import (
#     molecular_hamiltonian_fragment_mulliken_projection,
# )
# qh, audit = molecular_hamiltonian_fragment_mulliken_projection(...)
```

---

## 6. 验证命令

```bash
pytest tests/integrations/test_projection_mulliken_hamiltonian.py -q

python -c "from qchem_stack.config import load_experiment_config; assert load_experiment_config('configs/example_h2_projection_trace.yaml').embedding.mode=='projection'; print('ok')"
```

期望打印 `ok`。

---

## 7. 调参建议

| 目标 | 建议 |
|------|------|
| 选对片段 | 仔细设 `fragment_atom_indices`；对照 Mulliken 权重 |
| CAS 过大 / 过小 | 调 `active_space.cas.n_orbitals` / `n_electrons` |
| 与全局 CAS 对照 | 同一分子设 `quantum_hamiltonian: global_active_space` 比指纹与能量 |
| Psi4 对照 | 见 `tests/chem/test_psi4_pyscf_projection_parity.py` |

---

## 8. 相关

- [嵌入总览](./embedding) · [DMET](./embedding-dmet) · [Schmidt](./embedding-schmidt)  
- `embedding/active_integrals.py` · `embedding/psi4_mo_eri.py`  
- 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
