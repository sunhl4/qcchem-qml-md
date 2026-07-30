---
title: P1 化学与嵌入
description: 分子、SCF、映射、双线路与嵌入选型决策指南。
---

# P1 化学与嵌入（Chemistry and embedding）

:::tip 模块手册
包级理论 / API / 参数 / 示例 → [chem 模块](/modules/chem/) · [dual-ingress](/modules/chem/dual-ingress) · [mappings](/modules/chem/mappings) · [embedding](/modules/chem/embedding) · [config](/modules/config)
:::

P1 对应化学问题定义层：把「要算什么」描述清楚，再交给后续算法和执行层。本页是**选型决策指南**；公式与 API 细节以模块手册为准。

## 你在 P1 主要做什么

- 定义分子几何、基组、电荷与自旋
- 选择 SCF 驱动（PySCF / Psi4 / precomputed）与活性空间策略
- 选定费米子—量子比特映射
- 配置 projection / DMET / Schmidt / ONIOM 等嵌入（或明确不用）

## 决策总表

| 决策点 | 常见选项 | 默认建议 | 模块深读 |
|--------|----------|----------|----------|
| 经典输入 | 在线几何 + SCF / `geometry_file` / `precomputed` | 小分子在线；大体系或 parity 用离线 | [dual-ingress](/modules/chem/dual-ingress) |
| SCF 驱动 | `pyscf` / `psi4` / 自定义 solver | CI 与日常用 PySCF；交叉验证用 Psi4 | [solvers](/modules/chem/solvers) · [Psi4](./psi4-backend) |
| 活性空间 | `cas` / `avas` / `manual` | H₂ 烟测用 `cas(2,2)` | [AVAS](./avas-casscf-workflow) |
| 映射 | JW / BK / SCBK / JKMN / HCB | 默认 JW；UCCSD 主线要求 JW | [mappings](./fermion-qubit-mappings) |
| 嵌入 | `none` / `projection` / `dmet` / `schmidt` / `oniom` / `plugin` | 先无嵌入跑通；再叠加 | [embedding](/modules/chem/embedding) |

## 何时不要用（边界）

| 场景 | 不要 | 原因 |
|------|------|------|
| 第一次跑通管线 | 同时开 DMET + AVAS + 自定义映射 | 无法定位失败点 |
| UCCSD 主线 | 随意改成 BK / HCB | UCCSD 实现标为 JW-only |
| 生产能量对比 | 把 post-variational 嵌入审计当主能量 | `embedding_workflow` 多为审计/演示 |
| 需要严格自洽 DMET | 把 toy / one-shot ledger 当论文级结果 | 见 DMET 模块页的 stub 边界 |
| 无 Psi4 环境 | 直接切 `scf.driver: psi4` | 需 micromamba / CI `pytest -m psi4` |

## 何时改算符 vs 何时仅审计

- **变分之前**（`build_pre_quantum_stage`）：Schmidt、projection、`embedding.mode=plugin`、或默认 canonical active-space integral pack 会确定 `QubitHamiltonian`；`PreQuantumInput.meta` 与 `repro.parity_snapshot` 写入 `hamiltonian_branch`、`hamiltonian_fixed_before_variational`。
- **变分之后**（`embedding_workflow`）：DMET fragment 演示、Schmidt per-fragment VQE、ONIOM 玩具元数据等**不**改写主路径上的 `qh`；`post_variational_embedding_audit_only=true` 表示审计/演示用途。
- 允许/禁止的 YAML 组合见仓库 [`docs/pre_quantum_yaml_matrix.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/pre_quantum_yaml_matrix.md)。

## 代表配置

| 意图 | YAML |
|------|------|
| 最小 H₂ | `configs/example_h2.yaml` |
| 双线路：几何文件 | `configs/example_h2_geometry_file_xyz.yaml` |
| 双线路：预计算包 | `configs/example_h2_precomputed_bundle.yaml` |
| JW → BK 对照 | `configs/example_h2_uccsd_bk.yaml` |
| Projection | `configs/example_h2_projection_trace.yaml` · `example_h4_projection_mulliken.yaml` |
| DMET 自洽演示 | `configs/example_h4_dmet_self_consistent.yaml` · `example_h2_dimer_dmet_self_consistent.yaml` |
| Schmidt | `configs/example_h4_schmidt_multifragment.yaml` |
| ONIOM 玩具 | `configs/example_oniom_toy.yaml` · `example_oniom_qm_mm_demo.yaml` |
| AVAS → CASSCF | `configs/example_h2_avas_casscf_workflow.yaml` |
| Psi4 RHF | `configs/example_h2_psi4_rhf_sto3g.yaml` |

## 推荐最小 YAML 形状

```yaml
schema_version: "2"
molecule:
  symbols: [H, H]
  coordinates: [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]
  coordinate_unit: bohr
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  mapping:
    fermion_qubit: jordan_wigner
  cas:
    n_orbitals: 2
    n_electrons: 2
embedding:
  mode: none
```

嵌入开启时只改 `embedding` 块；保持 `molecule` / `active_space` 不变，便于对照 `hamiltonian_fingerprint`。

## 嵌入模式速查

| `embedding.mode` | 作用阶段 | 典型用途 |
|------------------|----------|----------|
| `none` | — | 默认；canonical CAS 积分 |
| `projection` | pre_quantum | Mulliken / 投影嵌入 |
| `dmet` | 多为 post_variational 审计 + 部分自洽演示 | 分片 / bath |
| `schmidt` | pre_quantum（可改主哈密顿） | 碎片+浴轨道 |
| `oniom` | 多为元数据 / 玩具层 | QM/MM 层叠演示 |
| `plugin` | pre_quantum | 自定义分解插件 |

深读：[embedding](/modules/chem/embedding) · [DMET](/modules/chem/embedding-dmet) · [projection](/modules/chem/embedding-projection) · [Schmidt](/modules/chem/embedding-schmidt)。

## 输入与输出（维护视角）

- **输入**：`molecule`、`scf`、`active_space`、`embedding`、可选 `chemistry_extended`
- **输出**：`PreQuantumInput` / `QubitHamiltonian`，经 pipeline 交给 P2
- **审计键**：`hamiltonian_fingerprint`、`hamiltonian_branch`、`reference_energy_au`

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
cfg = load_experiment_config('configs/example_h2.yaml')
pqi = build_pre_quantum_input(cfg)
fp = getattr(pqi, 'hamiltonian_fingerprint', None)
if fp is None and getattr(pqi, 'meta', None):
  fp = pqi.meta.get('hamiltonian_fingerprint')
print('fingerprint', fp)
print('ok', fp is not None)
"
```

期望：打印非空 `fingerprint`，且 `ok True`。

更轻量的配置烟测：

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h4_dmet_self_consistent.yaml')
print(c.experiment_id, c.embedding.mode)
"
```

期望：`h4_dmet_self_consistent_demo dmet`。

## 常见误区

- 一次性改太多字段，导致无法定位问题来源
- 把化学定义和执行策略（shots / ZNE / jobs）混在同一「大爆炸」改动里
- 跳过最小样例直接上复杂体系
- 把 post-variational 嵌入能量当成主变分能量

## 推荐工作方式

1. `example_h2.yaml` 跑通 → 记录 fingerprint 与能量
2. 只改映射或只改嵌入，再对照 fingerprint
3. 需要 AVAS / Psi4 / DMET 时，分别用代表 YAML，不要手工拼未知组合
4. 对照 [pre_quantum YAML 矩阵](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/pre_quantum_yaml_matrix.md)

## 相关教程

- [Projection 嵌入深读](../tutorial/projection-embedding-deep-dive)
- [DMET 自洽烟测](../tutorial/dmet-self-consistent)
- [ONIOM 烟测](../tutorial/oniom-smoke)
- [CASSCF 审计](../tutorial/casscf-audit-workflow)

## 下一步

- [费米子—量子比特映射](./fermion-qubit-mappings)
- [双线路经典输入](./dual-classical-ingress)
- [后端适配快速接入](./backend-adapter-quickstart)
- [AVAS → CASSCF](./avas-casscf-workflow)
- 进入 [P2 程序构建](./program-construction)
