# Molecule 配置说明、自旋多重度与 ECP

本文说明实验 YAML 中 `molecule:` 段各字段的作用、与 `MoleculeSpec`（`src/qchem_stack/config/molecule.py`）的对应关系，以及 **自旋多重度（multiplicity）** 与 PySCF `spin` 的换算、**有效核势（ECP）** 的写法与注意点。配置校验分层见 [config_校验分层约定.md](config_校验分层约定.md)；`geometry_file` 在线路中的位置见 [技术文档_双线路经典输入与统一PreQuantumInput契约.md](技术文档_双线路经典输入与统一PreQuantumInput契约.md)。

---

## 1. YAML 与 `MoleculeSpec` 为何看起来不一致

`MoleculeSpec` 只描述**加载完成后**内存中的分子对象。部分 YAML 键在 Pydantic 校验**之前**由预处理展开，因此不会出现在类定义里。

典型流程（`load_experiment_config`，详见 [说明_实验配置加载_io.md](说明_实验配置加载_io.md)）：

```
example_*.yaml
    → yaml.safe_load                    # io.py
    → preprocess_experiment_dict_geometry_files   # geometry_files.py
    → ExperimentConfig.model_validate   # experiment.py
    → cfg.molecule: MoleculeSpec
    → coordinates_in_bohr()  # 内部一律 Bohr
```

| YAML 里可能写的 | 是否在 `MoleculeSpec` 中 | 说明 |
|-----------------|--------------------------|------|
| `geometry_file` | **否**（预处理键） | 读 `.xyz` 等，填入 `symbols` + `coordinates` 后删除该键 |
| `geometry_file_format` | **否** | 可选，当前支持 `xyz` |
| `symbols` | **是**（必填） | 元素符号列表；用 `geometry_file` 时可由文件自动填入 |
| `coordinates` / `coordinates_bohr` | **是**（与 `zmatrix` 二选一） | 笛卡尔坐标；`coordinates_bohr` 为旧键名 |
| `zmatrix` / `z_matrix` | **是** | 内坐标；需 PySCF 转成笛卡尔 |
| `coordinate_unit` | **是** | `angstrom` 或 `bohr` |
| `charge`, `multiplicity`, `basis`, `ecp` | **是** | 电荷、多重度、基组、ECP |

示例：`configs/example_h2_geometry_file_xyz.yaml` 只写 `geometry_file`，加载后等价于内联 `symbols` + `coordinates`（见 `configs/structures_h2.xyz`）。

### 1.1 外置几何文件（`geometry_file`）与坐标单位（必读）

> **读源码：** 各函数职责、调用链、扩展清单见 [说明_geometry_files源码学习.md](说明_geometry_files源码学习.md)。

`geometry_files.py` 只负责**读文件并把数字填进** `molecule.coordinates`；**长度单位由 YAML 的 `coordinate_unit` 决定**，在 `MoleculeSpec.coordinates_in_bohr()` 里才统一成 Bohr。两步分开理解，避免把「文件里是什么单位」和「配置声明是什么单位」混在一起。

#### 加载分两阶段

| 阶段 | 代码 | 做什么 |
|------|------|--------|
| ① 预处理 | `merge_molecule_dict_from_geometry_file` | 读 `.xyz` → `symbols` + `coordinates`（**数值原样拷贝**，不在此步换算单位） |
| ② 运行时 | `coordinates_in_bohr()` | 按 `coordinate_unit`：埃 → 乘常数转 Bohr；已是 `bohr` → 不换算 |

```
structures_h2.xyz (Å 惯例)
    → coordinates: [[0,0,0], [0,0,0.74]]   # 仍是「文件里的数」
    → coordinate_unit: angstrom            # YAML 声明含义
    → coordinates_in_bohr()                # 内部 (N,3) Bohr
```

#### XYZ 文件的惯例

- `parse_xyz` 按常见 **XYZ 习惯**解析第三列起的三个浮点数；社区与本仓库样例（如 `configs/structures_h2.xyz`）通常按 **埃（Å）** 填写。
- **XYZ 文件本身没有单位字段**；工程不会在 xyz 里自动识别 Bohr。

#### `coordinate_unit` 怎么填

| `coordinate_unit` | 含义 | 典型用法 |
|-------------------|------|----------|
| `angstrom`（**默认**） | `coordinates` 里的数是 **Å** | `geometry_file` 读入的标准 xyz；内联 `coordinates:` 也推荐显式写此项 |
| `bohr` | `coordinates` 里的数 **已经是 Bohr** | 与旧键 `coordinates_bohr` 或未写 unit 时用 `coordinates_bohr` 等价 |

**注意：** 阶段①不会读 xyz 里的「单位」；阶段②**完全信任** `coordinate_unit`。填错会导致键长差约 **1.89 倍**（Å 被当成 Bohr，或反过来）。

#### 用户易错场景

**错误 A — 文件是 Å，`coordinate_unit: bohr`**

```yaml
molecule:
  geometry_file: "structures_h2.xyz"   # 文件内 0.74 实为 0.74 Å
  coordinate_unit: bohr              # 误：把 0.74 当成 0.74 Bohr
```

后果：几何严重压缩，SCF/量子阶段能量与结构错误，且不一定立刻报错。

**错误 B — 文件实际是 Bohr，却用默认 `angstrom`**

```yaml
molecule:
  geometry_file: "my_geom_bohr.xyz"
  # 未写 coordinate_unit → 默认 angstrom
```

后果：坐标被多乘一次 Å→Bohr，键长偏大。

**推荐写法（外置 xyz，Å）**

```yaml
molecule:
  geometry_file: "structures_h2.xyz"
  coordinate_unit: angstrom   # 建议显式写出，避免误解
  charge: 0
  multiplicity: 1
  basis: sto-3g
```

完整样例：`configs/example_h2_geometry_file_xyz.yaml`。

**若 xyz 内已是 Bohr**

- 要么 YAML 设 `coordinate_unit: bohr`；
- 要么不用 `geometry_file`，改用内联 `coordinates_bohr`（且勿再写 `coordinate_unit: angstrom`）。

#### 与内联坐标、旧键名一致

| 几何来源 | 建议 `coordinate_unit` |
|----------|-------------------------|
| `geometry_file`（标准 Å 的 xyz） | `angstrom` |
| 内联 `coordinates:`（Å） | `angstrom` |
| 内联 `coordinates_bohr:`（未写 unit 时自动 `bohr`） | 省略或 `bohr` |

#### 自检

加载配置后可在 Python 中核对（需已安装工程依赖）：

```python
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2_geometry_file_xyz.yaml")
m = cfg.molecule
print(m.coordinate_unit)           # angstrom
print(m.coordinates)               # 与 xyz 中数值相同
print(m.coordinates_in_bohr()[1, 2])  # H–H 间距方向：≈ 0.74 * 1.889725... Bohr
```

实现参考：[说明_geometry_files源码学习.md](说明_geometry_files源码学习.md)（读文件与各函数）、`molecule.py` 中 `coordinates_in_bohr()`（单位换算）。

---

## 2. `MoleculeSpec` 各字段作用

实现位置：`src/qchem_stack/config/molecule.py`。

### 几何（必须提供一种结构来源）

**`symbols: list[str]`**（必填）  
元素符号，顺序与坐标一一对应，例如 `["H", "H"]`。

**`coordinates: list[list[float]] | None`**  
笛卡尔坐标，每原子 `[x, y, z]`。YAML 可用 `coordinates` 或旧名 `coordinates_bohr`（未写 `coordinate_unit` 时后者按 **Bohr** 理解）。经 `coordinates_in_bohr()` 统一为 **Bohr**（与 PySCF 内部一致）。

**`zmatrix: str | None`**  
Z-matrix 文本（PySCF `gto.M(atom=...)` 格式）。与 `coordinates` **互斥**；无笛卡尔坐标时用 PySCF 转换，需已安装 PySCF。

**`coordinate_unit: Literal["angstrom", "bohr"]`**（默认 `"angstrom"`）  
仅作用于 `coordinates` 数值的单位。使用键 `coordinates_bohr` 且未显式指定时，校验器会自动设为 `bohr`。

### 电子态与基组

**`charge: int = 0`**  
体系总电荷：`0` 中性，`+1` 少一个电子，`-1` 多一个电子。  
电子数：$N_{\text{elec}} = \sum_i Z_i - \text{charge}$。

**`multiplicity: int = 1`**  
自旋多重度 $2S+1$（见下文第 3 节）。

**`basis: str = "sto-3g"`**  
基组名称字符串；**默认** STO-3G，可改为 PySCF/Psi4 支持的名称（如 `6-31g`、`cc-pvdz`），无仓库内白名单限制。

**`ecp: str | dict[str, str] | None = None`**  
有效核势（ECP）；默认 `None` 表示全电子计算。详见下文 **第 4 节**。

### 字段写法风格说明

几何相关字段使用 `Field`、别名与 `@model_validator`（兼容旧 YAML、互斥、单位）；`charge` / `basis` 等为简单标量默认值，直接映射到 `MolecularSystem` 与 PySCF/Psi4。行为一致，仅 schema 声明风格不同。

---

## 3. 自旋多重度（multiplicity）详解

### 3.1 三个量分别是什么

| 名称 | 符号 / 配置 / 代码 | 含义 |
|------|-------------------|------|
| **自旋多重度** | YAML: `multiplicity`，默认 `1` | 该电子态的自旋简并度（多少个自旋本征态） |
| **总自旋量子数** | $S$ | 总电子自旋角动量大小（单位 $\hbar$） |
| **PySCF 的 `spin`** | `gto.M(..., spin=...)` | **不是** $S$，而是 $2S$，也等于 $N_\alpha - N_\beta$ |

非相对论、忽略旋轨耦合时的关系：

$$
\text{multiplicity} = 2S + 1
$$

因此：

$$
S = \frac{\text{multiplicity} - 1}{2}, \qquad
\text{PySCF 的 } \texttt{spin} = 2S = \text{multiplicity} - 1
$$

本仓库构建 PySCF 分子时（`pyscf_solver.py`、`molecule.py` 的 z-matrix 分支）：

```python
spin=self.system.multiplicity - 1   # 或 int(self.multiplicity) - 1
```

Psi4 几何块第一行使用化学惯例 `charge multiplicity`（`psi4_solver.py`），**直接传 `multiplicity`**，不在 YAML 层写 PySCF 的 `spin`。

**配置层只暴露 `multiplicity`，避免与 PySCF `spin` 混用两套数字。**

### 3.2 例子

| 体系 | $S$ | multiplicity | PySCF `spin` |
|------|-------|--------------|--------------|
| 中性 H₂ 闭壳基态 | 0 | 1（单重态 singlet） | 0 |
| 自由基（一个未配对电子） | 1/2 | 2（双重态 doublet） | 1 |
| O₂ 基态（两未配对、自旋平行） | 1 | 3（三重态 triplet） | 2 |

记忆：**multiplicity = PySCF spin + 1**；**PySCF spin = 2S**（未配对自旋在 $2S$ 意义下的计数）。

### 3.3 与 `charge` 的一致性

$$
N_{\text{elec}} = \sum_i Z_i - \text{charge}
$$

$$
N_\alpha = \frac{N_{\text{elec}} + (\text{multiplicity}-1)}{2}, \quad
N_\beta = \frac{N_{\text{elec}} - (\text{multiplicity}-1)}{2}
$$

$N_\alpha$、$N_\beta$ 须为非负整数，否则 PySCF 报错或得到无物理意义的态。

| 体系 | charge | $N_{\text{elec}}$ | 常见 multiplicity | 说明 |
|------|--------|---------------------|-------------------|------|
| 中性 H₂ | 0 | 2 | 1 | 闭壳，偶数电子 → 通常单重态 |
| H₂⁺ | +1 | 1 | 2 | 奇数电子 → 双重态 |
| 中性 O₂ 基态 | 0 | 16 | 3 | 三重态基态 |
| 中性 O₂ 单重激发态 | 0 | 16 | 1 | 不同电子态，需刻意指定 |

**multiplicity 指定的是要计算的电子态的自旋对称性**，不会从几何自动推断；基态是 1 还是 3 需化学/实验知识。

### 3.4 与 `scf.method` 的关系

- **multiplicity**：态的 $2S+1$。
- **RHF / ROHF / UHF**（`scf.method`）：HF 如何处理自旋。

| multiplicity | 常见 HF |
|--------------|---------|
| 1（闭壳） | RHF 通常足够 |
| 2、3、…（开壳） | 常需 UHF 或 ROHF；开壳体系仅用 RHF 可能不正确或无法收敛 |

`multiplicity` 与 `scf` 需一起合理设置。

### 3.5 YAML 示例

```yaml
molecule:
  symbols: ["H", "H"]
  coordinates: [[0, 0, 0], [0, 0, 0.74]]
  coordinate_unit: angstrom
  charge: 0
  multiplicity: 1    # 闭壳单重态；自由基用 2；O₂ 基态用 3
  basis: sto-3g
```

外置几何文件时（`geometry_file` 展开后同样适用）：

```yaml
molecule:
  geometry_file: "structures_h2.xyz"
  coordinate_unit: angstrom
  charge: 0
  multiplicity: 1
  basis: sto-3g
```

### 3.6 快速对照

| 意图 | YAML |
|------|------|
| 闭壳单重态基态 | `multiplicity: 1` |
| 一个未配对电子 | `multiplicity: 2` |
| 两未配对电子、自旋平行 | `multiplicity: 3` |
| PySCF 内部（无需在 YAML 写） | `spin = multiplicity - 1` |

---

## 4. 有效核势（ECP）详解

### 4.1 是什么、何时使用

**ECP（Effective Core Potential，有效核势）** 又称赝势：对重元素用解析势 + 价层基函数**代替**内层芯电子的显式量子化处理，只保留价层（及必要时次价层）电子参与 SCF。

| 场景 | 是否常用 ECP |
|------|----------------|
| H、C、N、O 等轻元素小分子 | 通常 **不用**（`ecp: null` 或省略，全电子 + `sto-3g` / `6-31g` 等） |
| 过渡金属、镧系、含 Br/I 等较重卤素 | **常用**（如 `lanl2dz`、`def2-svp` 配套 ECP） |
| 需要显式芯区性质（如 NMR 芯屏蔽、绝对全电子能量对比） | 不用 ECP，改用全电子大基组 |

本仓库 **不实现** ECP 数学形式，只做配置透传：`MoleculeSpec.ecp` → `MolecularSystem.ecp` → PySCF `gto.M(..., ecp=...)`（与 [PySCF 文档](https://pyscf.org/user/gto.html#ecp) 一致）。能否跑通取决于当前 PySCF 安装是否包含对应 ECP 数据表。

### 4.2 三种配置形态

类型定义：`ecp: str | dict[str, str] | None = None`（`molecule.py` / `chem/system.py`）。

| 取值 | YAML 示例 | 行为 |
|------|-----------|------|
| **`None` / 省略** | （不写 `ecp`） | 全电子：每个原子的电子数由原子序数 $Z$ 决定 |
| **字符串** | `ecp: "lanl2dz"` | 对**每一个**原子尝试套用同名 ECP（PySCF 按元素查找该族下是否有定义） |
| **字典** | `ecp: {Pt: "lanl2dz", Cl: "lanl2dz"}` | **按元素符号**分别指定；未出现在字典里的元素一般为全电子（PySCF 规则） |

字典形式适用于**混合体系**：例如有机配体 + 金属中心，仅对金属（及部分配位原子）用 ECP，轻元素 H/C/N/O 仍全电子。键为 **元素符号字符串**（与 `symbols` 中一致，如 `"Pt"`、`"Mg"`）。

本仓库 **不在配置层校验** ECP 名称是否合法、是否与 `basis` 匹配；错误通常在 PySCF 建 `Mol` 或 SCF 阶段抛出。

### 4.3 与 `basis` 必须配套使用

ECP 永远和 **价层基组** `basis` 联用，且二者应来自**同一套赝势族**（同一文献/参数化），例如：

| 常见组合 | `basis` | `ecp` |
|----------|---------|-------|
| LANL2DZ 族 | `lanl2dz` | `lanl2dz` |
| （其他族） | 按 PySCF 内置名 | 与 basis 同名的 ECP 标签 |

**不要**对重金属只写 `basis: sto-3g` 而不写 ECP（基组本身也不适用于重元素）；也**不要**只写 `ecp` 却用与赝势不匹配的 `basis`（如 `basis: 6-31g` + `ecp: lanl2dz`），否则能量与轨道无可靠物理意义。

仓库内 parity 样例（Mg、HBr）均采用 **`basis` 与 `ecp` 同为 `lanl2dz`**：

- `configs/example_mg_lanl2dz_ecp_rhf.yaml`
- `configs/example_mg_lanl2dz_ecp_density_fit.yaml`
- `configs/example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml`

### 4.4 与 `charge`、`multiplicity` 的关系

使用 ECP 后，PySCF 中的 **电子数、自旋** 指 **价电子（赝势定义下的活性电子）**，不再等于全电子体系的 $\sum_i Z_i - \text{charge}$。

- **`charge`**：仍表示体系**总电荷**（相对中性分子得失电子数），但作用于价电子计数。
- **`multiplicity`**：仍表示价层电子态的 $2S+1$，换算 `spin = multiplicity - 1` 的方式不变（见第 3 节）。

例如中性 Mg 原子用 `lanl2dz`+ECP 时，价层为闭壳，仍常用 `multiplicity: 1`；开壳金属配合物则按价层未配对电子设 `2` 或更高。

### 4.5 在代码中的传递路径

```
YAML molecule.ecp
  → MoleculeSpec.ecp
  → MolecularSystem.ecp
  → PySCFIntegralSolver._make_mol → gto.M(..., ecp=...)
```

z-matrix 几何分支在 `MoleculeSpec.coordinates_in_bohr()` 里建临时 `gto.M` 时同样传入 `ecp=self.ecp`。

单元测试确认透传：`tests/chem/test_pyscf_solver_adapter.py::test_ecp_is_forwarded_to_pyscf_mol`。

**Psi4 路径（`scf.driver: psi4`）**：当前 `ecp` 会写入 `MolecularSystem` 与 `driver_meta["ecp"]`，但 **Psi4 SCF 入口尚未把 ECP 写入 Psi4 计算选项**（仅记录配置）。重元素 + ECP 的端到端经典计算请优先使用 **`scf.driver: pyscf`**。

### 4.6 YAML 示例

**全电子（默认，H₂ 等轻分子）：**

```yaml
molecule:
  symbols: ["H", "H"]
  coordinates: [[0, 0, 0], [0, 0, 0.74]]
  basis: sto-3g
  # ecp 省略 → None
```

**单一 ECP 族（全体原子，Mg parity 样例）：**

```yaml
molecule:
  symbols: ["Mg"]
  coordinates: [[0.0, 0.0, 0.0]]
  coordinate_unit: angstrom
  charge: 0
  multiplicity: 1
  basis: "lanl2dz"
  ecp: "lanl2dz"
```

**按元素指定（混合体系示意）：**

```yaml
molecule:
  symbols: ["Pt", "Cl", "Cl", "H", "H"]
  coordinates: [...]
  basis: "lanl2dz"
  ecp:
    Pt: "lanl2dz"
    Cl: "lanl2dz"
  # H 未列出 → PySCF 对 H 通常仍按全电子处理（具体以 PySCF 行为为准）
```

可与 `zmatrix`、`geometry_file`、`scf.density_fit` 等组合；见 `configs/example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml`。

### 4.7 常见错误与排查

| 现象 | 可能原因 |
|------|----------|
| `KeyError` / `ECP not found` | ECP 名称拼写错误或当前 PySCF 未带该库 |
| SCF 不收敛或能量异常 | `basis` 与 `ecp` 不匹配，或活性空间 / 电荷 / 多重度与价电子数不一致 |
| 轻元素误用 ECP | 对 H/C 全体写 `ecp: lanl2dz` 往往无必要且可能无对应参数 |
| Psi4 路径能量像全电子 | 见 4.5：ECP 尚未接入 Psi4 计算体 |

### 4.8 快速对照

| 意图 | YAML |
|------|------|
| 全电子（默认） | 省略 `ecp` 或 `ecp: null` |
| 全体同一赝势 | `ecp: "lanl2dz"`（并与 `basis` 配套） |
| 仅部分元素用 ECP | `ecp: {Pt: "lanl2dz", ...}` |
| PySCF 内部参数名 | 与配置 `ecp` 相同，原样传入 `gto.M` |

---

## 5. 在 Python 中确认加载结果

```python
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2_geometry_file_xyz.yaml")
m = cfg.molecule
print(m.symbols)              # ['H', 'H']
print(m.coordinates)          # 来自 xyz 的坐标
print(m.coordinate_unit)      # angstrom
print(m.multiplicity)         # 1
# 无 geometry_file 属性；几何已合并进 symbols/coordinates
```

加载含 ECP 的配置：

```python
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_mg_lanl2dz_ecp_rhf.yaml")
print(cfg.molecule.basis)  # lanl2dz
print(cfg.molecule.ecp)    # lanl2dz
```

---

## 6. 相关源码与样例

| 内容 | 路径 |
|------|------|
| `MoleculeSpec` | `src/qchem_stack/config/molecule.py` |
| `MolecularSystem.ecp` | `src/qchem_stack/chem/system.py` |
| `geometry_file` 预处理 | [说明_geometry_files源码学习.md](说明_geometry_files源码学习.md) · `src/qchem_stack/config/geometry_files.py` |
| 配置加载入口 | `src/qchem_stack/config/io.py` |
| PySCF `spin` / `ecp` | `src/qchem_stack/chem/solvers/pyscf_solver.py`（`_make_mol`） |
| Psi4（`ecp` 元数据） | `src/qchem_stack/chem/solvers/psi4_solver.py` |
| ECP 透传测试 | `tests/chem/test_pyscf_solver_adapter.py` |
| 几何文件示例 | `configs/example_h2_geometry_file_xyz.yaml`、`configs/structures_h2.xyz` |
| ECP + LANL2DZ 样例 | `configs/example_mg_lanl2dz_ecp_rhf.yaml`、`example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml` |
