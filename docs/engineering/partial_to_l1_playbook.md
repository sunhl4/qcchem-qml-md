# Partial → L1 convergence playbook

Use when upgrading a `partial` row in [`public_parity_matrix.md`](../public_parity_matrix.md).

## Checklist per gap

1. **L1 criterion** — numeric window or schema keys (not L0 binary parity).
2. **YAML** — minimal `configs/example_*.yaml` exercising the path.
3. **Test** — pytest name in CI (marker if optional dep).
4. **Contract** — `product_gap_categories()` / `capability-surface` row updated with `evidence`.
5. **Docs** — matrix row + optional Docusaurus excerpt.

## CI commands

```bash
pytest tests/test_api_runs.py::test_capability_surface_matches_product_contract -q
pytest tests/test_partial_l1_evidence.py -q
python scripts/check_parity_export_sample.py
```

## Top targets (Phase M)

| Gap anchor | L1 signal |
|------------|-----------|
| `adapt_iqeb_operator_pool_surface` | pool id resolves without fallback warning |
| `composable_computable` | workflow-preview ↔ DONE repro keys align |
| VQD deflation defaults | `run_summary` exports `vqd_overlap_mode_yaml` |
| DMET self-consistency | `parity_snapshot` includes `dmet_self_consistency_v1` cycles |
| MD/ML energy reference | `validate_loop_energy_consistency` green |
