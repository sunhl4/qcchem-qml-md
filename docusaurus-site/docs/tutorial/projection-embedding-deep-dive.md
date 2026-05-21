# Projection 嵌入深入

本页用于解释 projection 路径的配置语义、输出位置和验证方法。

Nested 配置字段见仓库 [`docs/说明_embedding配置.md`](https://github.com/NVIDIA/qcchem-qml-md/blob/main/docs/说明_embedding配置.md)（**schema v2**）。

## 目标

- 理解 projection 在配置中的位置
- 知道如何验证 projection 结果是否完整
- 建立从最小体系到复杂体系的渐进验证路径

## 最小 YAML（nested）

轨迹-only（默认 global active space，变分 Hamiltonian 与全局 CAS 相同）：

```yaml
embedding:
  mode: projection
  n_scf_cycles_embedding: 1
  classical_reference_method: MP2
  projection:
    low_level: HF
    high_level: CAS
    threshold: 1.0e-8
```

Mulliken 片段 MO 变分 Hamiltonian（见 `configs/example_h4_projection_mulliken.yaml`）：

```yaml
embedding:
  mode: projection
  projection:
    quantum_hamiltonian: fragment_mulliken_mo
    fragment_atom_indices: [0, 1]
```

## 关注点

- `embedding.projection.*` 配置键（非 flat `projection_*` 前缀）
- 与主变分流程的衔接位置
- 在 repro/parity_snapshot 中的记录方式（输出键仍可能使用历史 flat 名，如 `projection_quantum_hamiltonian`）

## 推荐执行顺序

1. 先使用 `configs/example_h2_projection_trace.yaml` 跑通 projection 模式  
2. 检查 `run_summary` 与 `repro` 中 projection 相关键  
3. 再扩展到 `configs/example_h4_projection_mulliken.yaml`

## 最小实践建议

- 以 `example_h2` 家族配置为起点，避免直接在大体系调参
- 每次改动只调整 `embedding.projection` 子块
- 保留运行配置快照，便于复盘

## 下一步

- [案例：H2 家族链式改配](./case-study-h2-family)
- [P1 化学与嵌入](../guide/chemistry-and-embedding)
