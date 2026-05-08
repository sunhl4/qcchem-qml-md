# Subprocess Chemistry Adapter Risk Checklist

## Licensing and distribution

- PySCF: Apache-2.0 (Python package distribution friendly).
- Psi4: LGPL-family constraints; verify dynamic-link and redistribution boundaries in release notes.
- ORCA: commercial/research license; cannot be vendored in this repository.
- Additional binary engines: require per-vendor redistribution/legal review before default enablement.

## Protocol conformance (`ChemIntegralSolver`)

- `set_physical_data` accepts canonical `ExperimentConfig`.
- `compute_mean_field` returns `MolecularMeanFieldResult`.
- `driver_meta` must include canonical bridge headers after facade merge.
- capability map must be explicit (`supports_*` booleans), no implicit backend assumptions.

## Product-language guard

- Do not describe subprocess mode as Nexus/closed-stack parity.
- Keep statement explicit: backend adapter isolation only, no vendor cloud/runtime equivalence.
