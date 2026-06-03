"""Onboarding scenario → representative YAML mapping."""

from __future__ import annotations

SCENARIOS: dict[str, tuple[str, str, list[str]]] = {
    "minimal_vqe": (
        "Minimal VQE (Path A)",
        "Default H2 sto-3g VQE smoke; start here for Methods/repro export.",
        ["example_h2.yaml", "profiles/minimal_h2.yaml"],
    ),
    "uccsd_pauli": (
        "UCCSD + Pauli protocol",
        "Chemical ansatz with grouped Pauli measurement protocol.",
        ["example_h2_uccsd_pauli_protocol.yaml", "example_h2_uccgd_pauli_protocol.yaml"],
    ),
    "adapt_iqeb": (
        "ADAPT / IQEB pools",
        "Adaptive / IQEB operator-pool variational paths.",
        [
            "example_h2_adapt_singles_pool.yaml",
            "example_h2_iqeb_fermionic_doubles_pool.yaml",
        ],
    ),
    "excited_states": (
        "Excited states (VQD / QSE / SCEOM)",
        "Post-variational excited-state stages with shot accounting.",
        ["example_h2_vqd_uccsd.yaml", "example_h2_excited_smoke.yaml"],
    ),
    "embedding_dmet": (
        "Embedding / DMET / projection",
        "Schmidt, DMET self-consistency, Mulliken projection traces.",
        [
            "example_h4_dmet_self_consistent.yaml",
            "example_h4_projection_mulliken.yaml",
        ],
    ),
    "mitigation_shots": (
        "Mitigation + shot paths",
        "ZNE fold, Qiskit bitstring Pauli, classical shadows.",
        ["example_h2_zne_qiskit_fold.yaml", "example_h2_qiskit_shots.yaml"],
    ),
    "qpe_ft": (
        "QPE / fault-tolerant demo",
        "Main-config QPE and dual-track demo YAMLs.",
        ["example_h2_qpe_main.yaml", "qpe_dual_track_demo.yaml"],
    ),
    "md_ml": (
        "MD / ML active learning",
        "QMEF dataset loops; optional QML-FF / UQC mock backends.",
        [
            "example_h2_qmlff_md.yaml",
            "example_h2_uqc_mock_md_ml.yaml",
            "example_h4_classical_md_stub.yaml",
            "example_h2_md_ml_trajectory_full_pipeline.yaml",
        ],
    ),
}


def list_scenarios_text(*, configs_prefix: str = "configs/") -> str:
    lines = ["Available config scenarios:", ""]
    for sid, (title, desc, yaml_names) in SCENARIOS.items():
        lines.append(f"  {sid:16}  {title}")
        lines.append(f"                    {desc}")
        lines.append(f"                    -> {configs_prefix}{yaml_names[0]}")
        lines.append("")
    return "\n".join(lines)
