---
title: 双线路经典输入（在线 + 离线）
description: 同一量子入口 PreQuantumInput：既支持结构文件驱动在线经典计算，也支持读取预计算经典结果数据集。
---

# 双线路经典输入（在线 + 离线）

目标：无论经典结果来自在线求解还是离线数据集，量子阶段都读取同一接口（`PreQuantumInput`）。

## 路线 1：在线经典（结构文件 → 经典计算 → 量子）

适合希望在本工程内端到端执行经典计算的场景。

### 最小配置

使用 `molecule.geometry_file`（当前支持 XYZ）而不是手写坐标：

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

完整样例：

- `configs/example_h2_geometry_file_xyz.yaml`
- `configs/structures_h2.xyz`

该路线在配置加载阶段解析结构文件，再由 `scf.driver` 后端完成经典计算。

## 路线 2：离线经典（预计算 bundle → 量子）

适合经典结果由外部软件或预制数据集提供的场景。

### 最小配置

```yaml
scf:
  driver: "precomputed"
  method: "RHF"
  precomputed_bundle_path: "configs/precomputed_classical_reference_h2.json"
```

完整样例：

- `configs/example_h2_precomputed_bundle.yaml`
- `configs/precomputed_classical_reference_h2.json`

## 统一接口说明

两条路线都会在量子阶段前收口为 `PreQuantumInput`，下游量子算法不需要知道经典结果来源。

- 在线路线：经典求解后构建 `PreQuantumInput`
- 离线路线：bundle 直接构建 `PreQuantumInput`

## 数据格式（离线）

离线文件 schema 为 `classical_reference_bundle_v1`，包含：

- `classical_reference`（`e_tot`、`mo_energy`、`driver_meta`）
- `pre_quantum_input.qubit_hamiltonian`（`n_qubits`、`terms`）

`terms[].label` 支持：

- 紧凑写法：`"II"`、`"ZZ"`、`"XYI"`
- 索引写法：`"Z0 Z1"`、`"X0 Y2"`

## 生成离线 bundle（脚本）

可将 decomposition-plugin JSON + 外部经典数值组装为 bundle：

```bash
python scripts/build_precomputed_bundle.py \
  --decomposition-json configs/decomposition_plugin_toy_integrals.json \
  --output configs/precomputed_classical_reference_h2.json \
  --e-tot -1.116708174 \
  --mo-energy=-0.580628,0.676341
```

## 常见问题

- **`scf.driver='precomputed'` 但没填路径**
  - 需要设置 `scf.precomputed_bundle_path`
- **非 `precomputed` driver 却填了 `precomputed_bundle_path`**
  - 配置校验会拒绝（避免歧义）
- **`geometry_file` 与 `coordinates` 同时填写**
  - 两者互斥，需二选一
- **结构文件后缀不支持**
  - 当前仅支持 XYZ（`.xyz`）
