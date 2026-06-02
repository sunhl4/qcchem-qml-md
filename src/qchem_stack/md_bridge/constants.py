"""Physical constants and unit conversions for molecular dynamics bridge.

This module centralizes domain-specific physical constants and unit conversion
factors used in the MD bridge modules, separate from numerical tolerances.
"""

from __future__ import annotations

# Unit conversions
_BOHR_TO_ANGSTROM = 0.529177210903
"""Conversion factor: Bohr radius to Angstroms."""

_HARTREE_TO_EV = 27.211386245988
"""Conversion factor: Hartree energy to electron volts."""

FS_TO_PS = 1e-3
"""Conversion factor: femtoseconds to picoseconds."""

_HARTREE_BOHR_TO_EV_ANG = _HARTREE_TO_EV / _BOHR_TO_ANGSTROM
"""Combined conversion: Hartree/Bohr to eV/Angstrom (force units)."""

# Morse potential parameters
MORSE_LOWER_DE = 1e-4
"""Lower bound for Morse potential D_e parameter (eV).

This prevents the dissociation energy from becoming too small during
nonlinear least squares fitting, which would lead to unphysical potentials.
"""
