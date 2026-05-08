"""qchem-stack: quantum chemistry orchestration with protocols, ML, and MD bridge."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

from qchem_stack.exceptions import (
    ConfigurationError,
    EmbeddingError,
    PipelineError,
    QChemStackError,
    ReproExportError,
)
from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps

try:
    __version__ = _package_version("qchem-stack")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "ConfigurationError",
    "EmbeddingError",
    "PipelineError",
    "QChemStackError",
    "ReproExportError",
    "__version__",
    "repro_dict_for_strict_json",
    "repro_json_dumps",
]
