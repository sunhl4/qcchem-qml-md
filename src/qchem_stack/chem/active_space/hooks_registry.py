"""Registry mapping ``backend_tag`` → :class:`ActiveSpaceBackendHooks`."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qchem_stack.exceptions import PreQuantumCapabilityError

if TYPE_CHECKING:
    from qchem_stack.chem.active_space.hooks_protocol import ActiveSpaceBackendHooks

_LOG = logging.getLogger(__name__)

_HOOKS: dict[str, ActiveSpaceBackendHooks] = {}
_REGISTRY_FROZEN = False
_BUILTINS_REGISTERED = False


def _normalized_backend_tag(backend_tag: str) -> str:
    return str(backend_tag).strip().lower()


def list_active_space_hooks() -> tuple[str, ...]:
    """Stable sorted registry view for diagnostics/tests."""
    _ensure_builtin_hooks_registered()
    return tuple(sorted(_HOOKS))


def freeze_active_space_hooks() -> None:
    """Disallow further runtime registry mutation in this process."""
    global _REGISTRY_FROZEN
    _REGISTRY_FROZEN = True


def _ensure_registry_mutable() -> None:
    if _REGISTRY_FROZEN:
        raise RuntimeError(
            "Active-space hooks registry is frozen for this process. "
            "Register hooks before calling freeze_active_space_hooks()."
        )


def register_active_space_hooks(
    backend_tag: str,
    hooks: ActiveSpaceBackendHooks,
    *,
    allow_override: bool = False,
) -> None:
    """Register active-space hooks by backend tag."""
    _ensure_registry_mutable()
    tag = _normalized_backend_tag(backend_tag)
    if tag in _HOOKS and not allow_override:
        raise ValueError(
            f"ActiveSpaceBackendHooks {tag!r} is already registered; "
            "pass allow_override=True to replace it explicitly."
        )
    if tag in _HOOKS and allow_override:
        _LOG.warning("Overriding ActiveSpaceBackendHooks for backend %s", tag)
    _HOOKS[tag] = hooks


def _ensure_builtin_hooks_registered() -> None:
    global _BUILTINS_REGISTERED
    if _BUILTINS_REGISTERED:
        return
    from qchem_stack.chem.active_space.psi4_active_space_hooks import Psi4ActiveSpaceHooks
    from qchem_stack.chem.active_space.pyscf_hooks_adapter import PySCFActiveSpaceHooks

    register_active_space_hooks("pyscf", PySCFActiveSpaceHooks(), allow_override=True)
    register_active_space_hooks("psi4", Psi4ActiveSpaceHooks(), allow_override=True)
    _BUILTINS_REGISTERED = True


def get_active_space_hooks(backend_tag: str) -> ActiveSpaceBackendHooks:
    _ensure_builtin_hooks_registered()
    tag = _normalized_backend_tag(backend_tag)
    hooks = _HOOKS.get(tag)
    if hooks is None:
        known = list_active_space_hooks()
        raise PreQuantumCapabilityError(
            f"No ActiveSpaceBackendHooks registered for backend {tag!r}. Known backends: {known}."
        )
    return hooks
