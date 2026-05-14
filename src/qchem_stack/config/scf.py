"""SCF driver selection and mean-field convergence controls."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SCFSpec(BaseModel):
    """Classical Hartree–Fock driver selection (Hamiltonian build path is PySCF-first today)."""

    driver: Literal["pyscf", "psi4"] = "pyscf"
    method: Literal["RHF", "ROHF", "UHF"] = "RHF"
    max_cycle: int | None = Field(
        default=None,
        ge=1,
        le=512,
        description="Optional PySCF ``mf.max_cycle`` override (open-shell / transition-metal SCF).",
    )
    chkfile: str | None = Field(
        default=None,
        description="Optional PySCF checkpoint path (``mf.chkfile``).",
    )
    init_guess: str | None = Field(
        default=None,
        description=(
            "Optional PySCF ``mf.init_guess`` token (e.g. ``minao``, ``atom``, ``huckel``, ``chkfile``)."
        ),
    )
    level_shift: float | None = Field(
        default=None,
        description="Optional mean-field ``level_shift`` when supported by PySCF SCF objects.",
    )
    use_newton: bool = Field(
        default=False,
        description="If True and method is RHF/ROHF, use ``scf.RHF(...).newton()`` pipeline when available.",
    )
    diis_space_dimension: int | None = Field(
        default=None,
        ge=2,
        description="Optional ``mf.diis_space`` dimension override (PySCF-dependent).",
    )
    density_fit: bool = Field(
        default=False,
        description="Enable density-fitting / RI SCF when supported by the selected backend.",
    )
    density_fit_auxbasis: str | None = Field(
        default=None,
        description="Optional auxiliary basis for density-fitting (PySCF ``mf.density_fit(auxbasis=...)``).",
    )

    @model_validator(mode="after")
    def _density_fit_auxbasis_consistency(self) -> SCFSpec:
        if self.density_fit_auxbasis and not self.density_fit:
            raise ValueError("scf.density_fit_auxbasis requires scf.density_fit=true.")
        return self
