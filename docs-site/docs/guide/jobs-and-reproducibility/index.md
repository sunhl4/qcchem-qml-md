# P4 · 作业与可复现（Jobs & reproducibility）

对标产品中分散在 **Nexus** 与各手册的作业流；本站 **聚合** 本地队列、`repro` 导出与 parity 机读键。

## 你将学到

- `SqliteJobStore`、全管线异步、`JobHandle.protocol_hash` 与 launch/retrieve 语义类比。  
- FastAPI：`POST/GET /v1/runs`、`summary`、`repro`（DONE）、`parity-gaps`、`queue-stats`。  
- Strict JSON：`repro_json_dumps`、`parity_snapshot` 白名单。

## 相关文档

- [HTTP API · SQLite](/reference/http-api-sqlite-jobs)  
- [Launch / Retrieve（Nexus 类比）](/concept/launch-retrieve-nexus-analog)  
- [公开矩阵 §1](/parity/public-matrix) — 作业网关行  
- [L1 签 off](/parity/l1-signoff)  

## 在 InQuanto 镜像中的对应位置

- [extensions / inquanto-nexus（n/a）](/mirror/extensions/inquanto_nexus/) — 真云不在范围；本地类比由本柱聚合

<PillarMirror pillar="P4" locale="zh" />

## 下一步

[首页](/) · [Y1 对标台账](/parity/y1-alignment-ledger)
