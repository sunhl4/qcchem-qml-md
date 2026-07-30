"""Configuration and record types for the MD validation active-learning loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import yaml

from qchem_stack.exceptions import ConfigurationError
from qchem_stack.quantum.algorithms.tolerances import DEFAULT_LEARNING_RATE

if TYPE_CHECKING:
    from qchem_stack.md_bridge.qchem_labeler import EnergyReference, TheoryLevel

Ensemble = Literal["nve", "nvt_langevin", "nvt_nose_hoover"]
SeedMode = Literal["jitter", "bond_stretch"]
MdInitFrame = Literal["base", "last"]
ForceFieldBackend = Literal[
    "qmlff_preset",
    "qmlff_quantum",
    "qmlff_angle",
    "qmlff_qmp_h2",
    "classical_h2",
]


@dataclass
class MdValidationLoopConfig:
    """All knobs for :func:`run_md_validation_loop`.

    The loop deliberately keeps its own stdlib dataclass rather than extending
    :class:`~qchem_stack.config.ExperimentConfig`: this keeps the orchestration
    schema stable across qchem releases and avoids leaking ML/MD concerns into
    the chemistry config tree.

    Two-stage labeling parallels the existing
    :class:`qmlff.data.qchem_online_loop.TwoStageLabelingSpec`: every candidate
    is first scored with cheap ``hf_scf`` screening, then the top-k with the
    largest QML-vs-qchem energy gap are upgraded to ``full_pipeline``.

    Attributes:
        max_rounds: number of active-learning iterations after cold-start.
        qmlff_preset: QML-FF preset name (``atomic_amplitude`` etc.) when
            ``force_field_backend`` is ``qmlff_preset`` or ``qmlff_angle``.
        force_field_backend: ``qmlff_preset`` | ``qmlff_quantum`` | ``qmlff_angle``
            | ``qmlff_qmp_h2`` | ``classical_h2``.
        qmlff_builder_overrides: forwarded to the preset ``get_config(**overrides)``
        qmp_h2_overrides: forwarded to ``SchurSchemeBQMLFFConfig`` for QMP path.
        lr_scheduler: QML-FF ``TrainerConfig.lr_scheduler`` (use ``constant`` for AL).
        warm_start_params_only: reuse model params each round but reset optimizer.
        energy_normalization: ``subtract_mean`` | ``per_atom`` | ``none`` (QML-FF native).
        grad_clip: forwarded to ``TrainerConfig.grad_clip``.
        qmlff_species_list: ordered list of element symbols the model must
            cover for all geometries it will see; defaults to whatever is in
            the experiment YAML's base molecule.
        n_seed_geometries: extra seed geometries to label and add to the
            initial training set (set to 0 for a strict 0-data cold-start).
        seed_mode: ``jitter`` (Gaussian noise) or ``bond_stretch`` (scan the
            diatomic bond length; falls back to jitter for non-diatomics).
        seed_jitter_bohr: σ of the Gaussian jitter (Bohr) when ``seed_mode=jitter``.
        seed_bond_min_bohr / seed_bond_max_bohr: bond-length scan range (Bohr)
            when ``seed_mode=bond_stretch``.
        round_bonds_per_round: if >0, each AL round also labels and merges this
            many **new** H–H bond lengths (staggered schedule complementary to
            the seed scan). Use this when MD alone does not cover the PES.
        stop_on_md_converged: when ``False``, keep running all ``max_rounds``
            even if MD candidates already meet ``energy_tolerance_hartree``
            (needed when the goal is a full bond-schedule online-learning pass).
        pretrain_epochs: if >0, after the quantum bond-scan seed set is built,
            train the force field on that dataset **alone** (no MD / no AL)
            before entering online-learning rounds. This is the non-zero-shot
            path: scan → pretrain → online learning.
        dissociation_bond_bohr: chemistry threshold for logging / coverage
            (bound vs dissociating). Does not by itself reject frames.
        max_train_bond_bohr: reject MD merge candidates with longer bonds.
            Default ``None`` → ``0.95 * cutoff`` (Å→Bohr). Beyond the FF
            cutoff, pair interactions are not evaluated — such frames must
            not enter training.
        tolerance_stage1_hartree / tolerance_stage1_until_round: looser early
            |ΔE| target (P1 staged convergence).
        tolerance_stage2_hartree / tolerance_stage2_until_round: mid-stage
            target before the final ``energy_tolerance_hartree``.
        md_init_frame: ``base`` starts MD from the equilibrium/base geometry;
            ``last`` uses the most recently merged training frame.
        n_epochs_per_round / batch_size / learning_rate / force_weight:
            forwarded to :class:`qmlff.training.TrainerConfig` each round.
        warm_start: reuse optimizer state from the previous round.
        md_ensemble / md_n_steps / md_dt_fs / md_temperature_K / md_save_stride /
            md_seed / md_gamma_ps_inv / md_tau_fs: MD knobs (see
            :func:`run_jaxmd_trajectory`).
        n_candidate_frames: how many MD frames to sample for validation.
        energy_tolerance_hartree: per-frame |ΔE| convergence target.
        add_top_k_per_round: ≤ ``n_candidate_frames``; merge the K worst gaps
            back into the training dataset each round.
        label_energy_reference: ``variational`` / ``scf`` / ``pauli_protocol``
            for the **labeling step** (training labels).
        validation_energy_reference: energy used when scoring MD frames
            (``|E_QML - E_ref|``). Defaults to ``label_energy_reference``.
        validation_theory_level: pipeline level for that scoring pass. Defaults
            to ``label_top_theory_level`` (not cheap HF screening).
        label_screening_theory_level: legacy cheap pass; ignored for |ΔE| when
            ``validation_theory_level`` is set explicitly in YAML.
        label_top_theory_level: ``full_pipeline`` (default) for the top-k
            geometries selected by the gap; ``hf_scf`` to stay HF throughout.
        dedupe_decimals: round positions (Bohr) to this many decimals when
            deduplicating frames during dataset merges.
        include_hf_nuclear_gradient: attach analytic HF forces (Hartree/Bohr)
            from PySCF where available (non-PBC only).
        write_per_round_extxyz: dump the cumulative dataset + MD trajectory
            for every round.
        seed: PRNG seed for seed-geometry jitter (and reproducibility).
        force_weight_during_screening: pass ``force_weight`` to the inner
            screening-only trainer when finer force fitting is required.
    """

    max_rounds: int = 2
    force_field_backend: ForceFieldBackend = "qmlff_preset"
    qmlff_preset: str = "atomic_amplitude"
    qmlff_builder_overrides: dict[str, Any] | None = None
    qmp_h2_overrides: dict[str, Any] | None = None
    qmlff_species_list: list[str] | None = None

    # Seeding (round 0 augmentation)
    n_seed_geometries: int = 0
    seed_mode: SeedMode = "jitter"
    seed_jitter_bohr: float = 0.08
    seed_bond_min_bohr: float = 0.8
    seed_bond_max_bohr: float = 2.2

    # Per-round bond-length injection (complementary to seed scan)
    round_bonds_per_round: int = 0
    stop_on_md_converged: bool = True

    # Phase B: train on seed dataset before online learning (not zero-shot)
    pretrain_epochs: int = 0

    # Dissociation / cutoff policy (H2 and other diatomics)
    dissociation_bond_bohr: float = 3.0
    max_train_bond_bohr: float | None = None

    # QML-FF training
    n_epochs_per_round: int = 3
    batch_size: int = 1
    learning_rate: float = DEFAULT_LEARNING_RATE
    force_weight: float = 100.0
    lr_scheduler: str = "constant"
    warm_start: bool = False
    warm_start_params_only: bool = True
    energy_normalization: str | None = "subtract_mean"
    grad_clip: float = 1.0
    qmlff_checkpoint_save_freq: int | None = 0
    """QML-FF ``TrainerConfig.save_freq``; ``0`` or ``None`` = only ``final`` checkpoint."""

    # JAX-MD
    md_ensemble: Ensemble = "nvt_langevin"
    md_n_steps: int = 100
    md_dt_fs: float = 0.5
    md_temperature_K: float = 300.0
    md_save_stride: int = 5
    md_seed: int = 0
    md_gamma_ps_inv: float = 0.1
    md_tau_fs: float = 100.0
    md_init_frame: MdInitFrame = "last"
    cutoff_ang: float | None = None
    max_neighbors: int = 32

    # Active learning
    n_candidate_frames: int = 4
    energy_tolerance_hartree: float = 5.0e-4  # ≈ 13.6 meV
    tolerance_stage1_hartree: float | None = None
    tolerance_stage1_until_round: int = 0
    tolerance_stage2_hartree: float | None = None
    tolerance_stage2_until_round: int = 0
    add_top_k_per_round: int = 2
    label_energy_reference: EnergyReference = "variational"
    validation_energy_reference: EnergyReference | None = None
    validation_theory_level: TheoryLevel | None = None
    label_screening_theory_level: TheoryLevel = "hf_scf"
    label_top_theory_level: TheoryLevel = "full_pipeline"
    include_hf_nuclear_gradient: bool = True
    dedupe_decimals: int = 4
    validation_skip_initial_md_frame: bool = False
    """When ``False``, include the first saved MD frame in validation (often near equilibrium)."""

    # IO
    write_per_round_extxyz: bool = True
    seed: int = 0

    def resolve_round_tolerance(self, round_i: int) -> float:
        """Staged |ΔE| target: stage1 → stage2 → final ``energy_tolerance_hartree``."""
        r = int(round_i)
        if (
            self.tolerance_stage1_hartree is not None
            and int(self.tolerance_stage1_until_round) > 0
            and r <= int(self.tolerance_stage1_until_round)
        ):
            return float(self.tolerance_stage1_hartree)
        if (
            self.tolerance_stage2_hartree is not None
            and int(self.tolerance_stage2_until_round) > 0
            and r <= int(self.tolerance_stage2_until_round)
        ):
            return float(self.tolerance_stage2_hartree)
        return float(self.energy_tolerance_hartree)

    @classmethod
    def from_yaml(cls, path: str | Path) -> MdValidationLoopConfig:
        """Load from a flat YAML mapping (only known fields are honored)."""
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"MD validation loop YAML not found: {p}")
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raise ConfigurationError(f"YAML at {p} must be a mapping; got {type(raw).__name__}")
        # Filter to known fields so future YAMLs with extra keys don't crash.
        valid = set(cls.__dataclass_fields__.keys())
        clean = {k: v for k, v in raw.items() if k in valid}
        return cls(**clean)


@dataclass
class FrameValidationRecord:
    """Per-frame |ΔE| record used to decide which MD frames to re-label."""

    frame_index: int
    time_ps: float
    energy_qml_hartree: float
    energy_qchem_hartree: float
    delta_hartree: float
    abs_delta_hartree: float
    converged: bool
    theory_level: str
    energy_reference_used: str = "variational"
    delta_hartree_raw: float = float("nan")
    abs_delta_hartree_raw: float = float("nan")


@dataclass
class MdValidationRoundLog:
    round_index: int
    n_train_before: int
    n_train_after: int
    n_md_frames_sampled: int
    max_abs_delta_hartree: float
    mean_abs_delta_hartree: float
    converged: bool
    training_metrics: dict[str, Any] = field(default_factory=dict)
    frames: list[FrameValidationRecord] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
