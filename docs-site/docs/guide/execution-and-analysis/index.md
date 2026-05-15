# P3 · 执行与分析（Execution & analysis）

对应 InQuanto 的 **Execution and Analysis**：电路执行、模拟器与硬件、误差缓解、资源指标。

## 你将学到

- `BackendSpec`（statevector / qiskit / ionstack）与 Pauli 采样三路：`executor`、`run_sampled`、`run_qiskit_shots`。  
- 资源行与可选 **pytket** 深度（与 TKET 叙事对齐，非厂商独占路由）。  
- PMSV / ZNE / SPAM 与 **qermit_analog** 图 + **mitigation_dag_execution**（非 Qermit 商业运行时）。

## 相关文档

- [Qiskit 比特串采样](/reference/qiskit-shot-counts)  
- [CircuitIR · TKET · 作业契约](/reference/circuitir-tket-jobs)  
- [缓解映射](/concept/mitigation-mapping)  

## 在 InQuanto 镜像中的对应位置

- [manual / noise mitigation](/mirror/manual/noise_mitigation/) — Qermit / PMSV / SPAM 概念
- [api / extensions / cutensornet](/mirror/api/extensions_cutensornet/) — `CuTensorNetProtocol` 接口

<PillarMirror pillar="P3" locale="zh" />

## 下一步

[P4 作业与可复现](/guide/jobs-and-reproducibility/) · [工程记忆](/concept/engineering-architecture)
