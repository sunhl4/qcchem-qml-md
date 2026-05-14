from __future__ import annotations

from importlib import import_module

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.config import ExperimentConfig


def _resolve_hook(name: str):
    key = str(name or "").strip()
    if not key:
        return None
    if key == "identity":
        return lambda mo, **_: np.asarray(mo, dtype=float)
    if key == "reverse_mo_columns":
        return lambda mo, **_: np.asarray(mo, dtype=float)[:, ::-1]
    if ":" in key:
        mod_name, fn_name = key.split(":", 1)
        mod = import_module(mod_name)
        fn = getattr(mod, fn_name)
        if not callable(fn):
            raise TypeError(f"mo_coeff_transform_hook {key!r} is not callable.")
        return fn
    raise ValueError(
        "Unsupported chemistry_extended.mo_coeff_transform_hook. "
        "Use '', 'identity', 'reverse_mo_columns', or 'module:function'."
    )


def apply_mo_coeff_transform_hook(cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference) -> None:
    hook_name = str(cfg.chemistry_extended.mo_coeff_transform_hook or "").strip()
    if not hook_name:
        return
    hook = _resolve_hook(hook_name)
    if hook is None:
        return
    mf = rhf.mf
    mo_coeff = getattr(mf, "mo_coeff", None)
    if mo_coeff is None:
        raise ValueError("mo_coeff_transform_hook requires mean-field handle with mo_coeff.")
    if not isinstance(mo_coeff, np.ndarray):
        raise ValueError(
            "mo_coeff_transform_hook currently supports molecular ndarray mo_coeff only."
        )
    before_shape = tuple(mo_coeff.shape)
    transformed = np.asarray(
        hook(mo_coeff, **dict(cfg.chemistry_extended.mo_coeff_transform_kwargs))
    )
    if tuple(transformed.shape) != before_shape:
        raise ValueError(
            "mo_coeff_transform_hook must preserve mo_coeff shape: "
            f"got {tuple(transformed.shape)} vs expected {before_shape}."
        )
    mf.mo_coeff = transformed
    rhf.driver_meta["mo_coeff_transform_hook_v1"] = {
        "schema": "mo_coeff_transform_hook_v1",
        "hook": hook_name,
        "kwargs": dict(cfg.chemistry_extended.mo_coeff_transform_kwargs),
        "shape": [int(before_shape[0]), int(before_shape[1])],
    }
