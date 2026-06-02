"""Unit tests for ``parity_finalize`` snapshot helpers."""

from __future__ import annotations

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.config import ExperimentConfig
from qchem_stack.config.embedding_enums import DmetHamiltonianSource, EmbeddingMode
from qchem_stack.contracts.schema_ids import (
    SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1,
    SCHMIDT_PER_FRAGMENT_VQE_V1,
    TKET_STATS_SKIPPED_V1,
    ZNE_QISKIT_UNIFICATION_V1,
)
from qchem_stack.orchestration.parity_finalize import (
    finalize_open_stack_parity_snapshot,
    schmidt_per_fragment_vqe_parity_summary,
)


def _cfg_with_parity(**parity_kwargs: object) -> ExperimentConfig:
    base = {
        "experiment_id": "parity_finalize_test",
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0, 0, 0], [0, 0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "manual",
            "manual": {"n_orbitals": 2, "n_electrons": 2},
            "mapping": {"fermion_qubit": "jordan_wigner"},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "quantum": {"algorithm": "vqe"},
        "backend": {"provider": "statevector"},
        "parity_integrations": {"enabled": True, **parity_kwargs},
    }
    return ExperimentConfig.model_validate(base)


def test_finalize_noop_when_parity_disabled() -> None:
    cfg = _cfg_with_parity(enabled=False)
    out = {"repro": {"parity_snapshot": {"existing": 1}}}
    finalize_open_stack_parity_snapshot(out, cfg, proto=None)
    assert out["repro"]["parity_snapshot"] == {"existing": 1}


def test_finalize_tket_skipped_when_no_proto() -> None:
    cfg = _cfg_with_parity(tket_first_circuit_stats=True)
    out = {"repro": {"parity_snapshot": {}}}
    finalize_open_stack_parity_snapshot(out, cfg, proto=None)
    probe = out["repro"]["parity_snapshot"]["tket_first_compiled_circuit_probe"]
    assert probe["schema"] == TKET_STATS_SKIPPED_V1
    assert probe["reason"] == "pauli_protocol_disabled_no_circuit_ir"


def test_schmidt_per_fragment_vqe_parity_summary() -> None:
    spfv = {
        "schema": SCHMIDT_PER_FRAGMENT_VQE_V1,
        "vqe_depth": 2,
        "vqe_maxiter_per_fragment": 50,
        "fragments": [
            {"fragment_id": "f0", "energy": -1.1, "n_qubits": 4, "nfev": 12},
        ],
    }
    summary = schmidt_per_fragment_vqe_parity_summary(spfv)
    assert summary["schema"] == SCHMIDT_PER_FRAGMENT_VQE_PARITY_SUMMARY_V1
    assert summary["n_fragments"] == 1
    assert summary["total_nfev"] == 12


class _ProtoWithCompiled:
    compiled_circuits = [
        CircuitIR(n_qubits=2, operations=[{"name": "RX", "qubits": [0], "params": [0.1]}])
    ]


def test_finalize_tket_probe_when_compiled_circuits() -> None:
    cfg = _cfg_with_parity(tket_first_circuit_stats=True)
    out = {"repro": {"parity_snapshot": {}}}
    finalize_open_stack_parity_snapshot(out, cfg, proto=_ProtoWithCompiled())  # type: ignore[arg-type]
    assert "tket_first_compiled_circuit_probe" in out["repro"]["parity_snapshot"]


def test_finalize_zne_qiskit_unification() -> None:
    base = {
        "experiment_id": "zne_qiskit",
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0, 0, 0], [0, 0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "manual",
            "manual": {"n_orbitals": 2, "n_electrons": 2},
            "mapping": {"fermion_qubit": "jordan_wigner"},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "quantum": {
            "algorithm": "vqe",
            "pauli": {"use_protocol": True, "run_qiskit_shots": True},
        },
        "backend": {"provider": "qiskit"},
        "mitigation": {"zne": {"enabled": True, "mode": "circuit_scale_fold"}},
        "parity_integrations": {"enabled": True},
    }
    cfg = ExperimentConfig.model_validate(base)
    out = {
        "repro": {"parity_snapshot": {}},
        "protocol_counts": {"zne_mode": "circuit_scale_fold"},
    }
    finalize_open_stack_parity_snapshot(out, cfg, proto=None)
    block = out["repro"]["parity_snapshot"]["zne_qiskit_unification_v1"]
    assert block["schema"] == ZNE_QISKIT_UNIFICATION_V1


def test_finalize_dmet_schmidt_atomic_production_mode() -> None:
    base = {
        "experiment_id": "dmet_schmidt",
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0, 0, 0], [0, 0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "manual",
            "manual": {"n_orbitals": 2, "n_electrons": 2},
            "mapping": {"fermion_qubit": "jordan_wigner"},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "quantum": {"algorithm": "vqe"},
        "backend": {"provider": "statevector"},
        "embedding": {
            "mode": "dmet",
            "dmet": {
                "hamiltonian_source": "schmidt_atomic_production",
                "fragment_labels": ["frag0"],
                "schmidt": {"fragment_atom_indices": [0, 1]},
            },
        },
        "parity_integrations": {"enabled": True, "dmet_stub_one_shot_ledger": True},
    }
    cfg = ExperimentConfig.model_validate(base)
    out = {
        "repro": {
            "parity_snapshot": {
                "hamiltonian_meta": {"schmidt_production_audit": {"ok": True}},
            }
        },
    }
    finalize_open_stack_parity_snapshot(out, cfg, proto=None)
    snap = out["repro"]["parity_snapshot"]
    assert snap["dmet_solver_mode"] == "schmidt_atomic_production"
    assert cfg.embedding.mode == EmbeddingMode.DMET
    assert cfg.embedding.dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION


def test_finalize_attaches_schmidt_summary() -> None:
    cfg = _cfg_with_parity()
    out = {
        "repro": {"parity_snapshot": {}},
        "schmidt_per_fragment_vqe": {
            "schema": SCHMIDT_PER_FRAGMENT_VQE_V1,
            "fragments": [{"fragment_id": "a", "energy": -0.5, "n_qubits": 2, "nfev": 3}],
        },
    }
    finalize_open_stack_parity_snapshot(out, cfg, proto=None)
    snap = out["repro"]["parity_snapshot"]
    assert snap["schmidt_per_fragment_vqe_summary"]["n_fragments"] == 1
