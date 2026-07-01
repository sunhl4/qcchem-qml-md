"""Publish/subscribe event bus for pipeline stage communication."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from qchem_stack.orchestration.pipeline_event_dispatch import dispatch_event_handlers

if TYPE_CHECKING:
    from collections.abc import Callable
from qchem_stack.orchestration.pipeline_event_types import (
    EventHandler,
    EventPriority,
    HandlerRegistration,
    PipelineEvent,
)


class EventBus:
    """Publish/subscribe event bus for pipeline stage communication."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[HandlerRegistration]] = defaultdict(list)
        self._wildcard_handlers: dict[str, list[HandlerRegistration]] = defaultdict(list)
        self._event_history: list[PipelineEvent] = []
        self._max_history: int = 1000

    def on(
        self,
        event_name: str,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
    ) -> Callable[[EventHandler], EventHandler]:
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
        registration = HandlerRegistration(handler=handler, priority=priority, once=once)
        if "*" in event_name:
            self._wildcard_handlers[event_name].append(registration)
            self._wildcard_handlers[event_name].sort(key=lambda r: r.priority.value)
        else:
            self._handlers[event_name].append(registration)
            self._handlers[event_name].sort(key=lambda r: r.priority.value)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        if event_name in self._handlers:
            self._handlers[event_name] = [
                reg for reg in self._handlers[event_name] if reg.handler != handler
            ]
        if event_name in self._wildcard_handlers:
            self._wildcard_handlers[event_name] = [
                reg for reg in self._wildcard_handlers[event_name] if reg.handler != handler
            ]

    def emit(self, event: PipelineEvent) -> None:
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        handlers_to_execute: list[HandlerRegistration] = []
        if event.name in self._handlers:
            handlers_to_execute.extend(self._handlers[event.name])
        for pattern, registrations in self._wildcard_handlers.items():
            if self._matches_wildcard(event.name, pattern):
                handlers_to_execute.extend(registrations)
        handlers_to_execute.sort(key=lambda r: r.priority.value)

        handlers_to_remove = dispatch_event_handlers(
            event,
            handlers_to_execute,
            wildcard_patterns=list(self._wildcard_handlers.keys()),
        )

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
        if "*" not in pattern:
            return event_name == pattern
        pattern_parts = pattern.split("*")
        if pattern_parts[0]:
            prefix = pattern_parts[0].rstrip(".")
            if not event_name.startswith(prefix):
                return False
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
        if event_name is None:
            events = self._event_history
        elif "*" in event_name:
            events = [e for e in self._event_history if self._matches_wildcard(e.name, event_name)]
        else:
            events = [e for e in self._event_history if e.name == event_name]
        if limit is not None:
            events = events[-limit:]
        return events

    def clear_history(self) -> None:
        self._event_history.clear()
