# Config migration (flat → nested)

Strict migrators reject unknown flat keys. See [`config_校验分层约定.md`](../config_校验分层约定.md).

| Legacy flat key | Nested path |
|-----------------|-------------|
| `zne_enabled` | `mitigation.zne.enabled` |
| `ncas` / `nelecas` | `active_space.cas.n_orbitals` / `n_electrons` |
| `scf.precomputed_bundle_path` | `scf.precomputed.bundle_path` |
| `attach_md_ml_to_repro` | `md_ml_export.attach_single_frame_to_repro` |

Codemods: `scripts/codemod_*.py`. Tests: `tests/config/test_migrations.py`.
