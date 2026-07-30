---
title: iQCC / iQCC+PT
description: 迭代量子比特耦合簇完整手册：DIS、哈密顿穿衣、EN2、YAML/API 与示例。
---

# iQCC / iQCC+PT（迭代量子比特耦合簇）

本页是 **QCC → iQCC → iQCC+PT** 族在本栈的完整手册：文献与族谱、与 ADAPT/IQEB/固定 QCC 的差异、数学步骤、全部参数与可复制调用。

实现：`qchem_stack.quantum.algorithms.iqcc.IQCCVQE`（穿衣工具在 `iqcc_dressing`）。  
管线入口：`quantum.algorithm: iqcc`（与 ADAPT/IQEB 同级外环算法）。  
报告 schema：`algorithm_iqcc_report_v1`（`ALGORITHM_IQCC_REPORT_V1`）。  
能力：`supports_hamiltonian_dressing` / `supports_en2_pt` / `open_stack_implementation`（开放实现，**不**宣称与闭源 OTI 比特级一致）。

固定全池单层 QCC 见 [QCC](./qcc-paired)；外环改 HEA 的对照见 [IQEB](./iqeb) / [ADAPT](./adapt-vqe)。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| **QCC** | I. G. Ryabinkin et al., *Qubit Coupled Cluster…*, [JCTC **14**, 6317 (2018)](https://doi.org/10.1021/acs.jctc.8b00932) / arXiv:1809.03827 |
| **iQCC** | I. G. Ryabinkin et al., *Iterative Qubit Coupled Cluster…*, [JCTC **16**, 1055 (2020)](https://doi.org/10.1021/acs.jctc.9b01074) / arXiv:1906.11192 |
| **iQCC+PT** | I. G. Ryabinkin et al., *iQCC with perturbative corrections*, arXiv:2009.13622 |
| **工业规模标定** | S. N. Genin et al., *Towards Quantum Advantage in Chemistry*, arXiv:2512.13657（经典同构 iQCC / OLED） |

组内文献四包（综述 / 复现规格 / 展望）见 Yaozheng `surveys/iqcc-family/`。

---

## 2. 要解决什么问题

| 痛点 | QCC 族对策 |
|------|------------|
| 费米子 UCC 编译深、模板重 | 在 **Pauli 字** 上筛 DIS（梯度非零的纠缠子） |
| ADAPT 式加长 $U$ 使深度随步数涨 | **穿衣** $H\leftarrow U^\dagger H U$，下一步仍用短 $U$ |
| 变分只能覆盖 DIS 子集 | **EN2** 吃剩余生成元（iQCC+PT） |

与本栈其它外环对照：

| | 固定 QCC | IQEB | **iQCC（本页）** |
|--|----------|------|------------------|
| YAML | `algorithm: vqe` + `ansatz: qcc` | `algorithm: iqeb` | **`algorithm: iqcc`** |
| 生长对象 | 一次优化全池振幅 | 把池算符加进有效 $H$，内层 HEA | 优化短 $U$ 后 **相似变换进 $H$** |
| 后处理 | 无 | 无 | 可选 `enable_pt`（EN2） |

---

## 3. 理论思想

1. **DIS**：在当前 dressed $H^{\left(n\right)}$ 与参考 $|0\rangle$（HF）上，对候选 Pauli 纠缠子算零振幅梯度 $g_\alpha$，只保留 $|g_\alpha|>0$ 者。  
2. **Top-$K$**：按 $|g|$ 取前 `top_k` 个，经典优化振幅 $\tau$。  
3. **穿衣**：$H^{\left(n+1\right)}=U^\dagger(\tau)\,H^{\left(n\right)}\,U(\tau)$，再按 `coeff_atol` / `max_terms` 截断。  
4. **停止**：用尽 `max_steps`，或相邻两步能量差小于配置项 `energy_tolerance`。  
5. **PT（可选）**：对未选用的 DIS 生成元做 EN2（$\Delta E=-\sum_k g_k^2/D_k$；分母过小则跳过）。

---

## 4. 数学实现（本栈）

### 4.1 纠缠子约定

试探因子（与文献一致）：

$$
\hat U(\tau)=\prod_k\exp\!\Big(-\mathrm{i}\,\hat T_k\tau_k/2\Big).
$$

默认 `pool_mode: genin_dis`：偶权重、恰一个 $Y$ 且在支撑最低比特、其余为 $X$、无 $Z$（对齐 Genin 工业文纠缠子形态的开放近似）。  
备选 `pool_mode: iqeb_qubit_excitation`：复用 IQEB 比特激发池并归一成单 Pauli 生成元。

零振幅梯度：

$$
g_\alpha
=\mathrm{Im}\,\langle 0|\hat H\,\hat T_\alpha|0\rangle
=-\frac{\mathrm{i}}{2}\langle 0|[\hat H,\hat T_\alpha]|0\rangle.
$$

### 4.2 单 Pauli 穿衣闭式

对 $U=\exp(-\mathrm{i}\tau P/2)$、$P^2=I$，令 $\theta=\tau/2$：

$$
H'
=\cos^2\theta\,H
+\sin^2\theta\,PHP
+\mathrm{i}\sin\theta\cos\theta\,[P,H].
$$

实现：`iqcc_dressing.dress_by_pauli_rotation`；多因子按序 `dress_product_unitary`。

### 4.3 EN2

$$
\Delta E_{\mathrm{EN2}}
=-\sum_{k\notin S}\frac{g_k^2}{D_k},\qquad
D_k=E_0-\langle 0|P_k H P_k|0\rangle,
$$

$|D_k|$ 小于配置项 `denom_cutoff` 时该项贡献置 0。总能量 $E=E_{\mathrm{iQCC}}+\Delta E_{\mathrm{EN2}}$。

### 4.4 结果

`IQCCResult`：`energy`、`energy_variational`、`energy_pt`、`amplitudes_history`、`selected_generators`、`nfev`、`meta`（含 `iqcc_steps`、`n_terms_final`）。  
报告：`iqcc_algorithm_report_v1`。

---

## 5. 管线位置

`quantum.algorithm: iqcc` → `builtins.run_iqcc` → `IQCCVQE`。  
YAML 块 `quantum.iqcc.*` 经 `config.quantum_helpers` 解析；内层振幅优化迭代上限复用 `quantum.vqe.maxiter`。

兼容：`algorithm: vqe` + `variational.ansatz: iqcc` 仍会转入同一 `run_iqcc`（遗留 UX）。

---

## 6. 参数详表

### 6.1 YAML

```yaml
quantum:
  algorithm: iqcc
  iqcc:
    max_steps: 3
    top_k: 2
    coeff_atol: 1.0e-8
    max_terms: null
    enable_pt: false          # true → iQCC+PT
    denom_cutoff: 1.0e-6
    pool_mode: genin_dis      # 或 iqeb_qubit_excitation
    pool_id: iqeb_qubit_excitation
    max_weight: 4
    energy_tolerance: 1.0e-8
  vqe:
    maxiter: 80               # 每步振幅优化 maxiter
```

| 字段 | 含义 | 默认 |
|------|------|------|
| `iqcc.max_steps` | 穿衣外环上限 | `4` |
| `iqcc.top_k` | 每步 Top-$|g|$ 纠缠子数 | `2` |
| `iqcc.coeff_atol` | 穿衣后丢弃小系数 | `1e-8` |
| `iqcc.max_terms` | 项数硬上限（可选） | `null` |
| `iqcc.enable_pt` | 启用 EN2 | `false` |
| `iqcc.denom_cutoff` | EN2 $\lvert D_k\rvert$ 截断 | `1e-6` |
| `iqcc.pool_mode` | 候选池模式 | `genin_dis` |
| `iqcc.pool_id` | `iqeb_*` 池名（备用模式） | `iqeb_qubit_excitation` |
| `iqcc.max_weight` | Genin 池最大 Pauli 权重 | `4` |
| `iqcc.energy_tolerance` | 外环能量收敛 | `1e-8` |

代表配置：

- `configs/example_h2_iqcc.yaml`（纯 iQCC）  
- `configs/example_h2_iqcc_pt.yaml`（`enable_pt: true`）

### 6.2 Python

```python
from qchem_stack.quantum.algorithms.iqcc import IQCCVQE

# algo = IQCCVQE(
#     qh,
#     max_steps=3,
#     top_k=2,
#     enable_pt=True,
#     pool_mode="genin_dis",
# )
# result = algo.run(seed=0)
# print(result.energy, result.energy_variational, result.energy_pt)
```

---

## 7. 函数调用与验证

```python
from qchem_stack.sdk import run_pipeline_from_config
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids

assert "iqcc" in list_registered_algorithm_ids()
out = run_pipeline_from_config("configs/example_h2_iqcc.yaml")
print(out.get("energy_after_variational"))
print(out.get("algorithm_report", {}).get("schema"))
```

### 验证命令

```bash
python3 -c "
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
assert 'iqcc' in list_registered_algorithm_ids()
print('ok')
"
pytest -q tests/quantum/test_iqcc_iterative.py
```

### 期望输出

- `ok`  
- 管线能量为负浮点（H₂ 烟雾）  
- 报告 schema 为 `algorithm_iqcc_report_v1`  

---

## 8. 调参与排错

| 现象 | 处理 |
|------|------|
| 能量几乎不变 | 增大 `max_steps` / `top_k`；检查 DIS 是否为空（日志 `iqcc_steps`） |
| 项数爆炸 / 慢 | 提高 `coeff_atol`；设 `max_terms` |
| PT 发散或 NaN | 增大 `denom_cutoff`；先关 `enable_pt` 核对变分路径 |
| 与固定 QCC 差很大 | 正常：固定 QCC 一次优化全池；iQCC 是穿衣迭代 |
| 要对齐工业 OLED 协议 | 见文献超参分阶段表；本栈为研究级开放近似，非生产跑分 |

---

## 9. 相关

- [QCC / upCCGSD / pUCCD](./qcc-paired) · [IQEB](./iqeb) · [ADAPT-VQE](./adapt-vqe) · [研究 ansatz 索引](./research-ansatze) · [算法菜单](/guide/algorithm-and-ansatz-menu)
