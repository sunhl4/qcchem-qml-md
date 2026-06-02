"""Packaged ``configs/*.yaml`` pipeline smoke tests (split from core orchestration tests)."""

from __future__ import annotations

import json
import math

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
    load_experiment_config,
)
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.embedding_nested import embedding_dmet
from tests.helpers.h2_yaml import H2_STO3G_FCI_ENERGY
from tests.helpers.paths import configs_path


def test_tutorial_chain_h2_yaml_runs() -> None:
    p = configs_path("tutorial_chain_h2.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out.get("embedding_workflow", {}).get("mode") == "dmet"
    assert len(out["embedding_workflow"]["fragment_labels"]) == 1
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("compiler_bundle_signature")
    assert snap.get("compiler_preoptimize_passes") == ["qubit_reuse_hint"]
    assert snap.get("mitigation_execution_class") == "shot_postselect"
    assert snap.get("open_stack_contract_schema") == "parity_open_stack_contract_v1"
    assert snap.get("dmet_open_loop_architecture", {}).get("schema") == "dmet_open_architecture_v1"
    assert snap.get("dmet_one_shot_open_ledger", {}).get("schema") == "dmet_one_shot_v1"
    assert snap.get("dmet_solver_mode") == "parity_stub"
    rsum = out["repro"]["run_summary"]
    assert rsum.get("dmet_one_shot_open_ledger_present") is True
    assert rsum.get("dmet_embedding_active") is True
    assert rsum.get("dmet_hamiltonian_source_yaml") == "parity_stub"
    assert "energy_pauli_protocol" in out
    pc = out["protocol_counts"]
    assert pc.get("hamiltonian_pauli_term_records")


def test_dmet_whole_active_system_impurity_vqe_matches_global_vqe() -> None:
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="dmet_whole_h2",
        random_seed=7,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(
            algorithm="vqe",
            vqe={"depth": 1, "maxiter": 120},
            pauli={"use_protocol": False},
        ),
        embedding=embedding_dmet(
            fragment_labels=["impurity"],
            hamiltonian_source="whole_active_system",
            n_scf_cycles_embedding=1,
        ),
    )
    out = run_pipeline_sync(cfg)
    e0 = float(out["energy_after_variational"])
    row = out["dmet_fragment_solve"]["fragments"][0]
    assert row["solver"] == "QubitHamiltonianFragmentSolverVQE"
    assert float(row["energy"]) == pytest.approx(e0, rel=1e-10, abs=1e-10)
    assert out["embedding_workflow"]["dmet_hamiltonian_source"] == "whole_active_system"
    assert out["repro"]["parity_snapshot"]["dmet_solver_mode"] == "whole_active_system"
    rsum = out["repro"]["run_summary"]
    assert rsum.get("dmet_embedding_active") is True
    assert rsum.get("dmet_fragment_solve_present") is True
    assert rsum.get("dmet_fragment_solve_schema") == "dmet_one_shot_v1"
    assert rsum.get("dmet_hamiltonian_source_yaml") == "whole_active_system"


def test_run_pipeline_sync_packaged_h2_vqd_uccsd_yaml() -> None:
    p = configs_path("example_h2_vqd_uccsd.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_uccsd.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == "uccsd"
    vqd = out.get("vqd") or {}
    assert vqd.get("schema") == "excited_vqd_bundle_v1"
    assert len(vqd["energies"]) == 2
    meta = vqd["meta"]
    assert meta.get("vqd_variety_yaml") == "uccsd"
    assert meta.get("reused_pipeline_ground") is True
    assert meta.get("vqd_overlap_mode_yaml") == cfg.quantum.excited.vqd.overlap_mode
    assert isinstance(meta.get("tangelo_deflation_analogy_v1"), dict)
    assert isinstance(meta.get("vqd_cross_stack_semantics_v1"), dict)
    assert vqd["energies"][0] == pytest.approx(float(out["energy_after_variational"]))
    rsum = out["repro"]["run_summary"]
    assert rsum.get("vqd_variety_yaml") == "uccsd"
    assert rsum.get("vqd_overlap_mode_yaml") == cfg.quantum.excited.vqd.overlap_mode


def test_run_pipeline_sync_packaged_h2_uccsd_yaml() -> None:
    p = configs_path("example_h2_uccsd.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "vqe"
    vm = out.get("vqe_meta")
    assert isinstance(vm, dict)
    assert vm.get("variational_ansatz") == "uccsd"
    assert vm.get("jw_fixed_electron_sector_projection") is True
    assert int(vm["uccsd_n_parameters"]) >= 1
    ev = float(out["energy_after_variational"])
    assert math.isfinite(ev)
    scf_e = float(out["scf_energy"])
    assert scf_e < -1.0
    assert ev <= scf_e + 1e-3
    assert ev >= H2_STO3G_FCI_ENERGY - 5e-3
    snap = out["repro"]["parity_snapshot"]
    assert snap["variational_ansatz"] == "uccsd"
    assert snap["uccsd_n_parameters"] == int(vm["uccsd_n_parameters"])
    rsum = out["repro"]["run_summary"]
    assert rsum["variational_ansatz_yaml"] == "uccsd"
    assert rsum["uccsd_n_parameters"] == int(vm["uccsd_n_parameters"])
    ar = out.get("algorithm_report")
    assert isinstance(ar, dict)
    assert ar.get("schema") == "algorithm_uccsd_report_v1"
    assert rsum.get("algorithm_report_schema") == "algorithm_uccsd_report_v1"
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is False
    assert "energy_pauli_protocol" not in out


def test_run_pipeline_sync_packaged_h2_uccsd_pauli_protocol_yaml() -> None:
    p = configs_path("example_h2_uccsd_pauli_protocol.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_uccsd_pauli_protocol.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == "uccsd"
    ev = float(out["energy_after_variational"])
    assert math.isfinite(ev)
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is True
    epp = out.get("energy_pauli_protocol")
    assert epp is not None
    assert math.isfinite(float(epp))
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("pauli_protocol_expectation_path") == "statevector_grouped_shot_simulation"
    prep = out["protocol_counts"].get("ansatz_prep") or {}
    assert prep.get("ansatz_kind") == "uccsd"


def test_run_pipeline_sync_classical_shadows_stub_e2e() -> None:
    p = configs_path("example_h2_classical_shadows_stub.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_classical_shadows_stub.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    dex = out.get("mitigation_dag_execution")
    assert isinstance(dex, dict)
    trace = dex.get("trace") or []
    assert trace and trace[0].get("node") == "classical_shadows_expectation_stub"
    assert trace[0].get("computable_runtime") == "classical_shadows_hamiltonian_expectation"
    assert out.get("classical_shadows_computable_runtime") is not None


def test_run_pipeline_sync_packaged_h2_vqd_three_computable_yaml() -> None:
    p = configs_path("example_h2_vqd_uccsd_three_computable.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_uccsd_three_computable.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vqd = out.get("vqd") or {}
    meta = vqd.get("meta") or {}
    assert meta.get("vqd_optimizer_mode") == "three_computable"
    assert len(meta.get("vqd_optimizer_trace") or []) >= 1


def test_run_pipeline_sync_packaged_h2_uccsd_qse_pauli_qiskit_yaml() -> None:
    pytest.importorskip("qiskit")
    p = configs_path("example_h2_uccsd_qse_pauli_qiskit.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_uccsd_qse_pauli_qiskit.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    qse = out.get("qse") or {}
    meta = qse.get("meta") or {}
    assert meta.get("qse_shot_mode") == "pauli_transitions_qiskit"
    assert meta.get("computable_runtime") == "QSEMatricesComputable"
    assert len(qse.get("excitation_energies") or []) >= 1


def test_run_pipeline_sync_packaged_h2_vqd_deflation_circuit_yaml() -> None:
    pytest.importorskip("qiskit")
    p = configs_path("example_h2_vqd_deflation_circuit.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_deflation_circuit.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vqd = out.get("vqd") or {}
    meta = vqd.get("meta") or {}
    assert meta.get("vqd_overlap_mode_yaml") == "deflation_circuit"
    tda = meta.get("tangelo_deflation_analogy_v1") or {}
    recipe = tda.get("deflation_circuit_recipe_v1") or {}
    assert recipe.get("qiskit_export_v1", {}).get("twoq_gate_count", 0) >= 1


def test_run_pipeline_sync_packaged_h2_uccsd_trotter_yaml() -> None:
    p = configs_path("example_h2_uccsd_trotter.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vm = out["vqe_meta"]
    assert vm.get("uccsd_trotter_steps") == 2
    assert vm.get("uccsd_product_formula") == "first_order_layer_repeat"
    assert vm.get("jw_fixed_electron_sector_projection") is True
    snap = out["repro"]["parity_snapshot"]
    assert snap["uccsd_trotter_steps"] == 2


def test_run_pipeline_sync_fe_helike_sto3g_cas22_smoke_yaml() -> None:
    p = configs_path("example_fe_sto3g_helike_rhf_cas22.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"]["n_qubits"] == 4
    assert math.isfinite(float(out["scf_energy"]))
    assert math.isfinite(float(out["energy_after_variational"]))


def test_run_pipeline_sync_oniom_toy_yaml_sets_embedding_layers() -> None:
    p = configs_path("example_oniom_toy.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    wf = out.get("embedding_workflow") or {}
    ot = wf.get("oniom_toy_v1")
    assert isinstance(ot, dict)
    assert ot.get("schema") == "oniom_toy_v1"
    assert len(ot.get("layers") or []) == 2


def test_run_pipeline_sync_h2_casscf_audit_yaml() -> None:
    p = configs_path("example_h2_casscf_audit.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    hm = out.get("hamiltonian_meta") or {}
    pd = hm.get("pyscf_driver") or {}
    audit = pd.get("casscf_orbital_audit_v1")
    assert isinstance(audit, dict)
    assert audit.get("schema") == "casscf_orbital_audit_v1"
    assert "casscf_energy_au" in audit
    assert audit.get("mo_coeff_rotated_into_casscf") is False


def test_run_pipeline_sync_packaged_h2_iqeb_yaml() -> None:
    p = configs_path("example_h2_iqeb.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "iqeb"
    assert isinstance(out.get("iqeb_meta"), dict)
    assert out["iqeb_meta"].get("rounds") == 2
    assert isinstance(out.get("iqeb_selected_pauli_strings"), list)
    rsum = out["repro"]["run_summary"]
    assert rsum["quantum_algorithm"] == "iqeb"
    assert rsum.get("iqeb_implementation_path") == "qchem_stack.quantum.algorithms.iqeb.IQEBVQE"
    assert rsum.get("iqeb_max_rounds_yaml") == 2
    snap = out["repro"]["parity_snapshot"]
    assert snap["quantum_algorithm"] == "iqeb"
    assert snap["iqeb_max_rounds"] == 2


def test_run_pipeline_sync_packaged_projection_trace_yaml() -> None:
    p = configs_path("example_h2_projection_trace.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    wf = out.get("embedding_workflow", {})
    assert wf.get("mode") == "projection"
    assert wf.get("schema") == "projection_embedding_workflow_v1"
    assert wf.get("projection_quantum_hamiltonian") == "global_active_space"
    assert "projection_low_level" in wf
    snap = out["repro"]["parity_snapshot"]
    pet = snap.get("projection_embedding_open_trace")
    assert isinstance(pet, dict)
    assert pet.get("schema") == "projection_embedding_open_trace_v1"
    assert pet.get("projection_hamiltonian_source") == "global_active_space"
    blob = str(pet)
    assert "not wired" not in blob.lower()
    stages = out["repro"]["run_summary"]["stages_completed"]
    assert "projection_embedding_trace" in stages
    assert "energy_pauli_protocol" in out


def test_run_pipeline_sync_projection_mulliken_h4_yaml() -> None:
    p = configs_path("example_h4_projection_mulliken.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"].get("integral_source") == "pyscf_projection_fragment_mulliken_v1"
    wf = out.get("embedding_workflow", {})
    assert wf.get("projection_quantum_hamiltonian") == "fragment_mulliken_mo"
    assert wf.get("projection_selected_mo_indices")
    stages = out["repro"]["run_summary"]["stages_completed"]
    assert "projection_embedding_trace" in stages
    snap = out["repro"]["parity_snapshot"]
    pet = snap.get("projection_embedding_open_trace")
    assert pet.get("projection_hamiltonian_source") == "fragment_mulliken_mo_v1"
    assert "not wired" not in json.dumps(snap).lower()
