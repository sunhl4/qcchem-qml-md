"""Handler dispatch helpers for :mod:`pipeline_events`."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qchem_stack.orchestration.pipeline_event_types import HandlerRegistration, PipelineEvent

_logger = logging.getLogger(__name__)


def dispatch_event_handlers(
    event: PipelineEvent,
    handlers_to_execute: list[HandlerRegistration],
    *,
    wildcard_patterns: list[str],
) -> list[tuple[str, HandlerRegistration]]:
    """Run handlers in priority order; return one-shot registrations to remove."""
    handlers_to_remove: list[tuple[str, HandlerRegistration]] = []
    for registration in handlers_to_execute:
        try:
            registration.handler(event)
            if registration.once:
                for pattern in [event.name, *wildcard_patterns]:
                    handlers_to_remove.append((pattern, registration))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            _logger.error(
                "Event handler failed for event '%s': %s",
                event.name,
                e,
                exc_info=True,
            )
    return handlers_to_remove
