# Config v3 scenario-first (RFC)

**Status:** Accepted MVP (2026-06)

## Problem

Nested v2 YAML (`embedding`, `quantum` with 16+ spec classes) has high cognitive load for onboarding and CI matrix maintenance.

## Proposal

Add optional top-level fields for schema version 3:

```yaml
schema_version: "3"
scenario: minimal_vqe
overrides:
  quantum:
    vqe:
      max_iter: 100
```

Compilation path:

1. Load scenario registry entry from `qchem_stack.config.scenarios`
2. Deep-merge `overrides` onto scenario base dict
3. Run existing v1→v2 migrations
4. Validate as `ExperimentConfig`

## Non-goals

- No breaking change to existing v2 YAML files
- No field-level redesign of `ExperimentConfig` in v3.0

## CLI

```bash
qchem-run --scenario minimal_vqe --set quantum.vqe.max_iter=100
```

## Migration

See `config/migrations_v2_to_v3.py` and `tests/config/test_scenario_v3_compile.py`.
