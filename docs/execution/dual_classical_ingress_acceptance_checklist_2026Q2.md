# Dual Classical Ingress Acceptance Checklist (2026Q2)

范围：验收“双线路经典输入（在线 + 离线）→ 统一 `PreQuantumInput`”能力闭环。

## A. 配置层验收

- [ ] 在线经典样例可加载：`configs/example_h2_geometry_file_xyz.yaml`
- [ ] 离线经典样例可加载：`configs/example_h2_precomputed_bundle.yaml`
- [ ] `scf.driver='precomputed'` 缺少 `scf.precomputed_bundle_path` 时报错
- [ ] 非 `precomputed` driver 使用 `scf.precomputed_bundle_path` 时报错
- [ ] 相对 `precomputed_bundle_path` 可按 YAML 目录解析为绝对路径

对应模块：

- `src/qchem_stack/config/scf.py`
- `src/qchem_stack/config/experiment.py`
- `src/qchem_stack/config/_experiment_validation.py`

## B. 在线经典（结构文件）验收

- [ ] `molecule.geometry_file`（XYZ）可解析为分子结构
- [ ] `geometry_file` 与 `coordinates` 同时提供时拒绝
- [ ] pipeline 端到端可运行并输出：
  - [ ] `scf_energy`
  - [ ] `pre_quantum_input.schema == "pre_quantum_input_v1"`

对应模块/样例：

- `src/qchem_stack/config/geometry_files.py`
- `configs/structures_h2.xyz`
- `configs/example_h2_geometry_file_xyz.yaml`
- `tests/test_geometry_files.py`

## C. 离线经典（预计算 bundle）验收

- [ ] `classical_reference_bundle_v1` 可读取
- [ ] 可生成 `MolecularMeanFieldResult`
- [ ] 可生成 `QubitHamiltonian`
- [ ] pipeline 预计算线路输出：
  - [ ] `out["pre_quantum_input"]["meta"]["source"] == "precomputed_bundle"`
  - [ ] `out["hamiltonian_meta"]["integral_source"] == "classical_reference_bundle_v1"`

对应模块/样例：

- `src/qchem_stack/chem/precomputed_bundle.py`
- `src/qchem_stack/chem/solvers/precomputed_solver.py`
- `configs/precomputed_classical_reference_h2.json`
- `tests/test_precomputed_bundle.py`
- `tests/test_pipeline_precomputed_lane.py`

## D. 统一量子入口验收

- [ ] 在线/离线两条路线都在量子阶段前收口为 `PreQuantumInput`
- [ ] 量子插件上下文优先读取 `pre_quantum_input`（兼容旧 `hamiltonian`）

对应模块：

- `src/qchem_stack/chem/pre_quantum_input.py`
- `src/qchem_stack/orchestration/pipeline.py`
- `src/qchem_stack/quantum/variational_plugins/spec.py`

## E. Registry 与扩展面验收

- [ ] `registered_solver_ids()` 包含 `precomputed`
- [ ] 现有 `pyscf` / `psi4` 行为不回归（契约测试通过）

对应模块：

- `src/qchem_stack/chem/solvers/registry.py`
- `tests/test_solver_registry_contract.py`

## F. 工具与文档验收

- [ ] 转换脚本可生成 bundle：`scripts/build_precomputed_bundle.py`
- [ ] 架构文档已声明 dual ingress invariant
- [ ] 用户指南中有“双线路经典输入”入口页（含中/英镜像）

对应文档：

- `docs/技术文档_双线路经典输入与统一PreQuantumInput契约.md`
- `docs/ENGINEERING_ARCHITECTURE.md`
- `docusaurus-site/docs/guide/dual-classical-ingress.md`
- `docs-site/docs/guide/chemistry-and-embedding/dual-classical-ingress.md`
- `docs-site/docs/en/guide/chemistry-and-embedding/dual-classical-ingress.md`

## 建议验收命令

```bash
python3 -m py_compile src/qchem_stack scripts tests
pytest tests/test_config_molecule_inputs.py -q
pytest tests/test_geometry_files.py -q
pytest tests/test_precomputed_bundle.py tests/test_pipeline_precomputed_lane.py -q
pytest tests/test_solver_registry_contract.py -q
```

> 注：若本机缺少 `pyscf` / `openfermion` / `pydantic`，请先安装依赖再执行完整验收。

## 签字区

- 验收日期：`YYYY-MM-DD`
- 验收环境（Python / extras）：
  - （填写）
- 结论：通过 / 有条件通过 / 未通过
- 阻塞项：
  - （填写）
- 负责人（签字）：
  - （填写）
