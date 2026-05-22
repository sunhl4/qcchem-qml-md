# Chem 模块代码与架构风格约定

本文是 `qchem_stack.chem` 的**权威风格标准**：分层边界、公开 API、后端插件挂载、deprecation 与文档写法。新增或重构经典化学路径时**必须先对照本文**。

包内入口：[`src/qchem_stack/chem/README.md`](../src/qchem_stack/chem/README.md)。整体软件分层见 [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md)。

---

## 0) 设计目标

| 目标 | 含义 |
|------|------|
| **多后端** | `scf.driver` 只是 registry id；编排层不绑定 PySCF |
| **可交换** | 平均场与活性空间积分进入 `ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack` 后，下游与上游程序无关 |
| **可扩展** | 新后端 = `ChemIntegralSolver` + `register_solver` + `SolverCapabilities`；新嵌入分支 = pre-quantum branch builder |
| **易维护** | 大文件按职责拆分；driver 专属逻辑不进 orchestration |

**样板路径（已实现）：** `create_solver` → `reference_factory` → `build_pre_quantum_input` / `restricted_active_space_quantum_problem_from_config`。

---

## 1) 分层与 import 纪律

```text
L1  Solver        solvers/           create_solver, compute_mean_field
L2  Bridge        bridges/           ClassicalMeanFieldReference, driver_meta
L3  Build         pre_quantum_*,     build_pre_quantum_input, hamiltonian_*
                  molecular_problem*
L4  Backend hook  active_space/,    AVAS, MO reorder, integral exporters
                  integrals/
L5  Legacy        drivers/           PySCFDriver (deprecated)
```

### 1.1 硬规则

1. **`orchestration/` 禁止** 为选路而 `import pyscf` / `import psi4`；只用 `create_solver` 与 capability 门控。
2. **进入 L2 之后** 的消费者（quantum、compiler、parity export）只依赖 bridge 类型与 schema id，不访问 `.mf` 除非明确标注为 backend hook。
3. **PySCF 专属能力**（AVAS、`mcscf.avas`、部分 Schmidt FCI 委托）必须在 hook 模块或 `driver_meta.kernel_bindings` 中标注，不得在编排层散落 `if driver == "pyscf"`。
4. **公开 API** 从 `qchem_stack.chem` 或 area 子包（`chem.bridges`、`chem.solvers`）导入；避免深路径 `chem.integrals.pyscf_active_space` 作为用户约定，除非文档明确为内部/测试 API。

---

## 2) 模块布局标准

| 区域 | 职责 | 典型入口 |
|------|------|----------|
| `solvers/` | 注册表、适配器协议、能力位 | `create_solver`, `ChemIntegralSolver` |
| `bridges/` | 交换物、reference 工厂、meta 视图 | `classical_mean_field_reference_from_config` |
| `pre_quantum_build.py` | 嵌入分支调度 → `PreQuantumInput` | `build_pre_quantum_input` |
| `molecular_problem_build.py` | RAS 三元组工厂 | `restricted_active_space_quantum_problem_from_config` |
| `systems/pyscf_factory.py` | AO/Löwdin 视图（无 driver） | `pyscf_ao_system_from_config` |
| `integrals/` | 积分提取、one-body、exporter registry | `active_space_integrals`, `one_electron_operator_*_from_rhf` |
| `active_space/` | 后端 hook 协议与 registry | `hooks_registry`, `backend_hooks` |
| `embedding/` | Schmidt / DMET / projection 数值 | 见 embedding 子模块 |
| `classical_benchmarks/` | 后 HF benchmark 分发 | `run_classical_post_hf_benchmarks` |
| `drivers/` | **仅** legacy 兼容 | `PySCFDriver`（DeprecationWarning） |

### 2.1 命名

- **`system.py`**：后端无关 `MolecularSystem`。
- **`systems/`**：后端专属 view dataclass（如 `PySCFAOSystem`）。
- **`bridges/driver_meta.py`** vs **`integration/meta_schema.py`**：前者是 interchange 浅拷贝 helper；后者是 multi-backend schema 与 `kernel_bindings`。
- **`*_factory.py`**：从 config / reference 构造对象的薄入口，不含 heavy 数值。
- **`*_build*.py`**：哈密顿量 / pre-quantum 组装流水线。
- **`_*_common.py`**：solver 间共享的非公开 helper。

---

## 3) 公开 API 与 lazy export

`chem/__init__.py` 与 `chem/bridges/__init__.py` 使用 **lazy `__getattr__`** 避免循环 import（尤其 `systems` ↔ `integrals`）。

新增稳定 API 的步骤：

1. 在实现模块定义函数/类型，写入该模块 `__all__`。
2. 若属于顶层推荐入口，加入 `chem/__init__.py` 的 `__all__` 与 `_LAZY_ATTRS`（或 eager import 若轻量且无环）。
3. 在 `tests/test_chem_public_surface.py` 或 area 契约测试中覆盖 import。
4. 更新 `chem/README.md` Layout 表（一行即可）。

`ChemIntegralSolver` / `SolverCapabilities`  intentionally 不在顶层 `chem.__all__`；从 `qchem_stack.chem.solvers` 导入（见 `chem/README.md`）。

---

## 4) Deprecation 策略

| 旧入口 | 新入口 |
|--------|--------|
| `PySCFDriver.from_config` / `run_rhf` | `create_solver` + `classical_mean_field_reference_from_config` |
| `PySCFDriver.get_restricted_active_space_quantum_problem` | `restricted_active_space_quantum_problem_from_config` |
| `PySCFDriver.get_system_ao` | `pyscf_ao_system_from_config` |
| `from qchem_stack.chem.drivers import PySCFAOSystem` | `from qchem_stack.chem.systems import PySCFAOSystem` |
| `integration.driver_meta` (internal) | `integration.meta_schema` |
| `PySCFDriver` in tests | bridge factories + `active_space.sizing` |
| `molecular_hamiltonian_from_classical_reference`（部分路径） | `build_pre_quantum_input` |

Deprecation 在 `__init__` / `from_config` 发 `DeprecationWarning`；保留 re-export 至少一个迁移窗口；文档与示例优先改新 API。

---

## 5) 文档分工

| 文档 | 侧重 |
|------|------|
| **本文** | 分层、import 纪律、布局、API 扩展流程 |
| [说明_chem模块技术参考手册.md](说明_chem模块技术参考手册.md) | 模块架构、API、文件布局、构建流水线、扩展流程、工作流映射 |
| [chem/README.md](../src/qchem_stack/chem/README.md) | 包内索引、build chain 一览 |
| [说明_经典化学后端驱动_registry与能力位.md](说明_经典化学后端驱动_registry与能力位.md) | 能力位表、driver 对照 |
| [统一经典化学接口_…](统一经典化学接口_ChemIntegralSolver与下游无关性.md) | L1–L3 理念与维护纪律 |
| `ENGINEERING_ARCHITECTURE.md` | 全栈位置 |

代码内 docstring：一行摘要 + 指向 factory/build 函数；长文放 `docs/说明_*.md`。

---

## 6) PR 自检清单

- [ ] 编排层无新增 `import pyscf` / `if scf.driver == "pyscf"` 选路
- [ ] 新能力位已写入 `SolverCapabilities` 并在 config 校验中门控
- [ ] 稳定 API 已加入对应 `__all__`；必要时加入 `qchem_stack.chem`
- [ ] 测试优先 `tests/fixtures/classical_reference` / `quantum_problem`，而非 `PySCFDriver`
- [ ] `chem/README.md` 或本文 Layout 表已更新（若新增 area 或改 build chain）
