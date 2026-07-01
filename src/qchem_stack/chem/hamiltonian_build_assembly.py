"""Shared QubitHamiltonian meta assembly (deduplicates hamiltonian_build paths)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta

from .hamiltonian_meta import (
    FermionQubitMappingName,
    _attach_reference_energy_meta,
    _classical_driver_meta_payload,
    _qubit_build_meta,
    _resolve_integral_metadata,
    hamiltonian_fingerprint_from_qubit_operator,
)

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian_build import QubitHamiltonian


def assemble_qubit_hamiltonian(
    qop: QubitOperator,
    fermion_space: FermionSpace,
    *,
    fermion_qubit_mapping: FermionQubitMappingName,
    build_route: str,
    n_active_orbitals: int,
    n_active_electrons: int,
    rhf: ClassicalMeanFieldReference | None = None,
    canonical_pack: CanonicalActiveSpaceIntegralPack | None = None,
    integral_source: str | None = None,
    integral_openfermion_bridge: str | None = None,
    jordan_wigner_coeff_atol: float | None = None,
    meta_extra: dict[str, Any] | None = None,
    pyscf_driver_meta: dict[str, Any] | None = None,
    classical_driver_meta: dict[str, Any] | None = None,
) -> QubitHamiltonian:
    """Build :class:`~qchem_stack.chem.hamiltonian_build.QubitHamiltonian` with standard meta keys."""
    from openfermion import count_qubits

    from qchem_stack.chem.hamiltonian_build import QubitHamiltonian

    n_phys = int(count_qubits(qop) or 0)
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    driver_meta, backend_tag = _classical_driver_meta_payload(rhf)
    source_tag, bridge_tag = _resolve_integral_metadata(
        canonical_pack=canonical_pack,
        backend_tag=backend_tag,
        integral_source=integral_source,
        integral_openfermion_bridge=integral_openfermion_bridge,
    )
    meta: dict[str, Any] = {
        **_qubit_build_meta(
            fermion_qubit_mapping=fermion_qubit_mapping,
            build_route=build_route,
            jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        ),
        "integral_source": source_tag,
        "integral_openfermion_bridge": bridge_tag,
        "n_active_orbitals": n_active_orbitals,
        "n_active_electrons": n_active_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if classical_driver_meta:
        meta["classical_driver"] = fork_driver_meta(classical_driver_meta)
    elif pyscf_driver_meta:
        meta["pyscf_driver"] = fork_driver_meta(pyscf_driver_meta)
    elif driver_meta:
        if backend_tag == "pyscf":
            meta["pyscf_driver"] = driver_meta
        else:
            meta["classical_driver"] = driver_meta
    if canonical_pack is not None:
        meta["canonical_integral_pack"] = {
            "schema": canonical_pack.schema,
            "provenance": dict(canonical_pack.provenance),
        }
        compact = canonical_pack.compact
        if hasattr(compact, "constant") and hasattr(compact, "h1_active_mo"):
            meta["spatial_mo_constant"] = float(compact.constant)
            meta["spatial_mo_h1"] = np.asarray(compact.h1_active_mo, dtype=float).tolist()
            if hasattr(compact, "dense_h2_chemist_spatial"):
                meta["spatial_mo_h2"] = np.asarray(
                    compact.dense_h2_chemist_spatial(), dtype=float
                ).tolist()
    if meta_extra:
        meta.update(meta_extra)
    _attach_reference_energy_meta(meta, rhf)
    return QubitHamiltonian(
        operator=qop,
        n_qubits=n_phys,
        fermion_space=fermion_space,
        meta=meta,
    )
