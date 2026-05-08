# ADR: Optional `SubprocessChemIntegralSolver`

- Status: proposed
- Date: 2026-05-08

## Context

Current adapters (`pyscf`, `psi4`) run in-process Python. Some external chemistry stacks are binary-first or environment-fragile, making in-process imports brittle for CI and plugin users.

## Decision

Introduce an **optional** adapter concept `SubprocessChemIntegralSolver` (design-only in this phase):

- keeps the same `ChemIntegralSolver` protocol surface,
- executes backend work in a subprocess boundary,
- exchanges only JSON-serializable payloads and canonical capability flags.

No implementation code is added in this ADR phase.

## Consequences

- Pros: tighter process isolation, dependency decoupling, easier multi-backend coexistence.
- Cons: serialization overhead, larger error-handling surface, more complex reproducibility metadata.

## Alignment checklist

- keep `create_solver` as the unique backend factory,
- preserve `SolverCapabilities` as branch gates,
- keep orchestration backend-agnostic after `ClassicalMeanFieldReference`.

## Mermaid sketch

```mermaid
flowchart LR
    Config[ExperimentConfig] --> Factory[create_solver]
    Factory --> SubprocessAdapter[SubprocessChemIntegralSolver]
    SubprocessAdapter --> Worker[BackendWorkerProcess]
    Worker --> Result[MolecularMeanFieldResult]
    Result --> Bridge[ClassicalMeanFieldReference]
    Bridge --> Pipeline[BackendAgnosticPipeline]
```
