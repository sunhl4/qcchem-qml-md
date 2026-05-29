---
title: AVAS → CASSCF → integrals 工作流
description: 一键 AVAS+CASSCF 实验 YAML 与 parity 导出路径（P4-B10/B11）。
---

# AVAS → CASSCF → integrals 工作流

本页面向**用户**（非内部 `说明_*.md`），说明如何用仓库里的 AVAS+CASSCF 模板跑通 active-space 积分，并导出 Methods 机读字段。

## 快速开始

1. 复制或直接使用 [`configs/example_h2_avas_casscf_workflow.yaml`](https://github.com/your-org/qchem_qml_md/blob/main/configs/example_h2_avas_casscf_workflow.yaml)（H₂ STO-3g 示例）。
2. 确保 `active_space.strategy: avas` 且 `chemistry_extended.avas.ao_labels` 非空。
3. 运行 pipeline（与 `example_h2.yaml` 相同 CLI）：

```bash
python -c "
from pathlib import Path
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
cfg = load_experiment_config('configs/example_h2_avas_casscf_workflow.yaml')
out = run_pipeline_sync(cfg, cfg_path=Path('configs/example_h2_avas_casscf_workflow.yaml'))
print('E_var =', out.get('energy_after_variational'))
"
```

## YAML 要点

| 块 | 作用 |
|----|------|
| `chemistry_extended.avas` | AO 标签、threshold、minao — AVAS 选轨输入 |
| `chemistry_extended.casscf.orbital_optimization_for_integrals` | 是否在积分前做 CASSCF 轨道优化（推荐路径见 `docs/说明_scf配置.md`） |
| `active_space.strategy: avas` | 触发 AVAS 选 active space |
| `quantum.*` | 后续 VQE/ADAPT 与 Pauli protocol（与常规模板相同） |

## Parity / Methods 导出

开启 `parity_integrations.resource_estimation_preview: true` 时，config-only 导出会附带：

- `algorithm_registry_alignment_v1`
- `md_ml_repro_freeze_fields_v1`（MD/ML 字段冻结清单）
- `operator_pool_registry_export_v1`

```bash
python scripts/export_parity_criteria_table.py configs/example_h2_avas_casscf_workflow.yaml | jq '.embedding.mode'
```

## 相关文档

- 内部 SCF/AVAS 细节：仓库 `docs/说明_scf配置.md`
- Psi4 后端 AVAS：[`Psi4 后端指南`](/guide/psi4-backend)
- 化学与嵌入总览：[`化学与嵌入`](/guide/chemistry-and-embedding)
