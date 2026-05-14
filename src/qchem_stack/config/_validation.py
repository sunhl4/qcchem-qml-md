"""Reusable validators for config schema normalization."""

from __future__ import annotations


def strip_optional_text(value: str | None) -> str | None:
    """Normalize optional text fields; blank strings become ``None``."""
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def strip_required_text(value: str, *, field_name: str) -> str:
    """Normalize required text fields and reject blank values."""
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return normalized
