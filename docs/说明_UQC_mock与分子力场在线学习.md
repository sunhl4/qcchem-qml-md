# UQC mock 与分子力场在线学习 — 操作说明

> **目的**：在不连接 UQC 真机的前提下，用 `backend.provider: uqc` + `uqc_mode: mock` 跑通  
> **qchem 流水线 → VQE 能量 → QMEF 标注 → QML-FF 训练 → JAX-MD 采样 → 主动学习回灌** 全链路。  
> 真机联调见 [`UQC云平台集成技术报告.md`](UQC云平台集成技术报告.md)。

---

## 1. 对接关系（一句话）

分子力场在线学习**不单独调用** UQC SDK；它在每次用 `label_geometries_with_pipeline` / `run_pipeline_sync` 标注几何时，读取实验 YAML 里的 `backend.provider`。设为 `uqc` 且 `uqc_mode: mock` 时，VQE 期望值由本地 statevector 模拟（与真机 API 无关）。

---

## 2. 配置文件

| 文件 | 作用 |
|------|------|
| [`configs/example_h2_uqc_mock_md_ml.yaml`](../configs/example_h2_uqc_mock_md_ml.yaml) | 主实验：PySCF + UQC mock VQE + `md_ml_export` 导出 QMEF |
| [`configs/example_h2_uqc_mock_qmlff_loop.yaml`](../configs/example_h2_uqc_mock_qmlff_loop.yaml) | 主动学习环参数（轮数、MD 步数、QML-FF 训练等） |

关键片段（实验 YAML）：

```yaml
backend:
  provider: uqc
  uqc_mode: mock          # 必须 mock，避免误提交真机
  shots_per_circuit: 1000
  meta:
    uqc_mode: mock
    uqc_target: iontrap-sim   # 仅作记录；mock 时不访问云

md_ml_export:
  attach_single_frame_to_repro: true
  energy_reference: variational   # 在线学习标注使用 VQE 能量
```

主动学习环（loop YAML）建议：

```yaml
label_energy_reference: variational   # 与 UQC mock VQE 对齐
max_rounds: 1                         # smoke 可先 1 轮
n_epochs_per_round: 1
md_n_steps: 4
```

---

## 3. 环境安装

```bash
cd /path/to/qchem_qml_md

# 化学 + 量子（含 PySCF、Qiskit；mock 模式不需要 uqc-client）
pip install -e ".[chem,quantum]"

# 分子力场 + MD（QML-FF 为兄弟仓库，需本地 editable 安装）
pip install -e /path/to/QML-FF
pip install jax-md
# 或：pip install -e ".[qmlff]"   # 仅声明 jax-md，不含 qmlff 包本身
```

**不需要**设置 `UQC_API_TOKEN`（mock 模式）。

---

## 4. 分步验证

### 4.1 仅测 UQC mock 后端注册

```bash
pytest tests/quantum/test_uqc_mock_md_ml_integration.py::test_uqc_mock_backend_registered_and_mock_energy -q
```

### 4.2 流水线 + QMEF 附件（需 PySCF）

```bash
pytest tests/quantum/test_uqc_mock_md_ml_integration.py::test_pipeline_uqc_mock_attaches_qmef_for_md_ml -q
```

或：

```python
from pathlib import Path
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync

cfg = load_experiment_config("configs/example_h2_uqc_mock_md_ml.yaml")
out = run_pipeline_sync(cfg, cfg_path=Path("configs/example_h2_uqc_mock_md_ml.yaml"))
assert "qmef_ml_attachment_v1" in out["repro"]
print("VQE energy:", out["energy_after_variational"])
```

### 4.3 完整一轮主动学习（需 PySCF + QML-FF + jax-md）

```bash
pytest tests/quantum/test_uqc_mock_md_ml_integration.py::test_md_validation_loop_one_round_uqc_mock_labeling -q
```

或命令行：

```bash
python -c "
from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop
cfg = MdValidationLoopConfig.from_yaml('configs/example_h2_uqc_mock_qmlff_loop.yaml')
run_md_validation_loop(
    'configs/example_h2_uqc_mock_md_ml.yaml',
    config=cfg,
    output_dir='results/uqc_mock_md_ml',
)
"
```

成功后可检查：

- `results/uqc_mock_md_ml/md_validation_summary.json`
- `results/uqc_mock_md_ml/train_final.xyz`
- `results/uqc_mock_md_ml/train_round_*.xyz`

---

## 5. CI 行为

主 CI（`.github/workflows/ci.yml`）在 **L1 MD/ML** 阶段会执行：

```bash
pytest tests/quantum/test_uqc_mock_md_ml_integration.py -m "not slow" -q --tb=short
```

覆盖：UQC provider 注册 + mock 能量 + 流水线 QMEF 附件（需 PySCF，随 `[dev]` 安装）。

标记为 `@pytest.mark.slow` 的**完整主动学习环**测试在 CI 默认矩阵中**不运行**（需本机安装 QML-FF）；本地用上一节命令执行。

---

## 6. 云平台模拟器 + 两轮在线学习（真 API，非 mock）

使用离子阱**云模拟器** `iontrap-sim`（不是 `Matrix2` 真机）：

| 文件 | 说明 |
|------|------|
| `configs/example_h2_uqc_cloud_sim_md_ml.yaml` | `uqc_mode: real`，`meta.uqc_target: iontrap-sim`，`uqc_allow_fallback: false` |
| `configs/example_h2_uqc_cloud_sim_qmlff_loop.yaml` | `max_rounds: 2`，高保真标注 `label_top_theory_level: full_pipeline` |
| `scripts/run_uqc_cloud_sim_online_learning.py` | 预检云连接 + 跑两轮 |

```bash
export UQC_API_TOKEN='从幺正量子云平台用户中心复制'
pip install uqc-client
python scripts/run_uqc_cloud_sim_online_learning.py
```

输出目录默认：`results/uqc_cloud_sim_md_ml_2rounds/`。

**注意：** 每次 VQE 优化会多次调用 `submit_task`（与 `vqe.maxiter` 成正比）；云模拟验证已将 `maxiter` 设为 5、`shots` 为 100。需能访问 `cloud.unitaryqubit.com:8003`（公司 VPN/内网）。

---

## 7. 切换到真机（生产前 checklist）

1. 将 `uqc_mode: mock` 改为 `real`。
2. 导出 token：`export UQC_API_TOKEN='...'`（有效期约 30 分钟）。
3. `meta.uqc_target` 设为 `Matrix2`（真机）或 `iontrap-sim`（云模拟器）。
4. 确认活性空间 qubit 数 ≤ 7（当前芯片限制）。
5. 安装 `pip install uqc-client` 或 `pip install -e ".[uqc]"`。
6. 主动学习每帧 `label_energy_reference: variational` 会触发完整 VQE + 云提交，成本高，建议先用 `iontrap-sim` 验证。

---

## 8. 相关文档

- [`UQC云平台集成技术报告.md`](UQC云平台集成技术报告.md) — API、注意点、已知限制
- [`qmlff_md_integration_说明.md`](qmlff_md_integration_说明.md) — MD/ML 桥接总览
- [`h2_md_validation_phases_技术说明.md`](h2_md_validation_phases_技术说明.md) — H₂ 三阶段实践
