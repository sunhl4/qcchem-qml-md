"""Computable reference descriptors (shared by graph + list helpers)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComputableRef:
    """A single high-level computational target."""

    name: str
    kind: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ComputableSpec:
    """Typed twin of :class:`ComputableRef` for specs / rich workflow export."""

    name: str
    kind: str
    details: dict[str, object] = field(default_factory=dict)

    @staticmethod
    def from_ref(r: ComputableRef) -> ComputableSpec:
        return ComputableSpec(name=r.name, kind=r.kind, details=dict(r.details))

    def to_ref(self) -> ComputableRef:
        return ComputableRef(name=self.name, kind=self.kind, details=dict(self.details))
