# qchem-stack-uqc

UQC (幺正量子) Cloud Platform backend plugin for qchem-stack.

## Installation

```bash
pip install -e packages/qchem-stack-uqc
```

## Usage

Once installed, the UQC backend is automatically available:

```yaml
backend:
  provider: uqc
  meta:
    uqc_token: "your-api-token"
```

## Features

- Ion-trap quantum computer support via UQC cloud API
- Native gate set: rzz, rx, ry
- Automatic circuit transpilation
- Optional ZNE error mitigation
- Pauli measurement optimization

## API Reference

See the [qchem-stack documentation](../../docs/backends.md) for details.
