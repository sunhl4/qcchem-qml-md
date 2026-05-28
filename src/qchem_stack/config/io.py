"""YAML I/O and runtime adapter conversion helpers for experiment configs.

User-facing overview (plain language): ``docs/说明_实验配置加载_io.md``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from qchem_stack.exceptions import ConfigurationError

from .experiment import ExperimentConfig

if TYPE_CHECKING:
    from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle


def load_experiment_config(
    path: str | Path,
    *,
    strict_top_level_keys: bool = False,
) -> ExperimentConfig:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Experiment config file not found: {p}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Could not read experiment config file {p}: {exc}") from exc
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {p}: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise ConfigurationError(f"Config must be a mapping: {p}")
    return ExperimentConfig.from_yaml_dict(
        raw,
        geometry_files_base_dir=p.parent,
        strict_top_level_keys=strict_top_level_keys,
    )


def _strip_callables(obj: object) -> object:
    """YAML repro dump must not embed runtime callables (e.g. IonStack ``expectation_fn`` tests)."""
    if isinstance(obj, dict):
        return {str(k): _strip_callables(v) for k, v in obj.items() if not callable(v)}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_strip_callables(v) for v in obj if not callable(v))
    return obj


def dump_experiment_config(cfg: ExperimentConfig) -> str:
    raw = _strip_callables(cfg.model_dump(mode="json"))
    return yaml.safe_dump(raw, sort_keys=False, allow_unicode=True)


def backend_spec_from_config(cfg: ExperimentConfig) -> BackendSpec:
    from qchem_stack.backends.spec import BackendSpec

    b = cfg.backend
    meta = dict(b.meta)
    uqc_kwargs: dict[str, object] = {}
    if b.provider == "uqc":
        uqc_kwargs["uqc_token"] = b.uqc_token
        uqc_kwargs["uqc_backend_name"] = b.uqc_backend_name
        uqc_kwargs["uqc_mode"] = b.uqc_mode
        uqc_kwargs["uqc_transpile_opt_level"] = b.uqc_transpile_opt_level
        meta.setdefault("uqc_token", b.uqc_token)
        meta.setdefault("uqc_backend_name", b.uqc_backend_name)
        meta.setdefault("uqc_mode", b.uqc_mode)
        meta.setdefault("uqc_transpile_opt_level", b.uqc_transpile_opt_level)
    return BackendSpec(
        name=b.name,
        provider=b.provider,
        shots_per_circuit=b.shots_per_circuit,
        target_energy_stderr=b.target_energy_stderr,
        qiskit_mode=b.qiskit_mode,
        ionstack_endpoint=b.ionstack_endpoint,
        native_twoq=cfg.compiler.native_twoq,
        meta=meta,
        **uqc_kwargs,
    )


def compiler_pass_bundle_from_config(cfg: ExperimentConfig) -> CompilerPassBundle:
    from qchem_stack.backends.spec import CompilerPassBundle

    c = cfg.compiler
    return CompilerPassBundle(
        optimization_level=c.optimization_level,
        preoptimize_passes=list(c.preoptimize_passes),
        compiler_passes=list(c.compiler_passes),
    )


def compiler_bundle_signature_from_config(cfg: ExperimentConfig) -> str:
    """Stable short hash for Methods (pass list + native 2Q + optimization level)."""
    import hashlib
    import json

    c = cfg.compiler
    payload = json.dumps(
        {
            "optimization_level": int(c.optimization_level),
            "native_twoq": str(c.native_twoq),
            "preoptimize_passes": sorted(c.preoptimize_passes),
            "compiler_passes": sorted(c.compiler_passes),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
