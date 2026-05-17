"""
Typed error surface for integrations, ops, and customer-facing traceability.

Domain code should raise these (or subclasses) at package boundaries instead of bare
``ValueError`` / ``RuntimeError`` where the caller needs to branch on *kind* of failure.
"""

from __future__ import annotations


class QChemStackError(Exception):
    """Base for all library-raised errors that are intended to be caught or logged distinctly."""


class ConfigurationError(QChemStackError):
    """Experiment config file I/O, invalid YAML root shape, or missing deps from config helpers.

    Field-level and cross-field validation for :class:`~qchem_stack.config.ExperimentConfig` is
    raised as ``pydantic.ValidationError`` by Pydantic (e.g. ``model_validate`` / ``from_yaml_dict``).
    """


class ReproExportError(QChemStackError):
    """``repro`` or run payload cannot be made JSON-serializable under the strict export rules."""


class PipelineError(QChemStackError):
    """Orchestration failed after config validation (driver, Hamiltonian build, variational stage)."""


class EmbeddingError(QChemStackError):
    """Fragment / bath / Schmidt embedding construction or self-consistency failure."""


class PreQuantumError(QChemStackError):
    """Base class for pre-quantum contract/build failures."""


class PreQuantumCapabilityError(PreQuantumError):
    """Selected backend or registered adapters cannot satisfy a required pre-quantum capability."""
