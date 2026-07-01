"""Shared wrapper for ``importlib.metadata.entry_points`` (Python 3.9+ / 3.12 compat)."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points


def iter_entry_points(group: str) -> list[EntryPoint]:
    """Return sorted entry points for *group*, compatible with both legacy and modern APIs."""
    eps = entry_points()
    selected = (
        list(eps.select(group=group)) if hasattr(eps, "select") else list(eps.get(group, []))  # type: ignore[attr-defined]
    )
    return sorted(selected, key=lambda ep: (ep.name.strip().lower(), ep.value))
