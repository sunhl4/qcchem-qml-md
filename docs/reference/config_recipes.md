# Config recipes (common YAML)

| Recipe | Config | Command |
|--------|--------|---------|
| H₂ VQE smoke | `configs/example_h2.yaml` | `python scripts/smoke_pipeline.py` |
| Precomputed (no PySCF) | `configs/example_h2_precomputed_bundle.yaml` | `python scripts/smoke_pipeline.py --precomputed-only` |
| VQD excited | `configs/example_h2_excited_smoke.yaml` | `python scripts/smoke_pipeline.py --excited-only` |
| UCCSD Pauli protocol | `configs/example_h2_uccsd_pauli_protocol.yaml` | full pipeline |
| Psi4 driver | `configs/example_h2_psi4_rhf_sto3g.yaml` | `pytest -m psi4` |
| DMET self-consistent | `configs/example_h4_dmet_self_consistent.yaml` | `pytest -m slow` |
| UQC mock MD/ML | `configs/example_h2_uqc_mock_md_ml.yaml` | `pytest -m uqc_mock` |
| QML-FF active learning | `configs/example_h2_uqc_mock_qmlff_loop.yaml` | loop YAML + experiment YAML |
| SCBK mapping | `configs/example_h2_scbk_hea.yaml` | HEA + symmetry_conserving_bk |
| HTTP API job | `configs/example_h2.yaml` + `job_db` | `run_pipeline_from_config(..., job_db=...)` |
