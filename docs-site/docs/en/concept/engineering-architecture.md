# Engineering architecture (English placeholder)

The English version is being filled in. Please refer to the Chinese page for the canonical content: [/concept/engineering-architecture](/concept/engineering-architecture).

The same layering applies in both languages:

| Layer | Modules |
|---|---|
| Domain config | `qchem_stack.config` |
| Chemistry drivers | `qchem_stack.chem.*` |
| Quantum algorithms | `qchem_stack.quantum.*` |
| Backends & protocols | `qchem_stack.backends.*`, `qchem_stack.protocols.*` |
| Orchestration | `qchem_stack.orchestration` |
| Integrations | `qchem_stack.integrations` |
| Jobs / cloud analogs | `qchem_stack.jobs` |
| Repro export | `qchem_stack.repro` |
| Errors | `qchem_stack.exceptions` |
