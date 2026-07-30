"""Experimental / stub schema id strings (not part of the stable integrator contract).

Stable contracts live in :mod:`qchem_stack.contracts.schema_ids`.
These IDs remain importable via ``schema_ids`` for one compatibility cycle.
"""

from __future__ import annotations

MITIGATION_PEC_LITERATURE_STUB_V1 = "mitigation_pec_literature_stub_v1"
CUTENSORTNET_PROTOCOL_STUB_V1 = "cutensornet_protocol_stub_v1"
L3_ENERGY_BOOTSTRAP_STUB_V1 = "l3_energy_bootstrap_stub_v1"
ML_MD_TRAINER_STUB_FIT_V1 = "ml_md_trainer_stub_fit_v1"
BAYESIAN_QPE_STUB_MAP_V1 = "bayesian_qpe_stub_map_v1"

__all__ = [
    "MITIGATION_PEC_LITERATURE_STUB_V1",
    "CUTENSORTNET_PROTOCOL_STUB_V1",
    "L3_ENERGY_BOOTSTRAP_STUB_V1",
    "ML_MD_TRAINER_STUB_FIT_V1",
    "BAYESIAN_QPE_STUB_MAP_V1",
]
