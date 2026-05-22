from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec, SCFSpec
from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.variational_plugins.examples.echo_runner import (
    echo_runner_factory,
    run_echo_variational,
)
from qchem_stack.quantum.variational_plugins.loader import (
    load_variational_runner_from_factory,
    validate_factory_import_path,
)
from qchem_stack.quantum.variational_plugins.registry import (
    is_registered_variational_id,
    register_variational_plugin,
    resolve_variational_runner,
    run_variational_stage,
)
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext


def _minimal_cfg(**q_kw: object) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="t",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(dict(q_kw)),  # type: ignore[arg-type]
    )


def _tiny_qh() -> QubitHamiltonian:
    op = QubitOperator(
        (
            (0, "Z"),
            (1, "Z"),
        ),
        1.0,
    )
    return QubitHamiltonian(operator=op, n_qubits=2)


def _tiny_pre_quantum_input(*, n_qubits: int) -> PreQuantumInput:
    op = QubitOperator(tuple((i, "Z") for i in range(max(1, n_qubits))), 1.0)
    qh = QubitHamiltonian(operator=op, n_qubits=n_qubits)
    ref = ClassicalMeanFieldReference(
        mf={"backend": "unit-test"},
        e_tot=0.0,
        mo_energy=np.asarray([0.0], dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
            charge=0,
            multiplicity=1,
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "unit-test"},
    )
    return PreQuantumInput(
        classical_reference=ref,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=None,
        meta={"source": "unit-test"},
    )


def test_validate_factory_import_path_accepts_dotted_attr() -> None:
    m, a = validate_factory_import_path(
        "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory",
    )
    assert m.endswith("echo_runner")
    assert a == "echo_runner_factory"


def test_validate_factory_import_path_rejects_bare_module() -> None:
    with pytest.raises(ValueError, match="algorithm_factory"):
        validate_factory_import_path("nope")


def test_quantum_spec_unknown_algorithm_without_factory() -> None:
    with pytest.raises(ValueError, match="Unknown quantum.algorithm"):
        _minimal_cfg(algorithm="not_a_real_algorithm")


def test_quantum_spec_allows_arbitrary_algorithm_with_factory() -> None:
    cfg = _minimal_cfg(
        algorithm="my_custom_label",
        algorithm_factory="qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory",
    )
    assert cfg.quantum.algorithm == "my_custom_label"
    assert "echo_runner" in (cfg.quantum.algorithm_factory or "")


def test_resolve_variational_runner_prefers_factory() -> None:
    r = resolve_variational_runner(
        algorithm="ignored_when_factory_present",
        algorithm_factory="qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory",
    )
    qh = _tiny_qh()
    exe = StatevectorHeaExecutor()
    ctx = VariationalRunContext(cfg=_minimal_cfg(), hamiltonian=qh, executor=exe, seed=0)
    out = r(ctx)
    assert isinstance(out.energy, float)
    assert out.algo_meta.get("variational_echo_plugin") is True


def test_load_bad_factory_module_raises_pipeline_error() -> None:
    with pytest.raises(PipelineError, match="import failed"):
        load_variational_runner_from_factory("__not_a_python_module_xx__:fn")


@pytest.mark.parametrize("algo", ["vqe", "adapt", "iqeb", "tetris_adapt"])
def test_registered_builtin_ids(algo: str) -> None:
    assert is_registered_variational_id(algo)


def test_register_variational_plugin_overwrite_guard() -> None:
    register_variational_plugin(
        "___test_echo_dup___",
        runner=run_echo_variational,
        summary="t",
        implementation="t",
        overwrite=True,
    )
    register_variational_plugin(
        "___test_echo_dup___",
        runner=run_echo_variational,
        summary="t2",
        implementation="t",
        overwrite=True,
    )


def test_register_variational_plugin_no_overwrite_raises() -> None:
    register_variational_plugin(
        "___test_once___",
        runner=run_echo_variational,
        summary="once",
        implementation="once",
        overwrite=True,
    )
    with pytest.raises(ValueError, match="already registered"):
        register_variational_plugin(
            "___test_once___",
            runner=run_echo_variational,
            summary="again",
            implementation="again",
            overwrite=False,
        )


def test_echo_runner_factory_protocol() -> None:
    runner = echo_runner_factory()
    qh = _tiny_qh()
    ctx = VariationalRunContext(
        cfg=_minimal_cfg(
            algorithm="custom_echo",
            algorithm_factory=(
                "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
            ),
            vqe={"depth": 1},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
    )
    res = runner(ctx)
    assert res.angles.shape == (4,)


def test_run_variational_stage_builtin_vqe_zero_init() -> None:
    qh = _tiny_qh()
    ctx = VariationalRunContext(
        cfg=_minimal_cfg(
            algorithm="vqe",
            vqe={"depth": 1, "maxiter": 1, "initial_parameters_strategy": "zeros"},
            pauli={"use_protocol": False},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
    )
    st = run_variational_stage(ctx)
    assert "nfev" in st.algo_meta


def test_run_variational_stage_uccsd_branch() -> None:
    from qchem_stack.chem.fermion import FermionSpace

    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
    qh = QubitHamiltonian(
        operator=op,
        n_qubits=4,
        fermion_space=FermionSpace(n_spin_orbitals=4, n_electrons=2),
        meta={"fermion_to_qubit_map": "jordan_wigner"},
    )
    ctx = VariationalRunContext(
        cfg=_minimal_cfg(
            algorithm="vqe",
            variational={"ansatz": "uccsd"},
            vqe={"maxiter": 3},
            pauli={"use_protocol": False},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
    )
    st = run_variational_stage(ctx)
    assert st.algo_meta.get("algorithm") == "vqe"
    assert st.algo_meta.get("vqe_meta", {}).get("variational_ansatz") == "uccsd"


def test_algorithm_registry_synced_with_variational_builtins() -> None:
    from qchem_stack.quantum.algorithm_registry import ALGORITHM_REGISTRY
    from qchem_stack.quantum.variational_plugins.registry import is_registered_variational_id

    for pid in ("vqe", "adapt", "iqeb", "tetris_adapt"):
        assert is_registered_variational_id(pid)
        assert pid in ALGORITHM_REGISTRY
        assert ALGORITHM_REGISTRY[pid].factory is not None
    assert ALGORITHM_REGISTRY["vqe"].result_schema == "algorithm_vqe_report_v1"


def test_variational_context_prefers_pre_quantum_input_hamiltonian() -> None:
    qh_fallback = _tiny_qh()
    pqi = _tiny_pre_quantum_input(n_qubits=3)
    ctx = VariationalRunContext(
        cfg=_minimal_cfg(
            algorithm="custom_echo",
            algorithm_factory=(
                "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
            ),
            vqe={"depth": 1},
        ),
        hamiltonian=qh_fallback,
        executor=StatevectorHeaExecutor(),
        seed=0,
        pre_quantum_input=pqi,
    )
    out = run_echo_variational(ctx)
    assert out.angles.shape == (6,)


def test_variational_context_falls_back_without_pre_quantum_input() -> None:
    qh = _tiny_qh()
    ctx = VariationalRunContext(
        cfg=_minimal_cfg(
            algorithm="custom_echo",
            algorithm_factory=(
                "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
            ),
            vqe={"depth": 1},
        ),
        hamiltonian=qh,
        executor=StatevectorHeaExecutor(),
        seed=0,
        pre_quantum_input=None,
    )
    out = run_echo_variational(ctx)
    assert out.angles.shape == (4,)
