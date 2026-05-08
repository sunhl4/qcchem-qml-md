"""PySCF MO ERI layout → OpenFermion / ``spinorb_from_spatial`` ordering.

SandboxAQ `Tangelo`_ applies ``numpy.transpose(eri, (0, 2, 3, 1))`` to PySCF MO integrals
before :func:`openfermion.chem.molecular_data.spinorb_from_spatial`, then passes
``0.5 * two_body_spin_orb`` into :class:`openfermion.InteractionOperator` (see
``tangelo.toolboxes.molecular_computation.molecule.SecondQuantizedMolecule._get_fermionic_hamiltonian``).

.. _Tangelo: https://github.com/sandbox-quantum/Tangelo
"""

from __future__ import annotations

import numpy as np


def spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_spatial: np.ndarray) -> np.ndarray:
    """Reorder spatial MO chemist ERIs from PySCF ``ao2mo``/CASCI layout to OpenFermion pairing.

    Args:
        h2_spatial: real 4-index array ``(norb, norb, norb, norb)`` from ``ao2mo.restore(1, ...)``
            or CASCI ``get_h2eff`` after restore.

    Returns:
        Transposed array suitable for :func:`openfermion.chem.molecular_data.spinorb_from_spatial`.
    """
    a = np.asarray(h2_spatial, dtype=float)
    if a.ndim != 4 or a.shape[0] != a.shape[1] or a.shape[0] != a.shape[2] or a.shape[0] != a.shape[3]:
        raise ValueError("h2_spatial must be a real (norb, norb, norb, norb) array")
    return np.transpose(a, (0, 2, 3, 1))
