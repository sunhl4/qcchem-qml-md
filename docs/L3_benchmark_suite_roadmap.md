# L3 小体系基准套件（Y1 Q3 交付物 — 路线图）

**目的**：在 **排除云/硬件** 前提下，为「公开面最大对齐」提供 **可重复数值门槛**（不等价 InQuanto 闭源默认）。

## 规划项（实施顺序）

1. **基准 1**：H₂ sto-3g，活性 (2e,2o)，VQE+Pauli 协议 — 固定 `random_seed`、`energy_after_variational`、`energy_pauli_protocol` 阈值（见后续 `configs/l3_*.yaml`）。
2. **基准 2**：同上 + `run_sampled_pauli_protocol` 或 Qiskit shots 路径 — 方差/shots 门槛。
3. **基准 3（可选）**：极小 Schmidt 单轮 — `schmidt_dmet_cycles_executed` 与能量一致性与文档断言。

## CI 策略

- **主 CI**：仅 schema / config 校验 + **skip** 重型断言。
- **夜间 / 可选 job**：`pytest -m l3` 或环境变量 `QCHEM_RUN_L3=1` 时跑全量。

## 与 export

跑完后 `export_parity_criteria_table --results out.json` 必须包含文档用键（与 `scripts/export_parity_criteria_table.py` 一致）。

## 占位单测

见 `tests/test_l3_benchmark_smoke.py`（默认 skip，文档指针回本页）。
