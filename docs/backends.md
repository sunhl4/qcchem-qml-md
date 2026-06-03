# Backends (`qchem_stack.backends`)

Execution targets for variational and Pauli-protocol stages. Configuration flows from YAML `backend:` through `backend_spec_from_config` into `BackendSpec` and `executor_from_spec`.

## `BackendSpec` providers

| `provider` | Install extra | Notes |
|------------|---------------|--------|
| `statevector` | core | Default exact simulation |
| `qiskit` | `pip install qchem-stack[quantum]` | Aer or hardware via Qiskit 2.x |
| `ionstack` | core | Inject `meta.expectation_fn` or `ionstack_endpoint: mock` |
| `uqc` | `pip install -e packages/qchem-stack-uqc` | UQC cloud plugin (optional) |
| `qulacs` | optional | Lightweight simulator hook |
| `cirq` | optional (`cirq`) | Conformance tests in nightly CI |
| `braket` | optional (`amazon-braket-sdk`) | Conformance tests in nightly CI |

Source of truth: [`src/qchem_stack/backends/spec.py`](../src/qchem_stack/backends/spec.py).

## YAML example

```yaml
backend:
  provider: statevector
  shots_per_circuit: 1024
  # target_energy_stderr: 0.001  # optional stderr-driven shot budget
```

For Qiskit Pauli bitstring sampling, also set `quantum.run_qiskit_shots_pauli_protocol: true` (mutually exclusive with `run_sampled_pauli_protocol`).

## Related docs

- [ENGINEERING_ARCHITECTURE.md](ENGINEERING_ARCHITECTURE.md) — layering and HTTP touchpoints
- [技术文档_设备比特串与Qiskit采样路径.md](技术文档_设备比特串与Qiskit采样路径.md) — Qiskit `get_counts` path
- [packages/qchem-stack-uqc/README.md](../packages/qchem-stack-uqc/README.md) — UQC cloud plugin
