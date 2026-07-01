# Config module review — P16 polish

Date: 2026-05-20  
Follow-up to [CONFIG_REVIEW_P15.md](CONFIG_REVIEW_P15.md).

## Scope

| Item | Change |
|------|--------|
| Docs | `config/README.md` migration strict coverage; `docs/说明_scf配置.md` canonical nested SCF + `precomputed.bundle_path` |
| Mitigation validation | `validate_mitigation_cross_fields` wired in `MitigationSpec`; PMSV requires stabilizers when enabled |
| Repro dedupe | `repro_snapshot.repro_quantum_snapshot` uses `mitigation_repro_core_fields` |
| Tests | `test_mitigation_pmsv_requires_stabilizers_when_enabled`; SCF psi4 migration + nested dump roundtrip |
| Public API | Extended `qchem_stack.config.__all__` with `pmsv_enabled`, `resolve_scf_density_fit`, md_ml trajectory helpers |

## Verification

```bash
./scripts/venv-run pytest tests/test_config_*.py tests/config/test_migrations.py -q
./scripts/venv-run pyright src/qchem_stack/config
```

## Remaining optional (P17+)

- `repro_summary.py` mitigation yaml fields → shared helper
- active_space alias fields excluded from canonical dump
- SCF driver/sub-block consistency validator (`driver=psi4` vs populated `pyscf` block)
