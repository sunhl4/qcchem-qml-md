"""RunContext helpers without chemistry (trace headers)."""

from __future__ import annotations

import uuid

from qchem_stack.orchestration.run_context import RunContext


def test_from_headers_traceparent_sets_trace_id() -> None:
    tid = "a" * 32
    headers = {
        "traceparent": f"00-{tid}-b709e3e139b531b3-01",
        "X-Request-ID": "req-1",
    }
    rc = RunContext.from_headers(headers)
    assert rc.trace_id == tid
    assert rc.client_request_id == "req-1"


def test_from_headers_x_trace_id_without_traceparent() -> None:
    rc = RunContext.from_headers({"X-Trace-ID": "upstream-trace", "X-Request-ID": "r2"})
    assert rc.trace_id == "upstream-trace"
    assert rc.client_request_id == "r2"


def test_from_headers_new_uuid_when_no_trace() -> None:
    rc = RunContext.from_headers({"X-Request-ID": "only-req"})
    uuid.UUID(rc.trace_id)
    assert rc.client_request_id == "only-req"


def test_from_headers_invalid_traceparent_falls_back_to_new_uuid() -> None:
    rc = RunContext.from_headers({"traceparent": "garbage"})
    uuid.UUID(rc.trace_id)
