from __future__ import annotations

import pytest

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_embedding_input_lowdin_payload_in_workflow(tmp_path) -> None:
    cfg_path = tmp_path / "h2_lowdin.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: phase_b_lowdin
random_seed: 1
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
embedding:
  mode: dmet
  fragment_labels: ["frag0"]
  dmet_hamiltonian_source: parity_stub
  embedding_input_representation: lowdin_orth_ao
quantum:
  use_pauli_protocol: false
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    eis = out.get("embedding_input_system")
    assert isinstance(eis, dict)
    assert eis.get("schema") == "embedding_input_system_v1"
    assert eis.get("representation") == "lowdin_orth_ao"
    wf = out.get("embedding_workflow") or {}
    assert isinstance(wf.get("embedding_input_system"), dict)
    rs = out["repro"]["run_summary"]
    assert rs.get("embedding_input_representation_yaml") == "lowdin_orth_ao"
    assert rs.get("embedding_input_system_schema") == "embedding_input_system_v1"


def test_rdm_correction_stub_report_and_run_summary(tmp_path) -> None:
    cfg_path = tmp_path / "h2_rdm_stub.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: phase_c_rdm_stub
random_seed: 1
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
quantum:
  use_pauli_protocol: false
chemistry_extended:
  rdm_correction_method: stub_nevpt2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    rc = out.get("rdm_correction")
    assert isinstance(rc, dict)
    assert rc.get("schema") == "rdm_correction_report_v1"
    assert rc.get("method") == "stub_nevpt2"
    assert rc.get("status") == "stub"
    assert rc.get("kernel_class") == "placeholder_stub"
    rr = out.get("rdm_correction_readiness")
    assert isinstance(rr, dict)
    assert rr.get("schema") == "rdm_correction_readiness_v1"
    assert rr.get("nevpt2_pyscf_status") == "not_run"
    assert rr.get("rdm1_source") == "pyscf_scf_rdm1"
    assert rr.get("rdm_basis") == "spatial_ao_pyscf"
    assert rr.get("spin_model") == "restricted"
    rb = out.get("rdm_bundle_meta")
    assert isinstance(rb, dict)
    assert rb.get("schema") == "rdm_bundle_v2"
    assert rb.get("rdm_basis") == "spatial_ao_pyscf"
    assert rb.get("spin_model") == "restricted"
    rs = out["repro"]["run_summary"]
    assert rs.get("rdm_correction_present") is True
    assert rs.get("rdm_correction_method") == "stub_nevpt2"
    assert rs.get("rdm_correction_readiness_present") is True
    assert rs.get("rdm_correction_readiness_rdm_basis") == "spatial_ao_pyscf"
    assert rs.get("rdm_correction_readiness_spin_model") == "restricted"


def test_rdm_correction_pyscf_nevpt2_casci_pipeline(tmp_path) -> None:
    cfg_path = tmp_path / "h2_nevpt.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: phase3_nevpt
random_seed: 1
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
quantum:
  use_pauli_protocol: false
chemistry_extended:
  rdm_correction_method: pyscf_nevpt2_casci
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    rc = out.get("rdm_correction")
    assert isinstance(rc, dict)
    assert rc.get("method") == "pyscf_nevpt2_casci"
    assert rc.get("status") == "ok"
    assert rc.get("energy_correction_au") == pytest.approx(0.0, abs=1e-9)
    assert rc.get("kernel_class") == "pyscf_mrpt_nevpt2"
    rr = out.get("rdm_correction_readiness")
    assert isinstance(rr, dict)
    assert rr.get("nevpt2_pyscf_status") == "ok"
    assert rr.get("reference_wavefunction") == "casci"
    rs = out["repro"]["run_summary"]
    assert rs.get("rdm_correction_readiness_nevpt2_pyscf_status") == "ok"
