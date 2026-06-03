"""Two-layer ONIOM demo: classical MM shell energy + QM pipeline (open-stack partial).

When ``embedding.oniom_layers_v1`` declares QM and MM layers, the pipeline still runs the
standard mean-field → active-space → variational path on the full molecule; this module adds
an explicit classical MM pair-energy term into ``energy_components_v1`` for bookkeeping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.tolerances import ONIOM_BOND_LENGTH_TOLERANCE
from qchem_stack.contracts.schema_ids import ENERGY_COMPONENTS_V1, ONIOM_TOY_V1

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def _layer_atom_indices(layer: dict[str, Any], n_atoms: int) -> list[int]:
    raw = layer.get("atom_indices")
    if raw is not None:
        return [int(i) for i in raw]
    frag = str(layer.get("fragment_ids", [""])[0] if layer.get("fragment_ids") else "")
    if frag == "qm_core":
        return list(range(n_atoms // 2))
    if frag == "mm_shell":
        return list(range(n_atoms // 2, n_atoms))
    return []


def oniom_atom_groups_from_layers(
    layers: list[dict[str, Any]], *, n_atoms: int
) -> tuple[list[int], list[int]]:
    """Resolve QM and MM atom index lists from ``oniom_layers_v1`` layer dicts."""
    qm: list[int] = []
    mm: list[int] = []
    for layer in layers:
        role = str(layer.get("role", "")).upper()
        indices = _layer_atom_indices(layer, n_atoms)
        if role == "QM":
            qm.extend(indices)
        elif role == "MM":
            mm.extend(indices)
    qm = sorted(set(qm))
    mm = sorted(set(mm))
    if not qm or not mm:
        raise ValueError(
            "oniom_layers_v1 requires at least one QM layer and one MM layer with resolvable atom_indices"
        )
    return qm, mm


def classical_mm_pair_energy_au(
    coordinates_bohr: np.ndarray,
    mm_atom_indices: list[int],
    *,
    scale_au: float = 0.002,
) -> float:
    """Toy classical MM: harmonic pair repulsion between MM atoms (Hartree)."""
    if len(mm_atom_indices) < 2:
        return 0.0
    coords = np.asarray(coordinates_bohr, dtype=float)
    e_mm = 0.0
    for i, ai in enumerate(mm_atom_indices):
        for bi in mm_atom_indices[i + 1 :]:
            r = float(np.linalg.norm(coords[bi] - coords[ai]))
            if r < ONIOM_BOND_LENGTH_TOLERANCE:
                continue
            # Soft repulsion: grows as 1/r^2 (arbitrary classical MM stub).
            e_mm += float(scale_au) / (r * r)
    return float(e_mm)


def attach_classical_mm_to_energy_components(
    energy_components: dict[str, Any],
    *,
    classical_mm_energy_au: float,
    qm_atom_indices: list[int],
    mm_atom_indices: list[int],
) -> dict[str, Any]:
    """Return a copy of ``energy_components_v1`` with MM bookkeeping fields."""
    if energy_components.get("schema") != ENERGY_COMPONENTS_V1:
        raise ValueError(f"expected schema {ENERGY_COMPONENTS_V1!r}")
    out = dict(energy_components)
    out["classical_mm_energy_au"] = float(classical_mm_energy_au)
    out["embedding_correction_au"] = float(classical_mm_energy_au)
    out["oniom_accounting_model"] = "qm_mean_field_plus_classical_mm_pair_stub"
    out["oniom_qm_atom_indices"] = list(qm_atom_indices)
    out["oniom_mm_atom_indices"] = list(mm_atom_indices)
    out["note"] = (
        "ONIOM two-layer partial ledger: QM region uses mean_field_total_au; "
        "MM region adds classical_mm_energy_au (harmonic pair stub, not a full force field)."
    )
    return out


def oniom_three_layer_atom_groups(
    layers: list[dict[str, Any]], *, n_atoms: int
) -> tuple[list[int], list[int], list[int]]:
    """Resolve QM / MM / MM2 atom lists from three ONIOM layers."""
    qm: list[int] = []
    mm: list[int] = []
    mm2: list[int] = []
    for layer in layers:
        role = str(layer.get("role", "")).upper()
        indices = _layer_atom_indices(layer, n_atoms)
        if role == "QM":
            qm.extend(indices)
        elif role in {"MM", "MM1"}:
            mm.extend(indices)
        elif role in {"MM2", "LOW"}:
            mm2.extend(indices)
    return sorted(set(qm)), sorted(set(mm)), sorted(set(mm2))


def enrich_energy_components_oniom_if_configured(
    cfg: ExperimentConfig,
    coordinates_bohr: np.ndarray,
    energy_components: dict[str, Any],
) -> dict[str, Any]:
    """Add classical MM term when ``embedding.oniom_layers_v1`` is non-empty."""
    layers = list(cfg.embedding.oniom_layers_v1 or [])
    if not layers:
        return energy_components
    n_atoms = int(np.asarray(coordinates_bohr).shape[0])
    qm_idx, mm_idx = oniom_atom_groups_from_layers(layers, n_atoms=n_atoms)
    e_mm = classical_mm_pair_energy_au(coordinates_bohr, mm_idx)
    if len(layers) >= 3:
        _, _, mm2_idx = oniom_three_layer_atom_groups(layers, n_atoms=n_atoms)
        e_mm += classical_mm_pair_energy_au(coordinates_bohr, mm2_idx, scale_au=0.001)
    return attach_classical_mm_to_energy_components(
        energy_components,
        classical_mm_energy_au=e_mm,
        qm_atom_indices=qm_idx,
        mm_atom_indices=mm_idx,
    )


def oniom_two_layer_workflow_v1(
    cfg: ExperimentConfig,
    *,
    classical_mm_energy_au: float,
    qm_atom_indices: list[int],
    mm_atom_indices: list[int],
) -> dict[str, Any]:
    """Sidecar payload for ``embedding_workflow`` (beyond ``oniom_toy_v1`` metadata)."""
    return {
        "schema": "oniom_two_layer_v1",
        "layers": [dict(x) for x in cfg.embedding.oniom_layers_v1],
        "classical_mm_energy_au": float(classical_mm_energy_au),
        "qm_atom_indices": list(qm_atom_indices),
        "mm_atom_indices": list(mm_atom_indices),
        "toy_layers_schema": ONIOM_TOY_V1,
    }
