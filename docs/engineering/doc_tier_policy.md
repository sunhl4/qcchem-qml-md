# Documentation tier policy

This policy classifies repository documentation so contributors know what must stay in sync with code changes.

## Tier 1 — Authoritative (PRs must update when behavior changes)

| Path | Role |
|------|------|
| [`ENGINEERING_ARCHITECTURE.md`](../ENGINEERING_ARCHITECTURE.md) | Layer model, HTTP touchpoints, repro posture |
| [`说明_config模块技术参考手册.md`](../说明_config模块技术参考手册.md) | `ExperimentConfig` field reference |
| [`public_parity_matrix.md`](../public_parity_matrix.md) | Capability matrix and gap anchors |
| [`docusaurus-site/docs/`](../docusaurus-site/docs/) | Product guides, tutorials, API excerpts (curated) |
| [`QUICKSTART_CONTRIBUTORS.md`](../QUICKSTART_CONTRIBUTORS.md) | Contributor onboarding |

## Tier 2 — Archive (read-only; fix factual errors only)

| Path | Role |
|------|------|
| [`execution/archive/`](../execution/archive/) | Day-by-day execution closeout logs |
| Historical execution calendars under `docs/execution/` marked archived in file headers |

Do not extend Tier 2 files for new features; add Tier 1 docs or CHANGELOG instead.

## Tier 3 — Research / positioning (non-runtime)

| Path | Role |
|------|------|
| `竞争定位*.md`, `工程记忆*.md` | Competitive positioning and narrative |
| [`research/presentations/`](../research/presentations/) | Internal presentation notes (formerly at `docs/组会汇报_*.md`) |
| [`research/evaluations/`](../research/evaluations/) | LLM / research evaluations (formerly at `docs/qwen*.md`) |
| [`internal/`](../internal/) | Maintainer audits and research notes |
| [`research/README.md`](../research/README.md) | Index for Tier 3 docs |

These inform backlog and UX but are **not** runtime dependencies. Code must not import from Tier 3 paths.

## Drift checks (CI)

- `scripts/check_doc_test_paths.py` — Tier-1 docs must not reference stale flat `tests/test_*.py` paths (`--fix` remaps to layer paths)
- `scripts/check_doc_links.py` — Docusaurus `configs/*.yaml` references exist (docusaurus job)
- `scripts/check_comparative_execution_backlog.py` — backlog YAML consistency (lint job)
- `scripts/sync_pre_quantum_docs.py` — pre-quantum matrix sync
- `scripts/generate_config_reference_snippets.py --check` — Pydantic field tables under `docs/generated/`

Tier-1 also includes repository-root [`CONTRIBUTING.md`](../CONTRIBUTING.md).
