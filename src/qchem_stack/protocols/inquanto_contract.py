"""Parity / gap / export key registries (stable import path for docs and integrators).

Canonical implementations live in
``qchem_stack.internal_reports.competitor.inquanto_contract``. This module
re-exports that surface so references such as
``qchem_stack.protocols.inquanto_contract.PARITY_SNAPSHOT_DOCUMENTED_KEYS`` and
file links to ``src/qchem_stack/protocols/inquanto_contract.py`` stay valid
without duplicating registry literals.
"""

from __future__ import annotations

from qchem_stack.internal_reports.competitor.inquanto_contract import *  # noqa: F403
