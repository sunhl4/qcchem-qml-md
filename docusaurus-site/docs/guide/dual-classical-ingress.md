---
title: 双线路经典输入（在线 + 离线）
description: 同一量子入口 PreQuantumInput：在线 SCF 与预计算 bundle。
---

# 双线路经典输入（在线 + 离线）

:::tip 模块手册
深读实现与边界：[chem · dual-ingress](/modules/chem/dual-ingress) · [solvers](/modules/chem/solvers) · [config](/modules/config)
:::

目标：无论经典结果来自在线求解还是离线数据集，量子阶段都读取同一接口（`PreQuantumInput`）。

---

## 1. 何时选哪条路

| 路线 | 适合 | 不适合 |
|------|------|--------|
| **在线**（`pyscf` / `psi4`） | 本机有化学依赖、要改几何/基组 | 无 PySCF/Psi4、CI 轻量烟测 |
| **离线**（`precomputed`） | 无经典依赖、固定参考能量对照 | 需要现场 AVAS/CASSCF 等 live hooks |

解析：`resolve_pre_quantum_path(cfg)` → `PreQuantumPath`。

---

## 2. 路线 1：在线经典

使用 `molecule.geometry_file`（XYZ）或内联坐标：

```yaml
molecule:
  geometry_file: "structures_h2.xyz"
  coordinate_unit: "angstrom"
  charge: 0
  multiplicity: 1
  basis: "sto-3g"

scf:
  driver: "pyscf"
  method: "RHF"
```

样例：`configs/example_h2_geometry_file_xyz.yaml`、`configs/structures_h2.xyz`。

---

## 3. 路线 2：离线经典（预计算 bundle）

**正确字段**是嵌套块 `scf.precomputed.bundle_path`（不是扁平 `precomputed_bundle_path`）：

```yaml
scf:
  driver: precomputed
  method: RHF
  precomputed:
    bundle_path: precomputed_classical_reference_h2.json
```

样例：`configs/example_h2_precomputed_bundle.yaml`、`configs/precomputed_classical_reference_h2.json`。

### 数据格式

离线 schema：`classical_reference_bundle_v1`，含：

- `classical_reference`（`e_tot`、`mo_energy`、`driver_meta`）
- `pre_quantum_input.qubit_hamiltonian`（`n_qubits`、`terms`）

`terms[].label` 支持紧凑写法（`"ZZ"`）或索引写法（`"Z0 Z1"`）。

### 生成 bundle

```bash
python3 scripts/build_precomputed_bundle.py \
  --decomposition-json configs/decomposition_plugin_toy_integrals.json \
  --output configs/precomputed_classical_reference_h2.json \
  --e-tot -1.116708174 \
  --mo-energy=-0.580628,0.676341
```

---

## 4. 统一接口

两条路线都在量子前收口为 `PreQuantumInput`；下游算法不关心经典来源。

组合矩阵（driver × embedding × 活性空间）：站内 [pre-quantum 组合矩阵](/reference/pre-quantum-yaml-matrix)；源码 `config/_experiment_validation.py`。加载时可调用 `validate_pre_quantum_contract`。

Schmidt 多 fragment：`configs/example_h4_schmidt_multifragment.yaml`。

---

## 5. 常见问题

| 问题 | 处理 |
|------|------|
| `driver=precomputed` 但无路径 | 设置 `scf.precomputed.bundle_path` |
| 非 precomputed 却填了 bundle | 校验拒绝 |
| `geometry_file` 与 `coordinates` 同时有 | 互斥，二选一 |
| 结构后缀不支持 | 当前仅 XYZ |
| live hooks + precomputed | 见 `validate_precomputed_driver_excludes_live_hooks` |

---

## 6. 相关

- [化学与嵌入选型](./chemistry-and-embedding) · [字段参考 · scf](/reference/config-fields/scf) · [FAQ](/faq/)
