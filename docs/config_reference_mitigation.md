# `mitigation` — 误差缓解

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**详细说明：** [说明_mitigation配置.md](说明_mitigation配置.md)

| 字段 | 说明 |
|------|------|
| `execution_class` | 执行方式分类 |
| `zne.enabled` / `zne.mode` / `zne.scales` | 零噪声外推 |
| `pmsv.enabled` | 后选择（开了必须有 `stabilizers`） |
| `stubs.*` | 各类 stub |

**谁在用：** `orchestration/protocol_finalize_stage`。
