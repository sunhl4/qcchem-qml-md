---
title: UCCSD Trotter 层与 export
description: 使用 JW + quantum.uccsd_trotter_steps 跑 H₂，并用 export 脚本带出 parity 字段
---

本教程对应广义 P1 **波次 G1** 的一条可运行路径：在变分层使用 **一阶 Trotter 重复层** 的闭壳 UCCSD（与稠密簇指数 `UCCSDVQE` 相对），并在 **config-only** 导出中看到稳定的 `inquanto_gap_categories` 与 `parity_snapshot` 相关键。

## 你将学到

- `configs/example_h2_uccsd_trotter.yaml` 里 **`quantum.uccsd_trotter_steps`** 的含义（JW-only）。
- 如何用 `scripts/export_parity_criteria_table.py` 做 **无 PySCF** 的契约回归抽样。

## 运行管线（需 PySCF）

在仓库根目录：

```bash
python -c "from pathlib import Path; from qchem_stack.config import load_experiment_config; from qchem_stack.orchestration.pipeline import run_pipeline_sync; p=Path('configs/example_h2_uccsd_trotter.yaml'); cfg=load_experiment_config(p); out=run_pipeline_sync(cfg, cfg_path=p); print(out['vqe_meta'].get('uccsd_trotter_steps'), out['repro']['parity_snapshot'].get('uccsd_trotter_steps'))"
```

期望：`vqe_meta` 与 `parity_snapshot` 均含 **`uccsd_trotter_steps: 2`**（与 YAML 一致）。

## Export（可无 PySCF）

```bash
python scripts/export_parity_criteria_table.py configs/example_h2_uccsd_trotter.yaml
```

输出 JSON 中含 `parity_export_schema_version`、`inquanto_gap_categories` 等稳定键；CI 由 `scripts/check_parity_export_sample.py` 抽样覆盖本配置。

## 边界（诚实）

- **BK / SCBK**：同一套 UCCSD Trotter  ansatz **未**在非 JW 映射上实现；变分仍可用 HEA + BK/SCBK Hamiltonian。详见 [公开 parity 矩阵](/parity/public-matrix) §2。

## 相关

- [工作流与 YAML 概览](/tutorial/workflow-overview)
- [read repro 键](/tutorial/read-repro-keys)
- 仓库 `docs/inquanto_public_parity_matrix.md`
