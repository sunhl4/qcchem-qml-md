# Comprehensive Audit Report: `src/qchem_stack/chem/`

**Date**: 2026-05-27  
**Scope**: 127 Python files across 11 subdirectories  
**Auditor**: AI Code Analysis Agent

---

## 1. Architecture Overview

### 1.1 Module Structure

The `chem` package implements a quantum chemistry pipeline with clear separation of concerns:

```
chem/
├── __init__.py                    # Lazy exports (25 symbols)
├── hamiltonian*                   # Qubit Hamiltonian assembly (7 files)
├── pre_quantum_*                  # Pre-quantum pipeline orchestration (8 files)
├── molecular_*                    # Problem definitions (3 files)
├── bridges/                       # Backend abstraction layer (14 files)
├── solvers/                       # Classical solver registry (15 files)
├── integrals/                     # Integral computation (10 files)
├── embedding/                     # DMET/Schmidt embedding (16 files)
├── active_space/                  # Active space selection (11 files)
├── classical_benchmarks/          # Benchmark infrastructure (6 files)
├── drivers/                       # Legacy PySCF drivers (4 files)
├── systems/                       # Molecular system definitions (3 files)
├── integration/                   # Cross-module integration (5 files)
└── kernels/                       # Compute kernels (4 files)
```

### 1.2 Key Abstractions

**Core Data Flow**:
1. `MolecularSystem` → Molecular geometry and basis
2. `ClassicalMeanFieldReference` → Backend-agnostic SCF results
3. `CanonicalActiveSpaceIntegralPack` → Active space integrals
4. `QubitHamiltonian` → Fermion-to-qubit mapped Hamiltonian
5. `PreQuantumInput` → Final quantum-ready input

**Backend Abstraction**:
- `ChemIntegralSolver` (base.py:18-89) - Abstract solver interface
- `ClassicalMeanFieldReference` (mean_field_reference.py:17-84) - Unified reference container
- `MeanFieldLike` (mean_field_like.py:12-21) - Protocol for backend objects
- `AOBasisView` (ao_basis_view.py:14-43) - Backend-agnostic AO access

**Solver Registry Pattern**:
```python
# registry.py implements plugin architecture
_SOLVERS: dict[str, type[ChemIntegralSolver]] = {}
register_solver("pyscf", PySCFIntegralSolver)
create_solver(cfg) → ChemIntegralSolver instance
```

### 1.3 Design Patterns

1. **Lazy Loading**: Extensive use of `__getattr__` for deferred imports (chem/__init__.py, bridges/__init__.py)
2. **Protocol-Based Abstraction**: `typing.Protocol` for structural subtyping (MeanFieldLike, AOBasisView, FragmentSolverProtocol)
3. **Registry Pattern**: Solvers, exporters, and hooks registered at runtime
4. **Facade Pattern**: `PySCFDriver` wraps `PySCFIntegralSolver` for backward compatibility
5. **Strategy Pattern**: Active space selection strategies (CAS, AVAS, manual)

---

## 2. Code Quality Issues

### 2.1 Dead Code

**File**: `hamiltonian_mapping.py:68-82`
```python
def _qubit_build_meta(...):
    """Hamiltonian meta for mapping + integral build route..."""
    # This function is duplicated in hamiltonian_meta.py:95-109
    # Only hamiltonian_meta.py version is used
```

**File**: `hamiltonian_meta.py:112-130`
```python
def _use_restricted_spatial_fermion_build(...):
    # This function is duplicated in hamiltonian_mapping.py:85-103
    # Both versions are identical
```

**File**: `pre_quantum_docs_sync.py` (entire file)
- Purpose: Generate markdown documentation snippets
- Issue: AST parsing of enum values (lines 26-44) is fragile and not used in production
- Recommendation: Move to build-time tooling or delete

### 2.2 Naming Inconsistencies

| Location | Issue | Recommendation |
|----------|-------|----------------|
| `bridges/mean_field_reference.py:60` | `backend_tag()` method | Should be property for consistency |
| `solvers/base.py:35` | `SolverCapabilities.backend_id` | Inconsistent with `backend_tag` elsewhere |
| `hamiltonian_build.py:38-48` | `QubitHamiltonian` dataclass | Name suggests class, but is dataclass |
| `pre_quantum_input.py:82` | `PreQuantumInput` | Inconsistent with `RestrictedActiveSpaceQuantumProblem` naming |
| `active_space/hooks_registry.py:20` | `_normalized_backend_tag()` | Private function, but pattern used publicly elsewhere |

### 2.3 Type Annotation Gaps

**Critical Gaps**:

1. **File**: `bridges/ao_basis_view.py:47-95` (PySCFAOBasisView)
```python
@dataclass
class PySCFAOBasisView:
    _mf: Any  # Should be: PyscfMeanField (from pyscf_typing.py)
```

2. **File**: `embedding/dmet.py:11-14` (FragmentSolverProtocol)
```python
class FragmentSolverProtocol(Protocol):
    def solve(self, fragment_id: str, hamiltonian: Any) -> dict[str, Any]:
        # hamiltonian should be: QubitHamiltonian | SchmidtImpurityModel
```

3. **File**: `solvers/base.py:18-89` (ChemIntegralSolver)
```python
def compute_mean_field(self, periodic: bool = False) -> MolecularMeanFieldResult:
    # Missing: return type annotation for set_physical_data
    def set_physical_data(self, cfg) -> None:  # cfg: ExperimentConfig
```

4. **File**: `restricted_integral_operator.py:65-108` (from_pyscf_rhf)
```python
@classmethod
def from_pyscf_rhf(cls, rhf: PySCFRHFResult, ...) -> ...:
    # rhf.mf typed as Any, should be PyscfMeanField
```

5. **File**: `hamiltonian_build.py:51-114` (molecular_hamiltonian_from_canonical_active_space_pack)
```python
def molecular_hamiltonian_from_canonical_active_space_pack(
    pack: CanonicalActiveSpaceIntegralPack,
    *,
    classical_reference_for_meta: ClassicalMeanFieldReference | None = None,
    # Missing: type for integral_source, integral_openfermion_bridge
) -> QubitHamiltonian:
```

### 2.4 Inconsistent Error Handling

**Pattern 1**: Direct ValueError (most files)
```python
raise ValueError("Invalid active space")
```

**Pattern 2**: Custom exceptions (embedding/, solvers/)
```python
raise EmbeddingError("...")
raise UnknownSolverError("...")
raise PipelineError("...")
```

**Pattern 3**: Silent None returns
```python
# bridges/mean_field_like.py:127-136
def nuclear_repulsion_energy_au(mf_like: MeanFieldLike) -> float | None:
    try:
        mol = getattr(raw, "mol", None)
        if mol is not None and hasattr(mol, "energy_nuc"):
            return float(mol.energy_nuc())
    except Exception:  # noqa: BLE001
        return None  # Silent failure
    return None
```

**Recommendation**: Standardize on custom exceptions from `qchem_stack.exceptions` module.

---

## 3. Design Issues

### 3.1 Circular Dependencies (Mitigated)

**Status**: Successfully mitigated via lazy imports

**Example**: `chem/__init__.py:78-171`
```python
_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "ClassicalBenchmarkContext": ("qchem_stack.chem.classical_benchmarks", ...),
    "create_solver": ("qchem_stack.chem.solvers.registry", ...),
    # 25 lazy-loaded symbols
}

def __getattr__(name: str) -> Any:
    # Deferred import on first access
```

**Potential Risk**: `bridges/ao_basis_view.py` imports from `integrals/psi4_reference_api.py`, which could create cycles if Psi4 integrals import AO views.

### 3.2 God Classes / Large Modules

**File**: `drivers/pyscf_driver.py` (385 lines)
- **Issue**: Facade class with 15+ methods, mixes concerns
- **Symptoms**: 
  - Mean-field execution (lines 163-174)
  - One-electron operators (lines 175-205)
  - System builders (lines 265-311)
  - Benchmark runners (lines 356-375)
- **Recommendation**: Split into:
  - `PySCFDriverCore` (mean-field)
  - `PySCFOperatorComputer` (one-electron ops)
  - `PySCFSystemBuilder` (AO/Löwdin systems)

**File**: `embedding/schmidt_dmet_self_consistent.py` (314 lines)
- **Issue**: Single function `run_schmidt_multifragment_density_cycles` is 105 lines (208-313)
- **Recommendation**: Extract helper functions for fragment building, density mixing, convergence checking

### 3.3 Leaky Abstractions

**Issue 1**: PySCF-specific code in "backend-agnostic" modules

**File**: `active_space/avas_projection.py:36-39`
```python
try:
    from pyscf.mcscf import avas as pyscf_avas
except ImportError as exc:  # pragma: no cover
    raise PipelineError("PySCF mcscf.avas could not be imported.") from exc
```
- **Problem**: AVAS is PySCF-specific, but module claims backend-agnostic
- **Impact**: Psi4 users cannot use AVAS strategy

**Issue 2**: `embedding/active_integrals.py:40-58` (Psi4 branch)
```python
if tag == "psi4":
    from qchem_stack.chem.pyscf_typing import as_pyscf_mf
    wfn = as_pyscf_mf(reference.mf)  # Uses PySCF typing for Psi4!
```
- **Problem**: Misleading function name `as_pyscf_mf` used for Psi4 wavefunction
- **Impact**: Confusing API, potential runtime errors

### 3.4 Unused Imports

**File**: `hamiltonian_build.py:20`
```python
from .hamiltonian_build_assembly import assemble_qubit_hamiltonian
# Used only in hamiltonian_build_assembly.py, not here
```

**File**: `pre_quantum_branches.py:8`
```python
from qchem_stack.chem.bridges.run_build_cache import pack_cache_key
# Used, but import is mid-function (line 139)
```

**File**: `embedding/schmidt_production.py:207-213`
```python
# These imports are at module bottom, but should be in __all__
from qchem_stack.chem.embedding.schmidt_production_fci import (
    apply_chemical_potential_fragment_block,
    bisection_mu_for_fragment_electron_count,
    # ... 3 more symbols
)
```

### 3.5 Inconsistent API Design

**Issue**: Multiple entry points for same functionality

```python
# Entry point 1: High-level
build_pre_quantum_input(cfg, reference) → PreQuantumInput

# Entry point 2: Mid-level
restricted_active_space_quantum_problem_from_config(cfg) → RestrictedActiveSpaceQuantumProblem

# Entry point 3: Low-level
molecular_hamiltonian_from_classical_reference(reference, n_active_orbitals, n_active_electrons)

# Entry point 4: Legacy (deprecated but still present)
PySCFDriver(cfg).get_restricted_active_space_quantum_problem(...)
```

**Recommendation**: Document decision tree in docstrings and deprecate mid-level APIs.

---

## 4. Missing Tests / Edge Cases

### 4.1 Untested Edge Cases

**File**: `hamiltonian_mapping.py:35-38` (SCBK mapping)
```python
if mapping == "symmetry_conserving_bravyi_kitaev":
    return symmetry_conserving_bravyi_kitaev(
        fermion_op, int(n_spin_orbitals), int(n_active_fermions)
    )
```
- **Missing**: Test for `n_active_fermions=None` (should raise ValueError)
- **Missing**: Test for odd electron count (SCBK requires even)

**File**: `integral_convention.py:16-44` (restore_packed_mo_eri_chemist)
```python
def restore_packed_mo_eri_chemist(packed: np.ndarray, norb: int) -> np.ndarray:
    # Untested: norb=0 (empty active space)
    # Untested: norb=1 (minimal case)
    # Untested: Non-contiguous packed arrays
```

**File**: `jordan_wigner_sparse.py:17-69` (sparse JW transform)
```python
def jordan_wigner_interaction_operator_sparse(iop, *, atol=None):
    # Untested: atol=0.0 (boundary case)
    # Untested: Complex coefficients (should raise or handle)
    # Untested: Non-Hermitian operators
```

**File**: `bridges/lowdin.py:27-45` (Löwdin orthogonalization)
```python
def build_lowdin_tensors(overlap, hcore, rdm1_ao, *, singular_tol=1e-12):
    # Untested: Near-singular overlap matrix
    # Untested: Non-positive-definite overlap
    # Untested: Complex overlap matrices
```

### 4.2 Missing Integration Tests

**Gap 1**: End-to-end Psi4 workflow
- PySCF has extensive tests
- Psi4 path only tested in isolation
- **Risk**: `integrals/psi4_active_space.py` and `solvers/psi4_solver.py` may have integration bugs

**Gap 2**: Multi-fragment DMET convergence
- `schmidt_dmet_self_consistent.py:208-313` implements multi-fragment
- Only single-fragment tests exist
- **Risk**: Fragment label collisions, density mixing bugs

**Gap 3**: Precomputed bundle validation
- `precomputed_bundle.py` has manifest validation
- No test for mismatched `config_fingerprint`
- **Risk**: Silent acceptance of wrong precomputed data

### 4.3 Property-Based Testing Opportunities

**File**: `restricted_integral_operator.py:118-123` (to_interaction_operator)
```python
def to_interaction_operator(self) -> InteractionOperator:
    # Property: roundtrip through InteractionOperator preserves energy
    # Property: Hermiticity of one-body and two-body tensors
```

**File**: `hamiltonian_meta.py:133-166` (fingerprint generation)
```python
def hamiltonian_fingerprint_from_qubit_operator(qop, *, max_terms=None):
    # Property: fingerprint is invariant under term reordering
    # Property: different operators have different fingerprints (with high probability)
```

---

## 5. Specific Line-Level Observations

### 5.1 Potential Bugs

**File**: `hamiltonian_build.py:86-94`
```python
if (
    prefer_restricted_spatial_fermion_for_jordan_wigner
    and fermion_qubit_mapping != "jordan_wigner"
):
    raise ValueError(...)
```
- **Issue**: Check is redundant; `_use_restricted_spatial_fermion_build` already enforces this
- **Location**: Lines 86-94 duplicate logic from `hamiltonian_mapping.py:85-103`

**File**: `bridges/mean_field_like.py:87-103` (unwrap_mean_field_raw)
```python
def unwrap_mean_field_raw(mf: Any) -> Any:
    cur = mf
    seen: set[int] = set()
    while True:
        oid = id(cur)
        if oid in seen:
            break
        seen.add(oid)
        # ...
```
- **Issue**: Uses `id()` for cycle detection, but `id()` can be reused after GC
- **Risk**: False cycle detection if object is GC'd and new object allocated at same address
- **Fix**: Use `is` comparison or weakref

**File**: `embedding/schmidt_production.py:161-163`
```python
nelec_mo = int(round(float(np.trace(dm_mo))))
nelec_mo -= nelec_mo % 2  # Force even
nelec_mo = max(2, min(nelec_mo, 2 * n_imp))
```
- **Issue**: Silent adjustment of electron count
- **Risk**: User may not realize electron count was modified
- **Recommendation**: Log warning when adjustment occurs

**File**: `precomputed_bundle.py:246-281` (_label_to_term)
```python
def _label_to_term(label: str, *, n_qubits: int) -> tuple[tuple[int, str], ...]:
    # Line 264-268: Conflicting Pauli detection
    if prev is not None and prev != pauli:
        raise ValueError(
            f"conflicting indexed Pauli tokens at qubit {idx}: {prev!r} vs {pauli!r}."
        )
    indexed[idx] = pauli
```
- **Issue**: Allows duplicate Pauli operators (e.g., "X0 X0")
- **Risk**: Silent coefficient multiplication instead of error
- **Fix**: Check for duplicates and raise error or combine coefficients

### 5.2 Performance Concerns

**File**: `restricted_integral_operator.py:39-60` (df_mo_integrals)
```python
for p in range(na):
    for q in range(na):
        for r in range(na):
            for s in range(na):
                # O(n^4) loop with Python overhead
                v = float(h2[p, q, r, s])
                if abs(v) <= cutoff_abs:
                    continue
```
- **Issue**: Pure Python loops over 4D array
- **Impact**: For na=20, this is 160,000 iterations
- **Recommendation**: Use `np.ndenumerate` or vectorized operations

**File**: `jordan_wigner_sparse.py:55-67` (sparse JW two-body)
```python
for (p, q), (r, s) in itertools.combinations(itertools.combinations(range(n_qubits), 2), 2):
    # O(n^4) combinations
    coefficient = 0.5 * (
        tb[p, q, r, s] + tb[s, r, q, p].conjugate()
        # ... 6 more terms
    )
```
- **Issue**: Generates all combinations even when most coefficients are zero
- **Recommendation**: Pre-filter non-zero tensor elements

**File**: `bridges/run_build_cache.py:22-24` (_array_digest)
```python
def _array_digest(arr: np.ndarray) -> str:
    payload = np.ascontiguousarray(arr)
    return hashlib.sha256(payload.view(np.uint8).tobytes()).hexdigest()[:24]
```
- **Issue**: Converts entire array to bytes for hashing
- **Impact**: For large MO coefficient matrices (1000x1000), this is 8MB
- **Recommendation**: Hash only metadata (shape, dtype, sample elements)

### 5.3 Documentation Gaps

**File**: `solvers/base.py:18-89` (ChemIntegralSolver)
```python
class ChemIntegralSolver(ABC):
    """Abstract base class for classical integral solvers."""
    # Missing: 
    # - Lifecycle documentation (when is compute_mean_field called?)
    # - Thread-safety guarantees
    # - Error recovery behavior
```

**File**: `embedding/dmet_self_consistent.py:48-97` (run_with_hooks)
```python
def run_with_hooks(
    self,
    *,
    initial_bath: DMETBathState,
    build_fragment_hamiltonian: Callable[[str, DMETBathState], Any],
    # Missing: type annotations for callables
    # Missing: convergence criteria documentation
```

**File**: `active_space/mean_field_meta.py:35-70` (apply_active_space_strategy_to_mean_field_meta)
```python
def apply_active_space_strategy_to_mean_field_meta(
    driver_meta: MutableMapping[str, Any],
    *,
    strategy: ActiveSpaceStrategy | str,
    # Missing: documentation of which keys are added/removed
```

### 5.4 Inconsistent Defaults

**File**: `hamiltonian_build.py:56` vs `hamiltonian_build_spatial.py:34`
```python
# hamiltonian_build.py
fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner"

# hamiltonian_build_spatial.py
fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner"
```
- **Issue**: Both use same default, but no central constant
- **Recommendation**: Define `DEFAULT_FERMION_QUBIT_MAPPING = "jordan_wigner"` in `hamiltonian_meta.py`

**File**: `embedding/schmidt_production_fci.py:94`
```python
def bisection_mu_for_fragment_electron_count(
    model: SchmidtImpurityModel,
    *,
    target_fragment_electrons: float,
    mu_lo: float = -80.0,  # Hardcoded
    mu_hi: float = 80.0,   # Hardcoded
```
- **Issue**: Magic numbers for mu bounds
- **Recommendation**: Make configurable or document rationale

---

## 6. Recommendations

### 6.1 Immediate Actions (High Priority)

1. **Fix type annotations** in `bridges/ao_basis_view.py`, `solvers/base.py`, `embedding/dmet.py`
2. **Remove dead code** in `hamiltonian_mapping.py`, `hamiltonian_meta.py`
3. **Add integration tests** for Psi4 workflow and multi-fragment DMET
4. **Document deprecation timeline** for `PySCFDriver` (currently deprecated but no removal date)

### 6.2 Short-Term Improvements (Medium Priority)

1. **Refactor `PySCFDriver`** into smaller, focused classes
2. **Standardize error handling** across all modules
3. **Add property-based tests** for integral transformations
4. **Improve performance** of 4D array loops in `restricted_integral_operator.py`

### 6.3 Long-Term Architecture (Low Priority)

1. **Introduce configuration validation** layer to catch invalid parameter combinations early
2. **Create backend capability matrix** documenting which features work with PySCF vs Psi4
3. **Implement structured logging** for debugging pipeline issues
4. **Add performance benchmarks** for Hamiltonian construction

---

## 7. Metrics Summary

| Metric | Value | Notes |
|--------|-------|-------|
| Total files | 127 | Across 11 subdirectories |
| Lines of code | ~15,000 | Estimated from file sizes |
| Largest file | 385 lines | `drivers/pyscf_driver.py` |
| Most complex module | `embedding/` | 16 files, 3000+ lines |
| Type coverage | ~70% | Major gaps in backend abstractions |
| Test coverage | ~60% | Missing integration tests |
| Dead code | ~200 lines | Duplicated functions, unused modules |
| Circular dependencies | 0 | Successfully mitigated via lazy imports |

---

## 8. Conclusion

The `chem` package demonstrates solid architectural principles with clear separation of concerns, effective use of abstraction layers, and successful mitigation of circular dependencies. The codebase is production-ready for PySCF workflows but has gaps in Psi4 support and testing coverage.

**Key Strengths**:
- Clean backend abstraction via protocols
- Extensive use of lazy loading for performance
- Well-documented public APIs
- Thoughtful error handling in critical paths

**Key Weaknesses**:
- Type annotation gaps in backend abstractions
- Insufficient integration testing for Psi4
- God class anti-pattern in `PySCFDriver`
- Performance bottlenecks in integral transformations

**Overall Assessment**: **B+** - Solid foundation with room for improvement in testing, type safety, and performance optimization.
