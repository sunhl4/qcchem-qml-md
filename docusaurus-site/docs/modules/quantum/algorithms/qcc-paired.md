---
title: QCC / upCCGSD / pUCCD
description: 量子耦合簇与成对激发完整手册：文献、数学、实现边界、YAML/API 与示例。
---

# QCC / upCCGSD / pUCCD

本页覆盖三类 **结构化化学 ansatz**（相对 HEA）：固定比特簇 QCC、成对风格 UpCCGSD 插件、仅成对 doubles 的 pUCCD。风格对齐算法手册：理论 → 本栈实现 → 参数 → 调用。

相关：[UCCSD](./uccsd) · [IQEB 池](./operator-pools) · [算法菜单](/guide/algorithm-and-ansatz-menu)。

---

## 1. 文献

| 方法 | 文献 |
|------|------|
| **QCC** | I. G. Ryabinkin et al., *Qubit Coupled Cluster Method…*, [J. Chem. Theory Comput. **14**, 6317 (2018)](https://doi.org/10.1021/acs.jctc.8b00932) |
| **k-UpCCGSD** | J. Lee et al., *Generalized Unitary Coupled Cluster…*, [J. Chem. Theory Comput. **15**, 311 (2019)](https://doi.org/10.1021/acs.jctc.8b01004) |
| **pCCD / 成对 doubles** | 经典成对耦合簇与量子变体；本栈 `puccd` 用 **doubles-only** 费米子生成元 |

---

## 2. 要解决什么问题

| Ansatz | 适用直觉 |
|--------|----------|
| **QCC** | 在比特空间用固定激发池做乘积指数；比完整费米子 UCC 更「硬件/池友好」 |
| **upCCGSD** | 命名对齐成对 GSD；本栈当前实现复用 **UCCSD 生成元路径**（见 §4 边界） |
| **pUCCD** | 仅 doubles，参数更少，适合强调成对相关的粗粒度描述 |

三者都比随意 HEA 更结构化；需要完整 singles+doubles 化学主路径时优先 [UCCSD](./uccsd)。

---

## 3. 理论思想

### 3.1 QCC

在参考 $|\mathrm{HF}\rangle$ 上对池 Pauli 生成元做变分：

$$
|\psi(\boldsymbol{\theta})\rangle
= \Biggl(\prod_\ell e^{\theta_\ell\, i A_\ell}\Biggr)|\mathrm{HF}\rangle
$$

本栈默认 $A_\ell$ 来自 `iqeb_qubit_excitation` 池（与 IQEB 同池，但 **固定全部参数一次优化**，无外环筛选）。

### 3.2 成对 / doubles 簇

幺正形式仍是

$$
|\psi\rangle=e^{\hat{T}-\hat{T}^\dagger}|\mathrm{HF}\rangle
\quad\text{（或乘积指数）}
$$

pUCCD 取 $\hat{T}$ 仅为 doubles；UpCCGSD 在文献中限制成对双激发 + 选定单激发。

---

## 4. 数学实现（本栈）

### 4.1 `QCCVQE`（`quantum.algorithms.qcc_vqe`）

1. 要求 `fermion_space`；映射为 JW/BK 方阵（**拒 SCBK**）。  
2. `reference_state_dense(mapping, …)` → $|\mathrm{HF}\rangle$。  
3. `build_registered_operator_pool(pool_id, H)`，默认 `iqeb_qubit_excitation`。  
4. 簇矩阵：`1j * sparse(A_ℓ)`，态传播：

```text
psi ← |HF⟩
for θ, M in zip(angles, cluster_mats):
    psi ← expm(θ * M) @ psi;  normalize
```

5. SciPy `COBYLA` 最小化 $\langle H\rangle$；报告经 `qcc_algorithm_report_v1`。

### 4.2 `UpCCGSDVQE`（继承 `UCCSDVQE`）

- 当前构造：`build_spin_uccsd_fermion_generators` + `antihermitian_cluster_matrices`  
- 即 **与 UCCSD 同一生成元族**；meta 标 `variational_ansatz: upccgsd`  
- 边界：命名对齐文献 UpCCGSD，**实现上尚未单独切成对 doubles 子集**——对照实验请读 `meta` 与参数个数

### 4.3 `PUCCDVQE`

- `build_spin_ucc_doubles_only_fermion_generators` + 反厄米矩阵 + 同 UCCSD 传播/优化  
- meta：`variational_ansatz: puccd`

### 4.4 注册 ID

| `variational.ansatz` | 类 |
|----------------------|-----|
| `qcc` | `QCCVQE` |
| `upccgsd` | `UpCCGSDVQE` |
| `puccd` | `PUCCDVQE` |

---

## 5. 参数详表

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: qcc          # upccgsd | puccd
  vqe:
    maxiter: 80
    optimizer_method: COBYLA
active_space:
  fermion_qubit_mapping: jordan_wigner   # 或 bravyi_kitaev；勿对 QCC/成对硬跑 SCBK
```

| `ansatz` | 代表配置 |
|----------|----------|
| `qcc` | `configs/example_h2_qcc.yaml` |
| `upccgsd` | `configs/example_h2_upccgsd.yaml` |
| `puccd` | `configs/example_h2_puccd.yaml` |

优化器字段同 [VQE/HEA](./vqe-hea) 的 `quantum.vqe.*`。  
QCC 额外：构造参数 `pool_id`（默认 `iqeb_qubit_excitation`）。

---

## 6. 函数调用

```python
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids, ansatz_registry_export
from qchem_stack.sdk import run_pipeline_from_config

for name in ("qcc", "upccgsd", "puccd"):
    assert name in list_registered_ansatz_ids()
    print(name, ansatz_registry_export()[name]["summary"][:100])

out = run_pipeline_from_config("configs/example_h2_qcc.yaml")
print(out.get("energy_after_variational"))
```

### 直接构造 QCC

```python
from qchem_stack.quantum.algorithms.qcc_vqe import QCCVQE
# qcc = QCCVQE(qh, pool_id="iqeb_qubit_excitation")
# res = qcc.run(maxiter=200, seed=0)
```

### 验证命令

```bash
python3 -c "
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
s=set(list_registered_ansatz_ids())
assert {'qcc','upccgsd','puccd'}<=s
print('ok')
"
```

### 期望输出

- `ok`  
- 管线能量键存在  

---

## 7. 调参与边界

| 现象 | 处理 |
|------|------|
| SCBK ValueError | 换 JW/BK 方阵映射 |
| QCC 参数爆炸 | 小体系烟雾；或改更小池 / 先 IQEB 筛选 |
| upCCGSD ≈ UCCSD 能量 | 当前实现生成元同源；要严格成对限制请跟进源码演进或以 pUCCD 作 doubles-only |
| 迭代 QCC | `algorithm: iqcc` 见 [iQCC](./iqcc)；QITE/VSQS 见 [research-ansatze](./research-ansatze) |

---

## 8. 相关

- [UCCSD](./uccsd) · [IQEB](./iqeb) · [算符池](./operator-pools) · [映射](/modules/chem/mappings)
