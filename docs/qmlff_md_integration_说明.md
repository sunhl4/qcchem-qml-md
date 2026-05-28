# qchem-stack ↔ QML-FF ↔ JAX-MD 端到端对接说明

> 本文档描述如何把本工程（`qcchem-qml-md` / `qchem_stack`）与你的另一项工程 **QML-FF**（`/Users/shl/nvidia/QML-FF`，量子等变变分电路分子力场）以及 **JAX-MD** 拼成一条主动学习闭环。本对接 **完全增量**：不动本工程任何已有公共契约（`QMFrame`、`QMEFDataset`、`ExperimentConfig`、`run_pipeline_sync`、`md_bridge.from_pipeline` 等），所有新增模块对 `qmlff` / `jax_md` 均走 soft-import。

> **H₂ 三阶段实践**（训练修复、QMP/经典多后端、b benchmark）见：[`h2_md_validation_phases_技术说明.md`](h2_md_validation_phases_技术说明.md)。  
> **UQC 云平台 mock + 本闭环**（不连真机）见：[`说明_UQC_mock与分子力场在线学习.md`](说明_UQC_mock与分子力场在线学习.md)。

---

## 1. 总览

```
                    ┌──────────────────────────────────────────────┐
                    │     qchem_stack.orchestration.pipeline       │
 几何 (Bohr) ──▶───▶│  run_pipeline_sync (PySCF + VQE/ADAPT + ...) │──▶── E (Hartree), F (Ha/Bohr)
                    └──────────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────────┐
                    │ qchem_stack.md_bridge.qchem_labeler          │
                    │ label_geometries_with_pipeline(...)          │
                    │ 返回 QMEFDataset（Hartree/Bohr）             │
                    └──────────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────────┐
                    │ qchem_stack.md_bridge.qmlff_adapter          │
                    │ train_qmlff_on_qmef(handle, dataset, ...)    │  ← QML-FF (`qmlff.training.Trainer`)
                    │ run_jaxmd_trajectory(handle, ...)            │  ← JAX-MD (`qmlff.simulation.JAXMDSimulator`)
                    │ predict_energy_forces_hartree(handle, geom)  │
                    └──────────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────────┐
                    │ qchem_stack.md_bridge.md_validation_loop     │
                    │ run_md_validation_loop(experiment_yaml,...)  │
                    │ • 冷启动 → 训 QML-FF → 跑 jax-md             │
                    │ • |E_qml − E_qchem| > tol 的帧回灌再训        │
                    └──────────────────────────────────────────────┘
```

闭环的两个核心目标：

1. **端到端跑通**：用本工程算出来的能量去训练 QML 等变变分力场，再用 jax-md 做 MD。
2. **少数据 / 0 数据学习 + MD 反馈**：先标少量（甚至 0 个额外）结构 → 训力场 → 跑 MD → 对 MD 抽样帧的能量与 qchem 重新比对 → 不达标就把这些帧补成新训练样本回灌。

---

## 2. 安装

```bash
# 本工程
cd /Users/shl/nvidia/qcchem-qml-md
pip install -e ".[chem,quantum]"        # PySCF + Qiskit 可选；H2 demo 只需 chem

# 另一项工程：QML-FF（本地，editable 安装）
pip install -e /Users/shl/nvidia/QML-FF

# jax-md（可选；只有走到 MD 这一步才需要）
pip install -e ".[qmlff]"   # 等价于安装 jax-md，详见 pyproject.toml
# 或者直接：pip install jax-md
```

> **关键约束**：本工程默认不依赖 `qmlff` / `jax_md`；以上三件套全部缺席时，`qchem_stack` 的旧功能仍正常工作，所有新模块也能正常 `import`（只有调用到具体 QML-FF / JAX-MD 函数才会抛带安装提示的 `ImportError`）。

---

## 3. 三段对外接口

### 3.1 `qchem_stack.md_bridge.qchem_labeler` — 把任意 Bohr 几何标注成 `QMEFDataset`

```python
from qchem_stack.md_bridge import (
    label_base_geometry_only,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)

# 仅 base 几何（最便宜的冷启动）
base = label_base_geometry_only(
    "configs/example_h2.yaml",
    energy_reference="variational",   # variational | scf | pauli_protocol
    include_hf_nuclear_gradient=True,
)
# base.dataset 是 QMEFDataset（Hartree/Bohr）

# base + 一批扰动几何（两阶段标注）
ds_more = label_geometries_with_pipeline(
    "configs/example_h2.yaml",
    extra_coordinates_bohr=[
        [[0,0,0], [0,0,1.30]],
        [[0,0,0], [0,0,1.50]],
    ],
    energy_reference="variational",
    theory_level="full_pipeline",     # 也可以 hf_scf 走更便宜的 MF
    include_hf_nuclear_gradient=True,
    failure_isolation=True,           # 单帧崩了不影响其它帧
)
```

底层完全复用本工程现有的 `md_bridge.from_pipeline.build_qmef_ml_attachment_repro_block`，只是把它**反向**走通（接收一组几何 → 一次 pipeline 调用 → 解出 `QMEFDataset`），并额外提供失败隔离与合集去重。

### 3.2 `qchem_stack.md_bridge.qmlff_adapter` — QML-FF 训练 / 推理 / MD facade

```python
from qchem_stack.md_bridge import (
    build_qmlff_model_from_preset,
    train_qmlff_on_qmef,
    predict_energy_forces_hartree,
    run_jaxmd_trajectory,
    select_geometries_from_trajectory,
    QmlffModelHandle,
)
import numpy as np

handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")

train_qmlff_on_qmef(
    handle, ds_more.dataset,
    n_epochs=10, batch_size=1, learning_rate=1e-3, force_weight=100.0,
    warm_start=True,
)

# 单点能量/力（输入 Bohr / 输出 Hartree、Ha/Bohr）
E_h, F_hb = predict_energy_forces_hartree(
    handle,
    positions_bohr=np.array([[0,0,0], [0,0,1.40]]),
    atomic_numbers=[1, 1],
)

# JAX-MD 轨迹（NVT-Langevin / NVT-NoseHoover / NVE）
traj = run_jaxmd_trajectory(
    handle,
    initial_positions_bohr=np.array([[0,0,0], [0,0,1.40]]),
    atomic_numbers=[1, 1],
    n_steps=500, dt_fs=0.5,
    temperature_K=300.0, ensemble="nvt_langevin",
    save_stride=10, seed=42,
)
# traj.positions_bohr / traj.energies_hartree / traj.times_ps

# 从轨迹里挑 4 个候选几何回去做 qchem 二次验证
candidate_geoms_bohr = select_geometries_from_trajectory(traj, n_candidates=4)
```

**单位边界**：本 adapter 是两个世界之间唯一做单位换算的地方。外部所有持久化文件（`QMEFDataset`、extxyz、JSON 摘要）一律 **Hartree/Bohr**；调用 `qmlff` 内部时才换到 **eV/Å**；调 `jax_md` 时再换到 **eV/Å/ps/K/amu**。Caller 永远不用关心 QML-FF 的内部单位约定。

### 3.3 `qchem_stack.md_bridge.md_validation_loop` — 主动学习闭环

```python
from qchem_stack.md_bridge import (
    MdValidationLoopConfig,
    run_md_validation_loop,
)

cfg = MdValidationLoopConfig.from_yaml("configs/example_h2_qmlff_md.yaml")
summary = run_md_validation_loop(
    "configs/example_h2.yaml",
    config=cfg,
    output_dir="results/qmlff_md_h2",
)
print(summary["converged"], summary["n_total_frames"])
```

或者一行命令跑 H2：

```bash
python examples/qmlff_md_pipeline_demo.py \
    --experiment configs/example_h2.yaml \
    --loop       configs/example_h2_qmlff_md.yaml \
    --output     results/qmlff_md_h2
```

---

## 4. 主动学习闭环细节

`run_md_validation_loop` 的步骤序列（伪代码与实际实现一一对应）：

```
A. 冷启动
   ── label_base_geometry_only(experiment_yaml)
      → 1 帧 QMEFDataset (Hartree/Bohr)

B. 可选种子扩增
   if n_seed_geometries > 0:
       n 个 Gaussian 扰动几何 → label_geometries_with_pipeline(theory=full_pipeline)
       去重并入 dataset

C. 构建 QML-FF 模型
   build_qmlff_model_from_preset(species_list, preset)

D. for round in 1..max_rounds:
   1) train_qmlff_on_qmef(handle, dataset, warm_start=True)
   2) run_jaxmd_trajectory(handle, n_steps, save_stride, ensemble, ...)
   3) select_geometries_from_trajectory(traj, n_candidate_frames)
      → K 个候选 Bohr 几何
   4) label_geometries_with_pipeline(theory=hf_scf, failure_isolation=True)
      → 每帧便宜的参考能量
   5) 对每帧计算 |E_qml − E_qchem|
      - 全部 < energy_tolerance_hartree → 整体 converged，break
      - 否则按 |ΔE| 取 top-K（add_top_k_per_round），用更贵的
        theory_level（默认 full_pipeline）重标注，并入 dataset

E. 落盘
   results/<output_dir>/
       train_round_0_initial.xyz       (初始训练集，extxyz Hartree/Bohr)
       train_round_<i>.xyz             (第 i 轮训练后的累积训练集)
       md_round_<i>.xyz                (该轮 jax-md 轨迹)
       validation_round_<i>.json       (每帧 qml vs qchem 详细比对)
       train_final.xyz                 (最终训练集)
       md_validation_summary.json      (总摘要)
       qmlff_checkpoints/              (QML-FF 训练 checkpoint)
```

### 4.1 关键阈值

* `energy_tolerance_hartree`：默认 `5e-4 Ha ≈ 13.6 meV`，小分子较为常见的力场可接受误差量级。
* `n_candidate_frames`：默认 4；越多越能覆盖 MD 行为，越慢。
* `add_top_k_per_round ≤ n_candidate_frames`：每轮最多补几个最差帧；通常 `add_top_k = ceil(n_candidate / 2)`。

### 4.2 两阶段标注策略

借鉴你 QML-FF 现有 `qmlff.data.qchem_online_loop.TwoStageLabelingSpec` 的思路：

* 全部候选先走便宜 `hf_scf`（`label_screening_theory_level`），用得到的 `E_ref` 与 QML 预测求 |ΔE|。
* 只对 |ΔE| 最大的 `add_top_k_per_round` 个几何升级到 `full_pipeline`（`label_top_theory_level`）做高保真重标。
* 当 `label_top_theory_level == label_screening_theory_level` 时跳过升级步骤直接用 screening 标签 —— 适合纯 HF / 纯 full-pipeline 的两种极端。

### 4.3 与 QML-FF 自带的 `run_online_loop` 的关系

`qmlff.data.qchem_online_loop.run_online_loop` 已经覆盖了"用 Gaussian 扰动几何作为候选 pool"的离线主动学习；它**保持不变**，且仍可独立使用。本工程新增的 `run_md_validation_loop` 是它的姊妹：

| 维度 | `qmlff.data.qchem_online_loop` | `qchem_stack.md_bridge.md_validation_loop` |
|---|---|---|
| 候选 pool 来源 | 平衡构型周围 Gaussian 扰动 | **真实 MD 轨迹采样** |
| 入口位置 | QML-FF 一侧 | 本工程一侧 |
| 调度 QML-FF 训练 | ✅ | ✅（通过 adapter） |
| 调度 JAX-MD | ❌ | ✅ |
| 与 qchem-stack pipeline | 反向 import | 原生调用 |
| 适用场景 | 离线扩样 + 增量训练 | 在线 MD + 真实采样反馈 |

---

## 5. 0 数据 / 少数据冷启动

把 `n_seed_geometries: 0` 并把 `label_top_theory_level` 设为最便宜的级别即可达到"近似 0 数据"启动：

```yaml
# configs/example_h2_qmlff_md.yaml 中
n_seed_geometries: 0
label_screening_theory_level: hf_scf
label_top_theory_level: hf_scf
label_energy_reference: scf
energy_tolerance_hartree: 1.0e-3
md_n_steps: 100
```

此时只在 base 几何上算一次 SCF 作为唯一训练样本；剩下的训练数据全部由 MD → qchem-标注的闭环生成。

---

## 6. 设计原则与不动的边界

- **绝对不动**：`QMFrame` / `QMEFDataset` 字段、`MdMlExportSpec`、`ExperimentConfig` 任何子 schema、`from_pipeline` / `exporter` / `hooks` / `contracts` / `schema` 五个旧文件、`StubTorchMLIPTrainer` 接口与 `ForceFieldTrainerProtocol`。
- **`md_bridge/__init__.py`**：只做加法，旧 export 顺序与字符串完全保留。
- **soft-import**：`qmlff`、`jax_md`、`pyscf` 均在函数体内 import；缺依赖时抛带安装提示的 `ImportError`。
- **新测试 marker 隔离**：所有新增测试统一打 `l1_md_ml`，并按需 `pytest.importorskip("qmlff")` / `importorskip("jax_md")` / `importorskip("pyscf")`，对默认 CI 行为零影响。

---

## 7. 常见问题（FAQ）

**Q: 我只想做端到端跑通，最少需要哪几步？**
A:

```python
from qchem_stack.md_bridge import (
    label_base_geometry_only,
    build_qmlff_model_from_preset,
    train_qmlff_on_qmef,
    run_jaxmd_trajectory,
)

ds = label_base_geometry_only("configs/example_h2.yaml", energy_reference="scf").dataset
handle = build_qmlff_model_from_preset(["H"])
train_qmlff_on_qmef(handle, ds, n_epochs=5)
traj = run_jaxmd_trajectory(
    handle,
    initial_positions_bohr=np.asarray(ds.frames[0].positions_bohr),
    atomic_numbers=ds.frames[0].atomic_numbers,
    n_steps=200, dt_fs=0.5,
)
```

**Q: 我手上已经有 QML-FF online loop 跑的 checkpoint，可以接着用吗？**
A: 可以。`build_qmlff_model_from_preset` 之后用 `handle.model.set_parameters(np.load("ckpt.npz"))` 即可热启。`train_qmlff_on_qmef` 的 `warm_start=True` 会复用 `handle.opt_state`（如果存在）。

**Q: MD 跑出来能量发散 / 几何崩坏怎么办？**
A: 通常说明初始训练样本太少。把 `n_seed_geometries` 调到 4–8、`md_n_steps` 调小到 50 以内先跑通；之后再放大。

**Q: 周期性体系支持吗？**
A: 第一期只验证了非周期小分子；`MdValidationLoopConfig` 已经为 `box_bohr` 留了通路（`run_jaxmd_trajectory` 形参里），但 `label_geometries_with_pipeline` 对 PBC 的全 pipeline 还需要你在 `experiment_yaml` 内打开 `chemistry_extended.pbc` 才能联调。

---

## 8. 相关入口速查表

| 你想做的事 | 入口 |
|---|---|
| 把一批几何 → qchem 标签 → `QMEFDataset` | `qchem_stack.md_bridge.label_geometries_with_pipeline` |
| 把现有 `QMEFDataset` → 训 QML-FF | `qchem_stack.md_bridge.train_qmlff_on_qmef` |
| 用 QML-FF 跑 JAX-MD 轨迹 | `qchem_stack.md_bridge.run_jaxmd_trajectory` |
| 主动学习闭环 | `qchem_stack.md_bridge.run_md_validation_loop` |
| QML-FF 自己跑的离线扩样 loop | `qmlff.data.qchem_online_loop.run_online_loop` (在 QML-FF 项目里) |
| QMEF attachment 给 repro | `qchem_stack.md_bridge.from_pipeline.build_qmef_ml_attachment_repro_block`（旧入口，未变） |

---

## 9. 参考

- 本工程 ML/MD 桥：`src/qchem_stack/md_bridge/`
- QML-FF qchem 桥（反向）：`/Users/shl/nvidia/QML-FF/qmlff/data/qchem_bridge.py`
- QML-FF online loop：`/Users/shl/nvidia/QML-FF/qmlff/data/qchem_online_loop.py`
- jax-md：<https://github.com/jax-md/jax-md>
