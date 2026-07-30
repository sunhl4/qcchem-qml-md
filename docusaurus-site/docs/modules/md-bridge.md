---
title: md_bridge 模块
description: QMEF、label_geometries、md_ml_export、classical_h2 与 qmlff。
---

# md_bridge 模块

`qchem_stack.md_bridge` 把管线能量/力接到分子动力学与力场学习闭环。选型：[MD/ML 主动学习](/guide/md-ml-active-learning) · [教程](/tutorial/md-ml-active-learning)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| **QMEF** | 量子分子能量/力数据集模式（`QMEFDataset` / `QMFrame`） |
| **标签** | 用完整或 HF-only 管线给几何打标 |
| **力场** | `classical_h2`（无 qmlff）与 `qmlff`（软依赖）双后端 |
| HTTP | `/v1/meta/ml-md-bridge`、`qmef-validate`（见 [api-sdk](./api-sdk)） |

主动学习：量子标签 → 数据集 → 力场 → MD → 不确定性采样 → 再标签。

---

## 2. 理论

经典 MD（Verlet 示意）：

$$
\mathbf{r}(t+\Delta t) = 2\mathbf{r}(t) - \mathbf{r}(t-\Delta t) + \frac{\Delta t^2}{m}\mathbf{F}(t)
$$

量子标签提供 $E$ 与 $\mathbf{F}=-\nabla E$（或有限差分/解析梯度，依配置）。  
QMEF 把单帧/多帧附着到 `repro.qmef_ml_attachment_v1`（schema `QMEF_ML_ATTACHMENT_V1`）。

---

## 3. 实现

### QMEF

| 符号 | 路径 |
|------|------|
| `QMEFDataset`、`QMFrame` | `md_bridge/schema.py` |
| `build_qmef_ml_attachment_repro_block` | `md_bridge/from_pipeline.py` |
| 提取 | `from_pipeline_extract.energy_hartree_from_pipeline_out`、`primary_qmframe` |

附着点：`orchestration/protocol_finalize_sidecars.maybe_attach_md_ml_qmef_dataset`。

### `label_geometries`

| 函数 | 路径 |
|------|------|
| `label_geometries_with_pipeline` | `md_bridge/qchem_labeler.py` |
| `label_base_geometry_only` | 同上 |
| `merge_qmef_datasets` | 同上 |

做法：注入 `md_ml_export.trajectory.extra_coordinates_bohr`，跑管线，从 repro 块抬升数据集。

### `classical_h2` vs `qmlff`

| 后端 | 模块 | 关键 API |
|------|------|----------|
| **classical_h2** | `classical_h2_ff.py` | `build_classical_h2_handle`、`train_classical_h2_on_qmef` — Morse 拟合，**不依赖 qmlff** |
| **qmlff** | `qmlff_adapter.py`、`qmlff_builders.py`、`qmlff_md.py` | `build_qmlff_model_from_preset`、`train_qmlff_on_qmef`、`run_jaxmd_trajectory` — 软导入 `qmlff` / `jax_md` |

统一：`build_force_field_handle(..., backend="classical_h2"|"qmlff_preset"|...)`。  
包面：`md_bridge/__init__.py`。验证环：`md_loop_rounds.run_validation_round`。

---

## 4. YAML（`md_ml_export`）

```yaml
schema_version: "2"
md_ml_export:
  attach_single_frame_to_repro: true
  energy_reference: variational   # scf | variational | pauli_protocol
  include_hf_nuclear_gradient: false
  trajectory:
    theory_level: full_pipeline   # 或 hf_scf
    extra_coordinates_bohr: []    # 由 labeler 注入
```

| 字段 | 含义 |
|------|------|
| `attach_single_frame_to_repro` | 写入 `repro.qmef_ml_attachment_v1` |
| `energy_reference` | 能量来源 |
| `include_hf_nuclear_gradient` | 是否含 HF 核梯度 |
| `trajectory.theory_level` | `hf_scf` 轻量 vs `full_pipeline` |
| `trajectory.extra_coordinates_bohr` | 额外几何（Bohr） |

代表：`configs/example_h2_md_ml_qmef_attach.yaml`。详见仓库 `docs/说明_md_ml_export配置.md`。

---

## 5. Python

```python
from qchem_stack.md_bridge.from_pipeline_extract import (
    energy_hartree_from_pipeline_out,
    primary_qmframe,
)
from qchem_stack.md_bridge.from_pipeline import build_qmef_ml_attachment_repro_block
from qchem_stack.md_bridge.qchem_labeler import label_geometries_with_pipeline
from qchem_stack.md_bridge.classical_h2_ff import build_classical_h2_handle
from qchem_stack.sdk import run_pipeline_from_config, load_experiment_config

cfg = load_experiment_config("configs/example_h2.yaml")
out = run_pipeline_from_config("configs/example_h2.yaml")
print(energy_hartree_from_pipeline_out(cfg, out))
# geometries: label_geometries_with_pipeline(cfg_path, coords_bohr_list)
# ff = build_classical_h2_handle(...)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.md_bridge.from_pipeline_extract import normalize_coords; print(normalize_coords([[0.0,0.0,0.0],[0.0,0.0,0.74]]))"
```

期望：规范化坐标列表。

```bash
python3 -c "from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame; print(QMEFDataset.__name__, QMFrame.__name__)"
```

期望：打印类名。

---

## 7. 调优建议

- 无 extras 时用 `classical_h2` 做冒烟；有 `qmlff`/`jax_md` 再切 `qmlff_preset`。  
- 大批几何用 `hf_scf` 粗标，子集再 `full_pipeline`。  
- `attach_single_frame_to_repro` 适合单点；轨迹数据集用 labeler + `merge_qmef_datasets`。  
- 力场训练失败先查坐标单位（Bohr vs Å）。

---

## 8. 相关

- [orchestration](./orchestration) · [repro](./repro) · [api-sdk](./api-sdk) · [ops-light](./ops-light)  
- [MD/ML 教程](/tutorial/md-ml-active-learning)
