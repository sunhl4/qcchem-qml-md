"""Backend-neutral AO / MO primitives for embedding and active-space hooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, cast, runtime_checkable

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


@runtime_checkable
class AOBasisView(Protocol):
    """Minimal AO basis API shared by PySCF and Psi4 mean-field references."""

    @property
    def backend_tag(self) -> str: ...

    @property
    def n_atom(self) -> int: ...

    @property
    def nao(self) -> int: ...

    def aoslice_by_atom(self) -> list[tuple[int, int]]: ...

    def overlap_ao(self) -> np.ndarray: ...

    def hcore_ao(self) -> np.ndarray: ...

    def fock_ao(self, *, density_ao: np.ndarray | None = None) -> np.ndarray: ...

    def mo_coeff_ao(self) -> np.ndarray: ...

    def make_rdm1_ao(self) -> np.ndarray: ...

    def energy_nuc_au(self) -> float: ...

    def reference_class_name(self) -> str: ...

    def raw_handle(self) -> Any: ...


@dataclass
class PySCFAOBasisView:
    """AO view over a PySCF mean-field object."""

    _mf: Any
    backend_tag: str = "pyscf"

    def _mol(self) -> Any:
        return self._mf.mol

    @property
    def n_atom(self) -> int:
        return int(self._mol().natm)

    @property
    def nao(self) -> int:
        return int(self._mol().nao_nr())

    def aoslice_by_atom(self) -> list[tuple[int, int]]:
        sl = self._mol().aoslice_by_atom()
        return [(int(row[2]), int(row[3])) for row in sl]

    def overlap_ao(self) -> np.ndarray:
        return np.asarray(self._mf.get_ovlp(), dtype=float)

    def hcore_ao(self) -> np.ndarray:
        return np.asarray(self._mf.get_hcore(), dtype=float)

    def fock_ao(self, *, density_ao: np.ndarray | None = None) -> np.ndarray:
        if density_ao is None:
            return np.asarray(self._mf.get_fock(), dtype=float)
        return np.asarray(self._mf.get_fock(dm=density_ao), dtype=float)

    def mo_coeff_ao(self) -> np.ndarray:
        return np.asarray(self._mf.mo_coeff, dtype=float)

    def make_rdm1_ao(self) -> np.ndarray:
        dm = self._mf.make_rdm1()
        if isinstance(dm, (tuple, list)):
            return cast(
                "np.ndarray", np.asarray(dm[0], dtype=float) + np.asarray(dm[1], dtype=float)
            )
        return cast("np.ndarray", np.asarray(dm, dtype=float))

    def energy_nuc_au(self) -> float:
        return float(self._mol().energy_nuc())

    def reference_class_name(self) -> str:
        return str(self._mf.__class__.__name__)

    def raw_handle(self) -> Any:
        return self._mf


@dataclass
class Psi4AOBasisView:
    """AO view over a Psi4 ``Wavefunction``."""

    _wfn: Any
    backend_tag: str = "psi4"

    @property
    def n_atom(self) -> int:
        return int(self._wfn.molecule().natom())

    @property
    def nao(self) -> int:
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_nao

        return psi4_nao(self._wfn)

    def aoslice_by_atom(self) -> list[tuple[int, int]]:
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_aoslice_by_atom

        ranges = psi4_aoslice_by_atom(self._wfn)
        if sum(p1 - p0 for p0, p1 in ranges) != self.nao:
            raise ValueError(f"Psi4 AO slice sum does not match nao={self.nao}.")
        return ranges

    def overlap_ao(self) -> np.ndarray:
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_overlap_ao

        return psi4_overlap_ao(self._wfn)

    def hcore_ao(self) -> np.ndarray:
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_hcore_ao

        return psi4_hcore_ao(self._wfn)

    def fock_ao(self, *, density_ao: np.ndarray | None = None) -> np.ndarray:
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_fock_ao

        return psi4_fock_ao(self._wfn, density_ao=density_ao)

    def mo_coeff_ao(self) -> np.ndarray:
        return np.asarray(self._wfn.Ca(), dtype=float)

    def make_rdm1_ao(self) -> np.ndarray:
        return np.asarray(self._wfn.Da(), dtype=float)

    def energy_nuc_au(self) -> float:
        return float(self._wfn.molecule().nuclear_repulsion_energy())

    def reference_class_name(self) -> str:
        return "RHF"

    def raw_handle(self) -> Any:
        return self._wfn


def _unwrap_raw_mf(mf_like: Any) -> Any:
    from qchem_stack.chem.bridges.mean_field_like import unwrap_mean_field_raw

    return unwrap_mean_field_raw(mf_like)


def ao_basis_view_from_reference(reference: ClassicalMeanFieldReference) -> AOBasisView:
    tag = reference.backend_tag()
    raw = _unwrap_raw_mf(reference.mf)
    if tag == "pyscf":
        return PySCFAOBasisView(_mf=raw)
    if tag == "psi4":
        return Psi4AOBasisView(_wfn=raw)
    raise ValueError(f"No AOBasisView for backend {tag!r}; supported: pyscf, psi4.")


def require_ao_basis_view(
    reference: ClassicalMeanFieldReference,
    *,
    context: str,
    error_cls: type[Exception] = ValueError,
) -> AOBasisView:
    try:
        return cast("AOBasisView", reference.ao_basis_view())
    except Exception as e:  # noqa: BLE001
        raise error_cls(
            f"{context} requires a mean-field reference with AO basis view "
            f"(backend={reference.backend_tag()!r}): {e}"
        ) from e
