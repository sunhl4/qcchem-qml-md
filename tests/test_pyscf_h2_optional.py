from __future__ import annotations

import pytest

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import (
    ActiveSpaceSpec,
    ExperimentConfig,
    MoleculeSpec,
    load_experiment_config,
)
from qchem_stack.qpe_qec_demo import FaultTolerantDemoAdapter
from qchem_stack.quantum.algorithms.vqe import VQE
from tests.fixtures.classical_reference import pyscf_rhf_from_config

pyscf = pytest.importorskip("pyscf")


def _as_reference(rhf) -> ClassicalMeanFieldReference:
    return ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )


def test_h2_active_space_vqe(tmp_path_factory) -> None:
    root = tmp_path_factory.mktemp("cfg")
    cfg_path = root / "h2.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: t
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    r = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(r)).qubit_hamiltonian
    assert qh.meta.get("fermion_to_qubit_map") == "jordan_wigner"
    assert qh.meta.get("integral_source") == "pyscf_casci_h2eff_compact"
    assert qh.meta.get("integral_openfermion_bridge") == "pyscf_tangelo_openfermion_v1"
    assert qh.meta.get("n_active_electrons") == 2
    v = VQE(qh, depth=1).run(maxiter=200, seed=0)
    ad = FaultTolerantDemoAdapter()
    e_dense = ad.ground_energy_dense(qh)
    assert abs(v.energy - e_dense) < 0.2


def test_h2_active_space_bravyi_kitaev_meta() -> None:
    cfg = ExperimentConfig(
        experiment_id="bk_meta",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        active_space=ActiveSpaceSpec(
            strategy="cas",
            cas={"n_orbitals": 2, "n_electrons": 2},
            mapping={"fermion_qubit": "bravyi_kitaev"},
        ),
    )
    r = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(r)).qubit_hamiltonian
    assert qh.meta.get("fermion_to_qubit_map") == "bravyi_kitaev"


def test_h2_active_space_symmetry_conserving_bravyi_kitaev_dimension() -> None:
    cfg = ExperimentConfig(
        experiment_id="scbk_meta",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        active_space=ActiveSpaceSpec(
            strategy="cas",
            cas={"n_orbitals": 2, "n_electrons": 2},
            mapping={"fermion_qubit": "symmetry_conserving_bravyi_kitaev"},
        ),
    )
    r = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(r)).qubit_hamiltonian
    assert qh.meta.get("fermion_to_qubit_map") == "symmetry_conserving_bravyi_kitaev"
    assert qh.n_qubits == 2
    assert qh.meta.get("n_qubits") == 2


def test_h2_uccsd_bounded_lbfgsb_near_casci_energy() -> None:
    """Figure-asset strategy: bounded UCCSD amplitudes + L-BFGS-B stays variational vs CASCI."""
    from pathlib import Path

    import numpy as np
    from pyscf import mcscf

    from qchem_stack.backends.factory import executor_from_spec
    from qchem_stack.config import backend_spec_from_config, load_experiment_config
    from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_vqe_figure_near_casci.yaml")
    r = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(r)).qubit_hamiltonian
    exe = executor_from_spec(backend_spec_from_config(cfg))
    mo = r.mf.mo_coeff
    mo_arr = mo if isinstance(mo, np.ndarray) else np.asarray(mo[0], dtype=float)
    casci = float(mcscf.CASCI(r.mf, 2, 2).kernel(mo_arr)[0])

    b = 0.38
    u = UCCSDVQE(qh, executor=exe)
    npar = u.n_params
    bounds = [(-b, b)] * npar
    x0 = np.zeros(npar, dtype=float)
    res = u.run(
        maxiter=400,
        seed=42,
        executor=exe,
        record_energy_trace=True,
        scipy_method="L-BFGS-B",
        bounds=bounds,
        initial_parameters=x0,
        scipy_options={"ftol": 1e-11, "gtol": 1e-7, "maxfun": 1200},
    )
    assert res.energy >= casci - 5e-4  # not below CASCI by >0.5 mHa (numerical slack)
    assert res.energy <= casci + 0.02  # within ~20 mHa above (bounded ansatz)
    assert len(res.meta.get("energy_trace", [])) == res.nfev
