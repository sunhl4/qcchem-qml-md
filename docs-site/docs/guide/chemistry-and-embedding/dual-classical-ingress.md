# 双线路经典输入（在线 + 离线）

目标：无论经典结果来自在线求解还是离线数据集，量子阶段都读取同一接口（`PreQuantumInput`）。

## 路线 1：在线经典（结构文件 → 经典计算 → 量子）

通过 `molecule.geometry_file`（当前支持 XYZ）输入结构文件，无需手写 `coordinates`。

完整样例：

- `configs/example_h2_geometry_file_xyz.yaml`
- `configs/structures_h2.xyz`

## 路线 2：离线经典（预计算 bundle → 量子）

使用 `scf.driver: precomputed` + `scf.precomputed_bundle_path` 读取离线结果。

完整样例：

- `configs/example_h2_precomputed_bundle.yaml`
- `configs/precomputed_classical_reference_h2.json`

## 统一接口

两条路线都会在量子阶段前收口为 `PreQuantumInput`，量子侧不区分经典来源。

## 相关脚本

可用 `scripts/build_precomputed_bundle.py` 将 decomposition JSON + 外部经典数值组装为 `classical_reference_bundle_v1`。
