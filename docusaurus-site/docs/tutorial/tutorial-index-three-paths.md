---
sidebar_position: 2
---

# 教程索引：新用户三条路径（D61）

与仓库根 `examples/README.md` 并列维护。

| 路径 | 教程入口 | 脚本 / 命令 |
|------|-----------|-------------|
| **Quickstart（管线直觉）** | [快速上手](./quickstart) | `examples/tutorial_01_h2_vqe_export.py`、`python scripts/smoke_pipeline.py` |
| **Async HTTP（作业类比）** | [通过 HTTP 异步运行](./async-run-via-http) | `curl` / `TestClient`；母稿：`docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md` |
| **Parity export（Methods 对齐）** | [读取 repro 键](./read-repro-keys) | `python scripts/export_parity_criteria_table.py configs/example_h2.yaml`、`python scripts/check_parity_export_sample.py` |

**延伸阅读**：[`switch-backend-compare`](./switch-backend-compare)、[`decomposition-plugin-minimal`](./decomposition-plugin-minimal)。
