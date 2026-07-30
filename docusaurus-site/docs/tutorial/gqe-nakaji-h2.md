# GPT-QE（GQE）H₂ 快速上手

本教程用仓库内的 **Plan B** 实现跑通 Nakaji 等提出的 Generative Quantum Eigensolver（GPT-QE）在 H₂ / STO-3G / CAS(2,2) 上的最短路径。

## 目标

- 安装可选依赖 `.[gqe]`
- 用稳定 API `run_gqe_from_config` 完成一次短训练
- 读取 `GQE_TRAIN_REPORT_V1` 报告中的能量与化学精度标志

## 前置条件

```bash
pip install -e ".[chem,gqe]"
```

配置：`configs/example_h2_gqe_plan_b.yaml`（顶层 `gqe:` 块；**不是** `quantum.algorithm`）。

## 思想一句话

经典 **生成模型**（小型 Transformer）采样算符 token 序列 → 用 `qchem_stack` 的 **statevector 能量 oracle** 打分 → 在经典侧用 logit-matching / GRPO 更新生成模型。量子线路深度由固定序列长度 $L$ 控制；训练本身不依赖 `quantum.algorithm: vqe`。

## 运行示例

```bash
python examples/tutorial_gqe_h2_smoke.py
# 或显式指定配置
python examples/tutorial_gqe_h2_smoke.py --config configs/example_h2_gqe_plan_b.yaml --out /tmp/gqe_h2.json
```

Python API：

```python
from qchem_stack.integrations.gqe import run_gqe_from_config

report = run_gqe_from_config("configs/example_h2_gqe_plan_b.yaml")
print(report["best_energy"], report.get("chemical_accuracy"))
```

## 关键 YAML 字段（`gqe:`）

| 字段 | 含义（smoke 配置） |
|------|-------------------|
| `enabled` | `true` 时 pipeline 可挂钩运行 |
| `mode` | `paper` = 论文 Pauli×时间网格池 + paper trainer |
| `molecule` / `bond_angstrom` | 论文分子与键长（Å） |
| `epochs` / `n_sample` / `seq_len` | 短训练超参 |
| `loss` | `grpo` 或 `lm` |
| `skip_variational` | `true` 时跳过 HEA/UCCSD VQE，只跑 GQE |

## 验证清单

- 命令退出码为 0
- 打印 `schema=gqe_train_report_v1`、`paper=arXiv:2401.09253`
- `best_energy` 为有限浮点数，`n_energy_evals > 0`

## 论文级复现

```bash
python examples/gqe_nakaji_paper_repro.py --molecule h2 --bond 0.74 --epochs 30
python examples/gqe_nakaji_paper_repro.py --checklist
```

完整理论、数学与模块映射见 [GQE 技术手册](../guide/gqe-generative-eigensolver)。

## 下一步

- [GQE 技术手册](../guide/gqe-generative-eigensolver)
- [UCCSD Trotter 与导出](./uccsd-trotter-export)（对照变分基线）
- [读懂 repro 关键字段](./read-repro-keys)

## 验证命令

```bash
python examples/tutorial_gqe_h2_smoke.py
```

## 期望输出

- 退出码 `0`
- 写出 JSON 报告（若指定 `--out`）
