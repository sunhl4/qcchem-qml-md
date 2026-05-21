from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import CLASSICAL_BENCHMARK_SUMMARY_V1


def classical_benchmark_summary(cb: dict[str, Any]) -> dict[str, Any]:
    """Compact Methods-friendly digest for ``classical_benchmarks``."""
    rows: dict[str, dict[str, Any]] = {}
    for method_key in ("hf", "mp2", "ccsd", "casci"):
        v = cb.get(method_key)
        if isinstance(v, dict):
            rows[method_key] = v
    ok_vals: dict[str, float] = {}
    for k, row in rows.items():
        if row.get("status") == "ok" and row.get("value") is not None:
            ok_vals[k] = float(row["value"])
    hf = ok_vals.get("hf")
    best_method: str | None = None
    best_energy: float | None = None
    if ok_vals:
        best_method = min(ok_vals, key=lambda k: ok_vals[k])
        best_energy = float(ok_vals[best_method])
    deltas_vs_hf: dict[str, float] = {}
    if hf is not None:
        for k, v in ok_vals.items():
            if k == "hf":
                continue
            deltas_vs_hf[k] = float(v - hf)
    recommended_baseline_method: str | None = None
    for preferred in ("ccsd", "mp2", "hf"):
        if preferred in ok_vals:
            recommended_baseline_method = preferred
            break
    recommended_baseline_energy: float | None = (
        float(ok_vals[recommended_baseline_method])
        if recommended_baseline_method is not None
        else None
    )
    return {
        "schema": CLASSICAL_BENCHMARK_SUMMARY_V1,
        "recommended_baseline_policy": "prefer_ccsd_else_mp2_else_hf",
        "recommended_baseline_method": recommended_baseline_method,
        "recommended_baseline_energy_au": recommended_baseline_energy,
        "methods_reported": sorted(rows.keys()),
        "methods_ok": sorted(ok_vals.keys()),
        "methods_non_ok": sorted(k for k in rows if k not in ok_vals),
        "reference_hf_energy_au": hf,
        "best_method": best_method,
        "best_energy_au": best_energy,
        "delta_best_vs_hf_au": (
            float(best_energy - hf) if (best_energy is not None and hf is not None) else None
        ),
        "method_deltas_vs_hf_au": deltas_vs_hf,
    }
