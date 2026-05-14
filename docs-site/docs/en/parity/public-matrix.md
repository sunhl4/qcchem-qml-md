# Public InQuanto contract vs `qchem_stack` coverage matrix

**Purpose:** Compare this repository’s **independent** implementation against [Quantinuum’s public InQuanto docs and API](https://docs.quantinuum.com/inquanto/) only. We do **not** claim closed-source binary parity or vendor default hyperparameters.

**How-to narrative mapping:** [Engineering memory §14](/en/concept/engineering-memory-quantinuum) maps the official [How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html) story to this repo’s modules and `repro` exports.

**Gap-closure execution plan (B→J, L1 definitions):** [Gap plan — Appendix D](/parity/gap-implementation-plan#appendix-d) (Chinese; canonical).

**Gap list + phased plan:** [`/parity/gap-implementation-plan`](/parity/gap-implementation-plan) (machine-readable categories: `qchem_stack.protocols.inquanto_contract.inquanto_gap_categories`). **L1 sign-off:** [Appendix C](/parity/gap-implementation-plan#appendix-c).

**Boundary (read this):** **L1** = public narrative + verifiable artifacts; **L0** = full reproduction of closed-source defaults, all driver combinations, and commercial runtime details — **not** an engineering commitment without source and license. See [Engineering memory §0](/en/concept/engineering-memory-quantinuum).

**Legend:** `yes` shipped / `partial` different shape or semantics / `no` missing / `n/a` out of scope or non-public

## 0. Non-cloud, non-proprietary hardware: scope and “beyond” (L1+)

**Full alignment (repo promise):** Except for the **explicit exclusions** below, sections §1–4 of this matrix stay **in sync** with `inquanto_gap_categories()` and `GET /v1/meta/capability-surface`; every `partial` row has a gap anchor, caveat, or [Y1 SLA template (Appendix B §6)](/parity/gap-implementation-plan#y1-residual-partial-sla-template).

**Explicit exclusions:** Quantinuum **commercial cloud** (Nexus / `qnexus` / HQC / OAuth / quotas) and **proprietary hardware** (H-series calibration, native gate sets, topology-specific routing). Those rows stay `n/a` or “local analog”.

**Defensible “beyond”** (stronger **engineering verifiability** vs public docs + closed product — **not** L0 numeric/binary equivalence):

- **Open stack, auditable:** Methods-grade orchestration without a closed wheel for JSON contracts and semantics.
- **Criteria + CI gates:** `parity_snapshot` registry, `export_parity_criteria_table`, `check_parity_export_sample`, full `pytest`.
- **Pluggable backends:** One YAML surface for statevector / Qiskit / ionstack mock.
- **MD / ML surface:** `md_bridge` / `QMEFDataset`.

Machine-readable summary (same as HTTP): **`object_map`**, **`gaps`**, **`mitigation_execution_model`**, **`open_stack_differentiators`** (schema **`open_stack_differentiators_v1`**: `scope_excludes`, `beyond_public_doc_bundle`), **`tangelo_public_mapping_alias_surface_v1`**, **`operator_pool_registry_export_v1`** (ADAPT/IQEB pool ids and **`pool_id_aliases`**), **`algorithm_registry_export_v1`**, **`variational_registry_export_v1`**.

## 1. Protocols & workflow

| Public capability | Official entry | qchem_stack |
|---|---|---|
| Five phases instantiate→build→compile→run→evaluate | [Protocols overview](https://docs.quantinuum.com/inquanto/manual/protocols_overview.html) | `partial`: equivalent five phases; optional `run_sampled` (statevector MC) and `run_qiskit_shots_pauli_protocol` (Qiskit `get_counts` / Aer / hardware — [Qiskit shot counts](/en/reference/qiskit-shot-counts)); phases can carry **`nexus_analog` billing** and **`zne_scales`** when ZNE is on. Async path is **not** Nexus 1:1 — [Launch/retrieve (Nexus analog)](/en/concept/launch-retrieve-nexus-analog) (`JobHandle.protocol_hash`, local SQLite queue + worker; pickle protocol may carry `NexusAnalogSpec`). |
| `dataframe_circuit_shot`-style resource tables | [Resource estimation](https://docs.quantinuum.com/inquanto/manual/protocols/resource_estimation.html) | `yes`: `dataframe_circuit_shot_rows` + `spec.dataframe_circuit_shot` |
| Public `Computable` / Methods summaries | API & export scripts | `partial`→**verifiable L1**: `POST /v1/meta/computables-preview`, `POST /v1/meta/workflow-preview` (five phases + `computable_graph_v2` + optional `include_computables_rich` → **`computables_rich_v1`**); after a run, `GET /v1/runs/{id}/summary` and full `repro` on `GET /v1/runs/{id}/repro` (`DONE`); gap `composable_computable` state **`analog_v2_semantic_graph_rich_optional`** |
| Job submit / list / poll (product gateway) | Nexus / cloud UX | `partial`: **local FastAPI analog** `qchem_stack.api`: `POST/GET /v1/runs`, `GET /v1/meta/parity-gaps`, **`POST /v1/meta/computables-preview`**, **`GET /v1/meta/queue-stats`**; no vendor identity or quotas — [ENGINEERING_ARCHITECTURE](/en/concept/engineering-architecture) §9, [Launch/retrieve](/en/concept/launch-retrieve-nexus-analog) |
| `qnexus` / HQC pricing | same | `n/a` + **local analog**: `jobs/cost` + `nexus_analog` weights (`nexus_analog_ledger` / per-job `nexus_analog_billing`); **no** fake HQC currency. Optional `nexus_cloud` sidecar (`http`/`mock`, not the vendor SDK) |
| Qermit `MitRes`/`MitEx` | [Noise mitigation](https://docs.quantinuum.com/inquanto/manual/errmit.html) | `partial`: PMSV/ZNE/SPAM stubs; optional **`mitigation.zne_mode=circuit_scale_fold`** (per-scale HEA amplification + `protocol_counts.zne_curve` in **`mitigation_dag_execution`**); **ZNE × Qiskit Pauli** unified snapshot **`parity_snapshot.zne_qiskit_unification_v1`** ([mitigation mapping](/en/concept/mitigation-mapping)); Methods exports **`resource_estimation_preview_v1`** / **`methods_resource_unified_v1`** mirror **`mitigation_zne_mode_yaml`**, **`mitigation_zne_scales_yaml`**; with **`--results`**, **`parity_snapshot_mitigation_zne_*`**; graph **`mitigation/qermit_analog`** (`qermit_analog_v2`); linear trace **`mitigation/qermit_runtime`** → `mitigation_dag_execution` (not commercial Qermit); **L1 order invariant**: SPAM/PMSV/ZNE `kind` sequence matches `mitigation_dag_execution.trace[].node` (`tests/test_mitigation_dag_trace_homology.py`) |
| `CuTensorNetProtocol` | [inquanto-cutensornet API](https://docs.quantinuum.com/inquanto/api/extensions/inquanto-cutensornet_api.html) | `n/a` (honest): open stack has `tensornet/cutensornet_protocol_stub` + **`tensornet_engine_resolved`** / **`tensornet_fallback_reason`**; no bundled `inquanto-cutensornet`-scale chemistry contraction; L3 demos go through optional cuQuantum/cuPy envs, not product parity claims |

## 2. Algorithms ([algorithms API](https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html))

| Public class | qchem_stack | Notes |
|---|---|---|
| `AlgorithmVQE` | `yes`: `quantum/algorithms/vqe.py`; optional **`quantum.variational_ansatz: uccsd`** (JW, `quantum/algorithms/uccsd_vqe.py` — dense cluster exponentiation or first-order Trotter repeats via **`quantum.uccsd_trotter_steps`**, `configs/example_h2_uccsd.yaml` / `configs/example_h2_uccsd_trotter.yaml`); **`n/a`**: same UCCSD Trotter circuit semantics **not** wrapped on BK/SCBK reference (variational layer can still use HEA + BK/SCBK Hamiltonian) |
| `AlgorithmAdaptVQE` / FermionicAdapt | `partial(interface-ready)`: `adapt.py` now uses **commutator gradients** + executable pool registry (`fermionic_uccsd` / `toy_pair_xx`); adds experimental `quantum.algorithm: tetris_adapt` |
| `AlgorithmIQEB` | `partial(interface-ready)`: `IQEBVQE` supports `iqeb_n_grads` + `iqeb_energy_tolerance` + pool registry (default `iqeb_qubit_excitation`) |
| `AlgorithmVQD` | `partial`: `excited.py` multi-level deflation; single objective, **reports** three-channel `three_protocol` |
| `AlgorithmQSE` | `partial`: `excited.py` + `quantum/qse_transition.py` — per-$(i,j)$ Pauli transition noise + schedule; dense reference still available |
| `AlgorithmSCEOM` | `partial`: `run_sceom_nested_commutator` (D2SC05371C-style $M_{ij}=\langle\psi\|[S_i^\dagger,[H,S_j]]\|\psi\rangle$, toy Pauli generators) + reference subspace path |
| `Algorithm*QPE` | `partial(interface-ready)`: adds `quantum/algorithms/qpe.py` (Deterministic/Kitaev/InfoTheory) and feeds demo-track payloads; YAML gate `qpe_demo_track_after_variational` / `qpe_pipeline_integration`; `run_summary.qpe_open_stack_contract_v1` |
| `AlgorithmVQS` / `AlgorithmMcLachlan*` | `partial(interface-ready)`: `quantum/algorithms/vqs.py` + optional **`vqs_pipeline_integration`** YAML sidecar (`example_h2_vqs_track.yaml`) → `vqs_track` / `run_summary.vqs_open_stack_contract_v1`; RHS remains toy drift |
| `AlgorithmBayesianQPE` + Phayes | `partial`: `qpe_qec_demo/bayesian_stub.py` (`BayesianQPEStub`); module notes in repo file `src/qchem_stack/qpe_qec_demo/README.md` (open from clone root — not embedded in this site); wired into `qpe_demo_track` / `run_summary.qpe_demo_track_ran`; tests `tests/test_l1_phase_c_iqeb_bayesian.py` |
| YAML `quantum.algorithm_factory` / `variational_plugins` | `partial`: example `configs/example_h2_echo_variational_plugin.yaml`; export **`variational_registry_export_v1`** (inside `algorithm_registry_alignment_v1`, `resource_estimation_preview` flag) |
| `quantum.adapt_pool_id` / `quantum.iqeb_pool_id` | `partial`: `operator_pool_registry.py` + **`operator_pool_registry_export_v1`** (**`pool_id_aliases`**: `qubit_excitation`, `uccsd_jw`); examples `configs/example_h2_adapt_singles_pool.yaml`, `example_h2_adapt_uccsd_jw_alias.yaml`, `example_h2_iqeb_qubit_excitation_alias.yaml`, …; `run_summary` pool ids; **`GET /v1/meta/capability-surface`** embeds the same export block; gap **`adapt_iqeb_operator_pool_surface`** |

**Registry pin (P2-W5):** YAML `quantum.algorithm`, optional `quantum.algorithm_factory`, operator pools, variational ansatz, fermion→qubit map — [Appendix A §11](/parity/gap-implementation-plan#p2-w5-algorithm-registry-alignment).

## 3. Classical chemistry & embedding

| Capability | qchem_stack | Notes |
|---|---|---|
| PySCF RHF / active space → qubits | `yes`: `chem/drivers`, `hamiltonian.py`; `active_space.strategy=cas|manual|avas_stub|avas` (**`avas_stub`**: `configs/example_h2_avas_stub.yaml`; **`avas`**: `configs/example_h2_avas.yaml`, PySCF **`mcscf.avas.AVAS`** + `qchem_active_space_resolution_v1`; **CASSCF**: `casscf_orbital_optimization_audit` / **`casscf_orbital_optimization_for_integrals`** share one kernel); **geometry**: `molecule.ecp`, `molecule.zmatrix` (mutually exclusive with Cartesian); **RI/DF**: `scf.density_fit` / `density_fit_auxbasis` (traceable `driver_meta`); frozen MOs: `active_space.frozen_orbitals` → CASCI **`frozen`**; **orbital hook**: `chemistry_extended.mo_coeff_transform_hook`; **one-electron API**: `PySCFDriver.compute_one_electron_operator_*`; restricted “quantum problem tuple” still requires **closed-shell RHF**. **InQuanto product-grade** AVAS/CASSCF packaging remains **`partial`** — [Appendix A §10](/parity/gap-implementation-plan#p2-w3-avas-casscf-boundary) |
| DMET / fragment solver hooks | `partial`: `chem/embedding/dmet.py` (`DMETContext` placeholders); small-system dense fragment demo `QubitHamiltonianFragmentSolverExact` + shared Hamiltonian (`configs/example_h4_dmet_fragment_exact_small.yaml`); optional Schmidt JSON sidecar `embedding.schmidt_bath_sidecar_json_path` → `embedding_workflow.schmidt_bath_sidecar_v1`; ONIOM toy `embedding.oniom_layers_v1` → `embedding_workflow.oniom_toy_v1` (`configs/example_oniom_toy.yaml`); decomposition plugin `embedding.mode: plugin` + `configs/example_decomposition_plugin_toy.yaml` |
| Projection embedding | `partial`: **L1 trace** — `embedding.mode: projection` writes **`embedding_workflow`** + `parity_snapshot.projection_embedding_open_trace`. Default `embedding.projection_quantum_hamiltonian: global_active_space` keeps variational stage on the global `ActiveSpaceSpec` mapping (trace-only metadata). With `fragment_mulliken_mo` + `projection_fragment_atom_indices`, variational **`QubitHamiltonian`** from **RHF MO + fragment Mulliken order + PySCF CASCI active integrals** (`qchem_stack.chem.embedding.projection_hamiltonian`, **not** full many-body projection; see `epistemic_bound`). Examples: `configs/example_h2_projection_trace.yaml`, `configs/example_h4_projection_mulliken.yaml` |
| Full InQuanto driver surface (COSMO, PBC, multi-k, …) | `partial`: name map `chem/inquanto_driver_surface`; **PySCF** implements **ddCOSMO**, **PBC** (`pbc_kpoint_mesh`: Γ `RHF`, else `KRHF`), **PBC+ddCOSMO attempt** (PySCF-version dependent); **not** line-by-line vs closed `inquanto-pyscf` |

**Parity export CI samples (geometry / SCF extensions, config-only):** `configs/example_h2_sto3g_density_fit.yaml`, `example_h2_zmatrix_sto3g.yaml`, `example_h2_zmatrix_sto3g_density_fit.yaml`, `example_mg_lanl2dz_ecp_rhf.yaml`, `example_mg_lanl2dz_ecp_density_fit.yaml`, `example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml` — all in `scripts/check_parity_export_sample.py` `SAMPLE_CONFIGS_REL`. Export includes stable top-level **`geometry_source`** (`cartesian`|`zmatrix`) alongside `PARITY_EXPORT_V2_STABLE_KEYS`.

Unified policy: `scf.driver` is swappable; chemistry/embedding branch eligibility is capability-gated through `SolverCapabilities`, not hardcoded backend-brand string checks.

## 4. Differentiators vs closed product

- **Compile / TKET (`compiler_pass_bundle`):** default pipeline is `CompilerSpec` + in-repo `CircuitIR`; TKET **not** required. With `pytket` and `parity_integrations.tket_first_circuit_stats`, may write `parity_snapshot.tket_first_compiled_circuit_probe` when Pauli path produced `CircuitIR`. Ion-trap-specific routing and private pass packs **not** aligned. See [CircuitIR · TKET · jobs](/en/reference/circuitir-tket-jobs) §2–4.
- **Reproducibility:** YAML, `protocol_hash`, job metadata, versions in `orchestration`; `JobHandle.protocol_hash` vs SQLite `jobs` — same doc §6.
- **Multi-backend:** `BackendSpec` (statevector / qiskit / ionstack mock).
- **Resource metrics dual track** (aligned with resource-estimation narrative, **not** fake cloud pricing): `spec.circuit_resource_row`; optional `pytket` enrichment (`pytket_depth`, …).
- **MD / ML:** `md_bridge/contracts.py`, `QMEFDataset`.
- **Cost transparency:** per-circuit shots, stderr, grouping; **not** bound to Nexus HQC. Optional `nexus_cloud` / `nexus_analog` sidecars for Methods tables.
- **Criteria export:** `scripts/export_parity_criteria_table.py` (YAML + optional results JSON); **`geometry_source`** matches `molecular_system_from_experiment`.

## 5. PandM literature / positioning

Plain **qchem-stack** clones often **omit** the `PandM/` prose tree; if your monorepo includes it, search under **`PandM/materials/learning/quantum-chem/literature/`** by topic (competitor study, reproducibility routes, shots/dataflow guides).  

**Roadmap hub:** [/en/concept/competitive-positioning](/en/concept/competitive-positioning) (EN), [/concept/competitive-positioning](/concept/competitive-positioning) (ZH); repo manuscripts under `docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md`.

Chinese parity mirror of this matrix: [/parity/public-matrix](/parity/public-matrix).
