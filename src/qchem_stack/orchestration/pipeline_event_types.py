"""Event types for the pipeline publish/subscribe bus."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class EventPriority(Enum):
    """Event handler execution priority."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class PipelineEvent:
    """Represents an event emitted during pipeline execution."""

    name: str
    data: dict[str, object] = field(default_factory=dict)
    stage: str | None = None
    timestamp: float = field(default_factory=time.time)
    trace_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Event name cannot be empty")


class EventHandler(Protocol):
    """Protocol for event handler functions."""

    def __call__(self, event: PipelineEvent) -> None: ...


@dataclass
class HandlerRegistration:
    """Registration of an event handler (priority + optional once semantics)."""

    handler: EventHandler
    priority: EventPriority
    once: bool = False
