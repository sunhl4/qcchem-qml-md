"""Named backend profiles for multi-backend experiment selection (UQC cloud, mock, simulators)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig

ProviderId = Literal[
    "statevector",
    "qiskit",
    "ionstack",
    "uqc",
    "qulacs",
    "cirq",
    "braket",
]


@dataclass(frozen=True)
class BackendProfile:
    """Preset mapping from a short id to ``ExperimentConfig.backend`` fields."""

    profile_id: str
    provider: ProviderId
    name: str
    description: str
    uqc_mode: Literal["real", "mock"] | None = None
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    meta: dict[str, Any] | None = None


BACKEND_PROFILES: dict[str, BackendProfile] = {
    "uqc_cloud": BackendProfile(
        profile_id="uqc_cloud",
        provider="uqc",
        name="uqc_ion_trap_cloud_sim",
        description="幺正 UQC 内网云 iontrap-sim（需 UQC_API_TOKEN + SERVER_HOST）",
        uqc_mode="real",
        meta={
            "uqc_mode": "real",
            "uqc_target": "iontrap-sim",
            "uqc_allow_fallback": False,
            "uqc_timeout_s": 600.0,
            "uqc_poll_interval_s": 2.0,
        },
    ),
    "uqc_mock": BackendProfile(
        profile_id="uqc_mock",
        provider="uqc",
        name="uqc_ion_trap_mock",
        description="UQC 协议栈 + 本地 statevector mock（CI / 无 token）",
        uqc_mode="mock",
        meta={"uqc_mode": "mock", "uqc_target": "iontrap-sim"},
    ),
    "statevector": BackendProfile(
        profile_id="statevector",
        provider="statevector",
        name="statevector_sim",
        description="本地 numpy statevector HEA（最快调试）",
    ),
    "qiskit_statevector": BackendProfile(
        profile_id="qiskit_statevector",
        provider="qiskit",
        name="qiskit_aer_statevector",
        description="Qiskit Aer statevector",
        qiskit_mode="statevector",
        meta={"qiskit_shots_backend": "aer"},
    ),
    "qiskit_estimator": BackendProfile(
        profile_id="qiskit_estimator",
        provider="qiskit",
        name="qiskit_estimator",
        description="Qiskit Estimator 路径",
        qiskit_mode="estimator",
    ),
    "qulacs": BackendProfile(
        profile_id="qulacs",
        provider="qulacs",
        name="qulacs_statevector",
        description="Qulacs statevector 模拟",
    ),
    "cirq": BackendProfile(
        profile_id="cirq",
        provider="cirq",
        name="cirq_simulator",
        description="Google Cirq Simulator",
    ),
    "braket": BackendProfile(
        profile_id="braket",
        provider="braket",
        name="braket_local_sv",
        description="Amazon Braket local statevector",
    ),
    "ionstack": BackendProfile(
        profile_id="ionstack",
        provider="ionstack",
        name="ionstack_default",
        description="IonStack HTTP 适配（需 ionstack_endpoint）",
    ),
}


def list_backend_profile_ids() -> list[str]:
    return sorted(BACKEND_PROFILES.keys())


def get_backend_profile(profile_id: str) -> BackendProfile:
    key = str(profile_id).strip().lower().replace("-", "_")
    prof = BACKEND_PROFILES.get(key)
    if prof is None:
        raise ValueError(
            f"Unknown backend profile {profile_id!r}; choose from {list_backend_profile_ids()}"
        )
    return prof


def apply_backend_profile_immutable(
    cfg: ExperimentConfig, profile_id: str
) -> tuple[ExperimentConfig, BackendProfile]:
    """Return a new config with backend fields updated to match ``profile_id``.

    Apply a named backend profile and return an updated config copy.
    Instead of mutating the config in place, it returns a new config object
    using Pydantic's ``model_copy(update=...)`` pattern.

    Args:
        cfg: Original experiment configuration (not mutated).
        profile_id: Backend profile identifier (e.g., "uqc_cloud", "statevector").

    Returns:
        Tuple of (new_config, profile) where new_config is a copy with updated
        backend fields and profile is the applied BackendProfile object.

    Example:
        >>> cfg, profile = apply_backend_profile_immutable(cfg, "uqc_mock")
        >>> assert cfg.backend.provider == "uqc"
        >>> assert profile.profile_id == "uqc_mock"
    """
    prof = get_backend_profile(profile_id)

    # Build update dict for backend fields
    backend_updates: dict[str, Any] = {
        "name": prof.name,
        "provider": prof.provider,
        "qiskit_mode": prof.qiskit_mode,
    }

    # Handle UQC-specific fields
    if prof.uqc_mode is not None:
        backend_updates["uqc_mode"] = prof.uqc_mode
        meta = dict(cfg.backend.meta)
        meta["uqc_mode"] = prof.uqc_mode
        if prof.meta:
            meta.update(prof.meta)
        backend_updates["meta"] = meta
    elif prof.meta:
        meta = dict(cfg.backend.meta)
        meta.update(prof.meta)
        backend_updates["meta"] = meta

    # Create new backend config using Pydantic model_copy
    new_backend = cfg.backend.model_copy(update=backend_updates)

    # Create new experiment config with updated backend
    new_cfg = cfg.model_copy(update={"backend": new_backend})

    return new_cfg, prof


def backend_profile_catalog_v1() -> dict[str, Any]:
    """Machine-readable profile list for docs / parity export."""
    return {
        "schema": "backend_profile_catalog_v1",
        "profiles": [
            {
                "profile_id": p.profile_id,
                "provider": p.provider,
                "name": p.name,
                "description": p.description,
                "uqc_mode": p.uqc_mode,
                "qiskit_mode": p.qiskit_mode,
            }
            for p in BACKEND_PROFILES.values()
        ],
    }
