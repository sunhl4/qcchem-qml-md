"""Distributed-tracing-friendly run context and wall-clock stage profiling for the pipeline."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from qchem_stack.contracts.schema_ids import PIPELINE_PROFILE_V1

if TYPE_CHECKING:
    from collections.abc import Mapping


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

    def to_repro_dict(self) -> dict[str, object]:
        d: dict[str, object] = {
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
        self._stages: list[dict[str, object]] = []
        self._trace_memory = os.getenv("QCHEM_PIPELINE_PROFILE_MEM", "").lower() in {
            "1",
            "true",
            "yes",
        }
        if self._trace_memory:
            import tracemalloc

            if not tracemalloc.is_tracing():
                tracemalloc.start()

    def mark(self, stage: str) -> None:
        peak_memory_kb: float | None = None
        if self._trace_memory:
            import tracemalloc

            _current, peak = tracemalloc.get_traced_memory()
            peak_memory_kb = round(float(peak) / 1024.0, 2)
        now = time.perf_counter()
        duration_ms = (now - self._last) * 1000.0
        row: dict[str, object] = {
            "stage": stage,
            "duration_ms": round(float(duration_ms), 3),
        }
        if peak_memory_kb is not None:
            row["peak_memory_kb"] = peak_memory_kb
        self._stages.append(row)
        self._last = now

    def to_profile_dict(self) -> dict[str, object]:
        total_ms = (self._last - self._t0) * 1000.0
        out: dict[str, object] = {
            "schema": PIPELINE_PROFILE_V1,
            "stages": list(self._stages),
            "total_wall_ms": round(float(total_ms), 3),
        }
        if self._trace_memory:
            out["memory_tracing_enabled"] = True
        return out

    def slowest(self) -> tuple[str | None, float]:
        if not self._stages:
            return None, 0.0
        rows = [
            (row, float(duration_ms))
            for row in self._stages
            if isinstance(duration_ms := row.get("duration_ms"), int | float)
        ]
        if not rows:
            return None, 0.0
        row, duration_ms = max(rows, key=lambda item: item[1])
        return str(row.get("stage")), duration_ms


def emit_pipeline_stage_json_log(stage: str, *, trace_id: str | None = None) -> None:
    """Emit one JSON line per stage when ``QCHEM_STACK_JSON_LOG=1``."""
    if os.getenv("QCHEM_STACK_JSON_LOG", "").lower() not in {"1", "true", "yes"}:
        return
    payload: dict[str, object] = {"event": "pipeline_stage", "stage": stage}
    if trace_id:
        payload["trace_id"] = trace_id
    logging.getLogger("qchem_stack.pipeline.json").info(json.dumps(payload, sort_keys=True))
