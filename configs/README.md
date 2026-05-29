# Config 示例目录（`configs/`）

本目录包含 **104** 个可运行 YAML 示例（不含 `_template.yaml` 脚手架）。复制 [`_template.yaml`](_template.yaml) 并按需修改字段。

**CI parity export 抽样**：`python scripts/check_parity_export_sample.py` 覆盖 `SAMPLE_CONFIGS_REL` 中的配置（见脚本内列表）。下列 P4 算法示例已接入该门控；其余 YAML 由 smoke / 单测 / 教程按需引用。

| 文件 | 状态 |
|------|------|
| `example_h2_puccd.yaml` / `example_h2_puccd_pauli_protocol.yaml` | parity sample |
| `example_h2_upccgsd.yaml` / `example_h2_upccgsd_pauli_protocol.yaml` | parity sample |
| `example_h2_iqcc.yaml` / `example_h2_qite.yaml` | parity sample |
| `example_h2_vsqs.yaml` / `example_h2_jkmn.yaml` / `example_h2_hcb.yaml` | parity sample |
| `example_h2_qcc_pauli_protocol.yaml` | parity sample |
| `example_h2_uccgd_pauli_protocol.yaml` | 待修 YAML（暂不在 parity sample） |
| `example_h2_adapt_staggered_pool.yaml` | parity sample |
| `example_h2_qpe_deterministic.yaml` / `example_h2_qpe_info_theory.yaml` | parity sample |
| `example_h2_sceom_symmetry_filtered.yaml` | parity sample |
| `example_h4_adapt_qse_benchmark.yaml` | parity sample |
| `example_h2_md_ml_trajectory_full_pipeline.yaml` | parity sample |

## H₂ 基准族

| 文件 | 用途 |
|------|------|
| `example_h2.yaml` | 默认 VQE + Pauli 协议 |
| `example_h2_precomputed_bundle.yaml` | 离线 precomputed _lane（无 PySCF） |
| `example_h2_sampled.yaml` / `example_h2_qiskit_shots.yaml` | Shot 模拟路径 |
| `example_h2_excited_smoke.yaml` | VQD 激发态 smoke |

## UCCSD / ADAPT / IQEB

| 文件 | 用途 |
|------|------|
| `example_h2_uccsd.yaml` / `example_h2_uccsd_trotter.yaml` | UCCSD 变分 |
| `example_h2_uccsd_pauli_protocol.yaml` | UCCSD + Pauli 五阶段 |
| `example_h2_adapt_*_pool.yaml` | ADAPT 算符池 |
| `example_h2_iqeb*.yaml` | IQEB 外循环 |

## 激发态

| 文件 | 用途 |
|------|------|
| `example_h2_vqd_*.yaml` | VQD / deflation / three_computable |
| `example_h2_uccsd_qse_pauli_qiskit.yaml` | QSE + Qiskit transitions |
| `example_h2_sa_vqe.yaml` | SA-VQE |

## Embedding / DMET / Projection

| 文件 | 用途 |
|------|------|
| `example_h2_embedding_parity.yaml` | embedding parity snapshot |
| `example_h4_schmidt_multifragment.yaml` | Schmidt DMET（slow） |
| `example_h2_projection_trace.yaml` | projection L1 trace |

## UQC 云平台

| 文件 | 用途 |
|------|------|
| `uqc_h2.yaml` | UQC backend 基础 |
| `example_h2_uqc_mock_md_ml.yaml` | mock + QMEF 附件 |
| `example_h2_uqc_cloud_sim_*.yaml` | 云模拟 + MD/ML loop |

## MD / ML

| 文件 | 用途 |
|------|------|
| `example_h2_md_ml_*.yaml` | QMEF 导出变体 |
| `example_h2_qmlff_md.yaml` | QML-FF MD 桥 |

## 其它后端 / 体系

| 文件 | 用途 |
|------|------|
| `example_h2_psi4_*.yaml` | Psi4 交叉后端 |
| `example_h2o_sto3g_cas44.yaml` / `example_n2_sto3g_cas44.yaml` | 更大活性空间 |
| `example_h2_pbc_gamma.yaml` | 周期性边界 |
| `example_decomposition_plugin_*.yaml` | 分解插件 |

## 校验与 export

- Parity export 门控：`python scripts/check_parity_export_sample.py`
- 允许的组合：[`docs/pre_quantum_yaml_matrix.md`](../docs/pre_quantum_yaml_matrix.md)
