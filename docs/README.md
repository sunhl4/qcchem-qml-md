# Documentation index (`docs/`)

This directory is the **engineering and contract** documentation for `qchem-stack`. User-facing tutorials and onboarding live in [`docusaurus-site/`](../docusaurus-site/) (build with `cd docusaurus-site && npm install && npm start`).

> **Documentation zones (read the right tier)**
>
> | Zone | Start here | Not runtime API |
> |------|------------|-----------------|
> | **Product (3 must-read)** | [`QUICKSTART_CONTRIBUTORS.md`](QUICKSTART_CONTRIBUTORS.md) · [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md) · [`public_parity_matrix.md`](public_parity_matrix.md) | — |
> | **Reference (on demand)** | [`reference/config_field_index.md`](reference/config_field_index.md) · config `说明_*.md` | — |
> | **Non-runtime** | [`research/README.md`](research/README.md) · [`execution/archive/`](execution/archive/) · [`internal/`](internal/) | Competitive research, day calendars, audits |

## Reader paths

| Audience | Start here |
|----------|------------|
| **L1 — Users** | [`docusaurus-site/`](../docusaurus-site/), [`README.md`](../README.md), [`configs/README.md`](../configs/README.md) |
| **L2 — Integrators** | [`ONBOARDING_BY_ROLE.md`](ONBOARDING_BY_ROLE.md), [`QUICKSTART_CONTRIBUTORS.md`](QUICKSTART_CONTRIBUTORS.md), [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md), HTTP contract docs under `技术文档_HTTP_API*.md` |
| **L3 — Maintainers** | [`public_parity_matrix.md`](public_parity_matrix.md), active plans under [`execution/`](execution/) (archived closeouts: [`execution/archive/2026Q2/`](execution/archive/2026Q2/)) |

Tier policy: [`engineering/doc_tier_policy.md`](engineering/doc_tier_policy.md).

## New contributors (start here)

1. [`QUICKSTART_CONTRIBUTORS.md`](QUICKSTART_CONTRIBUTORS.md) — YAML → pipeline → `repro`
2. [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md) — layering and invariants
3. [`engineering/pipeline_stage_ownership.md`](engineering/pipeline_stage_ownership.md) — stage → output keys
4. [`backends.md`](backends.md) — `BackendSpec` providers and extras
5. [`public_parity_matrix.md`](public_parity_matrix.md) — capability gaps (L1 contract)

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

- **Split config reference:** [`reference/config_field_index.md`](reference/config_field_index.md), [`reference/config_recipes.md`](reference/config_recipes.md), [`reference/config_migration.md`](reference/config_migration.md)
- [`说明_config模块技术参考手册.md`](说明_config模块技术参考手册.md), [`config_字段索引.md`](config_字段索引.md), [`config_校验分层约定.md`](config_校验分层约定.md)
- [`说明_quantum配置.md`](说明_quantum配置.md), [`chem_模块风格约定.md`](chem_模块风格约定.md), [`quantum_模块风格约定.md`](quantum_模块风格约定.md)
- [`pre_quantum_yaml_matrix.md`](pre_quantum_yaml_matrix.md)

### Engineering / product

- [`engineering/api_stability_policy.md`](engineering/api_stability_policy.md), [`engineering/v1_0_acceptance.md`](engineering/v1_0_acceptance.md), [`engineering/migration_v0_8_to_v1_0.md`](engineering/migration_v0_8_to_v1_0.md), [`engineering/partial_to_l1_playbook.md`](engineering/partial_to_l1_playbook.md), [`engineering/pypi_release.md`](engineering/pypi_release.md)
- [`engineering/protocol_pickle_migration.md`](engineering/protocol_pickle_migration.md), [`engineering/protocol_serialization_v2_rfc.md`](engineering/protocol_serialization_v2_rfc.md)
- Generated config tables: [`generated/`](generated/) (`scripts/generate_config_reference_snippets.py`)
- [`product/non_goals.md`](product/non_goals.md)

### Contracts (stable interfaces)

- [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md)
- [`技术文档_CircuitIR与TKET桥接及作业契约.md`](技术文档_CircuitIR与TKET桥接及作业契约.md)
- [`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)
- [`parity_export_schema_versioning.md`](parity_export_schema_versioning.md)
- [`launch_retrieve_nexus_analog.md`](launch_retrieve_nexus_analog.md)

### Onboarding

- User index: [`user/README.md`](user/README.md)
- [`QUICKSTART_CONTRIBUTORS.md`](QUICKSTART_CONTRIBUTORS.md)
- [`QUICKSTART_HTTP_API_en.md`](QUICKSTART_HTTP_API_en.md)
- [`说明_config入门_通俗导读.md`](说明_config入门_通俗导读.md)
- [`学习路线图_框架理论到源码阅读顺序.md`](学习路线图_框架理论到源码阅读顺序.md)

### Research / 对标 (historical — not runtime dependencies)

- Index: [`research/README.md`](research/README.md)
- [`竞争定位与路线图_对标Quantinuum产品与技术路线.md`](竞争定位与路线图_对标Quantinuum产品与技术路线.md)
- [`工程记忆_Quantinuum对标与数据流技术文档.md`](工程记忆_Quantinuum对标与数据流技术文档.md)
- [`public_parity_matrix.md`](public_parity_matrix.md) (also used as engineering contract)
- [`quantum_InQuanto_Tangelo_对照矩阵.md`](quantum_InQuanto_Tangelo_对照矩阵.md)

### Execution archive

- Active plans: [`execution/comparative_execution_rd_plan_strict_2026Q3Q4.md`](execution/comparative_execution_rd_plan_strict_2026Q3Q4.md), [`execution/comparative_execution_backlog.yaml`](execution/comparative_execution_backlog.yaml)
- Day-by-day evidence logs: [`execution/archive/`](execution/archive/) **and** duplicate working copies at [`execution/*.md`](execution/) (same content; archive is canonical for long-term storage)

### Internal (maintainer notes)

- [`internal/`](internal/) — config reviews, style roadmap, import layers, audit reports
