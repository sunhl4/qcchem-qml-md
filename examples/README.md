# Examples index（仓库根 `examples/`）

与 [CONTRIBUTING.md](../CONTRIBUTING.md) 中的 CI、`scripts/check_parity_export_sample.py` 及 **docs-site** 教程并列使用。

这些路径也对应 **YAML → pipeline → `run_summary` / export → pytest** 的可复现 **open-stack** 入口（见 `docs/execution/day001_day090_tangelo_gap_calendar.md`）；不声称与 InQuanto / Tangelo 行级 parity。

## 新用户三条路径（精简）

| 路径 | 入口 |
|------|------|
| **Quickstart + export** | `tutorial_01_h2_vqe_export.py`；配置母版 `configs/example_h2.yaml` |
| **UCCSD / 管线** | `tutorial_02_uccsd_pipeline.py`；`configs/example_h2_uccsd.yaml` |
| **QPE / ZNE / parity** | `tutorial_03_qpe_zne_paths.py`；`configs/example_h2_qpe_track_parity_integrations.yaml`、`configs/example_h2_zne_circuit_fold.yaml` |
| **UCCSD below SCF** | `tutorial_04_uccsd_below_scf.py` |
| **张量网络 / DMRG toy（自旋链）** | `toy_dmrg_spin_chain.py`；配套讲义 [`docs/tensor_network_qchem_self_study.md`](../docs/tensor_network_qchem_self_study.md) |

详细叙事见站点 [onboarding-three-paths](../docs-site/docs/guide/onboarding-three-paths.md)（`docs-site/` 下 `npm run docs:dev`）。

## 一次性烟测

```bash
python examples/run_all_smoke.py
```

## Tangelo → qchem-stack

见 `tangelo_facade_demo.py`：通过 **命名封装 YAML** 加载 `ExperimentConfig`（保持 YAML 为 SSOT，而非_solver dict）。

## Declarative YAML pipelines（Path B）

使用 `qchem_stack.config.load_experiment_config` 与 `qchem_stack.orchestration.pipeline.run_pipeline_sync` 加载 `configs/example_*.yaml`（或打包的 parity / 教程 YAML）。示例：

- Mean-field + VQE: `configs/example_h2.yaml`
- Decomposition plugin（contract schema + fragment energy stubs）: `configs/example_decomposition_plugin_contract.yaml`
- AVAS **stub**（`strategy=avas_stub`）: `configs/example_h2_avas_stub.yaml` — meta 经 `chem.active_space.mean_field_meta`
- **PySCF AVAS**（`strategy=avas` 且 `chemistry_extended.avas_ao_labels` 非空）: `configs/example_h2_avas.yaml`
- Classical shadows **stub**: `configs/example_h2_classical_shadows_stub.yaml`

CI 中 parity export 抽样见 `scripts/check_parity_export_sample.py`。

## MD / QMEF bridge（Path C）

- Schema 与 stub：`qchem_stack.md_bridge`（`QMEFDataset`、`QMFrame`、`StubTorchMLIPTrainer`）
- 测试：`tests/test_md_bridge.py`、`tests/test_qmef_trainer_smoke.py`（marker `l1_md_ml`）

## InQuanto-style quantum problem（PySCF → OpenFermion）

可运行脚本：`examples/example_inquanto_style_quantum_problem.py`。

**Docs-site（VitePress）：**

- 中文：`docs-site/docs/guide/chemistry-and-embedding/inquanto-pyscf-problem-analog.md`
- 英文：`docs-site/docs/en/guide/chemistry-and-embedding/inquanto-pyscf-problem-analog.md`
