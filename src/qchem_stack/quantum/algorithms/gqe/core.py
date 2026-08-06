"""GQE algorithm classes (peer level to :class:`~qchem_stack.quantum.algorithms.vqe.VQE`)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.gqe.train import run_gqe_training
from qchem_stack.quantum.algorithms.gqe.types import GQEConfig, GQEResult, GQEVariant

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

ALGORITHM_GQE_REPORT_V1 = "algorithm_gqe_report_v1"


class GQE(AlgorithmBase):
    """Generative Quantum Eigensolver (Nakaji GPT-QE baseline).

    Classical policy generates discrete operator-token sequences; the quantum
    backend only evaluates energy (or a variant-specific oracle).
    """

    _variant: GQEVariant = "gpt_qe"

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        config: GQEConfig | None = None,
        **overrides: Any,
    ) -> None:
        super().__init__()
        self.hamiltonian = hamiltonian
        self._algorithm_name = str(overrides.pop("algorithm_name", self._variant))
        self._report_schema = ALGORITHM_GQE_REPORT_V1
        cfg = config or GQEConfig(variant=self._variant)
        if cfg.variant != self._variant:
            cfg = replace(cfg, variant=self._variant)
        for key, value in overrides.items():
            if hasattr(cfg, key):
                cfg = replace(cfg, **{key: value})
        self.config = cfg
        self._last_result: GQEResult | None = None
        self._condition: np.ndarray | None = None
        self._teacher_sequences: list[list[int]] | None = None

    def build(
        self,
        *,
        condition: np.ndarray | None = None,
        teacher_sequences: list[list[int]] | None = None,
        **kwargs: Any,
    ) -> GQE:
        if condition is not None:
            self._condition = np.asarray(condition, dtype=float).ravel()
        if teacher_sequences is not None:
            self._teacher_sequences = [list(map(int, s)) for s in teacher_sequences]
        return super().build(condition=condition is not None, **kwargs)  # type: ignore[return-value]

    def run(
        self,
        *,
        max_iters: int | None = None,
        seed: int | None = None,
        condition: np.ndarray | None = None,
        teacher_sequences: list[list[int]] | None = None,
    ) -> GQEResult:
        self._ensure_built()
        cfg = self.config
        if max_iters is not None:
            cfg = replace(cfg, max_iters=int(max_iters))
        if seed is not None:
            cfg = replace(cfg, seed=int(seed))
        cond = self._condition if condition is None else np.asarray(condition, dtype=float).ravel()
        teachers = self._teacher_sequences if teacher_sequences is None else teacher_sequences
        result = run_gqe_training(
            self.hamiltonian,
            cfg,
            condition=cond,
            teacher_sequences=teachers,
        )
        self._last_result = result
        self._set_report(
            metrics={
                "energy": result.energy,
                "n_oracle_calls": result.n_oracle_calls,
                "nfev": result.nfev,
            },
            artifacts={
                "best_sequence": list(result.best_sequence),
                "best_labels": list(result.best_labels),
                "energy_trace": list(result.energy_trace),
            },
            diagnostics={"meta": dict(result.meta)},
        )
        return result

    def generate_report(self) -> dict[str, Any]:
        if self._last_result is None:
            return super().generate_report()
        r = self._last_result
        return {
            "schema": ALGORITHM_GQE_REPORT_V1,
            "algorithm": self._algorithm_name,
            "variant": self._variant,
            "final_value": float(r.energy),
            "nfev": int(r.nfev),
            "n_oracle_calls": int(r.n_oracle_calls),
            "best_sequence": list(r.best_sequence),
            "best_labels": list(r.best_labels),
            "energy_trace": list(r.energy_trace),
            "meta": dict(r.meta),
        }


class ConditionalGQE(GQE):
    """A1 Conditional-GQE: problem-conditioned generative policy."""

    _variant: GQEVariant = "conditional"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, algorithm_name="conditional_gqe", **kw)


class PersistentDPOGQE(GQE):
    """A2 Persistent-DPO + QCC budget masking."""

    _variant: GQEVariant = "pdpo_qcc"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("qcc_budget", 8.0)
        kw.setdefault("loss", "pdpo")
        super().__init__(hamiltonian, config, algorithm_name="pdpo_gqe", **kw)
        if self.config.qcc_budget is None:
            self.config = replace(self.config, qcc_budget=8.0)
        if self.config.loss != "pdpo":
            self.config = replace(self.config, loss="pdpo")


class SmilesTransferGQE(GQE):
    """A3 SMILES-inspired operator text vocabulary for transfer learning."""

    _variant: GQEVariant = "smiles"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("pool_mode", "uccsd")
        super().__init__(hamiltonian, config, algorithm_name="smiles_gqe", **kw)


class QSCIGQE(GQE):
    """A4 GQE + QSCI subspace-energy reward."""

    _variant: GQEVariant = "qsci"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("loss", "grpo")
        super().__init__(hamiltonian, config, algorithm_name="gqe_qsci", **kw)


class AugerGQE(GQE):
    """A5 Auger / spectral GQE workflow (excited-weight oracle)."""

    _variant: GQEVariant = "auger"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, algorithm_name="auger_gqe", **kw)


class GQKAE(GQE):
    """A6 Generative Quantum-inspired Kolmogorov–Arnold Eigensolver."""

    _variant: GQEVariant = "gqkae"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("backbone", "kan")
        kw.setdefault("loss", "grpo")
        super().__init__(hamiltonian, config, algorithm_name="gqkae", **kw)


class SpinGQE(GQE):
    """A7 SpinGQE: spin Hamiltonian pool + WMSE prefix supervision."""

    _variant: GQEVariant = "spin"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("loss", "wmse")
        kw.setdefault("pool_mode", "spin_heisenberg")
        super().__init__(hamiltonian, config, algorithm_name="spin_gqe", **kw)


class AdaptGQE(GQE):
    """A8 ADAPT-GQE: optional ADAPT teacher sequences + GRPO fine-tune."""

    _variant: GQEVariant = "adapt_gqe"

    def __init__(self, hamiltonian: QubitHamiltonian, config: GQEConfig | None = None, **kw: Any):
        kw.setdefault("loss", "grpo")
        kw.setdefault("pool_mode", "uccsd")
        super().__init__(hamiltonian, config, algorithm_name="adapt_gqe", **kw)


VARIANT_TO_CLASS: dict[str, type[GQE]] = {
    "gpt_qe": GQE,
    "gqe": GQE,
    "conditional": ConditionalGQE,
    "conditional_gqe": ConditionalGQE,
    "pdpo_qcc": PersistentDPOGQE,
    "pdpo_gqe": PersistentDPOGQE,
    "smiles": SmilesTransferGQE,
    "smiles_gqe": SmilesTransferGQE,
    "qsci": QSCIGQE,
    "gqe_qsci": QSCIGQE,
    "auger": AugerGQE,
    "auger_gqe": AugerGQE,
    "gqkae": GQKAE,
    "spin": SpinGQE,
    "spin_gqe": SpinGQE,
    "adapt_gqe": AdaptGQE,
}


def gqe_algorithm_report_v1(result: GQEResult, *, algorithm: str = "gqe") -> dict[str, Any]:
    return {
        "schema": ALGORITHM_GQE_REPORT_V1,
        "algorithm": algorithm,
        "variant": result.meta.get("variant"),
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "n_oracle_calls": int(result.n_oracle_calls),
        "best_sequence": list(result.best_sequence),
        "best_labels": list(result.best_labels),
        "meta": dict(result.meta),
    }
