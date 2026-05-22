# Style optimization roadmap (P0–P4)

Tracker for the qchem-stack code style program. Do not duplicate the full plan here; see the approved implementation plan in Cursor.

## Milestones

| Phase | Scope | Status | Notes |
|-------|--------|--------|-------|
| P0 | Governance, baseline script, doc §6.1–6.3 | done | `scripts/code_health_baseline.py` |
| P1-1 | `active_space` canonical + `mapping` + helpers | done | |
| P1-2 | `quantum_helpers.py` | done | |
| P1-3 | `ScfDriverId`, precomputed path | done | |
| P1-4 | `_experiment_validation` split | done | |
| P1-5 | `chemistry_extended` doc complete | done | |
| P2-1 | `hamiltonian*` split | done | |
| P2-2 | `excited_*` split | done | |
| P2-3 | `repro_summary_*` split | done | |
| P2-4 | `pre_quantum_schmidt.py` | done | |
| P2-5 | `pipeline.py` cleanup | done | |
| P3-1 | `repro/schema.py` TypedDict | done | |
| P3-2 | Narrow `Any` hotspots | done | |
| P3-3 | pyright basic + CI | done | soft-fail job |
| P4 | Ruff TCH (+ per-file ignores elsewhere) | done | B/SIM deferred |
| P5-A | jobs/store + api/app + protocol_hea/counts | done | schema/sql/service; API routers |
| P5-B | pyscf_solver_* + protocol_* stages + excited types | done | mf/integrals/build/run/job split |
| P5-C | pyscf_driver_* + excited_stages_* + pyright expand | done | driver mf/mo; vqd/qse/sceom stages |
| P6 | protocol_run shot modes + pipeline stage map + Ruff B/SIM | done | shot_modes/mitigation; pyright pipeline |
| P7 | store_service_* + protocol_finalize_* + contracts registry | done | mixins; schema_ids + validate; API/job IDs |
| P8 | hamiltonian_build_assembly + workflow_preview_graph + schema_ids batch | done | dedupe meta; orchestration pyright dir |
| P9 | parity/repro schema_ids + rdm TypedDict + pyright hard gate | done | CI typecheck-stack; ExcitedResourceSummary unify |
| P10 | integrations schema_ids + repro ParityExportV3 + typecheck-config hard | done | integrations subset; config/repro pyright gate |
| P11 | fermion_mapping_registry + integrations pyright 0 + md_bridge/l3 schema_ids | done | CI typecheck-stack → full integrations/ |
| P12 | chem/jobs/quantum/md_bridge schema_ids + pyright gate (non-chem) | done | `schema_ids` +40; typecheck-stack +quantum/jobs/md_bridge/protocols |
| P13 | chem + backends pyright 0 + `pyscf_typing` shims | done | CI typecheck-stack +chem +backends; MeanFieldLike wrap at MF boundaries |
| P14 | `PipelineResultV1` TypedDict + pipeline schema tag + psi4_solver split + integrations index + contributor quick start | done | `orchestration/pipeline_result.py`; `integrations/README.md`; `docs/QUICKSTART_CONTRIBUTORS.md` |
| P14 | full `src/qchem_stack` pyright gate + excited_stages_types import fix | done | CI `pyright src/qchem_stack`; pyproject include unified |
| P15-config | config helpers/validation split, property shim removal, migration strict, SCF nested driver blocks, canonical active_space | done | `mitigation_helpers`, `scf_helpers`, codemods, `CONFIG_REVIEW_P15.md` |
| P16-config | docs sync (SCF nested), mitigation validation wired, repro helper dedupe, SCF dump tests, public helper exports | done | `说明_scf配置.md`, `CONFIG_REVIEW_P16.md` |

## PR log

| PR ID | Merged | Summary |
|-------|--------|---------|
| PR-P0-1 | — | Docs + baseline |

## Baseline

Regenerate after each major phase:

```bash
./scripts/venv-run python scripts/code_health_baseline.py --write docs/internal/code_health_baseline.json
```

Target at P4 end: zero files >500 lines under `src/qchem_stack`; orchestration reads `quantum` via helpers only.

## Large-file watch (chem)

Before adding the next feature, split submodules if either file grows further:

- `src/qchem_stack/chem/hamiltonian_build.py` (~385 lines)
- `src/qchem_stack/chem/embedding/schmidt_production.py` (~377 lines)
