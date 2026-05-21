"""Build :class:`QMEFDataset` snapshots from :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync` results."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

import yaml

from qchem_stack.contracts.schema_ids import QMEF_ML_ATTACHMENT_V1
from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult
    from qchem_stack.config import ExperimentConfig

MD_ML_MAX_EXTRA_GEOMETRIES = 48


def _is_periodic_rhf(rhf: PySCFRHFResult) -> bool:
    dm = getattr(rhf, "driver_meta", None) or {}
    if dm.get("pbc"):
        return True
    mol = rhf.mf.mol
    return type(mol).__name__ == "Cell"


def _atomic_numbers_from_pyscf_mol(rhf: PySCFRHFResult) -> list[int]:
    mol = rhf.mf.mol
    return [int(mol.atom_charge(i)) for i in range(mol.natm)]


def _hf_nuclear_forces_neg_gradient_hartree_bohr(
    rhf: PySCFRHFResult, method: str
) -> list[list[float]] | None:
    """
    Classical nuclear forces :math:`-\\partial E/\\partial R` (Hartree/Bohr) when PySCF gradients succeed.

    PySCF ``grad.*.kernel()`` returns :math:`\\partial E/\\partial R`; ML datasets conventionally store ``-grad``.
    """
    if _is_periodic_rhf(rhf):
        return None
    try:
        import numpy as np
        from pyscf import grad
    except ImportError:
        return None
    mf = rhf.mf
    try:
        if method == "RHF":
            g = grad.RHF(mf)
        elif method == "ROHF":
            g = grad.ROHF(mf)
        elif method == "UHF":
            g = grad.UHF(mf)
        else:
            return None
        arr = -np.asarray(g.kernel(), dtype=float)
        return arr.tolist()
    except Exception:
        return None


def _active_space_digest(cfg: ExperimentConfig) -> str:
    blob = json.dumps(
        cfg.active_space.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _protocol_hash_prefix(out: dict[str, Any]) -> str:
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return ""
    snap = repro.get("parity_snapshot")
    if not isinstance(snap, dict):
        return ""
    sig = snap.get("compiler_bundle_signature")
    return str(sig)[:48] if isinstance(sig, str) else ""


def _config_sha_prefix(out: dict[str, Any]) -> str:
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return ""
    return str(repro.get("config_sha256_prefix") or "")


def _normalize_coords(coords: list[list[float]]) -> list[list[float]]:
    return [[float(x), float(y), float(z)] for x, y, z in coords]


def _energy_hartree_from_pipeline_out(cfg: ExperimentConfig, out: dict[str, Any]) -> float:
    ref = cfg.md_ml_export.energy_reference
    if ref == "scf":
        scf = out.get("scf_energy")
        if scf is None:
            raise PipelineError(
                "md_ml_export.energy_reference='scf' requires scf_energy on pipeline output."
            )
        return float(scf)
    if ref == "pauli_protocol":
        if "energy_pauli_protocol" not in out:
            raise PipelineError(
                "md_ml_export.energy_reference='pauli_protocol' requires a completed Pauli stage "
                "(missing energy_pauli_protocol on pipeline output)."
            )
        return float(out["energy_pauli_protocol"])
    return float(out["energy_after_variational"])


def _rhf_at_coordinates(cfg: ExperimentConfig, coords: list[list[float]]) -> PySCFRHFResult:
    """Fresh mean-field solve at ``coords`` (same stoichiometry / charge / mult / basis / solvent / PBC as ``cfg``)."""
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.config import MdMlExportSpec

    child = cfg.model_copy(
        deep=True,
        update={
            "molecule": cfg.molecule.model_copy(
                update={"coordinates": _normalize_coords(coords), "coordinate_unit": "bohr"}
            ),
            "md_ml_export": MdMlExportSpec(),
        },
    )
    drv = PySCFDriver.from_config(child)
    if child.chemistry_extended.pbc.cell_vectors_bohr is not None:
        return drv.run_pbc_rhf()
    if child.scf.method == "RHF":
        return drv.run_rhf()
    if child.scf.method == "ROHF":
        return drv.run_rohf()
    return drv.run_uhf()


def _as_pyscf_rhf(reference: ClassicalMeanFieldReference) -> PySCFRHFResult:
    if reference.backend_tag() != "pyscf":
        raise PipelineError(
            "QMEF attachment currently requires a PySCF-backed classical reference "
            f"(got backend={reference.backend_tag()!r})."
        )
    return reference.as_pyscf_rhf_result()


def _qmframe_from_rhf(
    cfg: ExperimentConfig,
    out: dict[str, Any],
    rhf: PySCFRHFResult,
    coords: list[list[float]],
    *,
    energy_hartree: float,
    method_tag: str,
) -> QMFrame:
    zs = _atomic_numbers_from_pyscf_mol(rhf)
    forces: list[list[float]] = []
    if cfg.md_ml_export.include_hf_nuclear_gradient:
        frc = _hf_nuclear_forces_neg_gradient_hartree_bohr(rhf, str(cfg.scf.method))
        if frc is not None:
            forces = frc
    return QMFrame(
        atomic_numbers=zs,
        positions_bohr=_normalize_coords(coords),
        energy_hartree=float(energy_hartree),
        forces_hartree_bohr=forces,
        charge=int(cfg.molecule.charge),
        multiplicity=int(cfg.molecule.multiplicity),
        box=None,
        method_tag=method_tag,
        active_space_hash=_active_space_digest(cfg),
        protocol_hash=_protocol_hash_prefix(out),
        repro_config_sha256_prefix=_config_sha_prefix(out),
        backend_noise_tag=str(cfg.backend.provider),
    )


def _primary_qmframe(cfg: ExperimentConfig, out: dict[str, Any], rhf: PySCFRHFResult) -> QMFrame:
    energy = _energy_hartree_from_pipeline_out(cfg, out)
    positions = _normalize_coords(cfg.molecule.coordinates_in_bohr().tolist())
    tag = f"{cfg.scf.method}/{cfg.quantum.algorithm}/JW-{cfg.active_space.mapping.fermion_qubit}"
    return _qmframe_from_rhf(cfg, out, rhf, positions, energy_hartree=energy, method_tag=tag)


def _extra_frame_hf_scf(
    cfg: ExperimentConfig,
    out: dict[str, Any],
    coords: list[list[float]],
    *,
    index: int,
) -> QMFrame:
    rhf = _rhf_at_coordinates(cfg, coords)
    tag = f"{cfg.scf.method}/HF-SCF-trajectory[{index}]"
    return _qmframe_from_rhf(
        cfg,
        out,
        rhf,
        coords,
        energy_hartree=float(rhf.e_tot),
        method_tag=tag,
    )


def _extra_frame_full_pipeline(
    cfg: ExperimentConfig,
    primary_out: dict[str, Any],
    coords: list[list[float]],
    *,
    index: int,
    cfg_path: Path | None,
) -> QMFrame:
    from qchem_stack.config import MdMlExportSpec
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    child = cfg.model_copy(
        deep=True,
        update={
            "molecule": cfg.molecule.model_copy(
                update={"coordinates": _normalize_coords(coords), "coordinate_unit": "bohr"}
            ),
            "md_ml_export": MdMlExportSpec(),
        },
    )
    out_c = run_pipeline_sync(child, cfg_path=cfg_path)
    energy = _energy_hartree_from_pipeline_out(cfg, out_c)
    rhf_g = _rhf_at_coordinates(cfg, coords)
    forces: list[list[float]] = []
    if cfg.md_ml_export.include_hf_nuclear_gradient:
        frc = _hf_nuclear_forces_neg_gradient_hartree_bohr(rhf_g, str(cfg.scf.method))
        if frc is not None:
            forces = frc
    zs = _atomic_numbers_from_pyscf_mol(rhf_g)
    tag = f"{cfg.scf.method}/{cfg.quantum.algorithm}/JW-{cfg.active_space.mapping.fermion_qubit}/trajectory-FP[{index}]"
    return QMFrame(
        atomic_numbers=zs,
        positions_bohr=_normalize_coords(coords),
        energy_hartree=float(energy),
        forces_hartree_bohr=forces,
        charge=int(cfg.molecule.charge),
        multiplicity=int(cfg.molecule.multiplicity),
        box=None,
        method_tag=tag,
        active_space_hash=_active_space_digest(cfg),
        protocol_hash=_protocol_hash_prefix(primary_out),
        repro_config_sha256_prefix=_config_sha_prefix(primary_out),
        backend_noise_tag=str(cfg.backend.provider),
    )


def build_qmef_ml_attachment_repro_block(
    cfg: ExperimentConfig,
    out: dict[str, Any],
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> dict[str, Any]:
    """
    Canonical ``repro.qmef_ml_attachment_v1`` — one **primary** frame from the finished pipeline plus optional
    **extra** geometries (HF-SCF-only or full nested pipelines per ``md_ml_export.trajectory_theory_level``).
    """
    spec = cfg.md_ml_export
    rhf = _as_pyscf_rhf(reference)
    frames: list[QMFrame] = [_primary_qmframe(cfg, out, rhf)]
    frame_meta: list[dict[str, Any]] = [
        {
            "index": 0,
            "coordinates_source": "molecule.coordinates_bohr",
            "energy_theory": "primary_pipeline",
            "energy_reference_mode": spec.energy_reference,
            "forces_theory": "hf_rhf_analytic_same_reference_geometry"
            if spec.include_hf_nuclear_gradient
            else "none",
        }
    ]

    for i, raw_coords in enumerate(spec.trajectory.extra_coordinates_bohr):
        coords = _normalize_coords(raw_coords)
        idx = i + 1
        if spec.trajectory.theory_level == "full_pipeline":
            frames.append(_extra_frame_full_pipeline(cfg, out, coords, index=i, cfg_path=cfg_path))
            fm_energy = "nested_full_pipeline"
        else:
            frames.append(_extra_frame_hf_scf(cfg, out, coords, index=i))
            fm_energy = "hf_scf_only"
        frame_meta.append(
            {
                "index": idx,
                "coordinates_source": f"md_ml_export.extra_coordinates_bohr[{i}]",
                "energy_theory": fm_energy,
                "energy_reference_mode": spec.energy_reference
                if fm_energy == "nested_full_pipeline"
                else "scf_total",
                "forces_theory": (
                    "hf_rhf_analytic_same_geometry" if spec.include_hf_nuclear_gradient else "none"
                ),
            }
        )

    prov = yaml.safe_dump(
        {
            "experiment_id": cfg.experiment_id,
            "md_ml_export": spec.model_dump(mode="json"),
            "n_frames": len(frames),
            "frame_meta": frame_meta,
        },
        sort_keys=False,
        allow_unicode=True,
    )
    ds = QMEFDataset(frames=frames, provenance_yaml=prov)

    epistemic = (
        "QMEF attachment: frame 0 uses the primary pipeline geometry; "
        f"energy for frame 0 follows md_ml_export.energy_reference ({spec.energy_reference}: variational | scf | pauli_protocol). "
        "Pauli energy requires quantum.pauli.use_protocol and a completed Pauli stage. "
        "Extra frames use md_ml_export.extra_coordinates_bohr; trajectory_theory_level hf_scf runs PySCF mean-field only "
        "per geometry; full_pipeline re-invokes run_pipeline_sync per geometry (cost scales linearly; nested jobs do not attach QMEF). "
        "When include_hf_nuclear_gradient is true, forces are analytic HF −∂E/∂R (Hartree/Bohr) at that geometry's RHF reference "
        "(including after nested full_pipeline energies); non-PBC only; failures yield empty forces."
    )

    return {
        "schema": QMEF_ML_ATTACHMENT_V1,
        "epistemic_bound": epistemic,
        "frame_meta": frame_meta,
        "dataset": ds.model_dump(mode="json"),
    }


def build_qmef_dataset_single_frame_repro_block(
    cfg: ExperimentConfig,
    out: dict[str, Any],
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> dict[str, Any]:
    """Backward-compatible name — delegates to :func:`build_qmef_ml_attachment_repro_block`."""
    return build_qmef_ml_attachment_repro_block(cfg, out, reference, cfg_path=cfg_path)


__all__ = [
    "MD_ML_MAX_EXTRA_GEOMETRIES",
    "build_qmef_dataset_single_frame_repro_block",
    "build_qmef_ml_attachment_repro_block",
]
