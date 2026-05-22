# VQD 紧缩激发栈：行为、YAML 与机读出口

**定位**：说明开放栈内 **变分量子紧缩（VQD）** 的**可重复工程语义**（算法核、编排边界、JSON 契约）。  
**非目标**：声称与 Quantinuum Vendor platform 闭源包或 SandboxAQ Tangelo 默认实现的逐比特等价。

**实现入口**：`qchem_stack.quantum.algorithms.excited.VQD`；管线挂载：`qchem_stack.orchestration.pipeline`（`quantum.vqd_after_variational`）。

---

## 1. 算法核（单目标优化）

参考 Higgott 等 *Quantum* **3**, 156 (2019)。第 \(k\) 层（\(k\ge1\)）在态 \(|\psi(\theta)\rangle\) 上最小化标量目标：

\[
\mathcal{L}(\theta)= \langle H\rangle_{\psi(\theta)} + \lambda_k \sum_{j<k} \bigl|\langle \psi_j | \psi(\theta)\rangle\bigr|^{2p},
\]

其中 \(|\psi_j\rangle\) 为已接受的较低能级态（归一化），\(p=\) `quantum.vqd_overlap_exponent`（代码内对 \(\texttt{overlap\_exponent}\) 有下界裁剪）。  
**一层一次** `scipy.optimize.minimize`，方法由 `quantum.vqd_optimizer_method` 选择（`COBYLA` / `L-BFGS-B` / `Nelder-Mead`）；`quantum.vqd_cobyla_maxiter` 在各方法上用作迭代上限的共用命名。

**与 Vendor platform `AlgorithmVQD` 的边界**：公开文档中可将 Hamiltonian 期望值、重叠平方、权重等建模为多个 `Computable`；本栈在优化阶段将它们**折叠为上述单一标量**，便于与经典优化器直接对接。优化完成后仍可按通道写出 **`three_protocol`** 报告块（能量 / 重叠 / 权重及其可选 shot 估计），见 §4。

**与 Tangelo「deflation」叙事的边界**：Tangelo 侧常见叙事为在测量流程中附加 `deflation_circuits` 与系数。本栈默认在 **态向量或给定 executor** 上直接计算振幅重叠并写入正则项；当 `quantum.vqd_overlap_mode: deflation_circuit` 时，额外导出 **Fredkin/CSWAP swap-test CircuitIR sketch** 与 `qiskit_export_v1` 资源摘要（`backends/vqd_deflation_qiskit.py`），优化路径仍与 `statevector_overlap` 相同除非设置 VQD shot budgets。

---

## 2. 变分流形：HEA 与 UCCSD

| 场景 | `quantum.variational_ansatz` | VQD 参数化 | 基态角来源 |
|------|-----------------------------|------------|------------|
| 硬件高效 Ansatz | `hea`（默认） | `hea_state(angles, n_qubits, depth)`，`depth`=`quantum.vqe_depth` | 管线前置 VQE/ADAPT 输出的 `angles` |
| 簇 UCCSD | `uccsd` | `UCCSDVQE.prepare_state` / `UCCSDTrotterVQE.prepare_state`（由 `quantum.uccsd_trotter_steps` 是否为空选择） | **必须**与前置变分阶段同维参数向量；管线传入 `ground_angles` |

**约束**：

- **UCCSD + VQD / QSE / SCEOM**：均允许。QSE/SCEOM 在 `variational_ansatz=uccsd` 时通过 `build_uccsd_variational_model().prepare_state` 构建参考态；`qse.shot_mode=pauli_transitions` 使用 **fermionic singles** 基 + **grouped statevector Pauli shots**（`qse_transition.py`）；SCEOM `shots_per_matrix_element>0` 时对 M 元素使用 grouped Pauli shot sim。
- **UCCSD + PauliAveraging**：JW UCCSD CircuitIR prep + grouped Pauli shots（`quantum.pauli.use_protocol: true`）；`zne.mode=circuit_scale_fold` 与 UCCSD 互斥。
- **UCCSD + VQD** 要求前置变分已产出基态角；`VQD.run(..., ground_angles=..., ground_energy=...)` 内若使用 `prepare_state` 则禁止在无 `ground_angles` 时单独跑紧缩。

---

## 3. YAML（`quantum` 段常用键）

| 键 | 含义 |
|----|------|
| `vqd_after_variational` | 是否在变分结束后运行 VQD |
| `vqd_n_states` | 总层数（基态 + 激发层数）；能量列表长度 |
| `vqd_penalty_weight` | 标量 \(\lambda\)；当未设置 `vqd_penalty_weights` 时各层共用 |
| `vqd_penalty_weights` | 每层 \(\lambda_k\) 列表，长度须为 `vqd_n_states - 1` |
| `vqd_overlap_exponent` | 上式中的 \(p\) |
| `vqd_optimizer_method` | `COBYLA` / `L-BFGS-B` / `Nelder-Mead` |
| `vqd_cobyla_maxiter` | 通用最大迭代次数 |
| `vqd_init_strategy` | `legacy`（首层与历史行为一致）、`random_uniform`、`reuse_ground_perturb`、`previous_layer_perturb` |
| `vqd_init_noise_scale` | 扰动初始化幅度 |
| `vqd_max_overlap_warn` | 若与前序态平方重叠和超过阈值，写入 `meta.vqd_warnings`；`null` 关闭 |
| `vqd_shots_objective` / `vqd_shots_overlap` / `vqd_shots_weight` | 三通道报告的 shot 预算（可选） |

**示例配置**：

- HEA 基态 + VQD：`configs/example_h2_excited_smoke.yaml`
- UCCSD 基态 + 同簇紧缩：`configs/example_h2_vqd_uccsd.yaml`

---

## 4. 管线输出与机读契约

- **顶层**：`out["vqd"]` → `schema`: `excited_vqd_bundle_v1`；`energies` 为各层能量；`meta` 含算法元数据与通道列表。
- **`meta.vqd_channels`**：每层一条；第 0 层为基态引用；更高层含 `three_protocol`（`objective` / `overlap` / `weight` 三块汇报）。
- **`meta.vqd_variety_yaml`**：`hea` 或 `uccsd`，标明参数化来源。
- **`meta.tangelo_deflation_analogy_v1`** / **`meta.vqd_cross_stack_semantics_v1`**：跨栈叙事用的结构化摘要（**不等价于**闭源产品内部对象）。
- **`meta.vqd_warnings`**：可选，重叠过大时的可读告警列表。
- **复现**：`repro.run_summary` / `repro.parity_snapshot` 镜像部分 YAML 与运行态（键集合以编排与导出门禁为准；导出块见 `product_contract.PARITY_EXPORT_V3_STABLE_KEYS`）。

---

## 5. 与其它文档的关系

- 公开能力矩阵总表：`docs/public_parity_matrix.md` §2（`AlgorithmVQD` 行）。
- UCCSD 电路与映射边界：`docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md`
- Parity 快照白名单：`docs/技术文档_DMET与parity_snapshot开放契约.md`
