"""L1 phase F (序 21): ComputableRef ⟷ ComputableSpec round-trip."""

from __future__ import annotations

from qchem_stack.config import (
    ActiveSpaceSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.protocols.computable import (
    ComputableRef,
    ComputableSpec,
    list_computable_specs_for_config,
    list_computables_for_config,
)


def test_computable_spec_roundtrip_identity() -> None:
    r = ComputableRef("x", "energy", {"k": 1})
    s = ComputableSpec.from_ref(r)
    r2 = s.to_ref()
    assert r2.name == r.name and r2.kind == r.kind and r2.details == r.details


def test_list_specs_matches_refs_for_minimal_config() -> None:
    cfg = ExperimentConfig(
        experiment_id="c",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H"], coordinates_bohr=[[0, 0, 0]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=1, n_active_electrons=1),
        quantum=QuantumSpec(algorithm="vqe", use_pauli_protocol=True),
    )
    refs = list_computables_for_config(cfg)
    specs = list_computable_specs_for_config(cfg)
    assert len(specs) == len(refs)
    for s, r in zip(specs, refs, strict=True):
        assert s.to_ref().name == r.name


def test_list_specs_includes_iqeb_ground_energy_item() -> None:
    cfg = ExperimentConfig(
        experiment_id="c2",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H"], coordinates_bohr=[[0, 0, 0]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=1, n_active_electrons=1),
        quantum=QuantumSpec(algorithm="iqeb", iqeb_max_rounds=4, vqe_depth=2, use_pauli_protocol=False),
    )
    refs = list_computables_for_config(cfg)
    g = next(r for r in refs if r.name == "ground_state_energy")
    assert g.details["algorithm"] == "iqeb"
    assert g.details["iqeb_max_rounds"] == 4
    assert g.details["vqe_depth"] == 2
