# P1 化学与嵌入（Chemistry and embedding）

P1 对应化学问题定义层：把“要算什么”描述清楚，再交给后续算法和执行层。

## 你在 P1 主要做什么

- 定义分子几何、基组、电荷与自旋
- 选择 SCF 驱动与活性空间参数
- 配置 projection/DMET 等嵌入相关键（详见仓库 [`docs/说明_embedding配置.md`](https://github.com/NVIDIA/qcchem-qml-md/blob/main/docs/说明_embedding配置.md)）

## 输入与输出（维护视角）

- **输入**：`molecule`、`scf`、`active_space`、`embedding` 配置块
- **输出**：后续 P2/P3 所需的结构化化学问题表示（通过 pipeline 串联）

## 常见误区

- 一次性改太多字段，导致无法定位问题来源
- 把化学定义和执行策略混在一起，配置难维护
- 跳过最小样例直接上复杂体系，调试成本过高

## 推荐工作方式

- 先用最小样例 YAML 跑通，再逐步叠加字段
- 保持问题定义与执行参数分层
- 对关键字段保留可读注释，方便团队协作

## 何时改算符 vs 何时仅审计

- **变分之前**（`build_pre_quantum_stage`）：Schmidt、projection、`embedding.mode=plugin`、或默认 **canonical active-space integral pack** 会确定 `QubitHamiltonian`；`PreQuantumInput.meta` 与 `repro.parity_snapshot` 写入 `hamiltonian_branch`、`hamiltonian_fixed_before_variational`。
- **变分之后**（`embedding_workflow`）：DMET fragment 演示、Schmidt per-fragment VQE、ONIOM 玩具元数据等 **不** 改写主路径上的 `qh`；`post_variational_embedding_audit_only=true` 表示审计/演示用途。
- 允许/禁止的 YAML 组合见仓库 [`docs/pre_quantum_yaml_matrix.md`](https://github.com/NVIDIA/qcchem-qml-md/blob/main/docs/pre_quantum_yaml_matrix.md)（机读验收表）。

## 下一步

- [后端适配快速接入](./backend-adapter-quickstart)（新经典后端、`scf.driver`、entry points）
- [双线路经典输入（在线 + 离线）](./dual-classical-ingress)（`geometry_file` 在线求解 + `precomputed` 离线数据集）
- 进入 [P2 程序构建](./program-construction)。
