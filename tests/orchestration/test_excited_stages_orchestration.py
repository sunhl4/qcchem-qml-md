"""Orchestration-layer excited stages wiring (no PySCF)."""

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
from qchem_stack.orchestration.excited_stages import run_excited_stages

pytestmark = pytest.mark.l1_excited
from qchem_stack.orchestration.run_context import PipelineStageTimer
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext


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
    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
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


def test_run_excited_stages_forwards_pre_quantum_input(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _capture(ctx: ExcitedRunContext, out: dict | None = None) -> dict:
        captured["ctx"] = ctx
        return out if out is not None else {}

    monkeypatch.setattr(
        "qchem_stack.orchestration.excited_stages.run_excited_stages_from_context",
        _capture,
    )
    cfg = _minimal_cfg()
    qh = _tiny_qh()
    pqi = _tiny_pre_quantum_input(n_qubits=3)
    exe = StatevectorHeaExecutor()
    out: dict[str, object] = {}
    profile = PipelineStageTimer()
    emitted: list[str] = []

    run_excited_stages(
        cfg,
        qh=qh,
        exe=exe,
        angles=np.zeros(4, dtype=float),
        energy_pre=-1.0,
        out=out,
        profile=profile,
        emit=emitted.append,
        pre_quantum_input=pqi,
    )
    ctx = captured.get("ctx")
    assert isinstance(ctx, ExcitedRunContext)
    assert ctx.pre_quantum_input is pqi
    assert ctx.resolved_hamiltonian().n_qubits == 3
    assert "excited_stages" in emitted
