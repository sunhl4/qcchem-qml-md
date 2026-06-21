"""Pure extraction helpers for QMEF frames from pipeline outputs."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any, cast

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.schema import QMFrame

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.md_bridge.from_pipeline_types import PipelineOut


def as_out_dict(out: PipelineOut) -> dict[str, Any]:
    return cast("dict[str, Any]", out)


def is_periodic_rhf(rhf: PySCFRHFResult) -> bool:
    dm = getattr(rhf, "driver_meta", None) or {}
    if dm.get("pbc"):
        return True
    mol = rhf.mf.mol
    return type(mol).__name__ == "Cell"


def atomic_numbers_from_pyscf_mol(rhf: PySCFRHFResult) -> list[int]:
    mol = rhf.mf.mol
    return [int(mol.atom_charge(i)) for i in range(mol.natm)]


def hf_nuclear_forces_neg_gradient_hartree_bohr(
    rhf: PySCFRHFResult, method: str
) -> list[list[float]] | None:
    """
    Classical nuclear forces :math:`-\\partial E/\\partial R` (Hartree/Bohr) when PySCF gradients succeed.

    PySCF ``grad.*.kernel()`` returns :math:`\\partial E/\\partial R`; ML datasets conventionally store ``-grad``.
    """
    if is_periodic_rhf(rhf):
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
        return cast("list[list[float]]", arr.tolist())
    except (np.linalg.LinAlgError, ValueError, TypeError) as exc:
        _log = __import__("logging").getLogger(__name__)
        _log.warning("kernel matrix computation failed, returning None: %s", exc)
        return None


def active_space_digest(cfg: ExperimentConfig) -> str:
    blob = json.dumps(
        cfg.active_space.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def protocol_hash_prefix(out: PipelineOut) -> str:
    repro = as_out_dict(out).get("repro")
    if not isinstance(repro, dict):
        return ""
    snap = repro.get("parity_snapshot")
    if not isinstance(snap, dict):
        return ""
    sig = snap.get("compiler_bundle_signature")
    return str(sig)[:48] if isinstance(sig, str) else ""


def config_sha_prefix(out: PipelineOut) -> str:
    repro = as_out_dict(out).get("repro")
    if not isinstance(repro, dict):
        return ""
    return str(repro.get("config_sha256_prefix") or "")


def normalize_coords(coords: list[list[float]]) -> list[list[float]]:
    return [[float(x), float(y), float(z)] for x, y, z in coords]


def energy_hartree_from_pipeline_out(cfg: ExperimentConfig, out: PipelineOut) -> float:
    out_d = as_out_dict(out)
    ref = cfg.md_ml_export.energy_reference
    if ref == "scf":
        scf = out_d.get("scf_energy")
        if scf is None:
            raise PipelineError(
                "md_ml_export.energy_reference='scf' requires scf_energy on pipeline output."
            )
        return float(scf)
    if ref == "pauli_protocol":
        if "energy_pauli_protocol" not in out_d:
            raise PipelineError(
                "md_ml_export.energy_reference='pauli_protocol' requires a completed Pauli stage "
                "(missing energy_pauli_protocol on pipeline output)."
            )
        return float(out_d["energy_pauli_protocol"])
    energy_var = out_d.get("energy_after_variational")
    if energy_var is None:
        raise PipelineError("md_ml_export requires energy_after_variational on pipeline output.")
    return float(energy_var)


def rhf_at_coordinates(cfg: ExperimentConfig, coords: list[list[float]]) -> PySCFRHFResult:
    """Fresh mean-field solve at ``coords`` (same stoichiometry / charge / mult / basis / solvent / PBC as ``cfg``)."""
    from qchem_stack.chem.bridges.reference_factory import pyscf_rhf_result_from_config
    from qchem_stack.config import MdMlExportSpec

    child = cfg.model_copy(
        deep=True,
        update={
            "molecule": cfg.molecule.model_copy(
                update={"coordinates": normalize_coords(coords), "coordinate_unit": "bohr"}
            ),
            "md_ml_export": MdMlExportSpec(),
        },
    )
    return pyscf_rhf_result_from_config(child)


def as_pyscf_rhf(reference: ClassicalMeanFieldReference) -> PySCFRHFResult:
    if reference.backend_tag() != "pyscf":
        raise PipelineError(
            "QMEF attachment currently requires a PySCF-backed classical reference "
            f"(got backend={reference.backend_tag()!r})."
        )
    return reference.as_pyscf_rhf_result()


def qmframe_from_rhf(
    cfg: ExperimentConfig,
    out: PipelineOut,
    rhf: PySCFRHFResult,
    coords: list[list[float]],
    *,
    energy_hartree: float,
    method_tag: str,
) -> QMFrame:
    zs = atomic_numbers_from_pyscf_mol(rhf)
    forces: list[list[float]] = []
    if cfg.md_ml_export.include_hf_nuclear_gradient:
        frc = hf_nuclear_forces_neg_gradient_hartree_bohr(rhf, str(cfg.scf.method))
        if frc is not None:
            forces = frc
    return QMFrame(
        atomic_numbers=zs,
        positions_bohr=normalize_coords(coords),
        energy_hartree=float(energy_hartree),
        forces_hartree_bohr=forces,
        charge=int(cfg.molecule.charge),
        multiplicity=int(cfg.molecule.multiplicity),
        box=None,
        method_tag=method_tag,
        active_space_hash=active_space_digest(cfg),
        protocol_hash=protocol_hash_prefix(out),
        repro_config_sha256_prefix=config_sha_prefix(out),
        backend_noise_tag=str(cfg.backend.provider),
    )


def primary_qmframe(cfg: ExperimentConfig, out: PipelineOut, rhf: PySCFRHFResult) -> QMFrame:
    energy = energy_hartree_from_pipeline_out(cfg, out)
    positions = normalize_coords(cfg.molecule.coordinates_in_bohr().tolist())
    tag = f"{cfg.scf.method}/{cfg.quantum.algorithm}/JW-{cfg.active_space.mapping.fermion_qubit}"
    return qmframe_from_rhf(cfg, out, rhf, positions, energy_hartree=energy, method_tag=tag)


__all__ = [
    "active_space_digest",
    "as_out_dict",
    "as_pyscf_rhf",
    "atomic_numbers_from_pyscf_mol",
    "config_sha_prefix",
    "energy_hartree_from_pipeline_out",
    "hf_nuclear_forces_neg_gradient_hartree_bohr",
    "is_periodic_rhf",
    "normalize_coords",
    "primary_qmframe",
    "protocol_hash_prefix",
    "qmframe_from_rhf",
    "rhf_at_coordinates",
]
