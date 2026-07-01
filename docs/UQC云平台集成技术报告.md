# UQC 云平台集成技术报告

**日期:** 2026-05-28
**版本:** qchem-stack v0.1.0 → v0.2.0 (UQC 集成)
**作者:** qchem-stack 团队
**状态:** 已实现，待生产验证

---

## 目录

1. [概述](#1-概述)
2. [UQC 云平台技术分析](#2-uqc-云平台技术分析)
3. [集成架构设计](#3-集成架构设计)
4. [实现细节](#4-实现细节)
5. [配置使用说明](#5-配置使用说明)
6. [关键注意点与风险](#6-关键注意点与风险)
7. [测试验证](#7-测试验证)
8. [已知限制与后续工作](#8-已知限制与后续工作)
9. [附录：完整 API 对照表](#9-附录完整-api-对照表)

---

## 1. 概述

### 1.1 项目背景

qchem-stack 是一个量子化学编排平台，运行 7 阶段 YAML 驱动的流水线：

```
SCF → Pre-Quantum → Variational (VQE/ADAPT) → Embedding → Excited States → Pauli Protocol → Job Enqueue
```

本项目需要将 qchem-stack 对接公司（合肥幺正量子科技有限公司）的 UQC 云平台，通过云平台调用离子阱量子计算机执行量子化学计算。

### 1.2 集成目标

- 新增 `uqc` 作为后端 provider，与现有 `statevector`/`qiskit`/`ionstack` 并列
- 自动将 HEA 电路转译为离子阱原生门集 (rzz, rx, ry)
- 通过 `uqc-client` 提交 OpenQASM 3.0 格式任务到云平台
- 支持 mock 模式用于本地开发，real 模式提交真机
- 完全兼容现有 YAML 配置体系和 backend factory 插件机制

---

## 2. UQC 云平台技术分析

### 2.1 uqc-client v0.1.3 API 全景

通过对 PyPI 发布的 `uqc-client` v0.1.3 包进行完整逆向分析，确认其公开 API 如下：

| 导出名称 | 类型 | 说明 |
|----------|------|------|
| `UQC` | 类 | 低级客户端，Socket.IO / WebSocket 通信 |
| `UQCBackend` | 类 | Qiskit BackendV2 封装，高级接口 |
| `UQCConfig` | 类 | Pydantic 配置模型（环境变量 / .env） |
| `plot_hist` | 函数 | 可视化量子态概率直方图 |
| `ensure_static_qasm` | 函数 | 验证 OpenQASM 3.0 是否为静态线路 |

### 2.2 UQC 低级客户端 API

```python
from uqc_client import UQC

client = UQC(token="your_access_token")

# 查询可用芯片
chips = client.get_chips(chip_status="active")
chip_info = client.get_chip_info(chip_name="Matrix2")

# 提交任务
task_id = client.submit_task(
    convert_qprog=qasm3_string,  # OpenQASM 3.0 字符串
    target="Matrix2",             # "Matrix2"=真机, "iontrap-sim"=模拟器, "qiskit-sim"=Aer
    shots=100                     # 必须是 100 的倍数，范围 [100, 1000]
)

# 轮询状态
status = client.get_task_status(task_id)  # "STARTED" → "SUCCESS" / "FAILURE"

# 获取结果（ARTIQ 格式）
result = client.get_task_result(task_id)
# result[0]["datasets"]["computational_basis_histogram"] → [[index, count], ...]
```

### 2.3 UQC 硬件约束

| 约束项 | 限制 |
|--------|------|
| 原生门集 | rzz, rx, ry, measure, barrier |
| 拓扑 | 全连接 (all-to-all) |
| Shots | ∈ [100, 1000]，必须是 100 的整数倍 |
| 线路类型 | **仅支持静态线路**，禁止任何动态特性（条件分支、mid-circuit measure 等） |
| QASM 版本 | OpenQASM 3.0 |
| 芯片名称 | Matrix2（真机），iontrap-sim（模拟器） |
| 最大比特数 | 7 qubits（当前芯片） |
| Token 有效期 | **30 分钟** |
| 通信协议 | WebSocket (python-socketio), 服务器 `cloud.unitaryqubit.com:8003` |

### 2.4 结果数据格式

UQC 返回的结果采用 **ARTIQ 格式**，与标准 Qiskit `get_counts()` 不同：

```python
# ARTIQ 原始格式
result = [
    {
        "datasets": {
            "computational_basis_histogram": [
                [0, 48],   # index=0 (二进制 "000"), count=48
                [7, 52],   # index=7 (二进制 "111"), count=52
            ]
        }
    }
]

# 需要转换为 Qiskit 兼容格式
counts = {"000": 48, "111": 52}
```

---

## 3. 集成架构设计

### 3.1 模块拓扑

```
YAML Config
    ↓
BackendSpecConfig (config/backend.py)
    ↓ backend_spec_from_config()
BackendSpec (backends/spec.py)          ← +4 个 UQC 字段
    ↓ executor_from_spec()
factory._uqc_factory()                   ← 新增注册
    ↓
UQCCloudHeaExecutor (backends/uqc_executor.py)    ← 核心执行器
    ├── transpile_to_uqc_native()         (backends/uqc_transpiler.py)
    ├── UQC.submit_task() / get_task_status() / get_task_result()
    ├── _artiq_histogram_to_counts()      ← ARTIQ → bitstring 转换
    └── compute_hamiltonian_expectation_from_counts()  (backends/uqc_pauli_measurement.py)
```

### 3.2 与现有架构的关系

- **不侵入现有代码路径**：仅在 `BackendSpec` 新增可选字段，factory 新增 provider 注册
- **mock 模式复用** `StatevectorHeaExecutor`：无需 uqc-client 即可运行全部流水线
- **Qiskit 转译桥接**：HEA → Qiskit QuantumCircuit → transpile(rzz, rx, ry) → OpenQASM 3.0
- **配置双通道**：UQC 参数同时存储在 `BackendSpec` 顶层字段和 `meta` 字典中，executor 两处均检查

---

## 4. 实现细节

### 4.1 新增文件清单

| 文件 | 用途 | 行数 |
|------|------|------|
| `src/qchem_stack/backends/uqc_executor.py` | 核心执行器，实现 HamiltonianExpectationExecutor 协议 | ~277 |
| `src/qchem_stack/backends/uqc_transpiler.py` | 电路转译为离子阱原生门集 | ~81 |
| `src/qchem_stack/backends/uqc_pauli_measurement.py` | 从测量计数计算哈密顿量期望值 | ~123 |
| `configs/uqc_h2.yaml` | UQC 云平台 H2 计算示例配置 | ~250 |

### 4.2 修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `backends/spec.py` | BackendSpec 新增 `provider: "uqc"` 和 4 个 UQC 字段 |
| `backends/factory.py` | 注册 `_uqc_factory`，导入 `UQCCloudHeaExecutor` |
| `backends/__init__.py` | 导出 `UQCCloudHeaExecutor` |
| `config/backend.py` | `BackendSpecConfig` 新增 UQC 配置字段和验证器 |
| `config/io.py` | `backend_spec_from_config()` 传递 UQC 字段 |
| `pyproject.toml` | 新增 `uqc` 可选依赖组 |

### 4.3 核心执行流程

```
1. 构建 HEA 电路 → hea_circuit_qiskit(n_qubits, depth, angles)
2. 转译 → transpile(qc, basis_gates=["rzz", "rx", "ry"], optimization_level=2)
3. 添加测量 → qc.measure(range(n), range(n))
4. 导出 QASM → qiskit.qasm3.dumps(qc)
5. 静态验证 → ensure_static_qasm(qasm3_str)
6. Shots 约束 → max(100, min(1000, shots)); 向上取整到 100 的倍数
7. 提交任务 → UQC(token).submit_task(convert_qprog=qasm, target="Matrix2", shots=N)
8. 轮询等待 → while get_task_status() not in ("SUCCESS", "FAILURE"): sleep(2s)
9. 获取结果 → get_task_result() → ARTIQ histogram → bitstring counts
10. 计算期望 → compute_hamiltonian_expectation_from_counts(counts, H, n_qubits)
```

### 4.4 ARTIQ 格式转换

```python
@staticmethod
def _artiq_histogram_to_counts(hist_data: list[list], n_qubits: int) -> dict[str, int]:
    """ARTIQ [[index, count], ...] → {"000": 48, "111": 52}"""
    counts = {}
    for entry in hist_data:
        idx, count = int(entry[0]), int(entry[1])
        bitstring = format(idx, f"0{n_qubits}b")
        counts[bitstring] = count
    return counts
```

---

## 5. 配置使用说明

### 5.1 YAML 配置示例

```yaml
backend:
  name: uqc_ion_trap
  provider: uqc
  shots_per_circuit: 1000
  target_energy_stderr: null
  qiskit_mode: statevector
  # UQC 云平台配置
  uqc_token: null              # 或通过 UQC_API_TOKEN 环境变量
  uqc_backend_name: null       # UQC 后端名称
  uqc_mode: real               # real=提交真机, mock=本地模拟
  uqc_transpile_opt_level: 2   # 转译优化级别 0-3
  meta:
    uqc_target: Matrix2        # 目标设备: Matrix2/iontrap-sim/qiskit-sim
    uqc_timeout_s: 300.0       # 任务超时（秒）
    uqc_poll_interval_s: 2.0   # 轮询间隔（秒）

compiler:
  optimization_level: 2
  native_twoq: RZZ             # UQC 离子阱原生双比特门
```

### 5.2 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `UQC_API_TOKEN` | UQC 云平台 API Token | 从云平台用户管理系统获取 |

### 5.3 安装依赖

```bash
# 安装 UQC 可选依赖
pip install -e ".[uqc]"

# 或安装全部依赖
pip install -e ".[all]"

# 依赖列表: uqc-client>=0.1, qiskit>=2.0, qiskit-aer>=0.13
```

### 5.4 快速开始

```python
from qchem_stack.config import load_experiment_config, backend_spec_from_config
from qchem_stack.backends import executor_from_spec

# 1. 加载 UQC 配置
cfg = load_experiment_config("configs/uqc_h2.yaml")

# 2. 创建后端规格
spec = backend_spec_from_config(cfg)

# 3. 创建执行器
executor = executor_from_spec(spec)

# 4. 运行流水线
from qchem_stack.orchestration import run_pipeline_from_config
result = run_pipeline_from_config("configs/uqc_h2.yaml")
```

---

## 6. 关键注意点与风险

### 6.1 API 调用（严重 — 已修复）

**问题:** 初始实现使用了 `UQCBackend.submit_circuit()` 方法，该方法 **不存在于 uqc-client API 中**。

**正确 API:**
```python
# 低级 API（推荐，完全控制）
client = UQC(token)
task_id = client.submit_task(convert_qprog=qasm_str, target="Matrix2", shots=100)
status = client.get_task_status(task_id)
result = client.get_task_result(task_id)

# 高级 API（Qiskit 兼容）
backend = UQCBackend(token)
job = backend.run(transpiled_circuit, shots=100)
counts = job.result().get_counts()
```

**教训:** 必须在实现前验证第三方 API 的实际接口，不能基于名称推测。

### 6.2 结果解析格式（严重 — 已修复）

**问题:** 初始实现假设 `result.get_counts()` 返回标准 Qiskit 格式，但 UQC 低级 API 返回 **ARTIQ 格式**。

**正确解析:**
```python
# ARTIQ 原始格式: [[index, count], ...]
hist_data = result[0]["datasets"]["computational_basis_histogram"]
# index 是整数，需要转换为 n_qubits 位宽的二进制字符串

# 注意：如果使用 UQCBackend.run() 高级 API，则可直接 result.get_counts()
```

### 6.3 任务轮询机制（严重 — 已修复）

**问题:** 初始实现没有轮询逻辑，直接等待 `job.result()`。

**正确做法:** UQC 是异步任务系统，需要主动轮询状态：
```python
while True:
    status = client.get_task_status(task_id)
    if status == "SUCCESS":
        break
    if status == "FAILURE":
        raise RuntimeError("UQC task failed")
    time.sleep(2.0)  # 轮询间隔
```

### 6.4 QASM 导出方式（中等 — 已修复）

**问题:** 使用 `qc.qasm3()` 方法导出 QASM，可能产生与 `qiskit.qasm3.dumps()` 不同的输出。

**正确做法:** 统一使用 `qiskit.qasm3.dumps(qc)`，这是 Qiskit 2.x 的规范 API。

### 6.5 Shots 约束（中等 — 已修复）

**问题:** 仅检查 shots 是 100 的倍数，未检查上限。

**正确约束:**
```python
shots = max(100, min(1000, shots))      # 范围 [100, 1000]
shots = ((shots + 99) // 100) * 100     # 向上取整到 100 的倍数
```

### 6.6 静态线路验证（中等 — 已修复）

**问题:** 未验证线路是否为静态。UQC **严格禁止**动态特性。

**正确做法:**
```python
from uqc_client import ensure_static_qasm
ensure_static_qasm(qasm3_str)  # 验证失败会抛出异常
```

### 6.7 Token 过期风险（高 — 待解决）

**问题:** UQC token 有效期仅 **30 分钟**。VQE 优化通常需要数百次迭代，总运行时间可能远超 30 分钟。

**当前状态:** `_get_uqc_client()` 缓存了 client 实例，不会自动刷新 token。

**建议方案:**
1. 在每次 `submit_task` 前检查 token 剩余时间
2. 提供 token refresh 回调：`meta["uqc_token_refresh_fn"]`
3. 捕获认证异常并自动刷新：
```python
try:
    client.submit_task(...)
except UQCAuthenticationError:
    new_token = refresh_token()
    self._client = UQC(token=new_token)
    client.submit_task(...)
```

### 6.8 测量基旋转（高 — 待解决）

**问题:** 当前 `compute_hamiltonian_expectation_from_counts` 假设所有 Pauli 项均为 Z-basis 测量。但 VQE 哈密顿量包含 X/Y Pauli 项。

**影响:** 对于全 Z 项哈密顿量结果正确，混合 Pauli 基时给出**近似结果**。

**正确方案:** 需要实现多基旋转测量：
1. 按 Pauli 基分组（已有 `pauli_grouping.py`）
2. 对每个基组构建带旋转门的测量线路
3. 每个基组分别提交到 UQC（增加 N 倍提交次数）
4. 汇总各组期望值

**参考:** 现有 `pauli_measure_expand.py` 中的 `basis_change_operations` 已实现基旋转电路构建。

### 6.9 错误回退策略（中等 — 需注意）

**问题:** 当 UQC 云执行失败时，当前静默回退到 statevector 模拟。

**风险:** 用户可能不知道真机执行实际失败了，得到的结果来自本地模拟。

**建议:**
- 在 `PipelineResult` 中标记 `uqc_fallback_used: true`
- 增加配置项 `meta["uqc_allow_fallback"]` 控制是否允许回退
- 回退时发出 warning 级别的日志（当前已实现）

### 6.10 最大量子比特限制（信息 — 需注意）

**问题:** UQC 当前芯片仅支持 7 qubits。H2 STO-3G 最小活性空间 (2 orbital, 2 electron) 需要 4 qubits（JW 映射），尚在范围内。

**注意:** 更大分子（如 LiH、H2O）的活性空间可能超过 7 qubits 限制，需提前评估。

### 6.11 并发与速率限制（低 — 待观察）

**问题:** 未确认 UQC 云平台是否对并发任务数或 API 调用频率有限制。

**建议:** 在批量提交（如 Pauli 多基组测量）时，增加适当的提交间隔。

---

## 7. 测试验证

### 7.1 已有测试

| 测试文件 | 结果 | 说明 |
|----------|------|------|
| `test_executor_backends.py` | 7/7 PASSED | statevector, ionstack, qiskit, 动态注册 |
| `test_backend_capability_conformance.py` | 10/10 PASSED | 后端能力矩阵 |
| `test_backend_capability_parity.py` | 1/1 PASSED | PySCF/Psi4 对等性 |
| `test_pipeline_backend_gate.py` | 5/5 PASSED | 流水线后端门控 |

### 7.2 手动验证

```
✓ UQC executor imported successfully
✓ Registered providers: ['ion_stack', 'ionstack', 'local', 'numpy', 'qiskit', 'statevector', 'uqc']
✓ BackendSpec with UQC provider created
✓ UQC executor created: UQCCloudHeaExecutor
✓ Mock energy computed: 1.0
✓ UQC config loaded: h2_sto3g_uqc_cloud
✓ Backend spec created: provider=uqc, mode=real
✓ Native two-qubit gate: RZZ
✓ Ruff lint: 0 errors
```

### 7.3 自动化测试（已接入）

| 测试项 | 位置 | CI |
|--------|------|-----|
| UQC mock 注册 + mock 能量 | `tests/quantum/test_uqc_mock_md_ml_integration.py` | 是（`uqc_mock and not slow`） |
| 流水线 + QMEF 附件 | 同上 `test_pipeline_uqc_mock_attaches_qmef_for_md_ml` | 是 |
| 一轮主动学习环 | 同上 `test_md_validation_loop_one_round_uqc_mock_labeling`（`@pytest.mark.slow`） | 否（需本机 QML-FF） |

操作说明见 [`说明_UQC_mock与分子力场在线学习.md`](说明_UQC_mock与分子力场在线学习.md)。

### 7.4 待补充测试

| 测试项 | 优先级 | 说明 |
|--------|--------|------|
| ARTIQ 直方图解析 | P1 | 测试 `_artiq_histogram_to_counts` 各种边界情况 |
| Shots 约束逻辑 | P1 | 验证 [100, 1000] 和 100 倍数的截断逻辑 |
| Token 过期重连 | P2 | 模拟 UQCAuthenticationError 后的恢复路径 |
| 多基旋转测量 | P2 | 待实现后补充 |

---

## 8. 已知限制与后续工作

### 8.1 当前已知限制

1. **仅支持 HEA ansatz 的云提交**：UCCSD 等其他 ansatz 的 CircuitIR → QASM3 转换尚未覆盖
2. **单基 Z 测量**：混合 Pauli 基的哈密顿量期望值计算为近似
3. **无并发任务管理**：不支持批量异步提交
4. **无 token 自动刷新**：长时间运行的 VQE 可能因 token 过期而中断
5. **`_get_uqc_backend()` 未使用**：保留了 `UQCBackend` 高级接口的初始化代码，但当前执行路径仅使用低级 `UQC` 客户端

### 8.2 后续工作路线图

| 阶段 | 工作项 | 优先级 | 估计工时 |
|------|--------|--------|----------|
| Phase 1 | 真机联调验证 H2 STO-3G VQE | P0 | 1-2 天 |
| Phase 2 | 实现多基旋转 Pauli 测量 | P1 | 3-5 天 |
| Phase 3 | Token 自动刷新机制 | P1 | 1 天 |
| Phase 4 | UCCSD 线路 UQC 转译支持 | P2 | 2-3 天 |
| Phase 5 | 批量异步任务提交与结果收集 | P2 | 2-3 天 |
| Phase 6 | 回退标记写入 PipelineResult | P3 | 0.5 天 |
| Phase 7 | 完整测试套件（mock + 真机） | P1 | 2 天 |

---

## 9. 附录：完整 API 对照表

### 9.1 初始实现 vs 修复后实现

| 步骤 | 初始实现（错误） | 修复后实现（正确） |
|------|-----------------|-------------------|
| 客户端初始化 | `UQCBackend(token, backend_name)` | `UQC(token)` 低级客户端 |
| 电路转译 | `transpile(qc, basis_gates=["rzz","rx","ry"])` | 相同（正确） |
| QASM 导出 | `qc.qasm3()` | `qiskit.qasm3.dumps(qc)` |
| 静态验证 | 无 | `ensure_static_qasm(qasm_str)` |
| 任务提交 | `backend.submit_circuit(qasm, shots)` | `client.submit_task(convert_qprog=qasm, target="Matrix2", shots=100)` |
| 状态轮询 | `job.result()` 同步等待 | 循环 `client.get_task_status(task_id)` |
| 结果获取 | `result.get_counts()` | `result[0]["datasets"]["computational_basis_histogram"]` |
| 结果格式 | Qiskit 标准 counts dict | ARTIQ `[[index, count], ...]` 需手动转换 |
| Shots 约束 | 仅取 100 倍数 | `max(100, min(1000, shots))` + 100 倍数 |
| 测量添加 | 无（假设电路自带） | 显式添加 `qc.measure(range(n), range(n))` |

### 9.2 uqc-client 完整 API 速查

```python
from uqc_client import UQC, UQCBackend, UQCConfig, plot_hist, ensure_static_qasm

# ─── 低级 API ──────────────────────────────────────────
client = UQC(token="...")
client.get_chips(chip_status="active")           # → list | None
client.get_chip_info(chip_name="Matrix2")        # → dict | None
task_id = client.submit_task(                     # → str | None
    convert_qprog=qasm3_str,
    target="Matrix2",
    shots=100
)
status = client.get_task_status(task_id)          # → "STARTED" | "SUCCESS" | "FAILURE"
result = client.get_task_result(task_id)          # → ARTIQ dict | None

# ─── 高级 API (Qiskit BackendV2) ───────────────────────
backend = UQCBackend(token="...")
backend.num_qubits                               # int
backend.target                                   # Qiskit Target
backend.coupling_map                             # 全连接
transpiled = transpile(qc, backend)
job = backend.run(transpiled, shots=100)          # → UQCFakeJob
counts = job.result().get_counts()                # 标准 Qiskit counts

# ─── 验证工具 ──────────────────────────────────────────
ensure_static_qasm(qasm_source, allowed_gates=("rzz", "rx", "ry"))

# ─── 异常层级 ──────────────────────────────────────────
UQCError
├── UQCConnectionError
├── UQCTimeoutError
├── UQCTaskError
└── UQCAuthenticationError
```

### 9.3 目标设备对照

| target 名称 | 类型 | 用途 |
|-------------|------|------|
| `"Matrix2"` | 真机 | 离子阱量子处理器（生产计算） |
| `"iontrap-sim"` | 模拟器 | 离子阱模拟器（验证线路） |
| `"qiskit-sim"` | 模拟器 | Qiskit Aer 模拟器（快速调试） |

---

**文档结束**

*本文档记录了 qchem-stack 与 UQC 云平台集成的完整技术方案、已发现问题和修复记录。后续真机联调和新功能开发应持续更新本文档。*
