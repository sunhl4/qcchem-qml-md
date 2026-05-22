# Quantum 配置（`quantum` 节）

YAML 路径与 Python 属性一致，例如 `cfg.quantum.vqe.maxiter`。

## 顶层

| 字段 | 说明 |
|------|------|
| `algorithm` | 变分算法 id：`vqe`、`adapt`、`iqeb`、`tetris_adapt` 等 |
| `algorithm_factory` | 可选插件导入路径 `module:callable`；默认仅允许 `qchem_stack.*` 模块（见风格文档 §3.1） |

## 子块

| 子块 | 何时需要 |
|------|----------|
| `variational` | 变分 ansatz（`hea` / `uccsd`）与 `uccsd_trotter_steps` |
| `vqe` | `algorithm=vqe` 时的深度、优化器、初值策略 |
| `adapt` | `algorithm=adapt` / `tetris_adapt` |
| `iqeb` | `algorithm=iqeb` |
| `pauli` | Pauli 测量协议与采样模式 |
| `excited.vqd` / `excited.qse` / `excited.sceom` | 激发态后处理 |
| `demos.qpe` / `demos.vqs` | 演示侧车轨道 |
| `tensornet` | 张量网 stub |
| `graph` | workflow-preview 图边声明 |

## 示例（canonical 嵌套）

```yaml
quantum:
  algorithm: vqe
  variational:
    ansatz: hea
  vqe:
    depth: 1
    maxiter: 200
  pauli:
    use_protocol: true
    run_sampled: false
```

## 旧扁平键

仅接受嵌套块（如 `quantum.vqe.maxiter`）；`schema_version: "2"` 必填。

## 跨节校验

见 `config/_experiment_validation.py`（UCCSD 与 `active_space.mapping.fermion_qubit`、`md_ml_export` 等）。
