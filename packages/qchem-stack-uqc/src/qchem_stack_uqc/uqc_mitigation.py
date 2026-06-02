"""Optional post-shot energy mitigation for UQC cloud executors."""

from __future__ import annotations

from typing import Any

from qchem_stack.mitigation.zne import richardson_extrapolation, zne_scale_energy


def zne_config_from_meta(meta: dict[str, Any]) -> dict[str, Any] | None:
    """Return the ``uqc_mitigation.zne`` block when enabled."""
    return _zne_config(meta)


def _zne_config(meta: dict[str, Any]) -> dict[str, Any] | None:
    block = meta.get("uqc_mitigation")
    if not isinstance(block, dict):
        return None
    zne = block.get("zne")
    if not isinstance(zne, dict) or not zne.get("enabled"):
        return None
    return zne


def apply_uqc_zne_mitigation(
    raw_energy: float,
    meta: dict[str, Any],
    *,
    protocol_counts: dict[str, Any] | None = None,
) -> tuple[float, dict[str, Any] | None]:
    """Apply open-stack ZNE extrapolation to a scalar UQC energy estimate.

  Reads ``backend.meta.uqc_mitigation.zne``:

  .. code-block:: yaml

      meta:
        uqc_mitigation:
          zne:
            enabled: true
            scales: [1.0, 1.5, 2.0]
            mode: energy_stub   # default; circuit_scale_fold uses protocol_counts.zne_curve
    """
    zne = _zne_config(meta)
    if zne is None:
        return float(raw_energy), None

    scales = [float(x) for x in (zne.get("scales") or [1.0, 1.5, 2.0])]
    if not scales:
        return float(raw_energy), None

    mode = str(zne.get("mode") or "energy_stub")
    pc = protocol_counts or {}
    zcurve = pc.get("zne_curve")
    use_protocol_curve = (
        mode == "circuit_scale_fold"
        and isinstance(zcurve, list)
        and len(zcurve) == len(scales)
    )
    if use_protocol_curve and zcurve is not None:
        curve = [float(x) for x in zcurve]
        ex_opt = pc.get("zne_extrapolated_energy")
        extrapolated = (
            float(ex_opt) if ex_opt is not None else richardson_extrapolation(curve, scales)
        )
    else:
        e = float(raw_energy)
        curve = [zne_scale_energy(e, s) for s in scales]
        extrapolated = richardson_extrapolation(curve, scales, order=min(1, len(scales) - 1))

    trace = {
        "schema": "uqc_mitigation_zne_v1",
        "raw_energy": float(raw_energy),
        "zne_scales": scales,
        "zne_energies": curve,
        "zne_extrapolated_energy": extrapolated,
        "zne_extrapolation": "richardson",
        "zne_mode": mode,
    }
    return float(extrapolated), trace


__all__ = ["apply_uqc_zne_mitigation", "zne_config_from_meta"]
