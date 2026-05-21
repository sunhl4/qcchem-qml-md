"""Former 'not scheduled' items: nexus analog, qermit report, tensornet stub, chemistry extended validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import (
    ActiveSpaceSpec,
    ChemistryExtendedSpec,
    ExperimentConfig,
    MitigationSpec,
    MoleculeSpec,
    NexusAnalogSpec,
    QuantumSpec,
)
from qchem_stack.jobs.nexus_analog import (
    default_nexus_analog_for_job_result,
    nexus_analog_billing_for_job_result,
    nexus_analog_ledger_from_rows,
    nexus_analog_ledger_from_spec,
)
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.tensornet import run_cutensornet_expectation_stub


def _cfg(**q) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="x",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(dict(q)),
    )


def test_nexus_ledger_disabled_is_none() -> None:
    cfg = _cfg()
    assert nexus_analog_ledger_from_rows([{"total_shots": 10, "depth": 2}], cfg) is None


def test_nexus_ledger_enabled() -> None:
    c = _cfg().model_copy(
        update={"nexus_analog": NexusAnalogSpec(enabled=True, project_label="p1")}
    )
    led = nexus_analog_ledger_from_rows([{"total_shots": 1000, "depth": 0}], c)
    assert led is not None
    assert led["schema"] == "nexus_analog_v1"
    assert led["project_label"] == "p1"
    assert led["hqc_units"] > 0


def test_nexus_billing_on_job_respects_nexus_spec() -> None:
    na = NexusAnalogSpec(
        enabled=True, project_label="jobproj", unit_per_shot=0.2, unit_per_circuit=1.0
    )
    rows = [{"total_shots": 10, "depth": 0}]
    led = nexus_analog_ledger_from_spec(rows, na)
    bill = nexus_analog_billing_for_job_result(rows, na)
    assert led == bill
    assert bill["project_label"] == "jobproj"
    assert bill != nexus_analog_billing_for_job_result(rows, None)


def test_default_job_billing() -> None:
    d = default_nexus_analog_for_job_result([{"total_shots": 1, "depth": 1}])
    assert d["schema"] == "nexus_analog_v1"
    assert "hqc_units" in d


def test_qermit_report_when_pmsv() -> None:
    c = _cfg()
    c = c.model_copy(
        update={
            "mitigation": c.mitigation.model_copy(
                update={
                    "pmsv": c.mitigation.pmsv.model_copy(
                        update={"enabled": True, "stabilizers": ["Z0 Z1"]}
                    )
                }
            )
        }
    )
    r = build_qermit_style_mitigation_report(c)
    assert r is not None
    assert r["schema"] == "qermit_analog_v2"
    assert len(r["nodes"]) >= 1
    assert "edges" in r and r["edges"]
    assert "topological_order" in r


def test_tensornet_stub() -> None:
    o = run_cutensornet_expectation_stub(4)
    assert o["status"] == "stub_no_contraction"
    o2 = run_cutensornet_expectation_stub(2, requested_backend="opt_einsum")
    assert o2.get("status") == "opt_einsum_demo_ok"
    assert "contraction_value" in o2
    o3 = run_cutensornet_expectation_stub(2, requested_backend="cuquantum_if_available")
    assert o3.get("status") in (
        "cuquantum_import_ok",
        "cuquantum_not_installed_fell_back_opt_einsum",
    )


def test_pbc_cell_singular_rejected() -> None:
    with pytest.raises(ValidationError):
        ExperimentConfig(
            schema_version="2",
            experiment_id="p",
            random_seed=0,
            molecule=MoleculeSpec(
                symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
            ),
            active_space=ActiveSpaceSpec.model_validate(
                {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
            ),
            chemistry_extended=ChemistryExtendedSpec(
                pbc={"cell_vectors_bohr": [[1.0, 0, 0], [2.0, 0, 0], [0, 0, 1.0]]}
            ),
        )


def test_pbc_mesh_invalid_rejected() -> None:
    with pytest.raises(ValidationError):
        ChemistryExtendedSpec(pbc={"kpoint_mesh": [0, 1, 1]})


def test_pbc_with_ddcosmo_allowed() -> None:
    s = ChemistryExtendedSpec(
        solvent={"model": "ddcosmo"},
        pbc={"cell_vectors_bohr": [[4.0, 0, 0], [0, 4.0, 0], [0, 0, 4.0]]},
    )
    assert s.solvent.model == "ddcosmo"


def test_mitigation_zne_scales_default() -> None:
    from qchem_stack.config import MitigationSpec

    m = MitigationSpec.model_validate({"zne": {"enabled": True}})
    assert len(m.zne.scales) >= 1


def test_qermit_runtime_trace() -> None:
    from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag

    c = _cfg()
    c = c.model_copy(
        update={
            "mitigation": MitigationSpec.model_validate(
                {
                    **c.mitigation.model_dump(mode="python"),
                    "pmsv": {"enabled": True, "stabilizers": ["Z0"]},
                    "zne": {"enabled": True},
                }
            )
        }
    )
    r = build_qermit_style_mitigation_report(c)
    ex = execute_mitigation_dag(1.0, 0.1, r, c)
    assert ex["schema"] == "qermit_runtime_v1"
    assert "trace" in ex and ex["trace"]


def test_nexus_cloud_mock_sidecar() -> None:
    from qchem_stack.config import NexusCloudSpec
    from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar

    c = _cfg()
    c = c.model_copy(update={"nexus_cloud": NexusCloudSpec(mode="mock")})
    x = nexus_cloud_repro_sidecar(c)
    assert x and x.get("mode") == "mock"
