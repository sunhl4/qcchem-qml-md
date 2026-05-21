"""
Optional **Nexus / Quantinuum cloud** HTTP adapter (no secrets in YAML; no vendor SLA).

Real jobs require a reachable API, API keys in the environment, and a support contract.
This module records **typed** sidecar rows for reproducibility and optional health probes.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import NEXUS_CLOUD_ADAPTER_V1

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig, NexusCloudSpec


def nexus_cloud_repro_sidecar(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """If ``nexus_cloud.mode`` is not ``off``, attach a machine-readable adapter row to runs."""
    cloud = cfg.nexus_cloud
    if cloud.mode == "off":
        return None
    if cloud.mode == "mock":
        return {
            "schema": NEXUS_CLOUD_ADAPTER_V1,
            "mode": "mock",
            "synthetic_job_id": "nexus-mock-00000000",
            "note": "No HTTP; set nexus_cloud.mode=http and base_url for a real endpoint.",
        }
    if cloud.mode == "http":
        return _http_probe(cloud)
    return {"schema": NEXUS_CLOUD_ADAPTER_V1, "error": f"unknown mode {cloud.mode!r}"}


def _http_probe(cloud: NexusCloudSpec) -> dict[str, Any]:
    if not (cloud.base_url or "").strip():
        return {
            "schema": NEXUS_CLOUD_ADAPTER_V1,
            "mode": "http",
            "ok": False,
            "error": "nexus_cloud.base_url is empty",
        }
    key = os.environ.get(cloud.api_key_env) or ""
    base = cloud.base_url.rstrip("/")
    # Minimal GET to base URL (vendors use varying paths; this is a connectivity stub only)
    url = f"{base}/" if not base.endswith("/") else base
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={**({"Authorization": f"Bearer {key}"} if key else {})},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=cloud.timeout_s) as r:  # noqa: S310
            code = r.getcode()
    except urllib.error.HTTPError as e:
        return {
            "schema": NEXUS_CLOUD_ADAPTER_V1,
            "mode": "http",
            "ok": False,
            "url": url,
            "http_status": e.code,
            "error": str(e)[:500],
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {
            "schema": NEXUS_CLOUD_ADAPTER_V1,
            "mode": "http",
            "ok": False,
            "url": url,
            "error": str(e)[:500],
            "note": "Expected to fail without a real Nexus/Quantinuum API endpoint and credentials.",
        }
    return {
        "schema": NEXUS_CLOUD_ADAPTER_V1,
        "mode": "http",
        "ok": True,
        "url": url,
        "http_status": code,
    }
