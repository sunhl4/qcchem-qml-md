# `backend` — 量子计算跑在哪

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

| 字段 | 默认 | 说明 |
|------|------|------|
| `name` | `"statevector_sim"` | 后端实例名 |
| `provider` | `"statevector"` | statevector / qiskit / ionstack |
| `shots_per_circuit` | `2048` | 每条线路 shot 数 |
| `target_energy_stderr` | `None` | 目标能量标准误 |
| `qiskit_mode` | `"statevector"` | Qiskit 模式 |
| `ionstack_endpoint` | `None` | IonStack 地址 |
| `meta` | `{}` | 调试元数据 |

## CI 覆盖矩阵

| `provider` | PR 矩阵 (`pytest -m "not slow and not perf"`) | 3.12 Ubuntu smoke | 周频 optional job |
|------------|---------------------------------------------|-------------------|-------------------|
| `statevector` | 是 | 是 | — |
| `qiskit` | 部分（conformance `importorskip`） | `smoke_pipeline --qiskit-shots` | — |
| `pytket` | — | `test_pytket_bridge.py` | — |
| `ionstack` / `uqc` | marker `uqc_mock` | 是 | — |
| `cirq` | conformance（需安装 `cirq`） | — | `test-optional-backends` |
| `braket` | conformance（需安装 `amazon-braket-sdk`） | — | `test-optional-backends` |
