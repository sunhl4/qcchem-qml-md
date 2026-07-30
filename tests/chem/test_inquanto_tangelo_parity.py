"""InQuanto/Tangelo parity extensions: mappings, VSQS, QCC Pauli, QPE plugins."""

from __future__ import annotations

import math

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_spatial_chemist_integrals
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.protocols.ansatz_prep import (
    AnsatzPrepSpec,
    build_prep_operations,
    prepare_statevector,
)
from qchem_stack.quantum.algorithms.qcc_circuit import QCCCircuitContext
from qchem_stack.quantum.variational_plugins.registry import list_registered_variational_ids
from tests.helpers.paths import configs_path


def test_jkmn_hcb_mapping_status_executable() -> None:
    from qchem_stack.chem.fermion_mapping_registry import mapping_status_rows_v1

    rows = mapping_status_rows_v1()
    by_lit = {r["yaml_literal"]: r for r in rows if "yaml_literal" in r}
    assert by_lit["jkmn"]["execution_status"] == "executable"
    assert by_lit["hard_core_boson"]["execution_status"] == "executable"


def test_jkmn_and_hcb_spatial_hamiltonian_build() -> None:
    from openfermion import count_qubits

    h1 = np.diag([0.1, 0.2]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    qh_jkmn = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="jkmn"
    )
    qh_hcb = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="hard_core_boson"
    )
    assert qh_jkmn.meta["fermion_to_qubit_map"] == "jkmn"
    assert count_qubits(qh_jkmn.operator) == 4
    assert qh_hcb.meta["fermion_to_qubit_map"] == "hard_core_boson"
    assert count_qubits(qh_hcb.operator) == 2


def test_qcc_ansatz_prep_pauli_ops_match_statevector() -> None:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

    qh = QubitHamiltonian(
        operator=QubitOperator("Z0", 0.5),
        n_qubits=4,
        fermion_space=FermionSpace(4, 2),
    )
    ctx = QCCCircuitContext.from_hamiltonian(qh)
    assert len(ctx.cluster_mats) >= 1
    angles = np.linspace(0.1, 0.2, num=len(ctx.cluster_mats), dtype=float)
    spec = AnsatzPrepSpec.qcc(hamiltonian=qh, angles=angles)
    ops = build_prep_operations(spec)
    assert ops[0]["name"] == "INIT_STATEVECTOR"
    sv = prepare_statevector(spec)
    assert sv.shape == (16,)
    assert math.isfinite(float(np.vdot(sv, sv).real))


@pytest.mark.parametrize(
    "config_rel,ansatz_kind",
    [
        ("example_h2_qcc_pauli_protocol.yaml", "qcc"),
        ("example_h2_upccgsd_pauli_protocol.yaml", "upccgsd"),
        ("example_h2_puccd_pauli_protocol.yaml", "puccd"),
    ],
)
def test_cluster_pauli_protocol_yaml(config_rel: str, ansatz_kind: str) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == ansatz_kind
    assert out["resource_summary"]["pauli_averaging_protocol_ran"] is True
    prep = out["protocol_counts"].get("ansatz_prep") or {}
    assert prep.get("ansatz_kind") == ansatz_kind


def test_iqcc_algorithm_yaml() -> None:
    p = configs_path("example_h2_iqcc.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "iqcc"
    assert isinstance(out.get("iqcc_meta"), dict)
    ar = out.get("algorithm_report") or {}
    assert ar.get("schema") == "algorithm_iqcc_report_v1"
    assert math.isfinite(float(out["energy_after_variational"]))


@pytest.mark.parametrize(
    "config_rel,algorithm",
    [
        ("example_h2_qite.yaml", "qite"),
    ],
)
def test_research_ansatz_yaml(config_rel: str, algorithm: str) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == algorithm
    assert math.isfinite(float(out["energy_after_variational"]))


@pytest.mark.parametrize(
    "config_rel,algorithm",
    [
        ("example_h2_qpe_deterministic.yaml", "qpe_deterministic"),
        ("example_h2_qpe_info_theory.yaml", "qpe_info_theory"),
    ],
)
def test_qpe_main_plugins_yaml(config_rel: str, algorithm: str) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == algorithm
    assert math.isfinite(float(out["energy_after_variational"]))


def test_qpe_plugins_registered() -> None:
    ids = list_registered_variational_ids()
    assert "qpe_deterministic" in ids
    assert "qpe_info_theory" in ids


def test_adapt_staggered_pool_yaml() -> None:
    p = configs_path("example_h2_adapt_staggered_pool.yaml")
    cfg = load_experiment_config(p)
    assert cfg.quantum.adapt.pool_id == "fermionic_singles_doubles_staggered"
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "adapt"
    assert math.isfinite(float(out["energy_after_variational"]))


@pytest.mark.parametrize(
    "config_rel,expected",
    [
        ("example_h2_jkmn.yaml", {"ansatz": "uccsd", "mapping": "jkmn"}),
        ("example_h2_hcb.yaml", {"ansatz": "hea", "mapping": "hard_core_boson"}),
    ],
)
def test_mapping_pipeline_yaml(config_rel: str, expected: dict[str, str]) -> None:
    p = configs_path(config_rel)
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert cfg.quantum.variational.ansatz == expected["ansatz"]
    assert math.isfinite(float(out["energy_after_variational"]))
    assert cfg.active_space.mapping.fermion_qubit == expected["mapping"]


def test_vsqs_ansatz_registry_and_pipeline() -> None:
    from qchem_stack.quantum.ansatz_registry import ANSATZ_REGISTRY

    assert "vsqs" in ANSATZ_REGISTRY
    p = configs_path("example_h2_vsqs.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == "vsqs"
    assert math.isfinite(float(out["energy_after_variational"]))
