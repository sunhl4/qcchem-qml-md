from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ChemistryExtendedSpec, ExperimentConfig


@dataclass
class PySCFRHFResult:
    mf: Any
    e_tot: float
    mo_energy: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
    """e.g. ``ddcosmo`` flags — parity with InQuanto-PySCF *surface* (not product parity)."""


def _require_pyscf() -> Any:
    try:
        from pyscf import gto, scf
    except ImportError as e:  # pragma: no cover
        raise ImportError("PySCF is required for PySCFDriver. Install with: pip install qchem-stack[chem]") from e
    return gto, scf


def active_space_integrals(
    rhf: PySCFRHFResult,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return (constant, h1_spatial, h2_spatial) for OpenFermion ``InteractionOperator``.

    ``h2_spatial[p,q,r,s]`` is chemists' notation (pq|rs) over active spatial orbitals.
    ``constant`` is PySCF CASCI ``energy_core`` from ``get_h1eff`` (nuclear repulsion plus
    inactive-core contributions when ``ncore > 0``); it must not be summed again with ``energy_nuc``.
    """
    from pyscf import mcscf

    mf = rhf.mf
    meta = getattr(rhf, "driver_meta", None) or {}
    ik = int(meta.get("pbc_active_space_kpoint_index", 0))
    mo_coeff = mf.mo_coeff
    if isinstance(mo_coeff, np.ndarray):
        mo = mo_coeff
    else:
        moc = list(mo_coeff)
        if ik >= len(moc):
            ik = 0
        mo = np.asarray(moc[ik], dtype=complex)
        if np.max(np.abs(mo.imag)) < 1e-10:
            mo = np.asarray(mo.real, dtype=float)
    n_mo = int(mo.shape[1])
    if n_active_orbitals > n_mo:
        raise ValueError("active orbitals exceed MO count at chosen k-point")
    cas = mcscf.CASCI(mf, n_active_orbitals, n_active_electrons)
    h1, e_core = cas.get_h1eff(mo)
    h2 = cas.get_h2eff(mo)
    h1a = np.asarray(h1, dtype=complex)
    h2a = np.asarray(h2, dtype=complex)
    for label, arr in (("h1", h1a), ("h2", h2a)):
        if np.max(np.abs(arr.imag)) > 1e-7:
            raise ValueError(
                f"Active space {label} has non-trivial imaginary part; use Gamma (mesh [1,1,1]) or a real k-point."
            )
    # ``e_core`` from ``CASCI.get_h1eff`` / ``h1e_for_cas`` already starts at
    # ``energy_nuc()`` and adds inactive-orbital contributions when ``ncore > 0``;
    # do not add ``mol.energy_nuc()`` again (would double-count nuclear repulsion).
    constant = float(e_core)
    h1_out = np.asarray(h1a.real, dtype=float)
    h2_real = np.asarray(h2a.real, dtype=float)
    # PySCF 2.x ``get_h2eff`` often returns chemists' ERIs in compact 2D form
    # (``n * (n + 1) // 2`` square); OpenFermion expects full ``(n, n, n, n)``.
    n_act = int(n_active_orbitals)
    if h2_real.ndim == 4:
        h2_out = h2_real
    elif h2_real.ndim == 2:
        from pyscf import ao2mo

        h2_out = np.asarray(ao2mo.restore(1, h2_real, n_act), dtype=float)
    else:
        raise ValueError(f"unexpected active-space h2 shape {h2_real.shape} (ndim={h2_real.ndim})")
    return constant, h1_out, h2_out


class PySCFDriver:
    """Minimal PySCF RHF/ROHF/UHF driver behind extension boundary."""

    def __init__(
        self,
        system: MolecularSystem,
        method: Literal["RHF", "ROHF", "UHF"] = "RHF",
        chemistry_extended: ChemistryExtendedSpec | None = None,
    ) -> None:
        self.system = system
        self.method = method
        self.chemistry_extended = chemistry_extended or ChemistryExtendedSpec()

    @classmethod
    def from_config(cls, cfg: ExperimentConfig) -> PySCFDriver:
        m = cfg.molecule
        sys = MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.array(m.coordinates_bohr, dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
        )
        return cls(sys, method=cfg.scf.method, chemistry_extended=cfg.chemistry_extended)

    def _make_mol(self, gto: Any) -> Any:
        parts = []
        for sym, xyz in zip(self.system.symbols, self.system.coordinates_bohr, strict=True):
            parts.append(f"{sym} {float(xyz[0]):.12f} {float(xyz[1]):.12f} {float(xyz[2]):.12f}")
        atom = "; ".join(parts)
        return gto.M(
            atom=atom,
            basis=self.system.basis,
            charge=self.system.charge,
            spin=self.system.multiplicity - 1,
            unit="Bohr",
        )

    def _run_mean_field(self) -> PySCFRHFResult:
        gto, scf = _require_pyscf()
        mol = self._make_mol(gto)
        if self.method == "RHF":
            mf = scf.RHF(mol)
        elif self.method == "ROHF":
            mf = scf.ROHF(mol)
        else:
            mf = scf.UHF(mol)
        meta: dict[str, Any] = {}
        if self.chemistry_extended.solvent_model == "ddcosmo":
            from pyscf import solvent

            mf = solvent.ddCOSMO(mf)
            mf.with_solvent.eps = float(self.chemistry_extended.ddcosmo_epsilon)
            meta["solvent"] = "ddcosmo"
            meta["ddcosmo_epsilon"] = float(self.chemistry_extended.ddcosmo_epsilon)
        e = float(mf.kernel())
        return PySCFRHFResult(
            mf=mf, e_tot=e, mo_energy=mf.mo_energy, molecular_system=self.system, driver_meta=meta
        )

    def run_rhf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def run_rohf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def run_uhf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def _make_pbc_cell(self, gto_pbc: Any) -> Any:
        pbc = self.chemistry_extended.pbc_cell_vectors_bohr
        assert pbc is not None
        a = np.asarray(pbc, dtype=float)
        parts = []
        for sym, xyz in zip(self.system.symbols, self.system.coordinates_bohr, strict=True):
            parts.append(f"{sym} {float(xyz[0]):.12f} {float(xyz[1]):.12f} {float(xyz[2]):.12f}")
        atom = "; ".join(parts)
        return gto_pbc.M(
            atom=atom,
            a=a,
            basis=self.system.basis,
            charge=self.system.charge,
            spin=self.system.multiplicity - 1,
            unit="Bohr",
        )

    def run_pbc_rhf(self) -> PySCFRHFResult:
        """
        PySCF :mod:`pyscf.pbc` mean field: ``RHF`` at Γ if ``pbc_kpoint_mesh`` is ``[1,1,1]``,
        else :class:`pyscf.pbc.scf.khf.KRHF` with ``cell.make_kpts``.

        Optional :class:`pyscf.solvent.ddCOSMO` is applied when ``solvent_model==ddcosmo`` (PySCF-dependent).
        """
        pbc = self.chemistry_extended.pbc_cell_vectors_bohr
        if pbc is None:
            raise ValueError("run_pbc_rhf requires chemistry_extended.pbc_cell_vectors_bohr")
        if self.method != "RHF":
            raise ValueError("Open-stack PBC driver uses scf.method=RHF for the periodic branch (KRHF/k-mesh).")
        try:
            from pyscf.pbc import gto as pbc_gto
            from pyscf.pbc import scf as pbc_scf
        except ImportError as e:  # pragma: no cover
            raise ImportError("PySCF with pbc is required. Install with: pip install qchem-stack[chem]") from e
        cell = self._make_pbc_cell(pbc_gto)
        cell.build()
        mesh = list(self.chemistry_extended.pbc_kpoint_mesh)
        if any(m < 1 for m in mesh):
            raise ValueError("pbc_kpoint_mesh entries must be >= 1")
        use_k = max(mesh) > 1
        if use_k:
            kpts = cell.make_kpts(mesh)
            mf = pbc_scf.khf.KRHF(cell, kpts)
            kpa = np.asarray(kpts)
            n_k = int(kpa.shape[0])
        else:
            mf = pbc_scf.hf.RHF(cell)
            n_k = 1
        meta: dict[str, Any] = {
            "pbc": True,
            "gamma_only": not use_k,
            "pbc_kpoint_mesh": mesh,
            "n_kpoints": n_k,
            "pbc_active_space_kpoint_index": int(self.chemistry_extended.pbc_active_space_kpoint_index),
            "cell_vectors_bohr": [list(map(float, row)) for row in pbc],
        }
        if self.chemistry_extended.pbc_active_space_kpoint_index >= n_k:
            raise ValueError(
                f"pbc_active_space_kpoint_index={self.chemistry_extended.pbc_active_space_kpoint_index} "
                f"out of range for n_kpoints={n_k}"
            )
        if self.chemistry_extended.solvent_model == "ddcosmo":
            from pyscf import solvent

            try:
                mf = solvent.ddCOSMO(mf)
                mf.with_solvent.eps = float(self.chemistry_extended.ddcosmo_epsilon)
                meta["solvent"] = "ddcosmo"
                meta["ddcosmo_epsilon"] = float(self.chemistry_extended.ddcosmo_epsilon)
            except Exception as e:  # noqa: BLE001
                raise RuntimeError(
                    "ddCOSMO on this periodic mean-field object failed in your PySCF build. "
                    "Use chemistry_extended.solvent_model=none for PBC, or a PySCF version that supports it."
                ) from e
        e = float(mf.kernel())
        mo_e = mf.mo_energy
        if isinstance(mo_e, (list, tuple)):
            ik = int(self.chemistry_extended.pbc_active_space_kpoint_index)
            mo_e_out = np.asarray(mo_e[ik], dtype=float)
        else:
            mo_e_out = np.asarray(mo_e, dtype=float)
        return PySCFRHFResult(
            mf=mf,
            e_tot=e,
            mo_energy=mo_e_out,
            molecular_system=self.system,
            driver_meta=meta,
        )
