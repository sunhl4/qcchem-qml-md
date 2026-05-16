<style type="text/css">
/*
  正文：中文与英文混排均为四号 14 pt；与 docs/assets/generate_all_figures.py 插图内 14 pt 对齐。
  VS Code / Typora / HTML 导出预览生效；贴入 Word 时请将「正文」设为四号（中英 Times New Roman + 宋体）。
*/
body, .markdown-body, .markdown-preview-view, article {
  font-family: "Times New Roman", "Songti SC", "SimSun", "Noto Serif CJK SC", serif !important;
  font-size: 14pt !important;
  line-height: 1.65;
}
h1 { font-size: 16pt; font-weight: bold; margin-top: 0.65em; }
h2 { font-size: 15pt; font-weight: bold; }
h3 { font-size: 14pt; font-weight: bold; }
p, ul, ol, li, td, th, blockquote {
  font-size: 14pt !important;
}
table { font-size: 14pt !important; }
code, pre, tt {
  font-size: 14pt !important;
  font-family: Consolas, "Courier New", "Noto Sans Mono CJK SC", monospace;
}
</style>

# 量子计算化学框架汇报

## 一、为什么计算化学需要量子计算

### 1.1 经典计算的"维数灾难"

FCI 要显式展开多电子波函数，活性轨道一多，Slater 行列式数就指数爆炸：
$$
\dim \mathcal{H}_{\mathrm{FCI}}=\binom{n_{\mathrm{so}}}{N_e}
$$

量子计算的机会：用约 $n_{\mathrm{so}}$ 个量子比特承载 $2^{n_{\mathrm{so}}}$ 维态空间，只测能量等关键观测量。

**尺度感**：2 个 H₂O 就有 20 个电子；真实化学体系很快超出经典精确求解范围。

![Why Quantum Chemistry](assets/why_quantum_chemistry.png)

### 1.2 为什么量子计算机天然适合

分子本身就是量子系统。量子比特（qubit）和电子的量子态"同构"——用量子计算机模拟量子系统。

### 1.3 工程目标

**搭建严谨、可审计的编排层，让化学家能可靠地把分子问题翻译成量子电路，并把结果可信地用回化学**。

---

## 二、分子的"量子内核"：活性空间与嵌入（Embedding）

现阶段量子计算机只有有限的量子比特（NISQ 时代）。如何用有限算力算大分子？

![Active Space and Embedding](assets/active_space_embedding_sci.png)

### 2.1 策略：经典与量子各司其职

| 区域 | 负责方 | 方法 |
|------|--------|------|
| 外层骨架（灰色） | 经典计算机 | Hartree-Fock / DFT（低成本近似） |
| 核心活性区（彩色轨道） | 量子计算机 | VQE / ADAPT-VQE（高精度求解） |

---

## 三、竞品深度拆解：Vendor platform vs Tangelo

了解竞品是定位自身优势的前提。主要有两个标杆性竞品：

---

### 3.1 Vendor platform：商业完整平台（Quantinuum）

Vendor platform 是 Quantinuum 的**商业量子化学平台**，与 H-Series 离子阱、TKET 编译器和 Nexus 云深度集成。

#### 3.1.1 三支柱工作流

![Vendor platform Workflow](assets/commercial_stack_workflow.png)

Vendor platform 的核心是**「真机与运营一体」**：用强类型 API 串起 `Computable` / `Protocol`、TKET、Nexus 与 H-Series 后端，把哈密顿量推向可运营的真机测量：

```python
# 以下为示意伪代码 — 商业栈 API 以各厂商 SDK 为准，与本仓库无 L0 绑定。
fs = build_fermion_space(mol, active_space=(4, 4))
algo = AlgorithmVQE(fermion_space=fs, ansatz="UCCSD", optimizer="L-BFGS-B")
computable = algo.expectation_value(fs.hamiltonian)
result = Protocol(computable, backend="H1-1", shots=10000).run()
```

---

### 3.2 Tangelo：开源研究工具包（SandboxAQ）

[Tangelo](https://github.com/sandbox-quantum/Tangelo) 是 SandboxAQ 维护的 Apache-2.0 开源工具包，定位研究与教学。

#### 3.2.1 工作流详解

![Tangelo Workflow](assets/tangelo_workflow_detailed.png)

Tangelo 的设计理念是**"研究员至上"**——用 Python 字典传参，几行代码跑通 VQE：

```python
from tangelo.algorithms import VQESolver
from tangelo.molecule_library import mol_H2_sto3g

vqe = VQESolver({
    "molecule": mol_H2_sto3g,
    "ansatz": "UCCSD",
    "qubit_mapping": "JW",
    "backend_options": {"target": "qulacs"},
})
vqe.build()
energy = vqe.simulate()
```

---

### 3.3 竞品启发与工程取舍

| 对比维度 | Vendor platform（优势/劣势） | Tangelo（优势/劣势） | `qchem-stack` 启发落地（取其长、避其短） |
|----------|------------------------|----------------------|-------------------------------------------|
| 平台形态 | **优**：闭环成熟；**劣**：闭源锁定 | **优**：开源灵活；**劣**：交付链路轻 | 开源 + 插拔式架构，补齐工程交付 |
| 配置体验 | **优**：规范；**劣**：机制不透明 | **优**：字典上手快；**劣**：弱校验 | YAML + Pydantic，失败早且明确 |
| 可审计性 | **优**：企业流程完整；**劣**：核心黑盒 | **优**：代码可见；**劣**：中间产物弱 | 显式 Driver 输出 + 哈密顿量指纹 + 分阶段导出 |
| 后端执行 | **优**：硬件优化深；**劣**：绑定强 | **优**：多后端方便；**劣**：偏研究态 | `BackendSpec` 统一后端契约 |
| 作业管理 | **优**：队列/配额成熟；**劣**：成本高 | **优**：本地轻便；**劣**：缺少恢复 | FastAPI + SQLite 打底异步作业 |
| 目标定位 | 企业级，但开放性不足 | 科研高效，但交付不足 | 可交付的开源量子化学流水线 |

一句话总结三者的本质差异：

- **Vendor platform**：买一套完整的商业产品，省心但被锁死
- **Tangelo**：在 Notebook 里快速验证想法，灵活但难以交付
- **qchem-stack**：像搭工业流水线一样，严谨、可插拔、可审计

---

## 四、`qchem-stack` 现阶段工程：坚实骨架

我们的策略是：**先搭严谨骨架，再逐步扩展算法能力**。

<img src="assets/driver_interface_design.png" alt="Classical-to-Quantum Pipeline" style="zoom:33%;" />

整体流水线：**YAML 契约** → **经典 Driver** → **`QubitHamiltonian`** → **量子算法** → **Pauli 测量协议** → **Repro 导出**。

---

### 4.1 配置即契约（Config as Contract）

**文件**：`src/qchem_stack/config.py`

我们用 **Pydantic + YAML** 替代松散字典，把非法参数拦截在 pipeline 启动阶段：

```python
# 不合法的配置 → 立刻报错，而不是在运行 3 小时后崩溃
ExperimentConfig.model_validate({
    "molecule": {"symbols": ["H", "H"]},
    "active_space": {
        "n_active_orbitals": 100,   # 超过实际轨道数
        "fermion_qubit_mapping": "joddan_wigner"  # 拼写错误
    }
})
# → ValidationError: n_active_orbitals must be <= total orbitals
#                    fermion_qubit_mapping: must be one of [...]
```

这让错误尽早暴露，避免长时间运行后才发现参数拼错或越界。

---

### 4.2 经典计算化学：**统一契约** + **驱动层**（当前主路径：PySCF 全绑定）

经典计算不埋进 VQE Solver，而是收敛到独立 Driver 层。当前默认 PySCF；未来替换驱动或走 plugin 分支时，量子算法仍消费同一份标准结果。

**文件**：`src/qchem_stack/chem/drivers/pyscf_driver.py`

```python
@dataclass
class PySCFRHFResult:
    mf: Any
    e_tot: float
    mo_energy: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict

class PySCFDriver:
    @classmethod
    def from_config(cls, cfg: ExperimentConfig) -> "PySCFDriver": ...

    def run_rhf(self) -> PySCFRHFResult: ...
    def run_rohf(self) -> PySCFRHFResult: ...
    def run_uhf(self) -> PySCFRHFResult: ...
    def run_pbc_rhf(self) -> PySCFRHFResult: ...
```

**设计要点**：

- **品牌隔离**：PySCF 只停留在驱动层。
- **结果显式**：SCF 能量、轨道、体系与元数据统一返回。
- **配置收口**：RHF / ROHF / UHF / PBC 等由 YAML 进入 Driver。
- **可追溯**：关键输入输出写入 repro JSON。

---

### 4.3 哈密顿量构建与费米子映射

经典层产出统一结构后，哈密顿量模块把 SCF 参考转为 **`QubitHamiltonian`**，并从此与具体经典程序解耦。

**文件**：`src/qchem_stack/chem/hamiltonian.py`, `src/qchem_stack/chem/fermion_mapping_registry.py`

```python
def molecular_hamiltonian_from_pyscf(
    rhf: PySCFRHFResult,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: Literal[
        "jordan_wigner",
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev"
    ]
) -> QubitHamiltonian:
    """
    活性空间积分提取 → 自旋轨道转换 → OpenFermion InteractionOperator
    → 量子比特哈密顿量。返回带 SHA-256 指纹的 QubitHamiltonian 对象。
    """
```

**可复现性保障**：每个哈密顿量生成 SHA-256 指纹，用于校验相同配置下的算符一致性。

---

### 4.4 量子算法注册表

**文件**：`src/qchem_stack/quantum/algorithm_registry.py`, `src/qchem_stack/quantum/algorithms/`

已接入统一注册表的算法：

| 算法 | 类型 | 说明 |
|------|------|------|
| `vqe` | 基态变分 | UCCSD、HEA ansatz，多优化器支持 |
| `adapt` | 自适应变分 | 梯度驱动的 ansatz 自动生长 |
| `iqeb` | 基于 Pauli 选择的优化 | 比 ADAPT 更精细的泡利算符贡献排序 |
| `uccsd` | 化学启发 ansatz | 经典量子化学的量子类比金标准 |
| `uccsd_trotter` | Trotter 化分解 | 可配置步数的哈密顿量时间演化 |
| `vqd` | 激发态 | Variational Quantum Deflation |
| `qse` | 量子子空间展开 | 基态+激发态联算 |
| `sceom` | 方程运动 | 强关联激发态方法 |

切换算法只需修改 YAML 一行：

```yaml
quantum:
  algorithm: "adapt"   # 或 "iqeb", "uccsd", "vqd" …
```

---

### 4.5 Pauli 测量协议（五阶段）

**文件**：`src/qchem_stack/protocols/protocol.py`

`PauliAveragingProtocol` 将期望值计算拆成五个阶段：

```
instantiate → build → compile → run → evaluate
   (初始化)    (构建)   (编译)   (运行)  (后处理)
```

- **`build`**：按对易性分组，减少电路数
- **`compile`**：生成 `CircuitIR`，对接 TKET / Qiskit
- **`run`**：插拔式后端执行
- **`evaluate`**：由 bit-string histogram 重建期望值

---

## 五、已跑通的示例与可视化结果

### 5.1 快速运行命令

```bash
# 基础 H2 VQE（statevector 精确模拟）
python scripts/smoke_pipeline.py

# Qiskit Aer 真实 shots 路径
python scripts/smoke_pipeline.py --qiskit-shots

# IQEB 算法变体
python scripts/smoke_pipeline.py --iqeb

# 激发态 VQD
python scripts/smoke_pipeline.py --excited-only
```

---

### 5.2 H₂ VQE 优化收敛

**配置文件（出图专用）**：`configs/example_h2_vqe_figure_near_casci.yaml`（H₂/sto-3g，UCCSD，关闭 Pauli protocol）

![VQE Convergence](assets/vqe_convergence_demo.png)

---

### 5.3 经典方法 vs 量子方法能量对比（实跑导出）

同一体系（H₂/sto-3g）的能量与误差对比：

![Classical vs Quantum](assets/classical_quantum_comparison.png)

| 方法 | 能量 (Ha) | 误差 vs FCI (mHa) | 来源 |
|------|-----------|-------------------|------|
| Hartree-Fock | −1.116714 | 20.562 | `export_classical_quantum_comparison_data.py`（PySCF RHF） |
| MP2 | −1.129872 | 7.404 | 同上（PySCF MP2） |
| CCSD | −1.137276 | 0.0002 | 同上（PySCF CCSD） |
| **VQE（我们的平台）** | −1.137276 | **≈0** | 同上（UCCSD + L-BFGS-B 实跑最优值） |
| FCI（active-space CASCI） | −1.137276 | 0 | 同上（PySCF CASCI, 2e/2o） |

---

### 5.4 费米子–量子比特映射（提要）

平台通过 `active_space.fermion_qubit_mapping` 支持 JW、BK 与对称守恒 BK / SCBK。

## 附录 A. 最小运行示例

```bash
# 安装（开发模式）
pip install -e ".[dev]"

# 运行基础流水线（需 PySCF）
pip install pyscf openfermion
python scripts/smoke_pipeline.py

# 启动本地 API 服务
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000

# 预览工作流（无需真实计算）
curl http://127.0.0.1:8000/workflow-preview
```

---

## 附录 B. 标准配置文件示例（`configs/example_h2.yaml`）

```yaml
schema_version: "1"
experiment_id: "h2_sto3g_vqe_demo"

molecule:
  symbols: ["H", "H"]
  coordinates_bohr: [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]
  charge: 0
  multiplicity: 1
  basis: "sto-3g"

scf:
  driver: "pyscf"
  method: "RHF"

active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
  fermion_qubit_mapping: "jordan_wigner"

quantum:
  algorithm: "vqe"
  vqe_depth: 1
  use_pauli_protocol: true

backend:
  provider: "statevector"
  shots_per_circuit: 1024
```
