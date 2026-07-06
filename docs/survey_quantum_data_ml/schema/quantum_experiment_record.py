"""Pydantic models for quantum experiment records (classical ML consumption).

Standalone schema for survey / data-lake ingestion. Copy or import from:
``docs/survey_quantum_data_ml/schema/``.

Example::

    from quantum_experiment_record import QuantumExperimentRecord

    record = QuantumExperimentRecord.model_validate(payload)
    record.model_dump_json(indent=2)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class PathType(str, Enum):
    LABELED = "labeled"
    NATIVE = "native"
    HYBRID = "hybrid"


class ProblemDomain(str, Enum):
    MANY_BODY = "many_body"
    CHEMISTRY = "chemistry"
    FINANCE = "finance"
    HEP = "hep"
    SENSING = "sensing"
    CV = "cv"
    SECURITY = "security"
    MATERIALS = "materials"
    OTHER = "other"


class MeasurementProtocol(str, Enum):
    COMPUTATIONAL = "computational"
    RANDOM_PAULI = "random_pauli"
    CLIFFORD = "clifford"
    SHADOW = "shadow"
    ADAPTIVE = "adaptive"
    CONTINUOUS = "continuous"
    OTHER = "other"


class MitigationMethod(str, Enum):
    ZNE = "zne"
    READOUT = "readout"
    CDR = "cdr"
    PEC = "pec"
    VIRTUAL_DISTILLATION = "virtual_distillation"
    ML_SURROGATE = "ml_surrogate"
    OTHER = "other"


class ProblemSpec(BaseModel):
    domain: ProblemDomain
    description: str | None = Field(default=None, max_length=4096)
    parameters: dict[str, Any] = Field(default_factory=dict)


class CircuitSpec(BaseModel):
    ansatz: str | None = None
    depth: int | None = Field(default=None, ge=0)
    n_qubits: int = Field(ge=1)
    params: list[float] = Field(default_factory=list)
    ir_hash: str | None = None


class MeasurementSpec(BaseModel):
    protocol: MeasurementProtocol
    n_shots: int = Field(ge=1)
    observables: list[str] = Field(default_factory=list)
    expectation_values: dict[str, float] = Field(default_factory=dict)
    raw_outcomes: list[str] = Field(default_factory=list)
    shadow_vectors: list[list[float]] = Field(default_factory=list)

    @field_validator("raw_outcomes")
    @classmethod
    def validate_bitstrings(cls, values: list[str]) -> list[str]:
        for bitstring in values:
            if bitstring and not set(bitstring).issubset({"0", "1"}):
                msg = f"raw_outcomes must be computational-basis bitstrings, got {bitstring!r}"
                raise ValueError(msg)
        return values


class QuantumExecution(BaseModel):
    backend: str
    device_calibration_id: str | None = None
    circuit: CircuitSpec
    measurement: MeasurementSpec


class Labels(BaseModel):
    energy_hartree: float | None = None
    forces_hartree_bohr: list[list[float]] | None = None
    class_label: str | int | None = None
    regression_target: float | None = None
    custom: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def at_least_one_label_field(self) -> Labels:
        if not any(
            [
                self.energy_hartree is not None,
                self.forces_hartree_bohr is not None,
                self.class_label is not None,
                self.regression_target is not None,
                self.custom,
            ]
        ):
            raise ValueError(
                "Labels must include at least one of: energy_hartree, forces, "
                "class_label, regression_target, or non-empty custom."
            )
        return self


class ClassicalReference(BaseModel):
    method: str
    value: Any = None
    uncertainty: float | None = Field(default=None, ge=0)


class MitigationSpec(BaseModel):
    applied: list[MitigationMethod] = Field(default_factory=list)
    surrogate_model_id: str | None = None
    notes: str | None = None


class ReproSpec(BaseModel):
    software_versions: dict[str, str] = Field(default_factory=dict)
    random_seed: int | None = None
    hash: str
    source_run_id: str | None = None


class QuantumExperimentRecord(BaseModel):
    """Top-level quantum experiment record for ML datasets."""

    schema_version: str = Field(default="1", pattern=r"^1$")
    id: UUID
    timestamp: datetime
    path_type: PathType
    problem: ProblemSpec
    quantum_execution: QuantumExecution
    labels: Labels | None = None
    classical_reference: ClassicalReference | None = None
    mitigation: MitigationSpec | None = None
    repro: ReproSpec

    @model_validator(mode="after")
    def validate_path_constraints(self) -> QuantumExperimentRecord:
        if self.path_type in (PathType.LABELED, PathType.HYBRID) and self.labels is None:
            raise ValueError("path_type 'labeled' or 'hybrid' requires 'labels'.")

        if self.path_type == PathType.NATIVE:
            m = self.quantum_execution.measurement
            if not m.raw_outcomes and not m.shadow_vectors:
                raise ValueError(
                    "path_type 'native' requires measurement.raw_outcomes or "
                    "measurement.shadow_vectors."
                )
        return self

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> QuantumExperimentRecord:
        return cls.model_validate(data)


def load_record(path: str) -> QuantumExperimentRecord:
    """Load and validate a record from a JSON file."""
    import json
    from pathlib import Path

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return QuantumExperimentRecord.model_validate(payload)


def dump_record(record: QuantumExperimentRecord, path: str) -> None:
    """Write a validated record to JSON."""
    from pathlib import Path

    Path(path).write_text(
        record.model_dump_json(indent=2),
        encoding="utf-8",
    )
