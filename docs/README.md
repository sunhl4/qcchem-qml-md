# Documentation index (`docs/`)

This directory is the **engineering and contract** documentation for `qchem-stack`. User-facing tutorials and onboarding live in [`docusaurus-site/`](../docusaurus-site/) (build with `cd docusaurus-site && npm install && npm start`).

## Documentation sync policy

| Surface | Role | Source of truth |
|---------|------|-----------------|
| **Parity / gap matrix** | Product capability gaps, L1 export keys | [`public_parity_matrix.md`](public_parity_matrix.md) |
| **Pre-quantum YAML matrix** | Allowed classical → qubit combinations | [`pre_quantum_yaml_matrix.md`](pre_quantum_yaml_matrix.md) (blocks auto-synced by `scripts/sync_pre_quantum_docs.py`) |
| **Docusaurus site** | Curated guides, tutorials, short parity excerpt | Hand-maintained subset; link to repo `docs/` for long contracts |
| **Engineering architecture** | Layering, HTTP, repro posture | [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md) (Docusaurus has a short summary only) |

When changing parity export keys or pre-quantum allowed combos, update the repo `docs/` file first, run `python scripts/sync_pre_quantum_docs.py` if applicable, then align Docusaurus links or excerpts.

## Categories

### Reference (day-to-day engineering)

- [`说明_config模块技术参考手册.md`](说明_config模块技术参考手册.md), [`config_字段索引.md`](config_字段索引.md), [`config_校验分层约定.md`](config_校验分层约定.md)
- [`说明_quantum配置.md`](说明_quantum配置.md), [`chem_模块风格约定.md`](chem_模块风格约定.md), [`quantum_模块风格约定.md`](quantum_模块风格约定.md)
- [`pre_quantum_yaml_matrix.md`](pre_quantum_yaml_matrix.md)

### Contracts (stable interfaces)

- [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md)
- [`技术文档_CircuitIR与TKET桥接及作业契约.md`](技术文档_CircuitIR与TKET桥接及作业契约.md)
- [`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)
- [`parity_export_schema_versioning.md`](parity_export_schema_versioning.md)
- [`launch_retrieve_nexus_analog.md`](launch_retrieve_nexus_analog.md)

### Onboarding

- [`QUICKSTART_CONTRIBUTORS.md`](QUICKSTART_CONTRIBUTORS.md)
- [`QUICKSTART_HTTP_API_en.md`](QUICKSTART_HTTP_API_en.md)
- [`说明_config入门_通俗导读.md`](说明_config入门_通俗导读.md)
- [`学习路线图_框架理论到源码阅读顺序.md`](学习路线图_框架理论到源码阅读顺序.md)

### Competitive / 对标 (historical — not runtime dependencies)

- [`竞争定位与路线图_对标Quantinuum产品与技术路线.md`](竞争定位与路线图_对标Quantinuum产品与技术路线.md)
- [`工程记忆_Quantinuum对标与数据流技术文档.md`](工程记忆_Quantinuum对标与数据流技术文档.md)
- [`public_parity_matrix.md`](public_parity_matrix.md) (also used as engineering contract)
- [`quantum_InQuanto_Tangelo_对照矩阵.md`](quantum_InQuanto_Tangelo_对照矩阵.md)

### Execution archive

- Active plans: [`execution/comparative_execution_rd_plan_strict_2026Q3Q4.md`](execution/comparative_execution_rd_plan_strict_2026Q3Q4.md), [`execution/comparative_execution_backlog.yaml`](execution/comparative_execution_backlog.yaml)
- Day-by-day evidence logs: [`execution/archive/`](execution/archive/) (see [`execution/README.md`](execution/README.md))

### Internal (maintainer notes)

- [`internal/`](internal/) — config reviews, style roadmap, import layers, audit reports
