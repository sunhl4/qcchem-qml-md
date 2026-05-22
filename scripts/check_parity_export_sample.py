#!/usr/bin/env python3
"""Smoke-check parity export JSON (config-only) for L1 regression.

Runs ``export_parity_criteria_table`` (config-only) on ``SAMPLE_CONFIGS_REL`` and asserts
stable keys + ``release_anchor`` on every gap row.

Does not require PySCF or a pipeline results file.

When adding parity-driven ``configs/*.yaml``, extend ``SAMPLE_CONFIGS_REL`` so CI keeps
schema coverage.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# M2-style sampling: VQE + ADAPT + excited + IQEB + projection + Pauli shot-path YAMLs (config-only export).
SAMPLE_CONFIGS_REL = (
    "configs/example_h2.yaml",
    # Second backend (`scf.driver=psi4`): registry + capabilities snapshot in export (no PySCF required).
    "configs/example_h2_psi4_rhf_sto3g.yaml",
    "configs/example_h2_psi4_schmidt_dmet.yaml",
    "configs/example_h2_psi4_avas.yaml",
    "configs/example_h2_psi4_projection_mulliken.yaml",
    "configs/example_h2_precomputed_bundle.yaml",
    "configs/example_h2_excited_smoke.yaml",
    "configs/example_h2_iqeb.yaml",
    "configs/example_h2_adapt_singles_pool.yaml",
    "configs/example_h2_adapt_doubles_pool.yaml",
    "configs/example_h2_iqeb_fermionic_doubles_pool.yaml",
    "configs/example_h2_iqeb_qubit_excitation_alias.yaml",
    "configs/example_h2_adapt_uccsd_jw_alias.yaml",
    "configs/example_h2_projection_trace.yaml",
    "configs/example_h4_projection_mulliken.yaml",
    "configs/example_h2_sampled.yaml",
    "configs/example_h2_qiskit_shots.yaml",
    "configs/example_h2_uccsd.yaml",
    "configs/example_h2_uccsd_trotter.yaml",
    "configs/example_h2_vqd_uccsd.yaml",
    "configs/example_h2_uccsd_bk.yaml",
    "configs/example_h2_zne_circuit_fold.yaml",
    "configs/qpe_dual_track_demo.yaml",
    "configs/example_decomposition_plugin_toy.yaml",
    "configs/example_decomposition_plugin_two_fragment.yaml",
    "configs/example_h2_pbc_gamma.yaml",
    "configs/example_oniom_toy.yaml",
    "configs/example_h4_dmet_fragment_exact_small.yaml",
    "configs/example_h4_schmidt_multifragment.yaml",
    "configs/example_h2_qpe_track.yaml",
    "configs/example_h2_vqs_track.yaml",
    "configs/example_h2_qpe_track_parity_integrations.yaml",
    "configs/example_h2_casscf_audit.yaml",
    "configs/example_h2_embedding_parity.yaml",
    "configs/example_h2_md_ml_trajectory_hf.yaml",
    "configs/example_h2_echo_variational_plugin.yaml",
    "configs/example_h2o_sto3g_cas44.yaml",
    "configs/example_n2_sto3g_cas44.yaml",
    "configs/example_fe_sto3g_helike_rhf_cas22.yaml",
    "configs/example_h2_avas_stub.yaml",
    "configs/example_h2_classical_shadows_stub.yaml",
    "configs/example_decomposition_plugin_contract.yaml",
    # Geometry / SCF extensions (parity_export molecule + scf surfaces; config-only)
    "configs/example_h2_sto3g_density_fit.yaml",
    "configs/example_h2_zmatrix_sto3g.yaml",
    "configs/example_h2_zmatrix_sto3g_density_fit.yaml",
    "configs/example_mg_lanl2dz_ecp_rhf.yaml",
    "configs/example_mg_lanl2dz_ecp_density_fit.yaml",
    "configs/example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml",
)


def _run_export(root: Path, cfg_rel: str, env: dict[str, str]) -> tuple[int, dict]:
    script = root / "scripts" / "export_parity_criteria_table.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(root / cfg_rel)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        return proc.returncode or 1, {}
    return 0, json.loads(proc.stdout)


def _sample_configs_unique_or_raise() -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    duplicated: list[str] = []
    for cfg in SAMPLE_CONFIGS_REL:
        if cfg in seen:
            duplicated.append(cfg)
            continue
        seen.add(cfg)
        deduped.append(cfg)
    if duplicated:
        d = ", ".join(sorted(set(duplicated)))
        raise ValueError(f"SAMPLE_CONFIGS_REL has duplicated entries: {d}")
    return tuple(deduped)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS

    env = {**os.environ, "PYTHONPATH": f"{src}" + os.pathsep + os.environ.get("PYTHONPATH", "")}
    try:
        samples = _sample_configs_unique_or_raise()
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        return 1
    for cfg_rel in samples:
        code, data = _run_export(root, cfg_rel, env)
        if code != 0:
            sys.stderr.write(f"export failed for {cfg_rel}\n")
            return code
        missing = sorted(PARITY_EXPORT_V3_STABLE_KEYS - set(data.keys()))
        if missing:
            sys.stderr.write(f"{cfg_rel}: export missing stable keys: {missing}\n")
            return 1
        if data.get("parity_export_schema_version") != "3":
            sys.stderr.write(f"{cfg_rel}: unexpected parity_export_schema_version\n")
            return 1
        gaps = data.get("capability_gap_categories")
        if not isinstance(gaps, list) or not gaps:
            sys.stderr.write(f"{cfg_rel}: capability_gap_categories empty\n")
            return 1
        for g in gaps:
            if not isinstance(g, dict) or not g.get("release_anchor"):
                sys.stderr.write(f"{cfg_rel}: gap row missing release_anchor\n")
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
