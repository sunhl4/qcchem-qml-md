# Examples index（仓库根 `examples/`）

与 [CONTRIBUTING.md](../CONTRIBUTING.md) 中的 CI、`scripts/check_parity_export_sample.py` 及 **docs-site** 教程并列使用。

## 新用户三条路径（精简）

| 路径 | 入口 |
|------|------|
| **Quickstart + export** | `tutorial_01_h2_vqe_export.py`；配置母版 `configs/example_h2.yaml` |
| **UCCSD / 管线** | `tutorial_02_uccsd_pipeline.py`；`configs/example_h2_uccsd.yaml` |
| **QPE / ZNE / parity** | `tutorial_03_qpe_zne_paths.py`；`configs/example_h2_qpe_track_parity_integrations.yaml`、`configs/example_h2_zne_circuit_fold.yaml` |
| **张量网络 / DMRG toy（自旋链）** | `toy_dmrg_spin_chain.py`；配套讲义 [`docs/tensor_network_qchem_self_study.md`](../docs/tensor_network_qchem_self_study.md) |

详细叙事见站点 [onboarding-three-paths](../docs-site/docs/guide/onboarding-three-paths.md)（`docs-site/` 下 `npm run docs:dev`）。

## 一次性烟测

```bash
python examples/run_all_smoke.py
```

## Tangelo → qchem-stack

见 `tangelo_facade_demo.py`：通过 **命名封装 YAML** 加载 `ExperimentConfig`（保持 YAML 为 SSOT，而非_solver dict）。
