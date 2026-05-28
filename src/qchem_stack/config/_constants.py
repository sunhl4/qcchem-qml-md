"""Shared physical constants and limits for experiment configuration."""

# CODATA-compatible: Bohr radius in ångströms (chemistry YAML often uses Å).
_BOHR_RADIUS_IN_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / _BOHR_RADIUS_IN_ANGSTROM

MD_ML_MAX_EXTRA_GEOMETRIES = 48
"""Upper bound on ``md_ml_export.trajectory.extra_coordinates_bohr`` length."""
