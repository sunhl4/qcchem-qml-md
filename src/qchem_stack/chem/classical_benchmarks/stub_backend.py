"""Placeholder backends when post-HF suites are not wired for the upstream chemistry driver."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.classical_benchmarks.schema import CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1

if TYPE_CHECKING:
    from qchem_stack.chem.classical_benchmarks.context import ClassicalBenchmarkContext


def _na(reason: str) -> dict[str, Any]:
    return {"status": "unavailable", "value": None, "reason": reason}


def run_auto_stub(ctx: ClassicalBenchmarkContext) -> dict[str, Any]:
    """No executable post-HF runner for the resolved backend (e.g. auto + non-PySCF reference)."""
    ref = ctx.mean_field_reference
    detail = "classical_post_hf_auto_resolution_no_runner_v1"
    hf_block: dict[str, Any]
    if ref is not None:
        hf_block = {"status": "ok", "value": float(ref.e_tot), "reason": None}
    else:
        hf_block = _na("no_mean_field_reference_for_classical_benchmarks_v1")
    return {
        "schema": CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1,
        "backend_id": "stub",
        "reference_scf_method": ctx.reference_scf_method,
        "hf": hf_block,
        "mp2": _na(detail),
        "ccsd": _na(detail),
        "casci": _na(detail),
    }


def run_psi4_placeholder(ctx: ClassicalBenchmarkContext) -> dict[str, Any]:
    """Reserved PSI4-shaped hook; numerical MP2/CCSD/CASCI not implemented in-tree."""
    ref = ctx.mean_field_reference
    detail = "psi4_classical_post_hf_benchmarks_not_implemented_v1"
    hf_block: dict[str, Any]
    if ref is not None:
        hf_block = {"status": "ok", "value": float(ref.e_tot), "reason": None}
    else:
        hf_block = _na("no_mean_field_reference_for_classical_benchmarks_v1")
    return {
        "schema": CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1,
        "backend_id": "psi4",
        "reference_scf_method": ctx.reference_scf_method,
        "hf": hf_block,
        "mp2": _na(detail),
        "ccsd": _na(detail),
        "casci": _na(detail),
    }


def run_missing_pyscf_upstream(ctx: ClassicalBenchmarkContext) -> dict[str, Any]:
    """User or policy requested PySCF benchmarks but the reference is not tagged ``pyscf``."""
    ref = ctx.mean_field_reference
    detail = "classical_benchmark_backend=pyscf_requires_upstream_classical_software_tag_pyscf_v1"
    hf_block: dict[str, Any]
    if ref is not None:
        hf_block = {"status": "ok", "value": float(ref.e_tot), "reason": None}
    else:
        hf_block = _na("no_mean_field_reference_for_classical_benchmarks_v1")
    return {
        "schema": CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1,
        "backend_id": "stub",
        "reference_scf_method": ctx.reference_scf_method,
        "hf": hf_block,
        "mp2": _na(detail),
        "ccsd": _na(detail),
        "casci": _na(detail),
    }
