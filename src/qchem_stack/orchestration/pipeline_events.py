"""Event-driven architecture for pipeline stage communication.

This module provides a publish/subscribe event system that decouples pipeline
stages, enabling:
- Custom stage insertion between existing stages
- Event hooks for observability (logging, metrics, tracing)
- Retry logic and error recovery at the event level
- Stage-level middleware (e.g., caching, validation)

Example usage:
    from qchem_stack.orchestration.pipeline_events import EventBus, PipelineEvent

    bus = EventBus()

    # Subscribe to an event
    @bus.on("stage.scf.completed")
    def handle_scf_completion(event: PipelineEvent):
        print(f"SCF completed with energy: {event.data['energy']}")

    # Publish an event
    bus.emit(PipelineEvent(
        name="stage.scf.completed",
        data={"energy": -1.137, "converged": True},
        stage="scf"
    ))
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

_logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event handler execution priority."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class PipelineEvent:
    """Represents an event emitted during pipeline execution.

    Attributes:
        name: Event identifier (e.g., "stage.scf.started", "stage.variational.completed")
        data: Event payload containing stage-specific information
        stage: Pipeline stage that emitted the event
        timestamp: Unix timestamp when event was created
        trace_id: Optional trace ID for distributed tracing
        metadata: Optional metadata (e.g., performance metrics, tags)
    """

    name: str
    data: dict[str, Any] = field(default_factory=dict)
    stage: str | None = None
    timestamp: float = field(default_factory=time.time)
    trace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate event structure."""
        if not self.name:
            raise ValueError("Event name cannot be empty")


class EventHandler(Protocol):
    """Protocol for event handler functions."""

    def __call__(self, event: PipelineEvent) -> None: ...


@dataclass
class _HandlerRegistration:
    """Internal registration of an event handler."""

    handler: EventHandler
    priority: EventPriority
    once: bool = False


class EventBus:
    """Publish/subscribe event bus for pipeline stage communication.

    The EventBus enables loose coupling between pipeline stages by allowing
    stages to emit events and other components to subscribe to those events
    without direct dependencies.

    Example:
        bus = EventBus()

        # Subscribe to all SCF events
        @bus.on("stage.scf.*")
        def log_scf_events(event: PipelineEvent):
            print(f"SCF event: {event.name}")

        # Subscribe to a specific event with high priority
        @bus.on("stage.variational.completed", priority=EventPriority.HIGH)
        def validate_variational_result(event: PipelineEvent):
            if event.data["energy"] > 0:
                raise ValueError("Variational energy should be negative")
    """

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._handlers: dict[str, list[_HandlerRegistration]] = defaultdict(list)
        self._wildcard_handlers: dict[str, list[_HandlerRegistration]] = defaultdict(list)
        self._event_history: list[PipelineEvent] = []
        self._max_history: int = 1000

    def on(
        self,
        event_name: str,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
    ) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register an event handler.

        Args:
            event_name: Event name to subscribe to. Supports wildcards (e.g., "stage.scf.*")
            priority: Handler execution priority (default: NORMAL)
            once: If True, handler is automatically removed after first invocation

        Returns:
            Decorator function

        Example:
            @bus.on("stage.scf.completed", priority=EventPriority.HIGH)
            def handle_scf_completion(event: PipelineEvent):
                print(f"SCF energy: {event.data['energy']}")
        """

        def decorator(func: EventHandler) -> EventHandler:
            self.subscribe(event_name, func, priority=priority, once=once)
            return func

        return decorator

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
    ) -> None:
        """Register an event handler.

        Args:
            event_name: Event name to subscribe to
            handler: Handler function to call when event is emitted
            priority: Handler execution priority
            once: If True, handler is removed after first invocation
        """
        registration = _HandlerRegistration(handler=handler, priority=priority, once=once)

        if "*" in event_name:
            # Wildcard subscription
            self._wildcard_handlers[event_name].append(registration)
            # Sort by priority
            self._wildcard_handlers[event_name].sort(key=lambda r: r.priority.value)
        else:
            # Exact match subscription
            self._handlers[event_name].append(registration)
            # Sort by priority
            self._handlers[event_name].sort(key=lambda r: r.priority.value)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove an event handler.

        Args:
            event_name: Event name to unsubscribe from
            handler: Handler function to remove
        """
        if event_name in self._handlers:
            self._handlers[event_name] = [
                reg for reg in self._handlers[event_name] if reg.handler != handler
            ]

        if event_name in self._wildcard_handlers:
            self._wildcard_handlers[event_name] = [
                reg for reg in self._wildcard_handlers[event_name] if reg.handler != handler
            ]

    def emit(self, event: PipelineEvent) -> None:
        """Emit an event to all subscribed handlers.

        Handlers are executed in priority order (CRITICAL first, LOW last).
        If a handler raises an exception, it is logged but does not prevent
        other handlers from executing.

        Args:
            event: Event to emit
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Collect all matching handlers
        handlers_to_execute: list[_HandlerRegistration] = []

        # Exact match handlers
        if event.name in self._handlers:
            handlers_to_execute.extend(self._handlers[event.name])

        # Wildcard match handlers
        for pattern, registrations in self._wildcard_handlers.items():
            if self._matches_wildcard(event.name, pattern):
                handlers_to_execute.extend(registrations)

        # Sort all handlers by priority
        handlers_to_execute.sort(key=lambda r: r.priority.value)

        # Execute handlers
        handlers_to_remove: list[tuple[str, _HandlerRegistration]] = []

        for registration in handlers_to_execute:
            try:
                registration.handler(event)
                if registration.once:
                    # Mark for removal
                    for pattern in [event.name, *self._wildcard_handlers.keys()]:
                        if pattern in self._handlers or pattern in self._wildcard_handlers:
                            handlers_to_remove.append((pattern, registration))
            except Exception as e:
                _logger.error(
                    f"Event handler failed for event '{event.name}': {e}",
                    exc_info=True,
                )

        # Remove one-time handlers
        for pattern, registration in handlers_to_remove:
            if pattern in self._handlers:
                self._handlers[pattern] = [
                    reg for reg in self._handlers[pattern] if reg != registration
                ]
            if pattern in self._wildcard_handlers:
                self._wildcard_handlers[pattern] = [
                    reg for reg in self._wildcard_handlers[pattern] if reg != registration
                ]

    def _matches_wildcard(self, event_name: str, pattern: str) -> bool:
        """Check if event name matches a wildcard pattern.

        Supports simple wildcard matching where '*' matches any sequence of characters.
        For example: "stage.scf.*" matches "stage.scf.started", "stage.scf.completed", etc.

        Args:
            event_name: Event name to check
            pattern: Wildcard pattern

        Returns:
            True if event name matches pattern
        """
        if "*" not in pattern:
            return event_name == pattern

        # Simple wildcard matching
        pattern_parts = pattern.split("*")

        # Check prefix
        if pattern_parts[0]:
            prefix = pattern_parts[0].rstrip(".")
            if not event_name.startswith(prefix):
                return False

        # Check suffix
        if pattern_parts[-1]:
            suffix = pattern_parts[-1].lstrip(".")
            if not event_name.endswith(suffix):
                return False

        return True

    def get_history(
        self,
        event_name: str | None = None,
        limit: int | None = None,
    ) -> list[PipelineEvent]:
        """Get event history.

        Args:
            event_name: Optional filter by event name (supports wildcards)
            limit: Maximum number of events to return

        Returns:
            List of events matching the filter
        """
        if event_name is None:
            events = self._event_history
        else:
            if "*" in event_name:
                events = [
                    e for e in self._event_history if self._matches_wildcard(e.name, event_name)
                ]
            else:
                events = [e for e in self._event_history if e.name == event_name]

        if limit is not None:
            events = events[-limit:]

        return events

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()


# Pipeline stage event names
class PipelineEvents:
    """Standard event names for pipeline stages.

    Each stage emits two events:
    - stage.<name>.started: Emitted when stage begins execution
    - stage.<name>.completed: Emitted when stage completes successfully

    Additional events may be emitted for errors, warnings, or intermediate progress.
    """

    # SCF stage
    SCF_STARTED = "stage.scf.started"
    SCF_COMPLETED = "stage.scf.completed"
    SCF_FAILED = "stage.scf.failed"

    # Pre-quantum stage
    PRE_QUANTUM_STARTED = "stage.pre_quantum.started"
    PRE_QUANTUM_COMPLETED = "stage.pre_quantum.completed"
    PRE_QUANTUM_FAILED = "stage.pre_quantum.failed"

    # Variational stage
    VARIATIONAL_STARTED = "stage.variational.started"
    VARIATIONAL_ITERATION = "stage.variational.iteration"
    VARIATIONAL_COMPLETED = "stage.variational.completed"
    VARIATIONAL_FAILED = "stage.variational.failed"

    # Embedding workflow stage
    EMBEDDING_WORKFLOW_STARTED = "stage.embedding_workflow.started"
    EMBEDDING_WORKFLOW_COMPLETED = "stage.embedding_workflow.completed"
    EMBEDDING_WORKFLOW_FAILED = "stage.embedding_workflow.failed"

    # Excited states stage
    EXCITED_STARTED = "stage.excited.started"
    EXCITED_COMPLETED = "stage.excited.completed"
    EXCITED_FAILED = "stage.excited.failed"

    # Protocol finalize stage
    PROTOCOL_FINALIZE_STARTED = "stage.protocol_finalize.started"
    PROTOCOL_FINALIZE_COMPLETED = "stage.protocol_finalize.completed"
    PROTOCOL_FINALIZE_FAILED = "stage.protocol_finalize.failed"

    # Pipeline-level events
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_FAILED = "pipeline.failed"


# Global event bus instance
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    Returns:
        Global EventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (mainly for testing)."""
    global _global_event_bus
    _global_event_bus = None


def emit_pipeline_event(
    event_name: str,
    data: dict[str, Any] | None = None,
    stage: str | None = None,
    trace_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Convenience function to emit a pipeline event.

    Args:
        event_name: Event name
        data: Event data payload
        stage: Pipeline stage name
        trace_id: Optional trace ID
        metadata: Optional metadata
    """
    bus = get_event_bus()
    event = PipelineEvent(
        name=event_name,
        data=data or {},
        stage=stage,
        trace_id=trace_id,
        metadata=metadata or {},
    )
    bus.emit(event)
