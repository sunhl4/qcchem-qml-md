"""
Typed error surface for integrations, ops, and customer-facing traceability.

Domain code should raise these (or subclasses) at package boundaries instead of bare
``ValueError`` / ``RuntimeError`` where the caller needs to branch on *kind* of failure.
"""

from __future__ import annotations


class QChemStackError(Exception):
    """Base for all library-raised errors that are intended to be caught or logged distinctly."""


class ConfigurationError(QChemStackError):
    """Invalid experiment YAML / :class:`~qchem_stack.config.ExperimentConfig` combination."""


class ReproExportError(QChemStackError):
    """``repro`` or run payload cannot be made JSON-serializable under the strict export rules."""


class PipelineError(QChemStackError):
    """Orchestration failed after config validation (driver, Hamiltonian build, variational stage)."""


class EmbeddingError(QChemStackError):
    """Fragment / bath / Schmidt embedding construction or self-consistency failure."""
