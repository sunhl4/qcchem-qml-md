---
title: Principles & suggested reading
description: "Deeper mechanisms and algorithms — suggested in-site order (not step-by-step tutorials)"
---

This is **not** a how-to checklist; it is a **reading order** after you can run examples. Contracts remain authoritative in [Reference pages](/en/reference/http-api-sqlite-jobs) (HTTP API → CircuitIR, Qiskit, DMET, …) and source.

## Classical–quantum interface & embedding

1. [Engineering architecture](/en/concept/engineering-architecture)  
2. [P1 Chemistry & embedding](/en/guide/chemistry-and-embedding/)  
3. [DMET · parity_snapshot](/en/reference/dmet-parity-snapshot)

## Algorithms, protocols, circuits

1. [P2 Algorithms & protocols](/en/guide/algorithms-and-protocols/)  
2. [CircuitIR · TKET · jobs](/en/reference/circuitir-tket-jobs)  
3. [Qiskit shot counts](/en/reference/qiskit-shot-counts)

## Execution, mitigation, cloud analogies

1. [P3 Execution & analysis](/en/guide/execution-and-analysis/)  
2. [Mitigation mapping](/en/concept/mitigation-mapping)  
3. [Launch / Retrieve (Nexus analog)](/en/concept/launch-retrieve-nexus-analog)

## Jobs, HTTP, reproducibility

1. [P4 Jobs & reproducibility](/en/guide/jobs-and-reproducibility/)  
2. [HTTP API · SQLite jobs](/en/reference/http-api-sqlite-jobs)  
3. [HTTP API worker memory](/en/concept/http-api-worker-memory)

## Public-doc benchmark (internal engineering)

For alignment and acceptance work, read [competitive positioning](/en/concept/competitive-positioning), [engineering memory (Quantinuum)](/en/concept/engineering-memory-quantinuum), and [Parity](/en/parity/public-matrix) — **internal targets**, not the first stop for product users.

## External textbooks & papers

Use your group’s QC / computational-chemistry curriculum and recent reviews; our guides map **concepts to this stack’s YAML and fields**, they do not replace systematic study.

## Repo prose under `docs/` (paths only)

These paths are relative to the **`qchem_qml_md` repo root** — source Markdown for many Concept / Parity / Reference pages. Open them in your editor (we do **not** link them from VitePress to avoid dead-link checks on files outside the docs tree).

- `docs/README.md` (topic map; matches `README.md` / `CONTRIBUTING.md` 与 `docs/技术文档_*.md` §2 groupings)
- `docs/ENGINEERING_ARCHITECTURE.md`
- `docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`
- `docs/技术文档_CircuitIR与TKET桥接及作业契约.md`
- `docs/技术文档_设备比特串与Qiskit采样路径.md`
- `docs/技术文档_DMET与parity_snapshot开放契约.md`
- `docs/P1_化学与嵌入_InQuanto镜像与qchem_stack复现程度对照.md`
- `docs/inquanto_public_parity_matrix.md`
- `docs/与InQuanto能力差距与实施计划.md`
- `docs/与InQuanto能力差距与实施计划.md`（附录 C）
- `docs/与InQuanto能力差距与实施计划.md`（附录 B） (§6 SLA, §7 L3; former standalone templates merged)
- `docs/工程记忆_Quantinuum对标与数据流技术文档.md` §13 (merged former `记忆_开放栈…`)
- `docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md`
- `docs/architecture-report-quantinuum-inquanto-web/INDEX.md` (multi-volume report hub; includes vol-03 tutorial patterns)
- `docs/inquanto-node-backlog.generated.json` (295-node machine backlog)
