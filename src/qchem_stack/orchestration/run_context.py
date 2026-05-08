"""Distributed-tracing-friendly run context and wall-clock stage profiling for the pipeline."""

from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True)
class RunContext:
    """Correlates a pipeline execution with an HTTP gateway or batch scheduler."""

    trace_id: str
    client_request_id: str | None = None

    SCHEMA: ClassVar[str] = "run_context_v1"

    @classmethod
    def new(cls, *, client_request_id: str | None = None) -> RunContext:
        return cls(trace_id=str(uuid.uuid4()), client_request_id=client_request_id)

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> RunContext:
        """Best-effort: W3C ``traceparent``, then ``X-Trace-ID``, else new UUID.

        ``X-Request-ID`` maps to ``client_request_id`` (optional). Keys are matched
        case-insensitively after lowercasing.
        """
        low = {str(k).lower(): str(v) for k, v in headers.items()}
        rid = low.get("x-request-id")
        tid_hdr = (low.get("x-trace-id") or "").strip() or None
        trace_id: str | None = None
        tp = low.get("traceparent")
        if tp:
            parts = [p for p in str(tp).strip().split("-") if p != ""]
            if len(parts) >= 2 and len(parts[1]) == 32:
                cand = parts[1].lower()
                if all(c in "0123456789abcdef" for c in cand):
                    trace_id = cand
        if trace_id is None and tid_hdr:
            trace_id = tid_hdr
        if trace_id is None:
            return cls.new(client_request_id=rid)
        return cls(trace_id=trace_id, client_request_id=rid)

    def to_repro_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schema": self.SCHEMA,
            "trace_id": self.trace_id,
        }
        if self.client_request_id is not None:
            d["client_request_id"] = self.client_request_id
        return d


class PipelineStageTimer:
    """Monotonic wall intervals between ``mark`` calls (milliseconds)."""

    def __init__(self) -> None:
        self._t0 = time.perf_counter()
        self._last = self._t0
        self._stages: list[dict[str, Any]] = []

    def mark(self, stage: str) -> None:
        now = time.perf_counter()
        duration_ms = (now - self._last) * 1000.0
        self._stages.append({"stage": stage, "duration_ms": round(float(duration_ms), 3)})
        self._last = now

    def to_profile_dict(self) -> dict[str, Any]:
        total_ms = (self._last - self._t0) * 1000.0
        return {
            "schema": "pipeline_profile_v1",
            "stages": list(self._stages),
            "total_wall_ms": round(float(total_ms), 3),
        }

    def slowest(self) -> tuple[str | None, float]:
        if not self._stages:
            return None, 0.0
        row = max(self._stages, key=lambda r: float(r["duration_ms"]))
        return str(row["stage"]), float(row["duration_ms"])
