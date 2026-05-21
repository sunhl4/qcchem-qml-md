"""Small shared helpers for cross-section experiment validation."""

from __future__ import annotations


def scf_driver_id(driver: str) -> str:
    """Normalized ``scf.driver`` token for capability gates."""
    return str(driver).strip().lower()
