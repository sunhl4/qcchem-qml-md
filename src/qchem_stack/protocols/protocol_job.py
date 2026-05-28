"""Async job helpers and circuit resource rows for Pauli averaging protocols."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Any, cast

from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.spec import circuit_resource_row
from qchem_stack.jobs.nexus_analog import nexus_analog_billing_for_job_result
from qchem_stack.protocols.secure_serialization import secure_loads_protocol

if TYPE_CHECKING:
    from qchem_stack.jobs.store import SqliteJobStore
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def dataframe_circuit_shot_rows(proto: PauliAveragingProtocol) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    plan = proto._measurement_plan or build_measurement_plan(
        proto.hamiltonian, proto.n_qubits, grouping=proto.measurement_grouping
    )
    metas = plan.to_circuit_metas()
    eff = int(proto._counts.get("shots_per_circuit_effective", proto.backend.shots_per_circuit))
    zne_scales = proto.zne_scales or []
    if proto._counts.get("zne_mode") == "circuit_scale_fold" and zne_scales:
        for si, sf in enumerate(float(s) for s in zne_scales):
            shot_m = max(1, int(round(sf)))
            for i, c in enumerate(proto._compiled):
                extra: dict[str, Any] = {"zne_scale": sf, "zne_scale_index": si}
                if i < len(metas):
                    extra["pauli_group_id"] = metas[i].get("group_id")
                    extra["n_pauli_terms"] = metas[i].get("n_terms")
                    extra["synthesized"] = metas[i].get("synthesized")
                rows.append(
                    circuit_resource_row(
                        f"zne{si}_circ_{i}",
                        c,
                        shots=eff * shot_m,
                        backend=proto.backend,
                        extra=extra,
                    )
                )
        return rows
    for i, c in enumerate(proto._compiled):
        extra: dict[str, Any] = {}
        if i < len(metas):
            extra["pauli_group_id"] = metas[i].get("group_id")
            extra["n_pauli_terms"] = metas[i].get("n_terms")
            extra["synthesized"] = metas[i].get("synthesized")
        rows.append(
            circuit_resource_row(
                f"circ_{i}",
                c,
                shots=eff,
                backend=proto.backend,
                extra=cast("dict[str, Any] | None", extra or None),
            )
        )
    return rows


def process_pauli_protocol_job(store: SqliteJobStore, job_id: str) -> None:
    con = sqlite3.connect(store.path)
    row = con.execute("SELECT payload FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    con.close()
    if row is None:
        raise KeyError(job_id)
    proto: PauliAveragingProtocol = secure_loads_protocol(row[0])
    proto.compile()
    proto.run()
    val = proto.evaluate()
    rows = dataframe_circuit_shot_rows(proto)
    stderr = proto._counts.get("energy_stderr")
    res: dict[str, Any] = {
        "expectation": val,
        "rows": rows,
        "energy_stderr": stderr,
        "total_shots_budget": proto._counts.get("total_shots_budget"),
        "n_measurement_circuits": proto._counts.get("n_measurement_circuits"),
        "shots_per_circuit_effective": proto._counts.get("shots_per_circuit_effective"),
        "nexus_analog_billing": nexus_analog_billing_for_job_result(rows, proto.nexus_analog),
    }
    store.complete(job_id, res)
