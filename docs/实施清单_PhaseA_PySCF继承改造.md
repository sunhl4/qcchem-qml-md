# 实施清单：Phase A（PySCF 继承改造）

## 1. 目标（本阶段只做三件事）

对应《`技术分析_Vendor platform_PySCF_vs_原生PySCF_及工程借鉴.md`》的 Phase A，本阶段目标限定为：

1. 统一 driver benchmark 输出（HF/MP2/CCSD/CASCI）；
2. 规范 `driver_meta` 字段（可用于 parity/回归）；
3. 统一 active-space 输入策略入口（先覆盖 manual + CAS 语义）。

> 本阶段不引入 AVAS、不做 AO/Lowdin 新接口、不做 NEVPT2/AC0。

---

## 2. 任务拆分（文件级）

## A1. 增加 benchmark 统一接口

- **改动文件**
  - `src/qchem_stack/chem/drivers/pyscf_driver.py`
  - `src/qchem_stack/config.py`（若需要新增开关）
  - `tests/` 下新增 benchmark driver 测试文件（见第 4 节）
- **实现要求**
  - 新增统一方法（建议名：`run_classical_benchmarks`），返回结构化 dict。
  - 至少包含键：`hf`, `mp2`, `ccsd`, `casci`。
  - 对不可用方法（依赖缺失/收敛失败）不要直接崩溃；返回 `{value: null, status: "unavailable|failed", reason: "..."}`
  - 对已完成 SCF 的场景复用已有 `mf`，避免重复全量 SCF。
- **验收标准**
  - RHF 小分子（H2/STO-3G）可返回 `hf/mp2/ccsd/casci`（允许 CASCI 需指定缺省 active-space 策略）。
  - pipeline 侧可以选择性写入结果到 artifacts（先 metadata 即可）。

## A2. 规范 `driver_meta`（形成最小公共契约）

- **改动文件**
  - `src/qchem_stack/chem/drivers/pyscf_driver.py`
  - `src/qchem_stack/integrations/open_driver_surface.py`（coverage 矩阵；与 `chem/drivers/pyscf_driver.py` 协同）
  - `docs/public_parity_matrix.md`（必要时更新说明）
- **实现要求（最小字段集）**
  - `driver_family`: `"pyscf"`
  - `scf_method`: `"RHF" | "ROHF" | "UHF"`
  - `integral_representation`: `"mo"`（本阶段先固定）
  - `solvent_model`: `"none" | "ddcosmo"`
  - `ddcosmo_epsilon`: number | null
  - `pbc`: bool
  - `pbc_kpoint_mesh`: `[int,int,int] | null`
  - `pbc_active_space_kpoint_index`: `int | null`
  - `energy_accounting_model`: 固定字符串（如 `"mf_e_tot_direct"`，后续可扩）
  - `pyscf_version`: string（可选但强烈建议）
- **验收标准**
  - 分子 RHF 与 PBC RHF/KRHF 路径均生成完整 `driver_meta`。
  - ddCOSMO 打开/关闭时字段一致且可机读判别。
  - `integrations/open_driver_surface`（与 `driver_meta`、`pyscf_driver`）文档说明与实际字段不冲突。

## A3. 统一 active-space 策略入口（manual + CAS）

- **改动文件**
  - `src/qchem_stack/config.py`
  - `src/qchem_stack/chem/drivers/pyscf_driver.py`
  - `src/qchem_stack/chem/hamiltonian.py`（若 active-space 入口在此）
  - `configs/` 新增最小示例 YAML（manual/CAS 各一个）
  - `tests/` 新增 active-space 策略测试
- **实现要求**
  - 配置上统一成一个入口（示例）：
    - `active_space.strategy: "manual" | "cas"`
    - `active_space.frozen_orbitals: [...]`（manual）
    - `active_space.ncas / nelecas`（cas）
  - 内部转换保持现有数值逻辑不变，先做“输入层统一”。
  - 错误信息要明确（比如 `ncas` 超过可用 MO 数、`nelecas` 奇偶不合法等）。
- **验收标准**
  - manual 与 cas 两种配置最终都能驱动到同一 active-space 积分生成路径。
  - 产物 metadata 中包含 `active_space_recipe`（如 `manual:frozen=[...]` / `cas:ncas=4,nelecas=4`）。

---

## 3. 建议执行顺序（减少返工）

1. 先做 A2（meta 契约），因为 A1/A3 都会往 meta 写字段；  
2. 再做 A3（active-space 入口统一），稳定数据流；  
3. 最后做 A1（benchmark），避免在接口未稳定时写两遍适配。

---

## 4. 测试清单（建议新增）

建议新增以下测试文件（命名可微调）：

- `tests/chem/test_pyscf_solver_adapter.py`
  - 覆盖分子 RHF 与 PBC RHF/KRHF 的 `driver_meta` 字段完整性；
  - 覆盖 `solvent_model=ddcosmo` 的字段与值。

- `tests/chem/test_active_space_strategy_unified.py`
  - `manual` / `cas` 两策略均可跑通；
  - 非法配置报错语义（参数缺失、范围错误）。

- `tests/chem/test_pyscf_classical_benchmarks.py`
  - benchmark 返回结构稳定；
  - 可用/不可用方法的 `status` 语义稳定；
  - 在可运行环境下校验 `hf <= mp2/ccsd/casci` 的基本趋势（仅做宽松断言）。

---

## 5. 回归与 CI 门槛

- **最小门槛**
  - 新增测试全部通过；
  - 原有 `tests/test_pyscf_*`、`tests/test_hamiltonian_*` 不回归。

- **建议门槛**
  - 在 `scripts/check_parity_export_sample.py` 产物中增加一项 `driver_meta_schema_version`（哪怕先固定为 `1`），为后续字段演化留钩子。

---

## 6. 交付物定义（完成判据）

当以下四项都满足，Phase A 视为完成：

1. 统一 benchmark 接口已可调用，且返回结构稳定；
2. `driver_meta` 最小字段集已落地并可机读；
3. active-space 统一入口支持 manual + cas；
4. 至少 3 个新增测试文件 + 2 份配置示例已提交。

---

## 7. 可直接开工的 TODO（复制到 issue 即可）

- [ ] 定义 `driver_meta` schema（字段、默认值、类型）并在 `PySCFDriver` 各分支填充  
- [ ] 补齐 **`open_driver_surface` / `pyscf_driver`** 对 `driver_meta` 的说明映射  - [ ] 引入统一 `active_space.strategy` 配置并保持向后兼容（若有旧字段）  
- [ ] 新增 manual/cas 两份最小可运行配置样例  
- [ ] 实现 `run_classical_benchmarks` 并处理不可用方法状态  
- [ ] 新增 `meta_contract` / `active_space` / `benchmarks` 三类测试  
- [ ] 跑一轮与 PySCF 相关测试并更新 parity 导出样例（如有字段变化）

---

## 8. 备注（避免超范围）

本清单是 Phase A。以下内容明确不在本阶段：

- AVAS 自动活性空间；
- Lowdin/AO 新接口；
- DMET/FMO 新 solver 协议扩展；
- RDM 驱动的 NEVPT2/AC0 校正接口。

这些内容留到 Phase B/C，避免本阶段目标漂移。

---

## 9. 执行核对（当前仓库）

- [x] A1：`run_classical_benchmarks` 已落地，支持 `hf/mp2/ccsd/casci` 与 `status/value/reason`。  
- [x] A2：`driver_meta` 最小字段集已落地（含 `driver_meta_schema_version=1`）。  
- [x] A3：`active_space.strategy=cas|manual` + `ncas/nelecas` + `frozen_orbitals` 已落地并保持旧字段兼容。  
- [x] 新增测试文件：`test_pyscf_driver_meta_contract.py`、`test_active_space_strategy_unified.py`、`test_pyscf_classical_benchmarks.py`。  
- [x] 新增示例配置：`example_h2_active_space_cas_strategy.yaml`、`example_h2_active_space_manual_strategy.yaml`。  
- [x] pipeline / `run_summary` / parity export 已接入 benchmark 与摘要字段。  
- [ ] 本机完整 pytest 回归：受运行环境缺少 `pydantic` 依赖阻塞（已完成语法与 lint 校验）。

