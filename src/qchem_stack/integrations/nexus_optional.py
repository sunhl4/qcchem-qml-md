"""
**qnexus** (Nexus client) install probe — no API keys, no network in CI.

Business flows (project, compile artifact upload, HQC) stay in user applications;
this module only answers: is the client importable, and which version string is reported.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import NEXUS_PUBLIC_WORKFLOW_BLUEPRINT_V1, QNEXUS_PROBE_V1


def probe_qnexus_installation() -> dict[str, Any]:
    """
    Return import health for optional ``qnexus`` (PyPI).

    Never raises: failures are encoded in ``available=False``.
    """
    try:
        import qnexus as qnx  # type: ignore[import-not-found]
    except ImportError as e:
        return {
            "schema": QNEXUS_PROBE_V1,
            "available": False,
            "package": "qnexus",
            "error": str(e)[:400],
        }
    ver = getattr(qnx, "__version__", None)
    out: dict[str, Any] = {
        "schema": QNEXUS_PROBE_V1,
        "available": True,
        "package": "qnexus",
        "version": str(ver) if ver is not None else "unknown",
    }
    # Optional submodules (API surface moves with release train).
    for attr in ("use_client", "client", "get_project"):
        out[f"has_{attr}"] = hasattr(qnx, attr)
    return out


def nexus_public_workflow_blueprint() -> dict[str, Any]:
    """
    Stages inferred from public Nexus / qnexus documentation (no private API contract).

    Use for Methods diagrams; actual calls live in user code with credentials.
    """
    return {
        "schema": NEXUS_PUBLIC_WORKFLOW_BLUEPRINT_V1,
        "stages": [
            {"id": "auth", "description": "API key / workspace session (qnexus / portal)"},
            {"id": "project_context", "description": "Select project + versioning context"},
            {
                "id": "compile_upload",
                "description": "Logical circuit + pass bundle → compiled artifact",
            },
            {"id": "job_submit", "description": "Queue job on target (simulator / H-series)"},
            {"id": "poll", "description": "Retrieve status + resource usage"},
            {
                "id": "result_fetch",
                "description": "Counts / expectation estimates → local repro ledger",
            },
        ],
        "open_stack_analog_rows": [
            "qchem_stack.jobs.nexus_cloud (http/mock probe)",
            "qchem_stack.jobs.nexus_analog (HQC unit ledger)",
            "parity_snapshot.qnexus_probe (client import health)",
        ],
    }
