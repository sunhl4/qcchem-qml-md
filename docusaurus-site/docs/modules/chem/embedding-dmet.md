---
title: chem · DMET 嵌入
description: DMET YAML、Schmidt 哈密顿源、密度反馈循环与片段求解器。
---

# chem · DMET 嵌入

本页覆盖 `embedding.mode: dmet`，尤其是生产路径 `hamiltonian_source: schmidt_atomic_production` 与密度自洽循环。

相关：[嵌入总览](./embedding) · [Schmidt 积分](./embedding-schmidt) · [哈密顿量](./hamiltonian)。

---

## 1. 文献与问题

| 角色 | 文献 |
|------|------|
| DMET | G. Knizia & G. K.-L. Chan, Phys. Rev. Lett. **109**, 186404 (2012) |
| 实践综述 | Wouters et al.; 开源 DMET / QEMIST 对照 |
| 本栈杂质 | Schmidt 原子片段 + 浴轨道（见 [Schmidt](./embedding-schmidt)） |

全分子相关计算昂贵。DMET 在片段上求解杂质问题，并通过密度匹配把局域相关信息反馈到全局。本栈 v1 实现的是 **Schmidt 杂质 + AO 密度混合** 的自洽循环，而非完整工业级多片段化学势优化全集。

---

## 2. 理论思想

典型循环：

1. 从全局 SCF 密度 $D$ 出发。  
2. 对片段构造杂质模型（片段 AO + 浴）。  
3. 在杂质空间求基态（FCI 或量子求解器）。  
4. 用杂质 1-RDM 更新全局密度并混合。  
5. 直至密度差收敛或达到最大轮数。

本栈密度反馈（`schmidt_dmet_self_consistent.py`）：

$$
D \leftarrow (1-\alpha)\,D + \alpha\,\mathrm{sym}\bigl(C_{\mathrm{imp}}\,\mathrm{dm1}\,C_{\mathrm{imp}}^{T}\bigr)
$$

并重归一 $\mathrm{Tr}(SD)=n_e$。收敛监视 Frobenius 意义下的 $\mathrm{dm1}-\gamma$，其中

$$
\gamma = C_{\mathrm{imp}}^{T} S\, D\, S\, C_{\mathrm{imp}}
$$

迭代中杂质化学势常取 $\mu=0$（可选事后二分求 $\mu$）。

---

## 3. 本栈实现

### 3.1 触发条件

- `embedding.mode: dmet`  
- 生产路径：`embedding.dmet.hamiltonian_source: schmidt_atomic_production`  
- 路径解析 → `PreQuantumPath.schmidt_atomic_production`

其他 `DmetHamiltonianSource`：`parity_stub`（默认）、`whole_active_system`（恰一个 fragment label）。

### 3.2 关键 API

| 符号 | 路径 |
|------|------|
| `DMETContext` / `FragmentSolverProtocol` | `embedding/dmet.py` |
| `QubitHamiltonianFragmentSolverExact` | 同文件；`exact_max_qubits` 默认 14，稠密 `eigh` |
| `schmidt_hamiltonian_and_context` | `pre_quantum_schmidt.py` |
| `run_schmidt_density_feedback_cycles` | `embedding/schmidt_dmet_self_consistent.py` |
| `run_schmidt_multifragment_density_cycles` | 同上 |

审计 schema：`schmidt_production_pipeline_v1`；密度反馈契约：`SCHMIDT_DMET_DENSITY_FEEDBACK_V1`。

### 3.3 约束

- `uniform_multifragment_toy` 与 `schmidt_atomic_production` **互斥**  
- `dmet_max_cycles` 配置校验上限 `SCHMIDT_DMET_MAX_CYCLES_LIMIT = 50`  
- `whole_active_system` 要求恰好一个 fragment label  
- `scf.driver=precomputed` 挡住 live Schmidt  
- 闭壳层 RHF（见 Schmidt 分册）

---

## 4. YAML 参数表

```yaml
embedding:
  mode: dmet
  dmet:
    fragment_labels: []
    hamiltonian_source: schmidt_atomic_production   # parity_stub | whole_active_system | …
    target_fragment_electrons: null
    uniform_multifragment_toy: false
    multifragment_one_shot_shared_hamiltonian: false
    fragment_solver:
      plugin_id: null
      use_exact: false
      exact_max_qubits: 14
    schmidt:
      fragment_atom_indices: [0]
      multi_fragment_atom_groups: []
      multi_primary_fragment_index: 0
      n_bath_spatial: 2
      max_impurity_spatial_orbitals: 14
      run_mu_bisection: false
      attach_fci_reference: true
      fci_reference_max_spatial_orbitals: 8
      dmet_max_cycles: 1
      dmet_mixing_alpha: 0.35
      dmet_convergence_tol: null          # 默认 RIDGE_REGULARIZATION
      run_vqe_on_all_fragments: false
      per_fragment_vqe_maxiter: null
      bath_sidecar_json_path: null
```

| 字段 | 默认 / 范围 | 作用 |
|------|-------------|------|
| `hamiltonian_source` | `parity_stub` | 生产请设 `schmidt_atomic_production` |
| `n_bath_spatial` | `2`（≥1） | 浴空间轨道数 |
| `max_impurity_spatial_orbitals` | `14` | 杂质空间上限 |
| `dmet_max_cycles` | `1`（1–256，校验 ≤50） | 密度反馈轮数 |
| `dmet_mixing_alpha` | `0.35` | 密度混合系数 $\alpha$ |
| `fragment_solver.use_exact` | `false` | 精确对角化片段 |
| `run_vqe_on_all_fragments` | `false` | 多片段各跑 VQE（高级） |

示例配置：`configs/example_h2_dimer_dmet_self_consistent.yaml`。

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path
from qchem_stack.sdk import run_pipeline_from_config

cfg = load_experiment_config("configs/example_h2_dimer_dmet_self_consistent.yaml")
assert cfg.embedding.mode == "dmet"
print(resolve_pre_quantum_path(cfg))

out = run_pipeline_from_config("configs/example_h2_dimer_dmet_self_consistent.yaml")
print(out["pre_quantum_input"].get("source") or out["pre_quantum_input"].get("schema"))
```

片段精确求解器（库内）：

```python
from qchem_stack.chem.embedding.dmet import QubitHamiltonianFragmentSolverExact
# solver = QubitHamiltonianFragmentSolverExact(max_qubits=14)
```

---

## 6. 验证命令

```bash
pytest tests/integrations/test_schmidt_embedding_production.py \
  tests/chem/test_dmet_multifragment_integration.py \
  tests/chem/test_chem_md_dmet.py -q

python -c "from qchem_stack.config import load_experiment_config; print(load_experiment_config('configs/example_h2_dimer_dmet_self_consistent.yaml').embedding.mode)"
```

期望打印 `dmet`。

---

## 7. 调参建议

| 症状 | 尝试 |
|------|------|
| 密度不收敛 | 增大 `dmet_max_cycles`；减小 $\alpha$；检查片段原子划分 |
| 杂质过大 | 减小 `n_bath_spatial` 或收紧片段；注意 14 空间轨道帽 |
| 只要烟雾 | `dmet_max_cycles: 1`、`attach_fci_reference: true` |
| 玩具多片段 | `uniform_multifragment_toy`（**勿**与生产 Schmidt 源同开） |
| 量子片段 | `fragment_solver` / `run_vqe_on_all_fragments`（成本高） |

---

## 8. 相关

- [Schmidt](./embedding-schmidt) · [嵌入总览](./embedding) · [projection](./embedding-projection)  
- `embedding/fragment_solvers/` · `contracts/schema_ids.py`  
- 选型：[P1 化学与嵌入](/guide/chemistry-and-embedding)
