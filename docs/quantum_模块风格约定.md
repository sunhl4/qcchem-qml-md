# Quantum 模块代码与架构风格约定

本文是 `qchem_stack.quantum` 的**权威风格标准**：分层边界、公开 API、插件 registry、config 访问与文档写法。新增或重构量子算法路径时**必须先对照本文**。

包内入口：[`src/qchem_stack/quantum/README.md`](../src/qchem_stack/quantum/README.md)。整体软件分层见 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md)。YAML 字段见 [说明_quantum配置.md](说明_quantum配置.md) 与 [config_校验分层约定.md](config_校验分层约定.md) §3.1。

---

## 0) 设计目标

| 目标 | 含义 |
|------|------|
| **后端无关** | 算法不 `import pyscf` / `import psi4`；只消费 `QubitHamiltonian` 与 executor |
| **PreQuantum handoff** | 变分 / 激发态阶段优先 `PreQuantumInput.qubit_hamiltonian`，不回溯经典 MF |
| **可扩展** | 新变分算法 = `register_variational_plugin`；新激发态 sidecar = `excited_plugins` registry |
| **易维护** | 配置读取走 `config.quantum_helpers`；算法模块不解析 YAML |

**样板路径（已实现）：** `PreQuantumInput` → `run_variational_stage` → `run_excited_stages` → Pauli protocol finalize。

---

## 1) 分层与 import 纪律

```text
L1  Algorithms     algorithms/           VQE, ADAPT, VQD, QSE, QPE, …
L2  Plugins        variational_plugins/  pipeline 变分 runner registry
                  excited_plugins/      激发态 sidecar registry
L3  Build          variational_branch.py UCCSD 分支 factory（共享 wiring）
L4  Registries     *_registry.py         algorithm / ansatz / operator_pool
L5  Kernels        statevector.py        HEA statevector、dense Pauli 期望
```

### 1.1 硬规则

1. **`quantum/` 禁止** module-scope `import qchem_stack.orchestration` 或 `import pyscf`（CI：`tests/quantum/test_quantum_layer_import_boundaries.py`）。
2. **算法不解析 YAML** — 只接收 `ExperimentConfig` 已通过 context 传入的字段，或显式 typed 参数；重复访问走 `config.quantum_helpers`。
3. **Fermionic UCC generator** 来自 `chem.kernels.spin_ucc`（非 `integrations.ucc_reference` 新代码路径）。
4. **公开 API** 从子模块显式 import（见 README 推荐路径）；`quantum/__init__.py` 保持空 `__all__` 以避免 chem↔config↔quantum 循环。

---

## 2) 模块布局标准

| 区域 | 职责 | 典型入口 |
|------|------|----------|
| `algorithms/` | 算法类与 lifecycle（build/run/report） | `VQE`, `FermionicAdaptVQE`, `VQD`, `QSE` |
| `algorithms/uccsd_mapping.py` | JW/BK reference 与 cluster 矩阵映射 | `reference_state_dense`, `antihermitian_cluster_matrices` |
| `variational_plugins/` | YAML `quantum.algorithm` 管线 runner | `run_variational_stage`, `register_variational_plugin` |
| `excited_plugins/` | YAML `quantum.excited.*` sidecar runner | `run_excited_stages_from_context`, `register_excited_plugin` |

激发态资源估算 canonical 路径：`orchestration/excited_stages_resource.py` → pipeline `out["excited_resource_summary"]`；**不在** `ExcitedStageOutcome` 重复 resource 字段。

变分 `algorithm_report`：HEA VQE / ADAPT / IQEB 经 `AlgorithmBase.generate_report()`；UCCSD 经 `uccsd_algorithm_report_v1`；iQCC 经 `iqcc_algorithm_report_v1`；pipeline 写入 `out["algorithm_report"]`，`repro.run_summary` 镜像 `algorithm_report_*` 摘要键。
| `variational_branch.py` | UCCSD / HEA 分支共享 factory | `build_uccsd_variational_model`, `run_uccsd_vqe_from_config` |
| `algorithm_registry.py` | 物化/导出（sync 自 variational） | `build_registered_algorithm` |
| `ansatz_registry.py` | UX/文档 ansatz 命名 | `ansatz_registry_export` |
| `operator_pool_registry.py` | ADAPT/IQEB pool | `build_registered_operator_pool` |
| `statevector.py` | NumPy statevector 内核 | `hea_state`, `expectation_qubit_operator` |
| `runtime.py` | 便捷 VQE 入口（lazy config） | `vqe_from_experiment_config` |

### 2.1 四套 registry 对照

| Registry | YAML 键 | 用途 |
|----------|---------|------|
| `variational_plugins.registry` | `quantum.algorithm` | 管线执行 runner |
| `algorithm_registry` | 同上（导出） | Methods / 物化 legacy 对象 |
| `ansatz_registry` | `quantum.variational.ansatz` | 文档与 workflow UX |
| `operator_pool_registry` | `quantum.adapt.pool_id`, `quantum.iqeb.pool_id`, `quantum.iqcc.pool_id` | ADAPT/IQEB/iQCC 算符池 |

---

## 3) 公开 API 策略

`quantum/__init__.py` ** deliberately 空 export**；推荐 import 见 [`quantum/README.md`](../src/qchem_stack/quantum/README.md)。

新增稳定 API 的步骤：

1. 在实现模块定义函数/类型，写入该模块 `__all__`。
2. 在 `tests/quantum/test_quantum_public_surface.py` 覆盖 import。
3. 更新 `quantum/README.md` Layout 表（一行即可）。
4. **不** 未经 cycle 测试向 `quantum/__init__.py` 加 lazy export。

`quantum.algorithms` 子包使用 **lazy `__getattr__`**（见 `algorithms/__init__.py`）；按需加载算法类，与根包空 export 策略一致。

### 3.1 `algorithm_factory` 安全约定

- YAML `quantum.algorithm_factory` 经 `variational_plugins.loader` 动态 import。
- **默认 allowlist**：模块名必须以 `qchem_stack.` 开头（内置示例插件均在此命名空间下）。
- **逃逸**：设置环境变量 `QCHEM_QUANTUM_ALGORITHM_FACTORY_ALLOW_EXTERNAL=1` 可加载任意外部模块（用户自担可复现与安全风险）。
- 违规模块 → `PipelineError`，消息说明 allowlist 与 env 开关。

---

## 4) Config 访问约定

- 插件 runner（`variational_plugins/builtins`, `excited_plugins/builtins`）通过 **`config.quantum_helpers`** 窄化读取；激发态 sidecar 使用 `excited_vqd_plugin_params` / `excited_qse_plugin_params` / `excited_sceom_plugin_params` 分组 dict。
- **禁止** 在 `QuantumSpec` 上新增与 helper 语义重复的方法。
- config 校验可 lazy import quantum registry（`_quantum_validation.py`）。
- orchestration 读取 Pauli / excited / demo / tensornet 开关时优先 **`config.quantum_helpers`**；Pauli 路径分类 canonical 实现在 `classify_pauli_expectation_path_for_config`；repro dump 使用 `quantum_repro_core_fields` + `quantum_repro_sidecar_fields`。

---

## 5) Deprecation 策略

| 旧入口 | 新入口 |
|--------|--------|
| `integrations.ucc_reference.*` | `chem.kernels.spin_ucc.*` |

`orchestration.excited_stages_vqd/qse/sceom` 已移除；激发态 sidecar 统一经 `quantum.excited_plugins.registry.run_excited_stages_from_context`。

Deprecation 发 `DeprecationWarning`；保留 re-export 至少一个迁移窗口。

---

## 6) 文档分工

| 文档 | 侧重 |
|------|------|
| **本文** | 分层、import 纪律、registry、API 扩展流程 |
| [quantum/README.md](../src/qchem_stack/quantum/README.md) | 包内索引、build chain、推荐 import |
| [说明_quantum配置.md](说明_quantum配置.md) | YAML 字段表 |
| [config_校验分层约定.md](config_校验分层约定.md) | config section 标准 |
| `ENGINEERING_ARCHITECTURE.md` | 全栈位置 |

---

## 7) PR 自检清单

- [ ] quantum 目录无 module-scope orchestration / pyscf import
- [ ] 新 `quantum.algorithm` 已注册 variational plugin 且 sync algorithm_registry
- [ ] 新 pool id 已加入 `operator_pool_registry` 且 `OperatorPoolId` enum 同步
- [ ] 插件路径使用 `quantum_helpers`，未新增 Spec 重复方法
- [ ] 测试优先 toy `QubitHamiltonian` / `tests/fixtures/quantum_problem`，非 PySCF driver
- [ ] `quantum/README.md` 或本文 Layout 表已更新（若新增 area）

---

## 8) Epistemic bounds（算法实现边界）

以下算法路径为 **open-stack prototype**，适用小 active space / CI；**非** shot-native 大体系生产路径：

| 算法 | 实现特点 | 局限 |
|------|----------|------|
| **ADAPT / IQEB** | dense statevector（`qubit_operator_to_sparse` + `expm` / HEA state） | 内存随 qubit 数指数增长；见 `algorithms/adapt.py` pool mat 预计算 |
| **iQCC / iQCC+PT** | Pauli DIS + 相似变换穿衣 + 可选 EN2（`iqcc.py` / `iqcc_dressing.py`） | 开放实现，非闭源 OTI 比特级一致；项数随穿衣增长，依赖截断 |
| **QSE / SCEOM** | HEA Pauli-X bump 或 UCCSD fermionic-singles 基；`exact` / `gaussian_h` / `pauli_transitions` / **`pauli_transitions_qiskit`** | `pauli_transitions` 经 **`QSEMatricesComputable`** + grouped statevector shot sim；Qiskit 过渡路径见 `backends/qiskit_qse_transition.py`；`gaussian_h` 标 `legacy_fast_path` |
| **VQD** | 支持 UCCSD `prepare_state`；`optimizer_mode: three_computable` 分通道优化 | COBYLA 内层优化；大体系需资源估算 |
| **Computable 运行时** | InQuanto Computable × Protocol | `protocols/computables/`（Expectation / QSE / SCEOM / Overlap）+ `ProtocolList.run_all`；classical shadows stub 接线 `ExpectationValueComputable`（`mitigation/qermit_runtime.py`） |

文档化这些边界是为了 Methods / parity 导出时不夸大设备可扩展性。
