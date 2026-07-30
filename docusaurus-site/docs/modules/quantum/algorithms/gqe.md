---
title: GQE（生成式量子本征求解）
description: GPT-QE 完整手册：文献、token 池数学、paper/native、YAML 全字段、调用与调参。
---

# GQE（Generative Quantum Eigensolver）

本页是 **使用者手册级** GQE 说明（风格对齐 PennyLane / InQuanto 算法章）：先讲问题与理论，再落到本栈池构造、训练环、顶层 `gqe:` 字段与可复制调用。

**重要**：GQE 是 **集成侧车**，配置在顶层 `gqe:`（`GqeSpec`），**不是** `quantum.algorithm` 注册表成员。选型短文：[GQE 技术手册](/guide/gqe-generative-eigensolver) · 包层：[integrations](/modules/integrations)。

实现：`qchem_stack.integrations.gqe`。入口：`run_gqe_from_config`。报告 schema：`gqe_train_report_v1`。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 方法提出 | K. Nakaji et al., *The generative quantum eigensolver (GQE) and its application for ground state search*, [arXiv:2401.09253](https://arxiv.org/abs/2401.09253)（2024） |
| 附录 A.2 池 | UCCSD Pauli 串 × 时间网格；本栈 `build_paper_uccsd_pool` |
| 附录 B 损失 | logit-matching 与 GRPO；本栈 `paper_losses` |

---

## 2. 要解决什么问题

固定 ansatz（HEA / UCCSD）在表达力与参数量之间折中；ADAPT 按梯度生长但仍是 **连续角度** 优化。  
**GQE** 把 ansatz 写成 **离散 token 序列**：生成模型（GPT）采样「选哪个算符 × 哪个时间步」，oracle 在量子态上估能量，再用 GRPO / logit-matching 更新模型——用学习到的先验探索组合空间。

| 场景 | 是否用 GQE |
|------|------------|
| 对照 Nakaji 数值（H₂ / LiH / …） | 是 |
| 固定长度 Pauli 旋转序列探索 | 是 |
| 标准连续变分 VQE | 否 → [VQE](./vqe-hea) / [UCCSD](./uccsd) |
| 硬件 shots / 噪声实验 | 本栈默认 **statevector oracle**；真机需另接 |

---

## 3. 理论思想

### 3.1 Token → 电路

池 $\mathcal{G}=\{U_j\}$，每个 token $j$ 对应一个酉（常为 $e^{i P t}$ 或单位元）。长度 $L$ 的序列 $\mathbf{j}=(j_1,\ldots,j_L)$ 制备

$$
|\psi(\mathbf{j})\rangle
= U_{j_L}\cdots U_{j_1}\,|\mathrm{ref}\rangle
$$

成本 $C(\mathbf{j})=\langle\psi(\mathbf{j})|H|\psi(\mathbf{j})\rangle$（本栈稠密 / statevector）。

### 3.2 训练环（论文 §3.1 风格）

1. **Warmup**：随机 / HF 类序列填 FIFO buffer，oracle 写能量。  
2. **采样**：GPT 按当前参数采 $N_{\mathrm{sample}}$ 条长度 $L$ 序列。  
3. **更新**：用 buffer 上的 logit-matching（`lm`）或 GRPO（`grpo`）做 $N_{\mathrm{iter}}$ 步。  
4. 重复 `epochs`；跟踪最优采样能量。

`prefill`：只做 warmup、不跑 GPT 更新。  
`condition`：实例条件（键长 / 哈密顿指纹）生成，见 `conditional_trainer`。

---

## 4. 数学实现（本栈）

### 4.1 Paper 池（`mode: paper`）

`build_paper_uccsd_pool`（附录 A.2）：

1. 取注册池 `fermionic_uccsd` 的费米子生成元 → 抽出 Hermitian Pauli 串 $\{P\}$。  
2. 与时间网格 $T$（`PAPER_TIME_GRID`，形如 $\pm 2^k/320$）做笛卡尔积。  
3. 存储生成元 $G=iP$，使传播 $\mathrm{expm}(t\,G)=e^{iPt}$；可选含单位元。  
4. `apply_pool_sequence` 按 token 顺序乘到参考态。

### 4.2 Native 池（`mode: native`）

`pool_id`（默认 `fermionic_uccsd`）→ `build_registered_operator_pool`；训练环 `run_gqe_lm_loop`（LM/GRPO 演示）。  
**约束**：native 下 `train_mode` 仅允许 `gpt`。

### 4.3 入口与模式分发

`run_gqe_from_config(cfg)`：

| 条件 | 行为 |
|------|------|
| 无 JAX/optax | `ImportError`（需 `qchem-stack[gqe]`） |
| `train_mode=condition` | `_run_condition_mode` |
| `mode=paper` | `run_paper_gqe_loop` + paper 池 |
| `mode=native` | `run_gqe_lm_loop` + 注册池 |

问题束：`build_gqe_problem_from_config` → `GQEProblemBundle`（含 `cost_fn` / `oracle_fn`、可选 FCI/SCF 对照）。

### 4.4 管线位置

编排 `_maybe_run_gqe_stage`：

- `gqe.enabled: true` 时，在变分阶段之后（或 `skip_variational: true` 时跳过 VQE，仍走 SCF / pre-quantum）调用同一 API。  
- 结果写入管线输出 / report（`gqe_train_report_v1`），**不**替换 `quantum.algorithm` 主 ID 语义。

---

## 5. 参数详表

### 5.1 YAML（顶层 `gqe:`）

```yaml
gqe:
  enabled: true                 # 默认 false
  mode: paper                   # paper | native
  train_mode: gpt               # gpt | prefill | condition
  molecule: h2                  # 可选：h2 | lih | beh2 | n2（覆盖几何）
  bond_angstrom: 0.74
  epochs: 5                     # null → 路径默认
  n_sample: 8
  seq_len: 6
  loss: grpo                    # lm | grpo（默认 grpo）
  seed: null                    # null → experiment random_seed
  d_model: 32
  n_layers: 2
  paper_model: false            # true → 强制 192×6
  warmup_samples: 32
  buffer_max: 128
  n_batch: 16
  n_iter: 2
  learning_rate: 1.0e-3
  checkpoint_dir: null
  checkpoint_every: 0
  log_every: 1
  condition_bonds: null         # condition 模式键长列表
  n_condition: 8
  pool_id: fermionic_uccsd      # native
  skip_variational: true
```

| 字段 | 含义 | 默认 |
|------|------|------|
| `enabled` | 是否跑 GQE 侧车 | `false` |
| `mode` | paper / native | `paper` |
| `train_mode` | gpt / prefill / condition | `gpt` |
| `molecule` | paper 几何重建 id | `null` |
| `bond_angstrom` | paper 键长 (Å) | `0.74` |
| `epochs` / `n_sample` / `seq_len` | 训练与序列长度 | 路径感知 |
| `loss` | `lm` \| `grpo` | `grpo` |
| `d_model` / `n_layers` | Transformer 宽/深 | `64` / `2` |
| `paper_model` | 强制论文规模 192×6 | `false` |
| `warmup_samples` | FIFO warmup 条数 | paper 常 200 |
| `buffer_max` / `n_batch` / `n_iter` | buffer 与每 epoch 更新 | 见 paper_spec |
| `learning_rate` | 优化步长 | `1e-3` |
| `condition_bonds` / `n_condition` | 条件特征 | 见上 |
| `pool_id` | native 算符池 | `fermionic_uccsd` |
| `skip_variational` | 跳过 HEA/UCCSD | `false` |

化学块仍用常规 `molecule` / `scf` / `active_space`；`gqe.molecule` 仅在 paper 覆盖几何时生效。

### 5.2 代表配置

| 文件 | 意图 |
|------|------|
| `configs/example_h2_gqe_gpt.yaml` | paper + gpt，烟雾规模 |
| `configs/example_h2_gqe_plan_b.yaml` | Plan B 对照 |
| `configs/example_h2_gqe_prefill.yaml` | 仅 warmup |
| `configs/example_h2_gqe_condition.yaml` | 条件生成 |

教程：[GQE 变体](/tutorial/gqe-variants) · [Nakaji H₂](/tutorial/gqe-nakaji-h2)。

### 5.3 Python

```python
from qchem_stack.integrations.gqe.api import run_gqe_from_config
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2_gqe_gpt.yaml")
# 需：pip install 'qchem-stack[gqe]'
report = run_gqe_from_config(cfg)
print(report.get("schema"), report.get("train_mode"), report.get("best_energy"))
```

管线：

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_gqe_gpt.yaml")
# 查 out 中 gqe / report 相关键（依编排写入）
```

---

## 6. 函数调用与验证

### 验证命令（无 JAX 时至少校验配置）

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for f in (
  'configs/example_h2_gqe_gpt.yaml',
  'configs/example_h2_gqe_plan_b.yaml',
  'configs/example_h2_gqe_prefill.yaml',
  'configs/example_h2_gqe_condition.yaml',
):
  c=load_experiment_config(f)
  assert c.gqe.enabled
  print(f, c.gqe.mode, c.gqe.train_mode)
print('ok')
"
```

### 期望输出

- 四行配置摘要 + `ok`  
- 若已装 `[gqe]`：`run_gqe_from_config` 返回 `schema == gqe_train_report_v1`（或契约常量等价字符串）

### 依赖探测

```bash
python3 -c "
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation
print(probe_gqe_jax_installation())
"
```

---

## 7. 调参与排错

| 现象 | 处理 |
|------|------|
| `ImportError: jax/optax` | `pip install 'qchem-stack[gqe]'` |
| native + `prefill`/`condition` | 换 `mode: paper` 或 `train_mode: gpt` |
| 太慢 / OOM | 减小 `d_model`/`n_layers`/`epochs`/`seq_len`；勿开 `paper_model` 烟雾 |
| 能量不降 | 增 `warmup_samples`；换 `loss: grpo`；查 pool 与活性空间 |
| 与 VQE 抢资源 | `skip_variational: true` |
| 想改池内容 | paper 改 `build_paper_uccsd_pool` 基底；native 改 `pool_id`（见 [算符池](./operator-pools)） |

---

## 8. 边界与相关

- **不是** `quantum.algorithm`；勿在算法注册表里找 `gqe`。  
- 默认 oracle 为 statevector；epistemic 上对齐算法数值，非论文硬件噪声段。  
- Blueprint / 探针：`integrations.gqe.blueprint`、`probe_gqe_jax_installation`。  

相关：

- [选型 · GQE](/guide/gqe-generative-eigensolver) · [VQE](./vqe-hea) · [UCCSD](./uccsd) · [ADAPT](./adapt-vqe) · [算符池](./operator-pools) · [integrations](/modules/integrations)
