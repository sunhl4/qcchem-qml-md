"""Shared AO / Löwdin embedding-input payloads for classical solvers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta
from qchem_stack.chem.bridges.lowdin import LowdinTensors, build_lowdin_tensors
from qchem_stack.contracts.schema_ids import EMBEDDING_INPUT_SYSTEM_V1

if TYPE_CHECKING:
    from collections.abc import Mapping


def build_ao_embedding_payload(
    *,
    e_tot: float,
    driver_meta: Mapping[str, Any],
    ao_reference_kind: str,
    epistemic_bound: str,
) -> dict[str, Any]:
    meta = fork_driver_meta(driver_meta)
    meta["integral_representation"] = "ao"
    meta["ao_reference_kind"] = ao_reference_kind
    if ao_reference_kind == "scf_object":
        meta["ao_run_hf"] = True
    return {
        "schema": EMBEDDING_INPUT_SYSTEM_V1,
        "representation": "ao",
        "has_run_hf": True,
        "e_tot": float(e_tot),
        "driver_meta": meta,
        "epistemic_bound": epistemic_bound,
    }


def build_lowdin_embedding_payload(
    *,
    overlap,
    hcore,
    rdm1_ao,
    energy_nuc: float,
    driver_meta: Mapping[str, Any],
    epistemic_bound: str,
    tensors: LowdinTensors | None = None,
) -> dict[str, Any]:
    lowdin = tensors or build_lowdin_tensors(overlap, hcore, rdm1_ao)
    meta = fork_driver_meta(driver_meta)
    meta["integral_representation"] = "lowdin_orth_ao"
    meta["lowdin_basis_transform"] = "s^-1/2"
    return {
        "schema": EMBEDDING_INPUT_SYSTEM_V1,
        "representation": "lowdin_orth_ao",
        "n_spatial_orbitals": int(lowdin.h1_low.shape[0]),
        "rdm1_trace": float(lowdin.dm_low.trace()),
        "constant": float(energy_nuc),
        "driver_meta": meta,
        "epistemic_bound": epistemic_bound,
    }
