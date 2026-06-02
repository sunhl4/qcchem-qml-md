# Execution evidence archive

This directory holds **program execution logs and backlog evidence** (Tier 2).

- **Canonical backlog:** [`comparative_execution_backlog.yaml`](comparative_execution_backlog.yaml) — validated in CI via `scripts/check_comparative_execution_backlog.py`.
- **Generated index:** [`INDEX.md`](INDEX.md) — regenerate with `python scripts/execution_doc_index.py`.
- **`archive/`:** read-only historical copies; do not extend for new features.

New product behavior belongs in Tier 1 docs (`docs/ENGINEERING_ARCHITECTURE.md`, CHANGELOG) — not new day-by-day execution diaries.
