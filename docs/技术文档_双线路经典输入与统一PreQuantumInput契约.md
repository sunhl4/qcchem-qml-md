# 技术文档：双线路经典输入与统一 `PreQuantumInput` 契约

## 1. 目标

本项目同时支持两条上游线路，并在量子阶段前统一收口为同一输入契约：

- 线路 A（在线经典）：用户提供结构/基组等输入，项目内调用 `scf.driver` 后端执行经典计算。
- 线路 B（离线经典）：用户或外部数据集提前计算经典结果，项目读取离线文件直接进入量子阶段。

统一收口对象为 `PreQuantumInput`（`src/qchem_stack/chem/pre_quantum_input.py`）。

## 2. 架构约束

- 量子算法与后续协议阶段不应区分 A/B 线路。
- A/B 线路在进入量子阶段前必须都转为 `PreQuantumInput`。
- 配置层通过 `scf.driver` 明确线路来源：
  - 在线：`pyscf` / `psi4` / 其它注册后端
  - 离线：`precomputed`

## 2.1 `PreQuantumInput` 稳定摘要字段

Pipeline 输出的 `out["pre_quantum_input"]` 仍保留完整 `hamiltonian_meta` 以兼容既有分析脚本；同时提供一组稳定顶层字段，作为 UI、API、Methods 表格优先消费的轻量契约：

| 字段 | 说明 |
|---|---|
| `schema` | 固定为 `pre_quantum_input_v1` |
| `source` | 进入量子前分支来源，例如 `canonical_active_space_integral_pack`、`precomputed_bundle`、`embedding_plugin` |
| `backend_tag` | `ClassicalMeanFieldReference.backend_tag()`，如 `pyscf`、`precomputed`、外部 solver 标签 |
| `n_qubits` | 当前 `QubitHamiltonian` 量子比特数 |
| `integral_source` | 哈密顿量积分/Pauli 来源；优先来自 `CanonicalActiveSpaceIntegralPack.provenance` 或 bundle/plugin schema |
| `fermion_to_qubit_map` | `jordan_wigner` / `bravyi_kitaev` / `symmetry_conserving_bravyi_kitaev`，若上游无法声明则可为空 |
| `hamiltonian_fingerprint` | 排序 Pauli 项与系数的稳定 SHA-256 摘要前缀 |
| `reference_energy_au` / `scf_energy_au` | 经典参考态总能量（与 `out["scf_energy"]` 对账） |
| `n_active_orbitals` / `n_active_electrons` | 活性空间尺寸（pack 或 qubit meta） |
| `hamiltonian_branch` | `canonical_active_space_integral_pack` / `schmidt` / `projection` / `plugin` / `precomputed` |
| `hamiltonian_fixed_before_variational` | 变分前算符是否已固定 |
| `post_variational_embedding_audit_only` | 变分后 `embedding_workflow` 是否仅审计 |
| `hamiltonian_summary` | 上述字段加 `integral_openfermion_bridge`、`jw_build`、active-space 尺寸等轻量补充 |
| `hamiltonian_meta` | 完整历史元数据；可能较大，供调试和深度审计 |
| `canonical_active_space_integral_pack` | canonical pack 存在时包含 schema、provenance、active-space 尺寸与 compact storage schema |

分支 `source` 当前约定：

<!-- BEGIN:PRE_QUANTUM_SOURCE_TABLE -->
| source | 路径 |
|---|---|
| `precomputed_bundle` | 离线 bundle 直接提供 pre-quantum Hamiltonian |
| `embedding_plugin` | `embedding.mode=plugin` 的 decomposition JSON / 外部 fragment payload |
| `schmidt_atomic_production` | Schmidt impurity Hamiltonian 分支 |
| `projection_fragment_mulliken_mo` | PySCF Mulliken MO projection 分支 |
| `canonical_active_space_integral_pack` | 在线经典主路径：`ClassicalMeanFieldReference` → `CanonicalActiveSpaceIntegralPack` → `QubitHamiltonian` |
<!-- END:PRE_QUANTUM_SOURCE_TABLE -->

`integral_source` 与 `integral_openfermion_bridge` 不应硬编码假装来自 PySCF。优先级为：显式参数 > canonical pack provenance > 后端标签兜底；离线 bundle 与 decomposition plugin 使用自己的 Pauli-term 来源标签。

## 3. 离线线路数据格式

离线模式读取 `classical_reference_bundle_v1` JSON（见 `src/qchem_stack/chem/precomputed_bundle.py`）。

最小结构：

```json
{
  "schema": "classical_reference_bundle_v1",
  "classical_reference": {
    "e_tot": -1.116708174,
    "mo_energy": [-0.580628, 0.676341],
    "driver_meta": {
      "upstream_classical_software_tag": "external_dataset"
    }
  },
  "pre_quantum_input": {
    "schema": "pre_quantum_input_v1",
    "qubit_hamiltonian": {
      "n_qubits": 2,
      "terms": [
        { "label": "II", "coeff": -0.55 },
        { "label": "ZZ", "coeff": 0.08 }
      ]
    }
  }
}
```

## 4. Pauli 标签支持

`qubit_hamiltonian.terms[].label` 支持两种写法：

- 紧凑写法：`"II"`、`"ZZ"`、`"XYZI"`（长度必须等于 `n_qubits`）
- 索引写法：`"Z0 Z1"`、`"X0 Y2"`

## 5. 配置方式

使用 `scf.driver='precomputed'` 并提供 `scf.precomputed_bundle_path`：

```yaml
scf:
  driver: "precomputed"
  method: "RHF"
  precomputed_bundle_path: "configs/precomputed_classical_reference_h2.json"
```

示例配置：

- `configs/example_h2_precomputed_bundle.yaml`
- `configs/precomputed_classical_reference_h2.json`

## 5.1 在线线路的结构文件输入（非手填坐标）

在线经典线路无需手写 `coordinates`，可通过 `molecule.geometry_file` 读取结构文件（当前支持 XYZ）：

```yaml
molecule:
  geometry_file: "structures_h2.xyz"
  coordinate_unit: "angstrom"
```

端到端示例：

- `configs/example_h2_geometry_file_xyz.yaml`
- `configs/structures_h2.xyz`

该线路会在配置加载阶段将几何文件解析为标准分子坐标，再进入 `scf.driver` 对应后端执行经典计算。

## 6. 迁移与转换工具

脚本 `scripts/build_precomputed_bundle.py` 可把 decomposition-plugin JSON + 外部经典数值组装为 bundle：

```bash
python scripts/build_precomputed_bundle.py \
  --decomposition-json configs/decomposition_plugin_toy_integrals.json \
  --output configs/precomputed_classical_reference_h2.json \
  --e-tot -1.116708174 \
  --mo-energy "-0.580628,0.676341"
```

## 7. 推荐 import（建哈密顿量 / PreQuantumInput）

| 场景 | 推荐入口 | 避免 |
|---|---|---|
| 端到端 YAML | `qchem_stack.orchestration.pipeline.run_pipeline_sync` / `run_pipeline_from_config` | 手写 SCF + 旧 `molecular_hamiltonian_from_classical_reference` |
| 库内已有 `ExperimentConfig` + `ClassicalMeanFieldReference` | `qchem_stack.chem.pre_quantum_build.build_pre_quantum_input` | 直接调 `hamiltonian_with_schmidt_context`（编排层） |
| 仅要 `QubitHamiltonian`（遗留脚本） | `build_pre_quantum_input(...).qubit_hamiltonian` | `molecular_hamiltonian_from_classical_reference`（已 `DeprecationWarning`） |
| 允许/禁止 YAML 组合 | `docs/pre_quantum_yaml_matrix.md` | 在业务代码里硬编码 driver 字符串分支 |

单次 pipeline run 内，`RunBuildCache` 会复用相同 `(cfg, mean_field)` 的 `CanonicalActiveSpaceIntegralPack`；统计见 `out["pre_quantum_build_cache"]`。

## 8. 兼容性说明

- 在线线路与离线线路最终都会产出 `PreQuantumInput`，量子侧入口统一。
- `precomputed` 线路不提供在线后端相关的派生能力（如 AO/Lowdin embedding 输入、在线 RDM 修正）。
- 配置约束：
  - `scf.driver='precomputed'` 时必须给 `scf.precomputed_bundle_path`
  - 其它 driver 不允许给 `scf.precomputed_bundle_path`
- `scf.driver=psi4`：闭壳 RHF + 小活性空间可走 `CanonicalActiveSpaceIntegralPack`（`chem.integrals.psi4_active_space_exporter`）；**不**支持 Schmidt / AVAS / Mulliken projection（配置层拒绝，见 `pre_quantum_yaml_matrix.md`）。
