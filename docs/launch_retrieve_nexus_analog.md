# `launch` / `retrieve` 与 Nexus 异步模型的对照

本仓库不实现 Quantinuum **Nexus** 或 HQC 计价；以下仅说明 **公开文档中的异步提交/拉结果** 与 `qchem_stack` 的**语义类比**，便于与 [Vendor platform Protocols 概述](https://www.quantinuum.com/) 对照。

| Nexus / 文档侧（概念） | `qchem_stack` |
|--------------------------|---------------|
| 将程序/电路提交为异步作业，获得引用 ID | **Pauli：** `PauliAveragingProtocol.launch(store) -> JobHandle`（pickle 负载）。**全管线：** `enqueue_full_pipeline_run(store, config_yaml=..., run_context=...)`，`job_kind=full_pipeline` |
| 作业与协议版本/指纹（可审计） | `JobHandle.protocol_hash` 与表列 `protocol_hash`（与 `pickle` 负载的 SHA-256 前缀一致） |
| 轮询或拉取终态与结果 | `retrieve` / `SqliteJobStore.result`；**HTTP**：`GET /v1/runs/{job_id}`、列表 `GET /v1/runs`、轻量 **`GET …/status`** 与粗粒度 **`GET …/events`**（SQLite 时间戳合成，非完整事件流） |
| 本地 worker 消费队列 | `qchem-jobs-worker`：`drain_one_queued` → `dispatch_job`（`pauli_protocol` 走 `PauliAveragingProtocol.process_job`，`full_pipeline` 走 `run_full_pipeline_job`） |
| 项目/计价字段（云侧 **HQC** 的类比） | 同步管线：`nexus_analog_ledger`（YAML `nexus_analog` 权重）；全管线异步 **DONE** 的 `full_pipeline_job_result_v1` 同样可含 **`nexus_analog_ledger`** 等侧车；Pauli pickle 作业：`result` 中 **`nexus_analog_billing`**（协议体带 `NexusAnalogSpec`，与同步权重一致；未带 spec 时用 `jobs/cost` 默认） |
| 机读「能力差距 / 对标」清单 | **`GET /v1/meta/parity-gaps`**；**Computable YAML 预览** **`POST /v1/meta/computables-preview`**；**队列深度** **`GET /v1/meta/queue-stats`**；**仅 repro** **`GET /v1/runs/{id}/repro`**（`DONE` 时） |

**未完成时**：`result` 返回含 `status` 的字典，**不** 填充能量；**不要** 假设存在 `expectation` 除非 `status == "DONE"`。
