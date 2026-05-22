# Config 入门：通俗导读

| 属性 | 值 |
|------|-----|
| **文档类型** | 入门导读（零基础友好） |
| **适合谁读** | 刚接触 `qchem_stack.config`、不熟悉 Python 对象模型的读者 |
| **详细参考** | [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md) |
| **校验规范** | [config_校验分层约定.md](config_校验分层约定.md) |

---

## 1. 这个模块在干什么

`qchem_stack.config` 做四件事：

```text
读实验 YAML → 检查有没有写错 → 变成 Python 对象 → 给后面的计算管线用
```

最后一句话里「变成 Python 对象」容易让人困惑——下面从这条链开始讲清楚。

---

## 2. 「变成 Python 对象」是什么意思

### 2.1 先说结论

**不是说 YAML 文件本身变成了对象。**

而是：程序**读取** YAML 文件后，在内存里构造出带类型、能检查、能点属性访问的数据结构，后面的代码就用这些结构，而不是反复去读磁盘上的文件。

### 2.2 分三步看

#### 第 1 步：磁盘上的 YAML（文本）

例如 `configs/example_h4_schmidt_multifragment.yaml`，在磁盘上就是一段**给人看的文本**：

```yaml
experiment_id: h4_schmidt_multifragment_demo
molecule:
  symbols: [H, H, H, H]
  charge: 0
```

程序不能直接对「字符串文件」做 `cfg.quantum.vqe.maxiter` 这种访问，必须先读进来。

#### 第 2 步：读成 Python 的 dict（字典）

`load_experiment_config` 里会先用 `yaml.safe_load` 把文本解析成 Python 里最常见的结构——**字典 + 列表**：

```python
{
    "experiment_id": "h4_schmidt_multifragment_demo",
    "molecule": {"symbols": ["H", "H", "H", "H"], "charge": 0, ...},
    ...
}
```

dict 已经是 Python 对象，但很「松」：

- 键名写错不会立刻报错（比如 `experment_id`）
- 不知道 `charge` 应该是 int 还是 str
- 没有 `.quantum.vqe.maxiter` 这种点号访问
- 不能挂方法（比如把坐标换算成 Bohr）

#### 第 3 步：整理成 `ExperimentConfig` 等强类型对象

项目用 Pydantic 把 dict **映射**到事先定义好的 Python 类上，比如 `ExperimentConfig`、`MoleculeSpec`。

加载完成后，你拿到的是内存里的**类实例**，不是文件：

```python
cfg = load_experiment_config("configs/example_h4_schmidt_multifragment.yaml")

type(cfg)                         # ExperimentConfig（不是 str，也不是 dict）
cfg.experiment_id                 # "h4_schmidt_multifragment_demo"
cfg.molecule.charge               # 0（已知是 int）
cfg.quantum.vqe.maxiter           # 点号访问嵌套字段
cfg.molecule.coordinates_in_bohr()  # 还可以调用方法
```

文档里说的「变成 Python 对象」，主要指**第 3 步**：从松散的 dict，变成有结构、有类型、能校验的类实例。

### 2.3 打个比方

| 阶段 | 像什么 |
|------|--------|
| YAML 文件 | 一张填好的**纸质表格** |
| `yaml.safe_load` 后的 dict | 抄进 Excel，但单元格类型都当文本 |
| `ExperimentConfig` | 导入**业务系统**：填错立刻报错，还能自动算衍生字段 |

### 2.4 为什么要多这一步

后面的计算管线需要**可靠的数据**：

1. **加载时就检查** — 类型不对、字段互斥、缺必填项，立刻报错
2. **IDE 和类型检查** — 知道 `cfg.quantum` 有哪些子块
3. **统一读取方式** — 用 helpers，不用到处 `cfg["quantum"]["vqe"]["maxiter"]`
4. **行为而不只是数据** — 如 `coordinates_in_bohr()` 把坐标换算好再给 chem 模块

---

## 3. `ExperimentConfig` 和 `MoleculeSpec` 是什么

### 3.1 一句话

- **`MoleculeSpec`**：这份实验里**分子本身**怎么描述（什么原子、在哪、电荷、基组……）
- **`ExperimentConfig`**：整份实验的**总清单**（分子 + SCF + 活性空间 + 量子算法 + 后端……全部打包）

### 3.2 `MoleculeSpec` — 分子档案卡

YAML 里 `molecule:` 那一块，加载后就变成 `MoleculeSpec` 对象。

**它回答：我要算的是哪个分子？长什么样？用什么基组？**

| 字段 | 通俗理解 |
|------|----------|
| `symbols` | 有哪些元素，如 `["H","H","H","H"]` |
| `coordinates` | 每个原子的 xyz 坐标 |
| `zmatrix` | 另一种写结构的方式；和 `coordinates` 二选一 |
| `coordinate_unit` | 坐标单位是埃还是 Bohr |
| `charge` | 总电荷，0 是中性 |
| `multiplicity` | 自旋多重度，单重态是 1 |
| `basis` | 基组，如 `sto-3g` |
| `ecp` | 是否用有效核芯势 |

**和普通 dict 的不同：**

- 加载时就检查（比如坐标和 zmatrix 不能同时写）
- 能「干活」，不只是存数据，例如 `cfg.molecule.coordinates_in_bohr()`

**示例：**

```yaml
molecule:
  symbols: [H, H]
  coordinates: [[0, 0, 0], [0, 0, 0.74]]
  charge: 0
  multiplicity: 1
  basis: sto-3g
```

```python
cfg = load_experiment_config("configs/example_h2.yaml")

cfg.molecule              # MoleculeSpec 对象
cfg.molecule.symbols      # ["H", "H"]
cfg.molecule.charge       # 0
```

### 3.3 `ExperimentConfig` — 整份实验的总文件夹

一个 YAML 文件加载后，**整份**变成 **一个** `ExperimentConfig` 对象。

**它回答：这次实验从头到尾要怎么跑？**

```text
ExperimentConfig（总文件夹）
├── molecule          → MoleculeSpec（分子）
├── scf               → SCFSpec（经典自洽场）
├── active_space      → ActiveSpaceSpec（活性空间）
├── quantum           → QuantumSpec（VQE/ADAPT 等）
├── embedding         → EmbeddingSpec（DMET/Schmidt 等）
├── backend           → 量子后端
└── ... 其他 sidecar
```

**示例：**

```python
cfg = load_experiment_config("configs/example_h4_schmidt_multifragment.yaml")

type(cfg)                 # ExperimentConfig
cfg.experiment_id         # "h4_schmidt_multifragment_demo"
cfg.molecule              # MoleculeSpec（嵌在里面）
cfg.scf.driver            # "pyscf"
cfg.quantum.vqe.maxiter   # 嵌套访问
```

### 3.4 两者怎么配合

**`ExperimentConfig` 是外层容器，`MoleculeSpec` 是其中一个必填子块。**

| 概念 | 像什么 |
|------|--------|
| `ExperimentConfig` | 一份**完整实验方案**（封面 + 各章节） |
| `MoleculeSpec` | 方案里**第 1 章：样品信息** |
| `QuantumSpec` 等 | 其他章节（怎么算、用什么机器） |

管线代码通常先拿整个 `cfg`，需要分子信息时再访问 `cfg.molecule`：

```python
cfg = load_experiment_config(path)

coords = cfg.molecule.coordinates_in_bohr()  # 分子
driver = cfg.scf.driver                      # SCF
maxiter = cfg.quantum.vqe.maxiter            # 量子
```

---

## 4. `cfg` 和 `ExperimentConfig` 什么关系

### 4.1 核心一句

**`cfg` 和 `ExperimentConfig` 不是两个并列的东西，而是「一个东西的两个层面」：**

- **`ExperimentConfig`** = 这种东西**叫什么类型**（类名）
- **`cfg`** = 你手里**这一份**东西**起什么变量名**

### 4.2 用手机类比

```python
phone = iPhone()
```

- **`iPhone`** = 手机**型号/类型**
- **`phone`** = 你口袋里的**这一部**，变量名叫 `phone`

配置里完全一样：

```python
cfg = load_experiment_config("configs/example_h2.yaml")
```

- **`ExperimentConfig`** = 这种对象的**类型名**
- **`cfg`** = 加载出来的**那一份**，变量名叫 `cfg`

```python
type(cfg)                    # ExperimentConfig
isinstance(cfg, ExperimentConfig)  # True
```

**`cfg` 就是名叫 `cfg` 的那一份 `ExperimentConfig`，不是副本，不是包装层。**

### 4.3 加载时在内存里发生什么

```text
example_h2.yaml（磁盘上的文件）
       │
       ▼
  load_experiment_config()
       │
       ▼
  ┌─────────────────────────┐
  │  ExperimentConfig 对象   │  ← 内存里真正存在的东西（只有这一份）
  │  experiment_id: my_h2   │
  │  molecule: {...}       │
  └─────────────────────────┘
       │
       │  赋给变量
       ▼
      cfg                    ← 只是给上面这个对象贴的标签/名字
```

你也可以换名字，指向同一个对象：

```python
cfg = load_experiment_config("...")
my_experiment = cfg
cfg is my_experiment   # True
```

### 4.4 常见误解

| 误解 | 实际情况 |
|------|----------|
| `cfg` 是 YAML，`ExperimentConfig` 是 Python 对象 | YAML 还在磁盘；`cfg` 已经是内存里的 Python 对象 |
| `cfg` 是 `ExperimentConfig` 的一部分 | `cfg` **整个就是**一个 `ExperimentConfig`；`cfg.molecule` 才是里面的一部分 |
| 先有一个 `ExperimentConfig`，再有一个 `cfg` 去用它 | `cfg = load_experiment_config(...)` 一行同时创建对象并绑定变量名 |

### 4.5 嵌套关系一览

```text
cfg  ──→  ExperimentConfig 对象（总配置）
              │
              ├── molecule  ──→  MoleculeSpec 对象
              ├── scf       ──→  SCFSpec 对象
              └── quantum   ──→  QuantumSpec 对象
```

| 写法 | 含义 |
|------|------|
| `cfg` | 整份实验配置 |
| `cfg.molecule` | 其中的分子部分 |
| `cfg.quantum.vqe.maxiter` | 量子 → VQE → maxiter |

---

## 5. `load_experiment_config` 和 `ExperimentConfig` 什么关系

### 5.1 一句话

**`ExperimentConfig` 是「配置对象这种类型」；`load_experiment_config` 是「从磁盘 YAML 文件造出这种对象的函数」。**

```text
load_experiment_config(...)  ──调用──▶  ExperimentConfig.from_yaml_dict(...)
                                              │
                                              ▼
                                        返回 ExperimentConfig 实例
```

### 5.2 各自干什么

| | `ExperimentConfig` | `load_experiment_config` |
|---|-------------------|-------------------------|
| **是什么** | 一个**类**（定义配置长什么样、怎么校验） | 一个**函数**（读文件并创建对象） |
| **在哪** | `experiment.py` | `io.py` |
| **输入** | 通常是 dict | YAML **文件路径** |
| **输出** | 调用后得到它的实例 | **返回** `ExperimentConfig` 实例 |
| **会不会读磁盘** | 不会 | 会 |

- **`ExperimentConfig`** = 模具 / 表格格式
- **`load_experiment_config`** = 开文件柜、拿出 YAML、填好表格、交给你

### 5.3 代码里怎么连起来

`load_experiment_config` 内部步骤：

```text
① 读文件文字          p.read_text()
② 变成 dict           yaml.safe_load(text)
③ 交给 ExperimentConfig  ExperimentConfig.from_yaml_dict(raw, ...)
④ 返回对象            → 通常赋给 cfg
```

拆开写等价于：

```python
text = Path("configs/example_h2.yaml").read_text()
raw = yaml.safe_load(text)
cfg = ExperimentConfig.from_yaml_dict(raw, geometry_files_base_dir=Path("configs"))
```

### 5.4 为什么要分成两个

**分工不同：**

| `load_experiment_config`（io.py） | `ExperimentConfig`（experiment.py） |
|----------------------------------|-------------------------------------|
| 管文件：在不在、能不能读、YAML 语法 | 管数据结构：有哪些字段、怎么校验 |
| 管相对路径基准目录 | 管跨 section 组合规则 |
| | 提供 `from_yaml_dict` / `model_validate` |

**没有 `load_experiment_config` 也可以有 `ExperimentConfig`：**

测试里经常不读文件，直接给 dict：

```python
cfg = ExperimentConfig.from_yaml_dict({
    "experiment_id": "test",
    "molecule": {...},
    "active_space": {...},
})
```

**没有 `ExperimentConfig`，`load_experiment_config` 也没意义**——它最终必须调用 `ExperimentConfig.from_yaml_dict`。

### 5.5 完整链条

```text
YAML 文件
   ↓ load_experiment_config（函数，读文件）
ExperimentConfig 对象（类型/实例）
   ↓ 通常赋给变量
cfg（变量名）
   ↓
cfg.molecule / cfg.scf / cfg.quantum ...
后面管线用这个对象跑计算
```

| 名字 | 角色 |
|------|------|
| YAML 文件 | 人写的原始配置 |
| `load_experiment_config` | **入口函数**：文件 → 对象 |
| `ExperimentConfig` | **对象类型**：规定配置是什么、怎么校验 |
| `cfg` | **变量名**：指向造出来的那个对象 |

### 5.6 三种常见用法

```python
# 方式 1：从文件加载（最常用）
cfg = load_experiment_config("configs/example_h2.yaml")

# 方式 2：已有 dict，不读文件（测试/API 常用）
cfg = ExperimentConfig.from_yaml_dict(data)

# 方式 3：把对象传给别的函数
validate_pre_quantum_contract(cfg)
run_pipeline_sync(cfg)
```

三种方式最后拿到的都是 **`ExperimentConfig` 实例**；区别只是**对象从哪来**。

---

## 6. 每个 section 的文件怎么拆（补充）

config 模块里，每个配置域（如 `embedding`、`quantum`）通常拆成五类文件：

```text
{section}_enums.py       # 合法选项（字符串 → 枚举）
{section}_specs.py       # 字段定义（子块长什么样）
{section}.py             # 对外入口（几种形态拼在一起）
{section}_helpers.py     # 给业务代码用的读取函数
_{section}_validation.py # 这一块内部的组合规则检查
```

| 文件 | 干什么 |
|------|--------|
| `*_enums.py` | YAML 里的字符串收成枚举，少写错字 |
| `*_specs.py` | 定义有哪些字段、默认值；只管结构 |
| `{section}.py` | 把几种子形态拼成整体，挂到 `ExperimentConfig` 上 |
| `_*_validation.py` | 同一块内部的复杂约束；跨块规则在 `_experiment_validation.py` |
| `*_helpers.py` | 业务代码用的 `require_*` / `resolve_*`，避免到处写 `if mode == ...` |

更完整的说明见 [说明_config模块技术参考手册.md §2.3](说明_config模块技术参考手册.md#23-每个-section-的文件怎么拆)。

---

## 7. 速查表

| 问题 | 答案 |
|------|------|
| YAML 文件是 Python 对象吗？ | 不是，是磁盘上的文本 |
| 「变成 Python 对象」指什么？ | 读入后在内存里构造 `ExperimentConfig` 等类实例 |
| `ExperimentConfig` 是什么？ | 整份实验配置的类型（总清单） |
| `MoleculeSpec` 是什么？ | 其中 `molecule` 那一块的类型（分子档案） |
| `cfg` 是什么？ | 通常指向某个 `ExperimentConfig` 实例的变量名 |
| `load_experiment_config` 是什么？ | 从 YAML 文件路径创建 `ExperimentConfig` 的函数 |
| 三者怎么串起来？ | YAML → `load_experiment_config()` → `ExperimentConfig` 实例 → 赋给 `cfg` |

---

## 8. 相关文档

| 文档 | 内容 |
|------|------|
| [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md) | 完整 API、文件清单、扩展流程 |
| [说明_实验配置加载_io.md](说明_实验配置加载_io.md) | `io.py` 通俗说明 |
| [说明_molecule配置与自旋多重度.md](说明_molecule配置与自旋多重度.md) | `molecule` 字段细节 |
| [config_校验分层约定.md](config_校验分层约定.md) | 校验分几层、提 PR 自查 |

---

## 9. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-22 | 初版：整理对话中的通俗解释（YAML→对象、ExperimentConfig/MoleculeSpec、cfg、load_experiment_config） |
