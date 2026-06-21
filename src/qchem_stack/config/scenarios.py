"""Onboarding scenario → representative YAML mapping."""

from __future__ import annotations

from pathlib import Path

from qchem_stack.config.config_paths import default_configs_dir

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
            "example_h2_uqc_mock_md_ml.yaml",
            "example_h2_qmlff_md.yaml",
            "example_h4_classical_md_stub.yaml",
            "example_h2_md_ml_trajectory_full_pipeline.yaml",
        ],
    ),
}

__all__ = [
    "SCENARIOS",
    "list_scenarios_text",
    "scenario_base_config_path",
    "scenario_config_path",
    "scenario_v3_path",
]


def _configs_root(configs_dir: Path | None) -> Path:
    return configs_dir if configs_dir is not None else default_configs_dir()


def scenario_v3_path(scenario_id: str, *, configs_dir: Path | None = None) -> Path:
    """Path to thin scenario-first v3 stub YAML (``configs/scenarios/{id}.yaml``)."""
    if scenario_id not in SCENARIOS:
        known = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"unknown scenario {scenario_id!r}; choose from: {known}")
    base = _configs_root(configs_dir)
    return (base / "scenarios" / f"{scenario_id}.yaml").resolve()


def scenario_base_config_path(scenario_id: str, *, configs_dir: Path | None = None) -> Path:
    """Full v2 reference YAML for a scenario (legacy onboarding path)."""
    if scenario_id not in SCENARIOS:
        known = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"unknown scenario {scenario_id!r}; choose from: {known}")
    rel = SCENARIOS[scenario_id][2][0]
    base = _configs_root(configs_dir)
    return (base / rel).resolve()


def scenario_config_path(scenario_id: str, *, configs_dir: Path | None = None) -> Path:
    """Resolve onboarding YAML: prefer ``configs/scenarios/{id}.yaml``, else full v2 reference."""
    v3 = scenario_v3_path(scenario_id, configs_dir=configs_dir)
    if v3.is_file():
        return v3
    return scenario_base_config_path(scenario_id, configs_dir=configs_dir)


def list_scenarios_text(*, configs_prefix: str = "configs/") -> str:
    lines = ["Available config scenarios:", ""]
    base = default_configs_dir()
    for sid, (title, desc, yaml_names) in SCENARIOS.items():
        v3_rel = f"{configs_prefix}scenarios/{sid}.yaml"
        v3_path = base / "scenarios" / f"{sid}.yaml"
        primary = v3_rel if v3_path.is_file() else f"{configs_prefix}{yaml_names[0]}"
        lines.append(f"  {sid:16}  {title}")
        lines.append(f"                    {desc}")
        lines.append(f"                    -> {primary}")
        lines.append("")
    return "\n".join(lines)
