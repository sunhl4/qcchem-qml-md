"""Restricted closed-shell MO integral packs — symmetry-aware compact ``get_h2eff`` storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from openfermion import InteractionOperator
from openfermion.chem.molecular_data import spinorb_from_spatial

from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering
from qchem_stack.chem.integrals.pyscf_active_space import active_space_casci_raw_blocks
from qchem_stack.quantum.algorithms.tolerances import CUTOFF_ABS_INTEGRAL

if TYPE_CHECKING:
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult


def interaction_operator_to_dataframe(
    op: InteractionOperator,
    *,
    max_spinorb_two_body: int | None = 8000,
    cutoff_abs: float = CUTOFF_ABS_INTEGRAL,
) -> pd.DataFrame:
    """Tabular view (spin-orbital sectors) analogous to chemistry-tutorial ``df()`` previews."""
    rows: list[dict[str, Any]] = [
        {
            "sector": "constant",
            "p": None,
            "q": None,
            "r": None,
            "s": None,
            "value_Eh": float(op.constant),
        }
    ]
    ob = np.asarray(op.one_body_tensor, dtype=float)
    n = int(ob.shape[0])
    for p in range(n):
        for q in range(n):
            v = float(ob[p, q])
            if abs(v) > cutoff_abs:
                rows.append(
                    {"sector": "one_body_spin", "p": p, "q": q, "r": None, "s": None, "value_Eh": v}
                )
    tb = np.asarray(op.two_body_tensor, dtype=float)
    count = 0
    for p in range(n):
        for q in range(n):
            for r in range(n):
                for s in range(n):
                    v = float(tb[p, q, r, s])
                    if abs(v) <= cutoff_abs:
                        continue
                    rows.append(
                        {"sector": "two_body_spin", "p": p, "q": q, "r": r, "s": s, "value_Eh": v}
                    )
                    count += 1
                    if max_spinorb_two_body is not None and count >= max_spinorb_two_body:
                        return pd.DataFrame(rows)
    return pd.DataFrame(rows)


@dataclass(frozen=True)
class RestrictedActiveSpaceIntegralOperatorCompact:
    """MO active-space integrals with PySCF ``get_h2eff`` storage (compact or dense).

    This is the open-stack analogue of symmetry-backed **compact integral containers** in proprietary
    stacks: the two-electron block keeps PySCF's packed layout until :meth:`dense_h2_chemist_spatial`
    expands it for OpenFermion mapping.
    """

    constant: float
    h1_active_mo: np.ndarray
    eri_active_mo_compact: np.ndarray
    n_active_orbitals: int
    n_active_electrons: int
    symmetry_meta: dict[str, Any] = field(default_factory=dict)
    storage_schema: str = "pyscf_casci_h2eff_compact_v1"

    @classmethod
    def from_pyscf_rhf(
        cls,
        rhf: PySCFRHFResult,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> RestrictedActiveSpaceIntegralOperatorCompact:
        constant, h1, h2_raw = active_space_casci_raw_blocks(
            rhf, n_active_orbitals, n_active_electrons
        )
        mol = getattr(rhf.mf, "mol", None)
        symm_orb = getattr(mol, "symm_orb", None) if mol is not None else None
        detected = symm_orb is not None and len(symm_orb) > 0
        meta = {
            "pyscf_symmetry_detected": bool(detected),
            "pyscf_symmetry_subgroup": getattr(mol, "groupname", None) if mol is not None else None,
            "eri_raw_ndim": int(np.asarray(h2_raw).ndim),
            "eri_raw_n_elements": int(np.asarray(h2_raw).size),
        }
        return cls(
            constant=float(constant),
            h1_active_mo=np.asarray(h1, dtype=float),
            eri_active_mo_compact=np.asarray(h2_raw, dtype=float),
            n_active_orbitals=int(n_active_orbitals),
            n_active_electrons=int(n_active_electrons),
            symmetry_meta=meta,
        )

    def dense_h2_chemist_spatial(self) -> np.ndarray:
        """Chemist-notation active-space MO ERIs ``(na, na, na, na)`` (PySCF layout before OF transpose)."""
        from qchem_stack.chem.integral_convention import restore_packed_mo_eri_chemist

        x = np.asarray(self.eri_active_mo_compact, dtype=float)
        na = int(self.n_active_orbitals)
        return restore_packed_mo_eri_chemist(x, na)

    def to_interaction_operator(self) -> InteractionOperator:
        """Materialize OpenFermion :class:`InteractionOperator` in the spin-orbital basis."""
        h2_sp = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(self.dense_h2_chemist_spatial())
        h1 = np.asarray(self.h1_active_mo, dtype=float)
        h1_so, h2_so = spinorb_from_spatial(h1, h2_sp)
        return InteractionOperator(float(self.constant), h1_so, 0.5 * h2_so)

    def df_mo_integrals(
        self,
        *,
        max_two_body: int | None = 10_000,
        cutoff_abs: float = CUTOFF_ABS_INTEGRAL,
    ) -> pd.DataFrame:
        """Spatial-MO integral table (scalar / ``h1`` / ``h2`` sectors)."""
        rows: list[dict[str, Any]] = [
            {
                "sector": "constant_energy_core",
                "p": None,
                "q": None,
                "r": None,
                "s": None,
                "value_Eh": float(self.constant),
            }
        ]
        na = int(self.n_active_orbitals)
        h1 = np.asarray(self.h1_active_mo, dtype=float)
        for p in range(na):
            for q in range(na):
                v = float(h1[p, q])
                if abs(v) > cutoff_abs:
                    rows.append(
                        {"sector": "h1_mo", "p": p, "q": q, "r": None, "s": None, "value_Eh": v}
                    )
        h2 = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(self.dense_h2_chemist_spatial())
        count = 0
        for p in range(na):
            for q in range(na):
                for r in range(na):
                    for s in range(na):
                        v = float(h2[p, q, r, s])
                        if abs(v) <= cutoff_abs:
                            continue
                        rows.append(
                            {"sector": "h2_mo", "p": p, "q": q, "r": r, "s": s, "value_Eh": v}
                        )
                        count += 1
                        if max_two_body is not None and count >= max_two_body:
                            return pd.DataFrame(rows)
        return pd.DataFrame(rows)

    def df(
        self, *, mo_max_two_body: int | None = 10_000, spinorb_max_two_body: int | None = 8000
    ) -> pd.DataFrame:
        """Notebook-friendly union view: MO sectors then spin-orbital sectors (truncated)."""
        mo = self.df_mo_integrals(max_two_body=mo_max_two_body)
        mo.insert(0, "basis", "spatial_mo")
        ferm = interaction_operator_to_dataframe(
            self.to_interaction_operator(), max_spinorb_two_body=spinorb_max_two_body
        )
        ferm.insert(0, "basis", "spin_orbital_jw_order")
        return pd.concat([mo, ferm], ignore_index=True)
