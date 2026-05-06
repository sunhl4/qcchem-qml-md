"""P1: same YAML on supported backends / mappings yields stable repro & resource schema (smoke)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.inquanto_contract import REPRO_DOCUMENTED_KEYS


def _require_pyscf() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")


def _require_qiskit() -> None:
    try:
        import qiskit  # noqa: F401
    except ImportError:
        pytest.skip("Qiskit not installed")


def _assert_pipeline_schema(out: dict, *, min_qubits: int = 1) -> None:
    repro = out.get("repro")
    assert isinstance(repro, dict)
    unknown_repro = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown_repro, f"Unexpected repro keys: {sorted(unknown_repro)}"
    assert isinstance(repro.get("workflow_preview_v1"), dict)
    rs = out.get("resource_summary")
    assert isinstance(rs, dict)
    for k in ("n_circuits", "n_qubits", "sum_shots"):
        assert k in rs
    assert int(rs["n_qubits"]) >= min_qubits


def _run_example_h2(cfg_path: Path, cfg_modifier):
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(cfg_path)
    cfg = cfg_modifier(cfg)
    return run_pipeline_sync(cfg, cfg_path=cfg_path)


@pytest.mark.parametrize(
    "provider,qiskit_mode",
    (
        ("statevector", None),
        ("qiskit", "statevector"),
        ("qiskit", "estimator"),
    ),
)
def test_example_h2_pipeline_repro_schema_backend_providers(provider: str, qiskit_mode: str | None) -> None:
    _require_pyscf()
    if provider == "qiskit":
        _require_qiskit()

    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"

    def mod(c):
        be = c.backend.model_copy(update={"provider": provider})
        if qiskit_mode is not None:
            be = be.model_copy(update={"qiskit_mode": qiskit_mode})
        return c.model_copy(update={"backend": be})

    out = _run_example_h2(cfg_path, mod)
    _assert_pipeline_schema(out)


@pytest.mark.parametrize(
    "fermion_qubit_mapping",
    (
        "jordan_wigner",
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev",
    ),
)
def test_example_h2_pipeline_repro_schema_fermion_mappings(fermion_qubit_mapping: str) -> None:
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"

    def mod(c):
        return c.model_copy(
            update={
                "active_space": c.active_space.model_copy(
                    update={"fermion_qubit_mapping": fermion_qubit_mapping}  # type: ignore[arg-type]
                )
            }
        )

    out = _run_example_h2(cfg_path, mod)
    snap = out["repro"]["parity_snapshot"]
    assert snap["hamiltonian_meta"]["fermion_to_qubit_map"] == fermion_qubit_mapping
    min_q = 2 if fermion_qubit_mapping == "symmetry_conserving_bravyi_kitaev" else 4
    _assert_pipeline_schema(out, min_qubits=min_q)


def test_example_h2_pipeline_ionstack_expectation_fn_bridge() -> None:
    """IonStack provider wiring: inject NumPy reference expectation without hardware."""
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    ref = StatevectorHeaExecutor()

    def expectation_fn(h, n_qubits, angles, hea_depth):  # type: ignore[no-untyped-def]
        return ref.expectation_hea(h, n_qubits, angles, hea_depth)

    def mod(c):
        be = c.backend.model_copy(
            update={
                "provider": "ionstack",
                "meta": {"expectation_fn": expectation_fn},
            }
        )
        return c.model_copy(update={"backend": be})

    out = _run_example_h2(cfg_path, mod)
    _assert_pipeline_schema(out)


def test_example_h2_uccsd_packaged_yaml_repro_schema() -> None:
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_uccsd.yaml"
    out = _run_example_h2(cfg_path, lambda c: c)
    _assert_pipeline_schema(out, min_qubits=4)
    assert out["repro"]["parity_snapshot"]["variational_ansatz"] == "uccsd"
    assert out["repro"]["run_summary"]["variational_ansatz_yaml"] == "uccsd"


def test_example_h2_uccsd_trotter_packaged_yaml_repro_schema() -> None:
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_uccsd_trotter.yaml"
    out = _run_example_h2(cfg_path, lambda c: c)
    _assert_pipeline_schema(out, min_qubits=4)
    snap = out["repro"]["parity_snapshot"]
    assert snap["variational_ansatz"] == "uccsd"
    assert snap["uccsd_trotter_steps"] == 2


def test_uccsd_trotter_rejects_non_jw_mapping() -> None:
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_uccsd_trotter.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg = cfg.model_copy(
        update={
            "active_space": cfg.active_space.model_copy(
                update={"fermion_qubit_mapping": "bravyi_kitaev"}  # type: ignore[arg-type]
            )
        }
    )
    with pytest.raises(ValueError, match="jordan_wigner"):
        from qchem_stack.orchestration.pipeline import run_pipeline_sync

        run_pipeline_sync(cfg, cfg_path=cfg_path)


def test_example_h2_tket_probe_dict_when_pauli_protocol_runs() -> None:
    """TKET optional: parity always records a structured probe (stats or skip/failure)."""
    _require_pyscf()
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    out = _run_example_h2(cfg_path, lambda c: c)
    tp = out["repro"]["parity_snapshot"].get("tket_first_compiled_circuit_probe")
    assert isinstance(tp, dict)
    assert tp.get("schema") in ("tket_stats_attempt_v1", "tket_stats_skipped_v1")
