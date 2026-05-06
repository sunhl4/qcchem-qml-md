"""P0: ``repro.run_summary`` keys emitted by ``_attach_run_summary`` stay whitelisted."""

from __future__ import annotations

import pytest

from qchem_stack.config import (
    ActiveSpaceSpec,
    EmbeddingSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.orchestration.pipeline import _attach_run_summary, collect_repro_metadata
from qchem_stack.protocols.inquanto_contract import RUN_SUMMARY_DOCUMENTED_KEYS


def _mol() -> MoleculeSpec:
    return MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]])


@pytest.mark.parametrize(
    "cfg,out_extra",
    [
        (
            ExperimentConfig(
                experiment_id="rs0",
                random_seed=0,
                molecule=_mol(),
                active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
                quantum=QuantumSpec(
                    use_pauli_protocol=True,
                    vqd_after_variational=True,
                    qse_after_variational=True,
                    sceom_after_variational=True,
                ),
            ),
            {
                "scf_energy": -1.0,
                "energy_after_variational": -1.2,
                "vqd": {"meta": {"reused_pipeline_ground": True}},
                "qse": {"excitation_energies": [0.1], "meta": {}},
                "sceom": {"energies": [-1.0], "meta": {"subspace_dim": 1, "construction": "x"}},
                "energy_pauli_protocol": -1.1,
                "resource_summary": {
                    "sum_shots": 10,
                    "pauli_averaging_protocol_ran": True,
                    "n_pauli_terms": 3,
                    "n_pauli_groups": 2,
                    "n_circuits": 2,
                    "n_qubits": 4,
                },
                "protocol_counts": {
                    "expectation_source": "executor_exact_or_device_mean",
                    "energy_stderr_model": "conservative_sum_bound_equal_shots",
                },
                "qpe_demo_track": {"schema": "qpe_demo_track_stub"},
                "nexus_analog_ledger": {"hqc_units": 1.5},
                "mitigation_graph_report": {"nodes": []},
                "mitigation_dag_execution": {"steps": []},
                "nexus_cloud_repro": {"schema": "nexus_cloud_repro_stub"},
            },
        ),
        (
            ExperimentConfig(
                experiment_id="rs_dmet",
                random_seed=0,
                molecule=_mol(),
                active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
                quantum=QuantumSpec(use_pauli_protocol=False),
                embedding=EmbeddingSpec(
                    mode="dmet",
                    fragment_labels=["A"],
                    dmet_hamiltonian_source="whole_active_system",
                ),
            ),
            {
                "scf_energy": -1.0,
                "energy_after_variational": -1.2,
                "dmet_fragment_solve": {"schema": "dmet_one_shot_v1"},
            },
        ),
    ],
)
def test_run_summary_keys_whitelisted(cfg: ExperimentConfig, out_extra: dict) -> None:
    out: dict = {"repro": collect_repro_metadata(cfg)}
    out.update(out_extra)
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    unknown = set(sm) - RUN_SUMMARY_DOCUMENTED_KEYS
    assert not unknown, f"Add keys to RUN_SUMMARY_DOCUMENTED_KEYS: {sorted(unknown)}"


def test_run_summary_with_parity_snapshot_sidecars_whitelisted() -> None:
    cfg = ExperimentConfig(
        experiment_id="rs_ps",
        random_seed=0,
        molecule=_mol(),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(use_pauli_protocol=False),
    )
    repro = collect_repro_metadata(cfg)
    repro["parity_snapshot"] = {
        "qnexus_probe": {"available": False},
        "tket_first_compiled_circuit_probe": {"ok": True},
        "dmet_one_shot_open_ledger": {"fragments": [{"energy": -0.5}]},
        "dmet_solver_mode": "parity_stub",
        "open_gap_closure_reference": {},
        "dmet_uniform_multifragment_toy": {},
        "schmidt_per_fragment_vqe_summary": {"schema": "schmidt_per_fragment_vqe_summary_v1", "n_fragments": 0},
    }
    repro["pipeline_profile"] = {
        "schema": "pipeline_profile_v1",
        "total_wall_ms": 12.0,
        "stages": [{"stage": "scf_done", "duration_ms": 5.0}, {"stage": "done", "duration_ms": 7.0}],
    }
    repro["run_context"] = {"trace_id": "tid", "client_request_id": "rid"}
    out: dict = {
        "repro": repro,
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    unknown = set(sm) - RUN_SUMMARY_DOCUMENTED_KEYS
    assert not unknown, f"Add keys to RUN_SUMMARY_DOCUMENTED_KEYS: {sorted(unknown)}"
