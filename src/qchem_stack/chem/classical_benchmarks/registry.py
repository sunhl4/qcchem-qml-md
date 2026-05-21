"""Resolve ``classical_benchmark_backend`` and dispatch to a runner."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.classical_benchmarks import pyscf_backend, stub_backend

if TYPE_CHECKING:
    from qchem_stack.chem.classical_benchmarks.context import ClassicalBenchmarkContext
    from qchem_stack.config import ExperimentConfig


def resolve_backend_id(
    cfg: ExperimentConfig | None,
    ctx: ClassicalBenchmarkContext,
    force_backend_id: str | None,
) -> str:
    if force_backend_id:
        return force_backend_id
    chosen = "auto"
    if cfg is not None:
        chosen = cfg.chemistry_extended.benchmarks.backend
    if chosen != "auto":
        return chosen
    ref = ctx.mean_field_reference
    tag = ref.backend_tag() if ref is not None else ""
    if tag == "pyscf":
        return "pyscf"
    return "stub"


def run_classical_post_hf_benchmarks(
    cfg: ExperimentConfig | None,
    ctx: ClassicalBenchmarkContext,
    *,
    force_backend_id: str | None = None,
) -> dict[str, Any]:
    """Run HF/MP2/CCSD/CASCI-style classical benchmarks via the configured backend."""
    bid = resolve_backend_id(cfg, ctx, force_backend_id)
    ref = ctx.mean_field_reference
    if bid == "pyscf":
        if ref is None or ref.backend_tag() != "pyscf":
            return stub_backend.run_missing_pyscf_upstream(ctx)
        return pyscf_backend.run_classical_post_hf_pyscf(ctx)
    if bid == "psi4":
        return stub_backend.run_psi4_placeholder(ctx)
    return stub_backend.run_auto_stub(ctx)
