# H₂ MD 主动学习三阶段方案 — 技术说明

> 本文档汇总 H₂ 端到端 demo（qchem-stack → 力场训练 → JAX-MD → 主动学习）的**三阶段演进**：训练配置修复、多后端力场路径、经典力场验证与量子 benchmark。与 [`qmlff_md_integration_说明.md`](qmlff_md_integration_说明.md) 互补：后者讲通用对接契约，本文聚焦 H₂ 实践与排障。

**推荐环境**：conda `qmlff-py311`（Python ≥ 3.11，`qchem-stack` + `qmlff` + `jax-md` + `pyscf` editable 安装）。

| 环境 | 结果 |
|------|------|
| `qmlff-py311` | 端到端可用（Python 3.11、numpy 1.26） |
| `base` | 不可用：Python 3.10 缺 `StrEnum`；numpy 2.x 与部分依赖不兼容 |

安装与变量：

```bash
conda activate qmlff-py311
cd "$QCHEM_REPO" && pip install -e ".[dev]"
cd "$QMLFF_ROOT" && pip install -e .
export QCHEM_STACK_PYTHON=/Users/shl/anaconda3/envs/qmlff-py311/bin/python
```

---

## 1. 背景：为什么「简单 H₂」也会训练失败

化学上 H₂ 是双原子、势能面近似一维 `E(r)`；但早期 demo 使用 **QML-FF 通用 QNN 路线**（`atomic_amplitude` preset），与 H₂ 并不匹配：

| 现象 | 原因 |
|------|------|
| 第 1 轮 loss 缓降、E_MAE ~14 eV 几乎不动 | 力损失权重过大；量子振幅编码 + barren plateau；per-atom QNN 对 `E(r)` 表达力弱 |
| 第 2 轮 loss 精确不变（如 `3005.051303`） | `warm_start` 继承 Adam `opt_state` + 默认 **cosine LR** 已衰减；第 2 轮 effective LR ≈ 0 |
| `n_qubits=4` 直接崩溃 | AtomicDescriptor 对 H-only 输出 **64 维** amplitude，需 `n_qubits≥6`（2⁶=64） |

因此后续工作拆成三阶段：**先修训练调度 → 再换 H₂ 合适架构 → 用经典势验证闭环**。

### 1.1 v1 / v2 demo 实测（`atomic_amplitude` + 旧配置）

| 运行 | 目录 | 现象 |
|------|------|------|
| v1 | `results/qmlff_md_h2/` | 2 轮 AL 未收敛；QML 能量 ~0 Ha vs qchem ~−1 Ha；MD 从坏帧出发导致解离 |
| v2 | `results/qmlff_md_h2_v2/` | 第 1 轮 loss 4214→3468，E_MAE ~14 eV 几乎不动；第 2 轮 loss 精确卡在 `3005.051303` |

**第 1 轮：loss 在降，但能量几乎不学**

| Epoch | Loss | E_MAE (eV/atom) | F_RMSE (eV/Å) |
|-------|------|-----------------|---------------|
| 10 | 4214 | 14.37 | 5.85 |
| 50 | 3468 | 13.96 | 4.61 |

- total loss 约 −18%，但 **E_MAE 仍 ~14 eV**（H₂ 合理目标应 ≪ 0.1 eV）
- loss 中 **力项占 ~94%**：`force_loss≈65 × force_weight=50 ≈ 3250`，`energy_loss≈195`
- 第 1 轮末 MD 有改善：`PE≈−1.72 eV`（v1 时 ~0 eV），说明并非完全没学

**第 2 轮：loss 完全卡死（优化器停滞）**

```
Epoch 10/50 | Loss: 3005.051303
Epoch 20/50 | Loss: 3005.051303   ← 6 位小数完全相同
```

根因：`warm_start: true` 继承 Adam `opt_state` + QML-FF Trainer 默认 **cosine LR** 在多轮 AL 中已衰减 → 第 2 轮 effective LR ≈ 0。另：`n_qubits=4` 与 H-only 64 维 amplitude 不匹配会直接崩溃。

---

## 2. 力场后端与量子路径对照

闭环通过 `MdValidationLoopConfig.force_field_backend` 选择力场实现，由 `build_force_field_handle()` 统一构建。

### 2.1 四种 backend

| `force_field_backend` | QML-FF / 经典路径 | H₂ 适用性 | 依赖 |
|----------------------|-------------------|-----------|------|
| `qmlff_preset` | AtomicDescriptor → **Amplitude** → StandardCircuit → WeightedDecoder | 通用原型，H₂ 上难训 | qmlff |
| `qmlff_angle` | AtomicDescriptor → **Angle (RY)** → StandardCircuit | 比 amplitude 稳，仍非 H₂ 专用 | qmlff |
| `qmlff_qmp_h2` | **SchurSchemeBQMLFF**（QMP Scheme B，等变消息传递） | **H₂ 推荐量子路线** | qmlff |
| `classical_h2` | **Morse 解析势**（scipy 拟合键长–能量） | 验证 AL 闭环；不训量子 | 无 qmlff 训练依赖 |

### 2.2 数据流（统一）

```
configs/example_h2.yaml          configs/example_h2_*_md.yaml
        │                                  │
        ▼                                  ▼
  qchem_labeler (HF-SCF)          MdValidationLoopConfig
        │                                  │
        ▼                                  ▼
     QMEFDataset  ──────────▶  build_force_field_handle(backend=…)
        │                                  │
        ▼                                  ▼
  train_force_field_on_qmef      run_jaxmd_trajectory
        │                                  │
        └──────── predict / |ΔE| 主动学习 ◀┘
```

单位边界（全模块一致）：

- qchem_stack / `QMEFDataset`：**Hartree、Bohr、Hartree/Bohr**
- QML-FF / JAX-MD 内部：**eV、Å、eV/Å**
- 转换集中在 `qmlff_adapter.py`

### 2.3 各路径架构示意

**A. `qmlff_preset`（原 QNN baseline）**

```
positions (Å) → AtomicDescriptor (64-d) → AmplitudeEmbedding (6 qubit)
  → StandardCircuit (2 layer) → per-atom E → Σ E → F = -∂E/∂R
```

**B. `qmlff_angle`**

```
同上，但 AmplitudeEmbedding 换为 RY 角编码（梯度更稳，qubit 需求更低）
```

**C. `qmlff_qmp_h2`（QML-FF 文档中的 H₂ 专用路线）**

```
positions → 边几何 (r, r̂) → 相干态编码 (D) → Schur 酉 (A)
  → L=0 / L=1 扇区读出 → 线性/二次 decoder → E, F
```

实现类：`qmlff.models.SchurSchemeBQMLFF` + `SchurSchemeBQMLFFConfig`。  
**未**走 `scripts/train_qmp_h2.py` CLI，而是通过 `md_bridge` 的 `Trainer` 接入同一 AL 闭环。

**D. `classical_h2`**

```
positions → 键长 r → Morse E(r; D_e, a, r_e, shift) → F = -∂E/∂R
```

实现模块：`qchem_stack.md_bridge.classical_h2_ff`。

---

## 3. 三阶段方案

### 阶段 1：训练调度修复（不换架构）

**目标**：消除第 2 轮 loss 卡死；减轻力项压制能量学习。

**配置项**（`MdValidationLoopConfig` / YAML）：

| 字段 | 推荐值 | 说明 |
|------|--------|------|
| `lr_scheduler` | `constant` | 避免 QML-FF Trainer 默认 cosine 在多轮 AL 中 LR→0 |
| `warm_start` | `true` | 跨轮保留已学参数 |
| `warm_start_params_only` | `true` | **只保留 params，每轮新建 Adam**（不继承 `opt_state` / `step`） |
| `force_weight` | `10`（QNN） | 降低力损失占比；QMP 可用 `50` |
| `n_epochs_per_round` | `50` | 小数据集需更多 epoch |
| `qmlff_builder_overrides.n_qubits` | `6` | H-only 时 amplitude 维数 64，至少 6 qubit |

**配置文件**：[`configs/example_h2_qmlff_md.yaml`](../configs/example_h2_qmlff_md.yaml)

**代码要点**：

- `train_force_field_on_qmef()`：`warm_start_params_only=true` 时不调用 `Trainer.from_warm_start()`
- `build_qmlff_model_from_preset()`：构建时校验 `descriptor.quantum_dim ≤ 2^n_qubits`

---

### 阶段 2：H₂ 量子力场多路径

**目标**：接入 QML-FF 为 H₂ 设计的 QMP 路线，并提供 angle 编码备选。

**新增 API**（`qchem_stack.md_bridge`）：

```python
from qchem_stack.md_bridge import (
    build_force_field_handle,
    build_qmp_h2_model,
    build_qmlff_model_angle,
    ForceFieldBackend,
)

# 统一入口
handle = build_force_field_handle(
    ["H"],
    backend="qmlff_qmp_h2",          # 或 qmlff_preset | qmlff_angle | classical_h2
    qmp_h2_overrides={"cutoff": 5.0, "cg_l": 1, "n_radial_basis": 8},
)
```

**配置文件**：

| 文件 | backend | 用途 |
|------|---------|------|
| [`configs/example_h2_qmp_md.yaml`](../configs/example_h2_qmp_md.yaml) | `qmlff_qmp_h2` | **推荐量子 AL demo** |
| [`configs/example_h2_angle_md.yaml`](../configs/example_h2_angle_md.yaml) | `qmlff_angle` | 角编码 QNN 对比 |
| [`configs/example_h2_qmlff_md.yaml`](../configs/example_h2_qmlff_md.yaml) | `qmlff_preset` | 原 amplitude QNN + 阶段 1 修复 |

**QMP 默认超参**（`qmp_h2_overrides`）：

```yaml
cutoff: 5.0
cg_l: 1
n_radial_basis: 8
decoder_type: linear
energy_readout: L0_L1norm
seed: 42
```

JAX-MD 注意：QMP 模型的 `cutoff` 在 `model.config.cutoff`，YAML 中请设 `cutoff_ang: 5.0` 与之一致。

---

### 阶段 3：经典 Morse 验证 + 量子 benchmark

**目标**：

1. 用**可拟合的 Morse 势**跑通 AL 闭环（不依赖量子训练是否收敛）
2. 用独立脚本横向对比各 backend 在键长扫描数据上的能量误差

#### 3.1 经典 H₂ AL demo

**配置文件**：[`configs/example_h2_classical_md.yaml`](../configs/example_h2_classical_md.yaml)

- `force_field_backend: classical_h2`
- `n_epochs_per_round: 1`（每轮仅重新拟合 Morse 参数）
- `energy_tolerance_hartree: 5.0e-3`（略放宽，经典势对 HF 有系统偏差）

模块：`src/qchem_stack/md_bridge/classical_h2_ff.py`

#### 3.2 多后端 benchmark（无 MD / 无 AL）

**脚本**：[`examples/qmlff_force_field_benchmark.py`](../examples/qmlff_force_field_benchmark.py)

对 12 个键长扫描帧（HF-SCF 标注）分别训练/拟合，输出 `benchmark_summary.json`（各 backend 的 `energy_mae_hartree`）。

```bash
python examples/qmlff_force_field_benchmark.py \
  --experiment configs/example_h2.yaml \
  --output results/qmlff_h2_benchmark \
  --backends classical_h2 qmlff_qmp_h2 qmlff_angle qmlff_preset \
  --n-epochs 30
```

---

## 4. 种子几何与 MD 启动

| 字段 | 推荐 | 说明 |
|------|------|------|
| `seed_mode` | `bond_stretch` | 沿 H–H 键扫描 0.8–2.2 Bohr（比随机 jitter 更贴 H₂ PES） |
| `n_seed_geometries` | `12` | 冷启动后训练集规模 |
| `md_init_frame` | `base` | 每轮 MD 从平衡构型起步（避免从 AL 坏帧出发解离） |
| `label_energy_reference` | `scf` | H₂ 上 HF 快且与验证参考一致 |

---

## 5. 推荐运行顺序

```bash
conda activate qmlff-py311
export QCHEM_STACK_PYTHON=/Users/shl/anaconda3/envs/qmlff-py311/bin/python
cd "$QCHEM_REPO"

# ① 经典 Morse — 验证 AL 闭环
python examples/qmlff_md_pipeline_demo.py \
  --experiment configs/example_h2.yaml \
  --loop       configs/example_h2_classical_md.yaml \
  --output     results/qmlff_md_h2_classical

# ② QMP H₂ — 推荐量子路线
python examples/qmlff_md_pipeline_demo.py \
  --experiment configs/example_h2.yaml \
  --loop       configs/example_h2_qmp_md.yaml \
  --output     results/qmlff_md_h2_qmp

# ③ 多后端能量 benchmark
python examples/qmlff_force_field_benchmark.py \
  --experiment configs/example_h2.yaml \
  --output     results/qmlff_h2_benchmark

# ④（可选）amplitude QNN + 阶段 1 训练修复
python examples/qmlff_md_pipeline_demo.py \
  --experiment configs/example_h2.yaml \
  --loop       configs/example_h2_qmlff_md.yaml \
  --output     results/qmlff_md_h2_qnn
```

产物目录典型内容：`train_round_*.xyz`、`md_round_*.xyz`、`validation_round_*.json`、`md_validation_summary.json`、`qmlff_checkpoints/`。

---

## 6. 配置字段速查（`MdValidationLoopConfig`）

### 6.1 力场与训练

| YAML 字段 | 类型 / 默认 | 说明 |
|-----------|-------------|------|
| `force_field_backend` | 见 §2.1 | 力场实现选择 |
| `qmlff_preset` | `atomic_amplitude` | preset / angle 后端使用 |
| `qmlff_builder_overrides` | dict | 转发给 preset `get_config(**)` |
| `qmp_h2_overrides` | dict | 转发给 `SchurSchemeBQMLFFConfig` |
| `lr_scheduler` | `constant` | QML-FF `TrainerConfig.lr_scheduler` |
| `warm_start` | `false`（代码默认） | 跨轮保留模型参数 |
| `warm_start_params_only` | `true` | 不继承 optimizer state |
| `force_weight` | `100`（代码默认） | H₂ YAML 建议 10–50 |
| `n_epochs_per_round` | `3` | 每轮训练 epoch 数 |

### 6.2 主动学习与 MD

| YAML 字段 | H₂ 推荐 | 说明 |
|-----------|---------|------|
| `max_rounds` | 3–5 | AL 轮数 |
| `energy_tolerance_hartree` | `5e-4`（量子）/ `5e-3`（经典） | 收敛阈值 |
| `seed_mode` | `bond_stretch` | 种子几何模式 |
| `md_init_frame` | `base` | MD 初态 |
| `label_energy_reference` | `scf` | 标注能量参考 |

完整 schema 见 [`md_validation_loop.py`](../src/qchem_stack/md_bridge/md_validation_loop.py) 中 `MdValidationLoopConfig`。

---

## 7. 代码模块索引

| 模块 | 路径 | 职责 |
|------|------|------|
| 主动学习闭环 | `md_bridge/md_validation_loop.py` | 冷启动、seed、训练、MD、验证、合并 |
| QML-FF / JAX-MD 适配 | `md_bridge/qmlff_adapter.py` | 构建、训练、推理、MD；多 backend 分发 |
| 经典 Morse H₂ | `md_bridge/classical_h2_ff.py` | 拟合与 JAX-MD 兼容接口 |
| qchem 标注 | `md_bridge/qchem_labeler.py` | Bohr 几何 → `QMEFDataset` |
| 端到端 demo | `examples/qmlff_md_pipeline_demo.py` | CLI 入口 |
| 后端 benchmark | `examples/qmlff_force_field_benchmark.py` | 能量 MAE 对比 |

**测试**：

- `tests/test_md_bridge_qmlff_adapter_imports.py` — 配置加载、export 面
- `tests/test_md_bridge_classical_h2_ff.py` — Morse 拟合

---

## 8. 排障备忘

| 症状 | 检查 |
|------|------|
| `Input state must be of length 16 or smaller; got length 64` | `n_qubits` 至少 6（H-only + amplitude） |
| 第 2 轮起 loss 完全不变 | `lr_scheduler: constant` + `warm_start_params_only: true` |
| E_MAE 长期 >10 eV | 换 `qmlff_qmp_h2` 或 `classical_h2` 做对照 |
| MD 分子解离 | `md_init_frame: base`；检查力场是否已拟合 |
| QMP MD cutoff 不对 | YAML `cutoff_ang` 与 `qmp_h2_overrides.cutoff` 一致 |

---

## 9. 与 QML-FF 独立 H₂ 脚本的关系

QML-FF 仓库内 [`scripts/train_qmp_h2.py`](../../QML-FF/scripts/train_qmp_h2.py) 与文档 [`QMP_H2_PIPELINE_ANALYSIS_AND_OPTIMIZATION.md`](../../QML-FF/docs/research/QMP_H2_PIPELINE_ANALYSIS_AND_OPTIMIZATION.md) 描述的是**同一 QMP 架构**的离线训练入口。  
本工程通过 `force_field_backend: qmlff_qmp_h2` 将其**嵌入 qchem AL 闭环**，数据来自 `qchem_labeler` 的 HF-SCF 标注，而非 QML-FF 自带 extxyz。

---

## 10. 新增 / 修改文件清单

| 文件 | 作用 |
|------|------|
| `src/qchem_stack/md_bridge/classical_h2_ff.py` | Morse H₂ 经典力场（scipy 拟合，JAX-MD 兼容） |
| `src/qchem_stack/md_bridge/qmlff_adapter.py` | `build_force_field_handle`、QMP / angle / classical 分支；`lr_scheduler`、`warm_start_params_only` |
| `src/qchem_stack/md_bridge/md_validation_loop.py` | 统一 `force_field_backend` 调度 |
| `src/qchem_stack/md_bridge/__init__.py` | 扩展 export（保留旧 API） |
| `configs/example_h2_qmlff_md.yaml` | 阶段 1：QNN + 训练修复 |
| `configs/example_h2_qmp_md.yaml` | 阶段 2：QMP H₂（推荐量子） |
| `configs/example_h2_angle_md.yaml` | 阶段 2：angle 编码 QNN |
| `configs/example_h2_classical_md.yaml` | 阶段 3：经典 Morse AL |
| `examples/qmlff_force_field_benchmark.py` | 阶段 3：多后端能量 MAE benchmark |
| `tests/test_md_bridge_classical_h2_ff.py` | Morse 拟合单元测试 |
| `tests/test_md_bridge_qmlff_adapter_imports.py` | 配置加载、export 面 |

---

## 11. 修订记录

| 日期 | 内容 |
|------|------|
| 2026-05-26 | 初版：三阶段方案、四 backend、配置与命令、排障 |
| 2026-05-26 | 补充 v1/v2 实测、loss 诊断、环境说明、文件清单 |
