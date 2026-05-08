from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class AlgorithmReport:
    """Serializable algorithm report shared across algorithm families."""

    schema: str
    algorithm: str
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "algorithm": self.algorithm,
            "metrics": dict(self.metrics),
            "artifacts": dict(self.artifacts),
            "diagnostics": dict(self.diagnostics),
        }


@runtime_checkable
class AlgorithmLifecycle(Protocol):
    """Unified algorithm lifecycle, analogous to InQuanto Algorithm classes."""

    def build(self, **kwargs: Any) -> AlgorithmLifecycle: ...

    def run(self, **kwargs: Any) -> Any: ...

    def generate_report(self) -> dict[str, Any]: ...


class AlgorithmBase:
    """Common build/run/report plumbing used by all algorithm classes."""

    _report_schema: str = "algorithm_report_v1"
    _algorithm_name: str = "algorithm"

    def __init__(self) -> None:
        self._built: bool = False
        self._build_meta: dict[str, Any] = {}
        self._last_report: dict[str, Any] = {}

    def build(self, **kwargs: Any) -> AlgorithmBase:
        self._build_meta = dict(kwargs)
        self._built = True
        return self

    def _ensure_built(self) -> None:
        if not self._built:
            self.build()

    def _set_report(
        self,
        *,
        metrics: dict[str, Any] | None = None,
        artifacts: dict[str, Any] | None = None,
        diagnostics: dict[str, Any] | None = None,
    ) -> None:
        report = AlgorithmReport(
            schema=self._report_schema,
            algorithm=self._algorithm_name,
            metrics=metrics or {},
            artifacts=artifacts or {},
            diagnostics=diagnostics or {},
        )
        self._last_report = report.to_dict()

    def generate_report(self) -> dict[str, Any]:
        if not self._last_report:
            self._set_report(
                diagnostics={
                    "built": self._built,
                    "note": "run() has not been called yet",
                }
            )
        return dict(self._last_report)
