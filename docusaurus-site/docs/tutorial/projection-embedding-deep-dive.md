# Projection 嵌入深入

本页用于解释 projection 路径的配置语义、输出位置和验证方法。

## 目标

- 理解 projection 在配置中的位置
- 知道如何验证 projection 结果是否完整
- 建立从最小体系到复杂体系的渐进验证路径

## 关注点

- projection 相关配置键
- 与主变分流程的衔接位置
- 在 repro/parity_snapshot 中的记录方式

## 推荐执行顺序

1. 先使用最小配置跑通 projection 模式  
2. 检查 `run_summary` 与 `repro` 中 projection 相关键  
3. 再扩展到多原子或更复杂体系

## 最小实践建议

- 以 `example_h2` 家族配置为起点，避免直接在大体系调参
- 每次改动只调整一个 projection 相关块
- 保留运行配置快照，便于复盘

## 建议实践

- 先在最小体系验证字段完整性
- 再逐步扩展到多原子案例
- 对关键结果配套保存输入配置快照

## 下一步

- [案例：H2 家族链式改配](./case-study-h2-family)
- [P1 化学与嵌入](../guide/chemistry-and-embedding)
