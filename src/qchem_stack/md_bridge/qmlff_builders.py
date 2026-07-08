"""QML-FF model construction helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

ForceFieldBackend = Literal[
    "qmlff_preset",
    "qmlff_quantum",
    "qmlff_angle",
    "qmlff_qmp_h2",
    "classical_h2",
]

_Z_TO_SYMBOL = {
    1: "H",
    2: "He",
    3: "Li",
    4: "Be",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    10: "Ne",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    18: "Ar",
    19: "K",
    20: "Ca",
    26: "Fe",
    27: "Co",
    28: "Ni",
    29: "Cu",
}
_SYMBOL_TO_Z = {v: k for k, v in _Z_TO_SYMBOL.items()}


def _require_qmlff() -> Any:
    """Import qmlff lazily; raise a helpful error if unavailable."""
    try:
        import qmlff  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via tests when qmlff present
        raise ImportError(
            "qmlff is not installed. Install the QML-FF project (sibling repo), e.g.:\n"
            "  pip install -e /path/to/QML-FF\n"
            "or set PYTHONPATH=/path/to/QML-FF before launching."
        ) from exc
    import qmlff as _q

    return _q


def atomic_number_to_symbol(z: int) -> str:
    """Best-effort Z → element-symbol lookup (returns ``'X'`` for unknown)."""
    return _Z_TO_SYMBOL.get(int(z), "X")


def symbol_to_atomic_number(sym: str) -> int:
    """Best-effort element-symbol → Z lookup (returns ``0`` for unknown)."""
    return _SYMBOL_TO_Z.get(str(sym), 0)


@dataclass
class QmlffModelHandle:
    """Opaque handle wrapping a QML-FF model + parameters + species table.

    Holding the raw ``qmlff`` model in a typed-only field keeps ``qchem_stack``
    importable when QML-FF is absent (the handle is only created inside
    ``build_qmlff_model_from_preset`` after a successful import).
    """

    model: Any
    params: dict[str, Any]
    species_list: list[str]
    preset_name: str = "atomic_amplitude"
    backend: ForceFieldBackend = "qmlff_preset"
    train_meta: dict[str, Any] = field(default_factory=dict)
    energy_norm_params: dict[str, Any] | None = None
    """QML-FF ``normalize_energies`` params; apply on predict when set."""
    opt_state: Any | None = None
    step: int = 0
    epoch: int = 0

    def species_indices(self, atomic_numbers: Sequence[int]) -> np.ndarray:
        """Map a list of Z to QML-FF ``species_list`` integer indices."""
        idx: list[int] = []
        for z in atomic_numbers:
            sym = atomic_number_to_symbol(int(z))
            if sym not in self.species_list:
                raise ValueError(
                    f"atomic_number {z} (symbol {sym!r}) not present in "
                    f"QML-FF species_list={self.species_list!r}; rebuild the model "
                    "with species_list covering all elements you will simulate."
                )
            idx.append(self.species_list.index(sym))
        return np.asarray(idx, dtype=np.int32)


def build_qmlff_model_angle(
    species_list: Sequence[str],
    *,
    preset: str = "atomic_amplitude",
    **builder_overrides: Any,
) -> QmlffModelHandle:
    """Atomic descriptor + **angle** encoding (more robust than amplitude on H2)."""
    _require_qmlff()
    from qmlff.api import ModelBuilder
    from qmlff.core.encoding.base import AngleEncoderConfig

    species_list = list(species_list)
    mod = __import__(f"qmlff.config.presets.{preset}", fromlist=["get_config"])
    config = mod.get_config(species_list=species_list, **builder_overrides)
    config.encoder = AngleEncoderConfig()
    model = ModelBuilder(config).build()
    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(getattr(model, "species_list", species_list)),
        preset_name=f"{preset}_angle",
        backend="qmlff_angle",
    )


def build_qmp_h2_model(
    species_list: Sequence[str],
    qmp_overrides: dict[str, Any] | None = None,
) -> QmlffModelHandle:
    """QML-FF Schur Scheme B QMP path (H2-native equivariant architecture)."""
    _require_qmlff()
    import jax
    from qmlff.models import SchurSchemeBQMLFF, SchurSchemeBQMLFFConfig

    overrides = dict(qmp_overrides or {})
    species_list = list(species_list or ["H"])
    cfg = SchurSchemeBQMLFFConfig(**overrides)
    model = SchurSchemeBQMLFF(config=cfg, species_list=species_list)
    if not hasattr(model, "cutoff"):
        model.cutoff = float(cfg.cutoff)
    key = jax.random.PRNGKey(int(overrides.get("seed", cfg.seed)))
    params = model.init_params(key)
    model.set_parameters(params)
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(species_list),
        preset_name="qmp_h2_schur_b",
        backend="qmlff_qmp_h2",
    )


def build_qmlff_model_quantum_ff(
    species_list: Sequence[str],
    *,
    n_qubits: int = 5,
    n_layers: int = 4,
    cutoff: float = 6.0,
    encoding_type: str = "angle",
    **kwargs: Any,
) -> QmlffModelHandle:
    """QML-FF ``QuantumForceField`` — same class as ``h2_complete_workflow`` / ``train.py``."""
    _require_qmlff()
    from qmlff.models import QuantumForceField

    species_list = list(species_list or ["H"])
    model = QuantumForceField(
        n_qubits=int(n_qubits),
        n_layers=int(n_layers),
        cutoff=float(cutoff),
        species_list=species_list,
        encoding_type=str(encoding_type),
        **kwargs,
    )
    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(species_list),
        preset_name="quantum_force_field",
        backend="qmlff_quantum",
    )


def build_force_field_handle(
    species_list: Sequence[str],
    *,
    backend: ForceFieldBackend = "qmlff_preset",
    preset: str = "atomic_amplitude",
    builder_overrides: dict[str, Any] | None = None,
    qmp_h2_overrides: dict[str, Any] | None = None,
) -> Any:
    """Dispatch to preset, angle, QMP-H2, or classical Morse backends."""
    overrides = dict(builder_overrides or {})
    if backend == "classical_h2":
        from qchem_stack.md_bridge.classical_h2_ff import build_classical_h2_handle

        return build_classical_h2_handle(species_list)
    if backend == "qmlff_angle":
        return build_qmlff_model_angle(species_list, preset=preset, **overrides)
    if backend == "qmlff_quantum":
        return build_qmlff_model_quantum_ff(species_list, **overrides)
    if backend == "qmlff_qmp_h2":
        return build_qmp_h2_model(species_list, qmp_h2_overrides)
    return build_qmlff_model_from_preset(species_list, preset=preset, **overrides)


def build_qmlff_model_from_preset(
    species_list: Sequence[str],
    *,
    preset: str = "atomic_amplitude",
    **builder_overrides: Any,
) -> QmlffModelHandle:
    """Construct a QML-FF model via ``qmlff.api.ModelBuilder.from_preset``.

    Args:
        species_list: ordered element symbols, e.g. ``["H", "O"]``.
        preset: ``atomic_amplitude`` | ``e3nn_chemical`` | ``equivariant``.
        builder_overrides: forwarded to the preset ``get_config(**overrides)``.

    Returns:
        :class:`QmlffModelHandle` with initial parameters from the model.
    """
    _require_qmlff()
    from qmlff.api import ModelBuilder

    species_list = list(species_list)
    if not species_list:
        raise ValueError("species_list must be non-empty (e.g. ['H'] for hydrogen)")

    builder = ModelBuilder.from_preset(preset, species_list=species_list, **builder_overrides)
    # Presets default device_name="auto"; resolve before qml.device() (HPC CPU has no "auto" plugin).
    try:
        from qmlff.utils.runtime_devices import resolve_quantum_device

        device_name = str(getattr(builder.config, "device_name", "auto")).strip()
        if device_name.lower() == "auto":
            builder.config.device_name = resolve_quantum_device("auto")
    except ImportError:
        pass
    model = builder.build()

    if hasattr(model, "descriptor") and hasattr(model, "n_qubits"):
        _qdim = int(getattr(model.descriptor, "quantum_dim", 0))
        _max_amp = 2 ** int(model.n_qubits)
        if _qdim > _max_amp:
            raise ValueError(
                f"QML-FF preset {preset!r} needs at least {_qdim} amplitude dimensions "
                f"(descriptor quantum_dim={_qdim}, requires n_qubits>="
                f"{int(np.ceil(np.log2(_qdim)))}), but circuit n_qubits={model.n_qubits} "
                f"(max {_max_amp}). Increase qmlff_builder_overrides.n_qubits or shrink the "
                "descriptor (n_radial_basis / n_angular_basis)."
            )

    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(getattr(model, "species_list", species_list)),
        preset_name=str(preset),
        backend="qmlff_preset",
    )
