# 90 天计划：统一经典化学接口（ChemIntegralSolver）与多程序适配

**填写锚定日**：将下行 `PLAN_START_DATE` 改为你开始执行本日历的日期（`YYYY-MM-DD`）。文中「第 N 天」= 从该日起第 N 个**日历日**。

```text
PLAN_START_DATE: 2026-05-08
```

---

## 全期工程原则（不可违背）

1. **统一接口**：经典阶段唯一入口为 `qchem_stack.chem.solvers.create_solver` → `ChemIntegralSolver` → `MolecularMeanFieldResult` / `ClassicalMeanFieldReference`；**禁止**在 `orchestration/`、`quantum/` 中把 PySCF 当作唯一化学后端。
2. **PySCF 非绑定**：`scf.driver=pyscf` 仅为**当前默认且实现最完整**的适配器；其它程序（Psi4、未来 ORCA/…）通过 **registry 注册 + `SolverCapabilities`** 接入，能力缺失时用 capability **显式门控**，不用 `driver` 字符串散落判断。
3. **下游无关性**：哈密顿量构造、嵌入、激发态、协议层只消费 **能力位 + 中间 DTO**（`MeanFieldLike`、`driver_meta`、`upstream_classical_software_tag`），不依赖具体量子化学程序 API。
4. **每日闸门**：至少 `pytest -q` 相关子集或 `scripts/check_parity_export_sample.py`（若当日改 export）；每周五全量 `pytest`。

### 第 1 天

**主题**：建立《统一经典化学接口》母稿与 execution 索引

**当日完成定义（DoD）**：

- 母稿：`docs/统一经典化学接口_ChemIntegralSolver与下游无关性.md`
- 更新 `docs/execution/README.md` 链到本日历

**日末检查**：`git diff` 可审；相关测试绿。

### 第 2 天

**主题**：registry 模块头文档：多适配器契约

**当日完成定义（DoD）**：

- `chem/solvers/registry.py` 文档串：注册表为唯一工厂
- 核对 `registered_solver_ids()` 与文档一致

**日末检查**：`git diff` 可审；相关测试绿。

### 第 3 天

**主题**：契约测试：桥接不经 PySCF 直连

**当日完成定义（DoD）**：

- 扩展 `tests/chem/test_solver_registry_contract.py`：门面 `classical_mean_field_via_solver_bridge` 走 registry
- 断言 `driver_meta` 含 canonical headers

**日末检查**：`git diff` 可审；相关测试绿。

### 第 4 天

**主题**：全仓 grep：`scf.driver` / `import pyscf` 在 orchestration 的用途清单

**当日完成定义（DoD）**：

- 输出 `docs/execution/unified_chem_driver_audit_notes.md` 或在日历附录记表
- 分类：可接受 / 应迁 capability / 长期

**日末检查**：`git diff` 可审；相关测试绿。

### 第 5 天

**主题**：pipeline：`_require_pyscf_reference` 调用点标注「仅 PySCF 专属能力」

**当日完成定义（DoD）**：

- 注释或 ADR：哪些路径必须 PySCF、哪些可抽象
- 不改行为，只留地图

**日末检查**：`git diff` 可审；相关测试绿。

### 第 6 天

**主题**：capabilities 矩阵草稿：每 embedding 分支所需 capability

**当日完成定义（DoD）**：

- 表格：projection / schmidt / plugin × capabilities
- 与 `pipeline` gate 对照

**日末检查**：`git diff` 可审；相关测试绿。

### 第 7 天

**主题**：周闸门：pytest 全量 + parity sample

**当日完成定义（DoD）**：

- CI 等价命令本地跑通
- 更新周记 `docs/execution/week_unified_chem_w01.md`（可选）

**日末检查**：`git diff` 可审；相关测试绿。

### 第 8 天

**主题**：Psi4：`SolverCapabilities` 全字段显式声明

**当日完成定义（DoD）**：

- `psi4_solver.py` 与文档对齐 false 项
- export 键若需 `scf.driver` 保持为事实源

**日末检查**：`git diff` 可审；相关测试绿。

### 第 9 天

**主题**：第二后端 smoke：`compute_mean_field` 不抛 + `driver_meta` 形状

**当日完成定义（DoD）**：

- 已有测则加固
- 补缺失 meta 键

**日末检查**：`git diff` 可审；相关测试绿。

### 第 10 天

**主题**：`classical_benchmark_backend` 与 `upstream_classical_software_tag` 对齐表

**当日完成定义（DoD）**：

- 文档：`docs/` 一小节
- auto 分支单测

**日末检查**：`git diff` 可审；相关测试绿。

### 第 11 天

**主题**：Hamiltonian：`molecular_hamiltonian_from_classical_reference` 入口审计

**当日完成定义（DoD）**：

- 确认无 `PySCFDriver` 硬依赖在默认路径
- grep `PySCFDriver` in orchestration

**日末检查**：`git diff` 可审；相关测试绿。

### 第 12 天

**主题**：embedding：`embedding_input_representation` 门控与 reference 类型

**当日完成定义（DoD）**：

- 仅文档+测试：非 pyscf 时错误信息指向 capability

**日末检查**：`git diff` 可审；相关测试绿。

### 第 13 天

**主题**：DMET / Schmidt：列出需 `supports_schmidt_*` 的精确分支

**当日完成定义（DoD）**：

- markdown 表

**日末检查**：`git diff` 可审；相关测试绿。

### 第 14 天

**主题**：周闸门

**当日完成定义（DoD）**：

- pytest 全量

**日末检查**：`git diff` 可审；相关测试绿。

### 第 15 天（第 3 周）

**主题**：将 `active_space.strategy=avas` 的报错文案改为同时提及 `supports_avas` 与 `scf.driver`（用户可理解非绑定）

**当日完成定义（DoD）**：

- 将 `active_space.strategy=avas` 的报错文案改为同时提及 `supports_avas` 与 `scf.driver`（用户可理解非绑定）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 16 天（第 3 周）

**主题**：`ExperimentConfig` 校验：`avas` 与 `SolverCapabilities.supports_avas_active_space_projection` 文档交叉链接

**当日完成定义（DoD）**：

- `ExperimentConfig` 校验：`avas` 与 `SolverCapabilities.supports_avas_active_space_projection` 文档交叉链接
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 17 天（第 3 周）

**主题**：`pipeline._refine_mean_field_for_active_space`：注释写明「仅当 reference 暴露 PySCF MF 时」调用 PySCF hooks

**当日完成定义（DoD）**：

- `pipeline._refine_mean_field_for_active_space`：注释写明「仅当 reference 暴露 PySCF MF 时」调用 PySCF hooks
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 18 天（第 3 周）

**主题**：`pyscf_active_space_hooks`：文件头 docstring 标明 **PySCF 插件** 非通用化学内核

**当日完成定义（DoD）**：

- `pyscf_active_space_hooks`：文件头 docstring 标明 **PySCF 插件** 非通用化学内核
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 19 天（第 3 周）

**主题**：单测：`strategy=avas` + `driver=psi4` 失败路径信息包含 capability 提示（若尚无则补测）

**当日完成定义（DoD）**：

- 单测：`strategy=avas` + `driver=psi4` 失败路径信息包含 capability 提示（若尚无则补测）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 20 天（第 3 周）

**主题**：`docs/统一经典化学接口_*.md`：增加「可选经典钩子按 backend 插件挂载」小节

**当日完成定义（DoD）**：

- `docs/统一经典化学接口_*.md`：增加「可选经典钩子按 backend 插件挂载」小节
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 21 天（第 3 周）

**主题**：周闸门：pytest + 记周总结到 `unified_chem_driver_audit_notes.md` 尾部

**当日完成定义（DoD）**：

- 周闸门：pytest + 记周总结到 `unified_chem_driver_audit_notes.md` 尾部
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 22 天（第 4 周）

**主题**：`ChemIntegralSolver.get_integrals`：在 base Protocol 文档中写清默认 NotImplemented 为合法

**当日完成定义（DoD）**：

- `ChemIntegralSolver.get_integrals`：在 base Protocol 文档中写清默认 NotImplemented 为合法
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 23 天（第 4 周）

**主题**：`PySCFIntegralSolver.get_integrals`：若未实现，docstring 指向「下游用 CASCI driver」

**当日完成定义（DoD）**：

- `PySCFIntegralSolver.get_integrals`：若未实现，docstring 指向「下游用 CASCI driver」
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 24 天（第 4 周）

**主题**：设计稿：`Psi4IntegralSolver.get_integrals` 返回形状（1 页 markdown 草案，可放 execution）

**当日完成定义（DoD）**：

- 设计稿：`Psi4IntegralSolver.get_integrals` 返回形状（1 页 markdown 草案，可放 execution）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 25 天（第 4 周）

**主题**：`CanonicalActiveSpaceIntegralPack` 构造路径 grep：确认从 `ClassicalMeanFieldReference` 进入

**当日完成定义（DoD）**：

- `CanonicalActiveSpaceIntegralPack` 构造路径 grep：确认从 `ClassicalMeanFieldReference` 进入
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 26 天（第 4 周）

**主题**：测试：`create_solver`+pyscf 的 mean field 能进 `molecular_hamiltonian_from_classical_reference`（已有则跳过）

**当日完成定义（DoD）**：

- 测试：`create_solver`+pyscf 的 mean field 能进 `molecular_hamiltonian_from_classical_reference`（已有则跳过）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 27 天（第 4 周）

**主题**：`hamiltonian.py`：公开函数 docstring 强调 **不 import 具体 driver 类**

**当日完成定义（DoD）**：

- `hamiltonian.py`：公开函数 docstring 强调 **不 import 具体 driver 类**
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 28 天（第 4 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 29 天（第 5 周）

**主题**：新增 `tests/fixtures/mock_chem_solver.py` 或内联：`register_solver("mockchem")` 仅测试注册

**当日完成定义（DoD）**：

- 新增 `tests/fixtures/mock_chem_solver.py` 或内联：`register_solver("mockchem")` 仅测试注册
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 30 天（第 5 周）

**主题**：`mockchem`：`MolecularMeanFieldResult` 最小桩（e_tot=0, mo_energy zeros）+ capabilities 全 false 除 molecular_scf

**当日完成定义（DoD）**：

- `mockchem`：`MolecularMeanFieldResult` 最小桩（e_tot=0, mo_energy zeros）+ capabilities 全 false 除 molecular_scf
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 31 天（第 5 周）

**主题**：CI：`test_pipeline_backend_gate` 或新测用 mockchem 触发 **canonical pack false** 的精确错误

**当日完成定义（DoD）**：

- CI：`test_pipeline_backend_gate` 或新测用 mockchem 触发 **canonical pack false** 的精确错误
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 32 天（第 5 周）

**主题**：文档：`registry.register_solver` 扩展示例（README 或母稿）

**当日完成定义（DoD）**：

- 文档：`registry.register_solver` 扩展示例（README 或母稿）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 33 天（第 5 周）

**主题**：移除测试中的 `register_solver` 泄漏：使用 autouse 或 module finalizer 注销（若 API 无 unregister 则文档说明测试顺序）

**当日完成定义（DoD）**：

- 移除测试中的 `register_solver` 泄漏：使用 autouse 或 module finalizer 注销（若 API 无 unregister 则文档说明测试顺序）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 34 天（第 5 周）

**主题**：`SolverCapabilities`：`backend_id="mockchem"` 导出到 parity export（若适用）

**当日完成定义（DoD）**：

- `SolverCapabilities`：`backend_id="mockchem"` 导出到 parity export（若适用）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 35 天（第 5 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 36 天（第 6 周）

**主题**：`_require_pyscf_reference`：为每个 call site 加一行「capability 替代 TODO」注释（不改逻辑）

**当日完成定义（DoD）**：

- `_require_pyscf_reference`：为每个 call site 加一行「capability 替代 TODO」注释（不改逻辑）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 37 天（第 6 周）

**主题**：`embedding_input_representation`：错误路径统一 `ConfigurationError` 文案模板

**当日完成定义（DoD）**：

- `embedding_input_representation`：错误路径统一 `ConfigurationError` 文案模板
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 38 天（第 6 周）

**主题**：`schmidt` 路径：文档声明需 `supports_schmidt_atomic_hamiltonian`

**当日完成定义（DoD）**：

- `schmidt` 路径：文档声明需 `supports_schmidt_atomic_hamiltonian`
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 39 天（第 6 周）

**主题**：`projection_fragment_mulliken`：同上 `supports_projection_fragment_mulliken_hamiltonian`

**当日完成定义（DoD）**：

- `projection_fragment_mulliken`：同上 `supports_projection_fragment_mulliken_hamiltonian`
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 40 天（第 6 周）

**主题**：`run_pyscf_nevpt2` 分支：docstring 标明 PySCF-only

**当日完成定义（DoD）**：

- `run_pyscf_nevpt2` 分支：docstring 标明 PySCF-only
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 41 天（第 6 周）

**主题**：`collect_repro_metadata`：`pyscf` 版本键改为 `classical_software_versions` 多键字典（若过大则 defer 为文档-only）

**当日完成定义（DoD）**：

- `collect_repro_metadata`：`pyscf` 版本键改为 `classical_software_versions` 多键字典（若过大则 defer 为文档-only）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 42 天（第 6 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 43 天（第 7 周）

**主题**：更新 `backend-adapter-unified-io.md`：加「过 registry 后下游零感知」段落

**当日完成定义（DoD）**：

- 更新 `backend-adapter-unified-io.md`：加「过 registry 后下游零感知」段落
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 44 天（第 7 周）

**主题**：英文 mirror 同步上一段

**当日完成定义（DoD）**：

- 英文 mirror 同步上一段
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 45 天（第 7 周）

**主题**：`vendor-pyscf-problem-analog.md`：脚注「PySCF 为默认适配器示例」

**当日完成定义（DoD）**：

- `vendor-pyscf-problem-analog.md`：脚注「PySCF 为默认适配器示例」
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 46 天（第 7 周）

**主题**：parity `public-matrix` §3：一句「driver 可换，能力位门控」

**当日完成定义（DoD）**：

- parity `public-matrix` §3：一句「driver 可换，能力位门控」
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 47 天（第 7 周）

**主题**：`cli-and-scripts.md`：增加 `create_solver` 调试说明一行

**当日完成定义（DoD）**：

- `cli-and-scripts.md`：增加 `create_solver` 调试说明一行
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 48 天（第 7 周）

**主题**：Docusaurus：`docusaurus-site` 若改用户站则 `npm run build`

**当日完成定义（DoD）**：

- Docusaurus：`cd docusaurus-site && npm run build` 若当周修改了 `docusaurus-site/docs/` 或站点配置
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 49 天（第 7 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 50 天（第 8 周）

**主题**：`export_parity_criteria_table.py`：确保输出 `scf.driver` 与 `solver_capabilities_snapshot`（若无则加 stub 键）

**当日完成定义（DoD）**：

- `export_parity_criteria_table.py`：确保输出 `scf.driver` 与 `solver_capabilities_snapshot`（若无则加 stub 键）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 51 天（第 8 周）

**主题**：`qchem_stack.protocols.product_contract.open_stack_differentiators_public`：若有 driver 绑定措辞则改为 adapter-first

**当日完成定义（DoD）**：

- `qchem_stack.protocols.product_contract.open_stack_differentiators_public`：若有 driver 绑定措辞则改为 adapter-first
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 52 天（第 8 周）

**主题**：`methods_resource_unified`：resource 行含 `classical_backend_id`

**当日完成定义（DoD）**：

- `methods_resource_unified`：resource 行含 `classical_backend_id`
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 53 天（第 8 周）

**主题**：单测：export 对 psi4 driver 的 config-only 行存在

**当日完成定义（DoD）**：

- 单测：export 对 psi4 driver 的 config-only 行存在
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 54 天（第 8 周）

**主题**：`parity_export_example_h2`：可选字段 `registered_solvers` 列表（config-only）

**当日完成定义（DoD）**：

- `parity_export_example_h2`：可选字段 `registered_solvers` 列表（config-only）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 55 天（第 8 周）

**主题**：文档：差距表 §2 一句「registry 为化学唯一工厂」

**当日完成定义（DoD）**：

- 文档：差距表 §2 一句「registry 为化学唯一工厂」
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 56 天（第 8 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 57 天（第 9 周）

**主题**：`quantum/excited.py` 头部：grep `pyscf` 若有则记录到 audit notes

**当日完成定义（DoD）**：

- `quantum/excited.py` 头部：grep `pyscf` 若有则记录到 audit notes
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 58 天（第 9 周）

**主题**：`pipeline` VQD 段：确认只消费 angles + qh

**当日完成定义（DoD）**：

- `pipeline` VQD 段：确认只消费 angles + qh
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 59 天（第 9 周）

**主题**：QSE：`qse_transition` 无 pyscf import 确认

**当日完成定义（DoD）**：

- QSE：`qse_transition` 无 pyscf import 确认
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 60 天（第 9 周）

**主题**：SCEOM：同上

**当日完成定义（DoD）**：

- SCEOM：同上
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 61 天（第 9 周）

**主题**：IQEB/VQE：`quantum/algorithms` 目录 pyscf grep

**当日完成定义（DoD）**：

- IQEB/VQE：`quantum/algorithms` 目录 pyscf grep
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 62 天（第 9 周）

**主题**：文档：激发态「与经典 driver 解耦」一段

**当日完成定义（DoD）**：

- 文档：激发态「与经典 driver 解耦」一段
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 63 天（第 9 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 64 天（第 10 周）

**主题**：`mitigation` DAG：`solver` 元数据是否传入检查（无则文档）

**当日完成定义（DoD）**：

- `mitigation` DAG：`solver` 元数据是否传入检查（无则文档）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 65 天（第 10 周）

**主题**：PMSV：`finalize` 不依赖 pyscf

**当日完成定义（DoD）**：

- PMSV：`finalize` 不依赖 pyscf
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 66 天（第 10 周）

**主题**：ZNE：同上

**当日完成定义（DoD）**：

- ZNE：同上
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 67 天（第 10 周）

**主题**：`qermit_analog`：节点 label 不含硬编码 pyscf

**当日完成定义（DoD）**：

- `qermit_analog`：节点 label 不含硬编码 pyscf
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 68 天（第 10 周）

**主题**：shadows stub：同上

**当日完成定义（DoD）**：

- shadows stub：同上
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 69 天（第 10 周）

**主题**：benchmark stub：`classical_benchmark_backend` 与 driver 组合表

**当日完成定义（DoD）**：

- benchmark stub：`classical_benchmark_backend` 与 driver 组合表
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 70 天（第 10 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 71 天（第 11 周）

**主题**：`repro_json_dumps`：`MeanFieldLike` 若可序列化则加回归

**当日完成定义（DoD）**：

- `repro_json_dumps`：`MeanFieldLike` 若可序列化则加回归
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 72 天（第 11 周）

**主题**：`JobHandle` pickle：含 `scf.driver` 字段快照测试

**当日完成定义（DoD）**：

- `JobHandle` pickle：含 `scf.driver` 字段快照测试
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 73 天（第 11 周）

**主题**：`driver_meta` 大键白名单文档

**当日完成定义（DoD）**：

- `driver_meta` 大键白名单文档
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 74 天（第 11 周）

**主题**：性能：`merge_canonical_classical_bridge_headers` 无热路径分配（profile 可选）

**当日完成定义（DoD）**：

- 性能：`merge_canonical_classical_bridge_headers` 无热路径分配（profile 可选）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 75 天（第 11 周）

**主题**：安全：`driver_meta` 禁止用户任意 pickle

**当日完成定义（DoD）**：

- 安全：`driver_meta` 禁止用户任意 pickle
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 76 天（第 11 周）

**主题**：文档：SQLite job 与 driver 无关说明

**当日完成定义（DoD）**：

- 文档：SQLite job 与 driver 无关说明
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 77 天（第 11 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 78 天（第 12 周）

**主题**：ADR：`docs/ADR_optional_subprocess_chem_adapter.md` 草稿（可 defer 为空壳）

**当日完成定义（DoD）**：

- ADR：`docs/ADR_optional_subprocess_chem_adapter.md` 草稿（可 defer 为空壳）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 79 天（第 12 周）

**主题**：接口：`SubprocessChemIntegralSolver` 是否立项（仅设计不编码）

**当日完成定义（DoD）**：

- 接口：`SubprocessChemIntegralSolver` 是否立项（仅设计不编码）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 80 天（第 12 周）

**主题**：风险：许可证与二进制分发的清单

**当日完成定义（DoD）**：

- 风险：许可证与二进制分发的清单
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 81 天（第 12 周）

**主题**：与 `ChemIntegralSolver` Protocol 对齐检查表

**当日完成定义（DoD）**：

- 与 `ChemIntegralSolver` Protocol 对齐检查表
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 82 天（第 12 周）

**主题**：与 Nexus analog 不混淆的说明

**当日完成定义（DoD）**：

- 与 Nexus analog 不混淆的说明
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 83 天（第 12 周）

**主题**：教程：「换 driver」一页 FAQ

**当日完成定义（DoD）**：

- 教程：「换 driver」一页 FAQ
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 84 天（第 12 周）

**主题**：周闸门

**当日完成定义（DoD）**：

- 周闸门
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 85 天（第 13 周）

**主题**：总审计：`unified_chem_driver_audit_notes.md` 关闭所有 `open` 项或标 `wontfix`

**当日完成定义（DoD）**：

- 总审计：`unified_chem_driver_audit_notes.md` 关闭所有 `open` 项或标 `wontfix`
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 86 天（第 13 周）

**主题**：更新 `public_parity_matrix.md` §3 一句多适配器

**当日完成定义（DoD）**：

- 更新 `public_parity_matrix.md` §3 一句多适配器
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 87 天（第 13 周）

**主题**：更新 `public_parity_matrix.md` §1「Psi4 等为 scaffold」若已过时则改

**当日完成定义（DoD）**：

- 更新 `public_parity_matrix.md` §1「Psi4 等为 scaffold」若已过时则改
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 88 天（第 13 周）

**主题**：Day88：`docusaurus-site` parity 英中同步检查

**当日完成定义（DoD）**：

- Day88：`docusaurus-site` parity 英中同步检查
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 89 天（第 13 周）

**主题**：Day89：全量 pytest + `docusaurus-site` `npm run build`

**当日完成定义（DoD）**：

- Day89：全量 pytest + `cd docusaurus-site && npm run build`（若当周改文档站）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

### 第 90 天（第 13 周）

**主题**：Day90：签字：`day090_unified_chemistry_interface_closeout.md`（本目录新建）

**当日完成定义（DoD）**：

- Day90：签字：`day090_unified_chemistry_interface_closeout.md`（本目录新建）
- 提交或更新可追溯产物（代码 / 测试 / `docs/execution/` 笔记 / 母稿其一）

**日末检查**：相关 `pytest` 子集或全量（周五规则）；`ruff` 若改 Python。

