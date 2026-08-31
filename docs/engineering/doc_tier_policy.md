# Documentation tier policy

This policy classifies repository documentation so contributors know what must stay in sync with code changes.

## Tier 1 — Authoritative (PRs must update when behavior changes)

| Path | Role |
|------|------|
| [`ENGINEERING_ARCHITECTURE.md`](../ENGINEERING_ARCHITECTURE.md) | Layer model, HTTP touchpoints, repro posture |
| [`说明_config模块技术参考手册.md`](../说明_config模块技术参考手册.md) | `ExperimentConfig` field reference |
| [`public_parity_matrix.md`](../public_parity_matrix.md) | Capability matrix and gap anchors |
| [`docusaurus-site/docs/`](../../docusaurus-site/docs/) | Product guides, tutorials, API excerpts (curated) |
| [`QUICKSTART_CONTRIBUTORS.md`](../QUICKSTART_CONTRIBUTORS.md) | Contributor onboarding |

## Tier 2 — Engineering reference (update when the related surface changes)

| Path | Role |
|------|------|
| `docs/技术文档_*.md`, `docs/说明_*.md`, `docs/config_reference_*.md` | Module / contract manuals |
| [`engineering/`](./) | Migrations, ownership, release, deployment |
| [`execution/`](../execution/) | Active engineering checklists + `comparative_execution_backlog.yaml` |
| [`research/`](../research/) | Classical chemistry delivery / usage handbooks |

## Drift checks (CI)

- `scripts/check_doc_test_paths.py` — Tier-1 docs must not reference stale flat `tests/test_*.py` paths (`--fix` remaps to layer paths)
- `scripts/check_doc_links.py` — Docusaurus `configs/*.yaml` references exist (docusaurus job)
- `scripts/check_comparative_execution_backlog.py` — backlog YAML consistency (lint job)
- `scripts/sync_pre_quantum_docs.py` — pre-quantum matrix sync
- `scripts/generate_config_reference_snippets.py --check` — Pydantic field tables under `docs/generated/`

Tier-1 also includes repository-root [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

Research surveys, presentation decks, day-by-day execution diaries, and competitive positioning drafts are **not** kept in this repository.
