# Config 示例目录（`configs/`）

本目录包含 **104** 个 YAML 文件：

| 类别 | 数量 | CI 门控 |
|------|------|---------|
| **ExperimentConfig**（`schema_version: 2` + `molecule`） | **96** | `python scripts/check_parity_export_sample.py` 自动发现全部 96 个并跑 config-only parity export |
| **MdValidationLoopConfig**（`max_rounds` + `force_field_backend`） | **8** | 同上脚本末尾校验 YAML 可加载 |
| 合计 | **104** | 无手工维护的抽样子集 |

复制 [`_template.yaml`](_template.yaml) 并按需修改字段。新增 experiment YAML 会自动纳入 CI，**无需**再编辑 `SAMPLE_CONFIGS_REL`。

## 全部 ExperimentConfig YAML（96，CI parity export 自动覆盖）

```
configs/_template.yaml
configs/example_custom_driver_template.yaml
configs/example_decomposition_plugin_contract.yaml
configs/example_decomposition_plugin_toy.yaml
configs/example_decomposition_plugin_two_fragment.yaml
configs/example_fe_sto3g_helike_rhf_cas22.yaml
configs/example_h2.yaml
configs/example_h2_active_space_cas_strategy.yaml
configs/example_h2_active_space_manual_strategy.yaml
configs/example_h2_adapt_doubles_pool.yaml
configs/example_h2_adapt_singles_pool.yaml
configs/example_h2_adapt_staggered_pool.yaml
configs/example_h2_adapt_uccsd_jw_alias.yaml
configs/example_h2_avas.yaml
configs/example_h2_avas_casscf_workflow.yaml
configs/example_h2_avas_stub.yaml
configs/example_h2_casscf_audit.yaml
configs/example_h2_classical_shadows_stub.yaml
configs/example_h2_echo_variational_plugin.yaml
configs/example_h2_embedding_parity.yaml
configs/example_h2_excited_smoke.yaml
configs/example_h2_geometry_file_xyz.yaml
configs/example_h2_hcb.yaml
configs/example_h2_iqcc.yaml
configs/example_h2_iqeb.yaml
configs/example_h2_iqeb_fermionic_doubles_pool.yaml
configs/example_h2_iqeb_qubit_excitation_alias.yaml
configs/example_h2_jkmn.yaml
configs/example_h2_md_ml_pauli_energy.yaml
configs/example_h2_md_ml_qmef_attach.yaml
configs/example_h2_md_ml_trajectory_full_pipeline.yaml
configs/example_h2_md_ml_trajectory_hf.yaml
configs/example_h2_micro_vqe_plugin.yaml
configs/example_h2_oo_vqe.yaml
configs/example_h2_pbc_gamma.yaml
configs/example_h2_pec_literature_stub.yaml
configs/example_h2_precomputed_bundle.yaml
configs/example_h2_projection_trace.yaml
configs/example_h2_psi4_avas.yaml
configs/example_h2_psi4_projection_mulliken.yaml
configs/example_h2_psi4_rhf_sto3g.yaml
configs/example_h2_psi4_schmidt_dmet.yaml
configs/example_h2_puccd.yaml
configs/example_h2_puccd_pauli_protocol.yaml
configs/example_h2_qcc.yaml
configs/example_h2_qcc_pauli_protocol.yaml
configs/example_h2_qiskit_shots.yaml
configs/example_h2_qite.yaml
configs/example_h2_qpe_deterministic.yaml
configs/example_h2_qpe_info_theory.yaml
configs/example_h2_qpe_main.yaml
configs/example_h2_qpe_track.yaml
configs/example_h2_qpe_track_parity_integrations.yaml
configs/example_h2_qpe_zne_pauli.yaml
configs/example_h2_sa_vqe.yaml
configs/example_h2_sampled.yaml
configs/example_h2_scbk_hea.yaml
configs/example_h2_sceom_symmetry_filtered.yaml
configs/example_h2_sto3g_density_fit.yaml
configs/example_h2_uccgd.yaml
configs/example_h2_uccgd_pauli_protocol.yaml
configs/example_h2_uccsd.yaml
configs/example_h2_uccsd_bk.yaml
configs/example_h2_uccsd_pauli_protocol.yaml
configs/example_h2_uccsd_qse_pauli_qiskit.yaml
configs/example_h2_uccsd_trotter.yaml
configs/example_h2_upccgsd.yaml
configs/example_h2_upccgsd_pauli_protocol.yaml
configs/example_h2_uqc_cloud_sim_md_ml.yaml
configs/example_h2_uqc_mock_md_ml.yaml
configs/example_h2_vqd_deflation_circuit.yaml
configs/example_h2_vqd_uccsd.yaml
configs/example_h2_vqd_uccsd_three_computable.yaml
configs/example_h2_vqe_figure_near_casci.yaml
configs/example_h2_vqs_track.yaml
configs/example_h2_vsqs.yaml
configs/example_h2_zmatrix_sto3g.yaml
configs/example_h2_zmatrix_sto3g_density_fit.yaml
configs/example_h2_zne_circuit_fold.yaml
configs/example_h2_zne_qiskit_fold.yaml
configs/example_h2o_oniom_qmmm.yaml
configs/example_h2o_sto3g_cas44.yaml
configs/example_h4_adapt_qse_benchmark.yaml
configs/example_h4_dmet_fragment_exact_small.yaml
configs/example_h4_dmet_self_consistent.yaml
configs/example_h4_projection_mulliken.yaml
configs/example_h4_schmidt_multifragment.yaml
configs/example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml
configs/example_mg_lanl2dz_ecp_density_fit.yaml
configs/example_mg_lanl2dz_ecp_rhf.yaml
configs/example_n2_sto3g_cas44.yaml
configs/example_oniom_qm_mm_demo.yaml
configs/example_oniom_toy.yaml
configs/qpe_dual_track_demo.yaml
configs/tutorial_chain_h2.yaml
configs/uqc_h2.yaml
```

## MdValidationLoopConfig YAML（8，CI 加载校验）

```
configs/example_h2_angle_md.yaml
configs/example_h2_classical_md.yaml
configs/example_h2_qmlff_md.yaml
configs/example_h2_qmp_md.yaml
configs/example_h2_qnn_native_md.yaml
configs/example_h2_uqc_cloud_sim_qmlff_loop.yaml
configs/example_h2_uqc_cloud_sim_qmlff_loop_5rounds.yaml
configs/example_h2_uqc_mock_qmlff_loop.yaml
```

## Experiment profiles (`configs/profiles/`)

Named overlays applied via `qchem_stack.config.experiment_profiles.apply_experiment_profile`:

| Profile | Template | Purpose |
|---------|----------|---------|
| `minimal` | [`profiles/minimal_h2.yaml`](profiles/minimal_h2.yaml) | Precomputed SCF, no Pauli protocol |
| `research` | [`profiles/research_h2.yaml`](profiles/research_h2.yaml) | Rich parity / workflow preview sidecars |
| `production` | [`profiles/production_h2.yaml`](profiles/production_h2.yaml) | Protocol-on defaults + repro preview |

Merge a profile dict onto any base experiment YAML, or load a template and edit `experiment_id` / `molecule`.

## 校验与 export

- **全量门控**：`python scripts/check_parity_export_sample.py`
- 允许的组合：[`docs/pre_quantum_yaml_matrix.md`](../docs/pre_quantum_yaml_matrix.md)
