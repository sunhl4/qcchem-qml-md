# Dual classical ingress (live + precomputed)

Goal: both classical lanes converge to the same quantum handoff (`PreQuantumInput`).

## Lane 1: live classical (structure file -> classical solve -> quantum)

Use `molecule.geometry_file` (XYZ currently supported) instead of inline coordinates.

Examples:

- `configs/example_h2_geometry_file_xyz.yaml`
- `configs/structures_h2.xyz`

## Lane 2: precomputed classical (bundle -> quantum)

Use `scf.driver: precomputed` with `scf.precomputed_bundle_path`.

Examples:

- `configs/example_h2_precomputed_bundle.yaml`
- `configs/precomputed_classical_reference_h2.json`

## Unified quantum interface

Both lanes are normalized into `PreQuantumInput` before quantum stages.

## Utility script

Use `scripts/build_precomputed_bundle.py` to assemble `classical_reference_bundle_v1` from decomposition JSON + external classical values.
