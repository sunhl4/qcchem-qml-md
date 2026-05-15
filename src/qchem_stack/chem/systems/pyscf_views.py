from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from qchem_stack.chem.system import MolecularSystem


@dataclass
class PySCFAOSystem:
    """AO-oriented handle that keeps the underlying PySCF SCF object accessible."""

    mf: Any
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
    has_run_hf: bool = True
    e_tot: float | None = None

    def ao_driver_summary_df(self) -> Any:
        """Notebook-friendly AO/system descriptor (cf. tutorials wrapping ``mf`` / ``mol``)."""
        import pandas as pd

        mol = self.mf.mol
        rows = [
            {"quantity": "nao_nr", "value": int(mol.nao_nr())},
            {"quantity": "nelectron", "value": int(mol.nelectron)},
            {"quantity": "spin", "value": int(mol.spin)},
            {"quantity": "basis_repr", "value": str(mol.basis)},
            {"quantity": "groupname", "value": getattr(mol, "groupname", None)},
            {
                "quantity": "integral_representation",
                "value": self.driver_meta.get("integral_representation"),
            },
            {"quantity": "ao_reference_kind", "value": self.driver_meta.get("ao_reference_kind")},
            {"quantity": "ao_run_hf", "value": self.driver_meta.get("ao_run_hf")},
        ]
        return pd.DataFrame(rows)


@dataclass
class PySCFLowdinSystem:
    """Löwdin-orthogonal AO representation for embedding-style workflows."""

    constant: float
    h1_spatial: np.ndarray
    h2_spatial: np.ndarray
    rdm1_spatial: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
