# Local run outputs (`results/`)

This directory is **not tracked in git**. Use it for MD/ML validation loops, UQC cloud runs, and analysis artifacts on your machine.

## Typical layout

```
results/
  <your_run_name>/
    md_validation_summary.json
    train_final.xyz
    train_round_*.xyz
    plots/
```

## Commands

```bash
# MD/ML active-learning loop (example)
python scripts/run_uqc_md_ml.py --config configs/example_h2_uqc_mock_md_ml.yaml \
  --output results/my_run_name

# Analyze a finished run
python scripts/analyze_uqc_md_ml_results.py results/my_run_name
```

## Tests

`tests/test_uqc_mock_md_ml_integration.py` may write under `results/uqc_mock_md_ml_test/` during local or CI runs. CI fixtures live under `tests/fixtures/` (not here).

## Reference summaries

For benchmark dashboards and docs, use committed fixtures such as `tests/fixtures/md_validation_summary.json` rather than checking large binaries into the repository.
