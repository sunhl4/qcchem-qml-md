"""Unified ``driver_meta`` keys for active-space strategies after classical reference build.

``strategy=avas_stub`` is hook-only: orbital selection follows **CAS** ``ncas`` / ``nelecas`` sizing
(same normalization as ``strategy=cas``). No PySCF/InQuanto-style AVAS threshold projection or
``frozen=avas.frozenf`` list is computed—see ``avas_stub_semantics`` and
``avas_atomic_projection_executed`` on the payload.

``strategy=avas`` executes PySCF :class:`~pyscf.mcscf.avas.AVAS`; the pipeline later sets
``avas_atomic_projection_executed=True`` plus ``qchem_active_space_resolution_v1`` on the reference.
"""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import Any, Literal

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
