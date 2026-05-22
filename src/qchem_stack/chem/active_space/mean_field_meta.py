"""Unified ``driver_meta`` keys for active-space strategies after classical reference build.

``strategy=avas_stub`` is hook-only: orbital selection follows **CAS** ``ncas`` / ``nelecas`` sizing
(same normalization as ``strategy=cas``). No vendor/PySCF-style AVAS threshold projection or
``frozen=avas.frozenf`` list is computed—see ``avas_stub_semantics`` and
``avas_atomic_projection_executed`` on the payload.

``strategy=avas`` executes PySCF :class:`~pyscf.mcscf.avas.AVAS`; the pipeline later sets
``avas_atomic_projection_executed=True`` plus ``qchem_active_space_resolution_v1`` on the reference.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import MutableMapping, Sequence

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig

ActiveSpaceStrategy = Literal["manual", "cas", "avas_stub", "avas"]

AVAS_PARTIAL_STUB_META_KEY = "avas_partial_stub"
AVAS_AO_LABELS_REQUESTED_META_KEY = "avas_ao_labels_requested"
AVAS_AO_LABELS_LOGGING_ONLY_META_KEY = "avas_ao_labels_logging_only"
AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY = "avas_atomic_projection_executed"
AVAS_STUB_SEMANTICS_META_KEY = "avas_stub_semantics"

AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1 = (
    "cas_ncas_nelecas_equivalent_no_avas_threshold_projection_v1"
)


def apply_active_space_strategy_to_mean_field_meta(
    driver_meta: MutableMapping[str, Any],
    *,
    strategy: ActiveSpaceStrategy | str,
    recipe: str,
    avas_ao_labels: Sequence[str] | None,
) -> None:
    """Mirror ``active_space`` + AVAS logging knobs into ``mean_field`` metadata (repro / parity).

    ``avas_ao_labels`` come from ``chemistry_extended.avas_ao_labels``:

    - For ``strategy!='avas'`` **and** non-empty labels: **logging only** — set
      ``avas_ao_labels_logging_only`` True and copy to ``avas_ao_labels_requested``.
    - For ``strategy='avas'`` the same keys are still written (labels are also AVAS inputs).
    """
    driver_meta["active_space_strategy"] = str(strategy)
    driver_meta["active_space_recipe"] = str(recipe)

    labels = [str(x) for x in avas_ao_labels] if avas_ao_labels else []
    if labels:
        driver_meta[AVAS_AO_LABELS_REQUESTED_META_KEY] = labels
        driver_meta[AVAS_AO_LABELS_LOGGING_ONLY_META_KEY] = bool(strategy != "avas")
    else:
        driver_meta.pop(AVAS_AO_LABELS_REQUESTED_META_KEY, None)
        driver_meta.pop(AVAS_AO_LABELS_LOGGING_ONLY_META_KEY, None)

    driver_meta.pop(AVAS_PARTIAL_STUB_META_KEY, None)
    driver_meta.pop(AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY, None)
    driver_meta.pop(AVAS_STUB_SEMANTICS_META_KEY, None)

    if strategy == "avas_stub":
        driver_meta[AVAS_PARTIAL_STUB_META_KEY] = True
        driver_meta[AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY] = False
        driver_meta[AVAS_STUB_SEMANTICS_META_KEY] = AVAS_STUB_SEMANTICS_CAS_EQUIVALENT_V1
    elif strategy == "avas":
        driver_meta[AVAS_ATOMIC_PROJECTION_EXECUTED_META_KEY] = False


def build_active_space_recipe(cfg: ExperimentConfig) -> str:
    """Human-readable active-space recipe string for repro / parity export."""
    if cfg.active_space.strategy == "manual":
        frz = list(cfg.active_space.manual.frozen_orbitals)
        return (
            "manual:"
            f"n_active_orbitals={cfg.active_space.cas.n_orbitals},"
            f"n_active_electrons={cfg.active_space.cas.n_electrons},"
            f"frozen_orbitals={frz}"
        )
    if cfg.active_space.strategy == "avas_stub":
        return (
            "avas_stub:"
            f"n_orbitals={cfg.active_space.cas.n_orbitals},"
            f"n_electrons={cfg.active_space.cas.n_electrons}:partial_open_stack_no_avas_projection"
        )
    if cfg.active_space.strategy == "avas":
        return (
            "avas:"
            f"ao_labels={cfg.chemistry_extended.avas.ao_labels}:"
            f"threshold={cfg.chemistry_extended.avas.threshold}:pyscf_mcscf_avas"
        )
    return (
        f"cas:n_orbitals={cfg.active_space.cas.n_orbitals},"
        f"n_electrons={cfg.active_space.cas.n_electrons}"
    )


def annotate_mean_field_reference_active_space(
    cfg: ExperimentConfig,
    ref: ClassicalMeanFieldReference,
) -> ClassicalMeanFieldReference:
    """Apply active-space strategy metadata to a classical mean-field reference."""
    apply_active_space_strategy_to_mean_field_meta(
        ref.driver_meta,
        strategy=cfg.active_space.strategy,
        recipe=build_active_space_recipe(cfg),
        avas_ao_labels=cfg.chemistry_extended.avas.ao_labels,
    )
    if cfg.active_space.manual.frozen_orbitals:
        ref.driver_meta["active_space_frozen_orbitals"] = list(
            cfg.active_space.manual.frozen_orbitals
        )
    return ref
