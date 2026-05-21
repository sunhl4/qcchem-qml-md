# 实验配置怎么从 YAML 读进来（`config/io.py`）

本文用通俗说法说明 `src/qchem_stack/config/io.py` 是干什么的、里面每个函数有什么用。它不教你怎么写 yaml 里每一个字段（分子见 [说明_molecule配置与自旋多重度.md](说明_molecule配置与自旋多重度.md)，经典 `scf:` 见 [说明_scf配置.md](说明_scf配置.md)，活性空间见 [说明_active_space配置.md](说明_active_space配置.md)，全仓库字段分层见 [config_校验分层约定.md](config_校验分层约定.md)）。

---

## 一句话

**`io.py` 是实验配置单的「收发室」：** 把磁盘上的 `.yaml` 读进来变成程序里的总配置对象；需要时再把对象变回 yaml 文字；另外把「量子设备、编译线路」相关设置单独打包给后面的模块。

这里**不算**分子能量、**不跑**量子线路，只做读文件、转格式、摘几段配置。

---

## 在整条流程里站在哪

你做实验时，往往在 `configs/` 里写一个 yaml，里面包括：分子长什么样、用哪家经典软件算、活性空间多大、量子模拟器怎么设、线路怎么编译等。

```
  configs/example_h2.yaml     ← 人用编辑器写的文件
           │
           ▼
      io.py（本模块）          ← 读文件、报错要说清楚
           │
           ▼
   ExperimentConfig          ← 程序里的「一整份实验设置」
           │
           ├── 经典化学、活性空间、VQE…（别的模块继续干）
           ├── backend_spec_from_config      → 量子后端
           └── compiler_*_from_config        → 编译线路
```

和邻居的分工：

| 模块 | 干什么 |
|------|--------|
| **`io.py`** | 读/写 yaml 文件；得到 `ExperimentConfig`；摘后端/编译小包 |
| **`experiment.py`** | 总配置长什么样、各块之间能不能同时开 |
| **`geometry_files.py`** | 若 yaml 写了 `geometry_file`，在进总配置**之前**先读 xyz（用户写法见 [说明_molecule §1.1](说明_molecule配置与自旋多重度.md#11-外置几何文件geometry_file与坐标单位必读)；源码学习见 [说明_geometry_files源码学习.md](说明_geometry_files源码学习.md)） |
| **`molecule.py` 等** | 分子、SCF、量子算法等各段的字段定义 |

---

## 各函数是干什么的

### `load_experiment_config(path, strict_top_level_keys=False)`

**最常用：** 给一个 yaml 路径，返回加载好的 `ExperimentConfig`。

里面大致四步：

1. **读文件**（UTF-8 文本）  
   - 找不到文件 → 报「配置错误」，带上路径  
2. **解析 yaml**  
   - 缩进、冒号写错 → 报「yaml 无效」  
3. **看根上是不是「一张表」**（键值对）  
   - 根若是列表等奇怪结构 → 报错  
4. **交给 `ExperimentConfig.from_yaml_dict`**  
   - 字段类型不对、几何互斥、策略冲突等 → 在这一步报错  

两个实用细节：

- **相对路径的基准**：yaml **所在文件夹**当作基准。例如 `configs/foo.yaml` 里写 `geometry_file: "a.xyz"`，会找 `configs/a.xyz`。  
- **`strict_top_level_keys=True`**：顶层不允许出现模型里没声明的键名（防拼错字）；默认 `False` 较宽松。

**谁在用：** 测试、命令行、HTTP 接口、任务队列等，凡是「读一份 yaml 开跑」基本都走这里。

```python
from qchem_stack.config import load_experiment_config

cfg = load_experiment_config("configs/example_h2_geometry_file_xyz.yaml")
# cfg 就是一整份实验设置，例如 cfg.molecule、cfg.scf、cfg.quantum
```

---

### `_strip_callables(obj)`（内部函数，名字以下划线开头）

**干什么：** 把配置里的「没法写成文字的东西」删掉。

有时测试会在配置对象里临时挂上 **Python 函数**（例如某个回调）。yaml 里不能保存函数。写回 yaml 前用这个函数递归扫一遍 dict/list，去掉所有「能当函数调用的」项。

**你不用自己调**；只有下面的 `dump_experiment_config` 会用到。

---

### `dump_experiment_config(cfg) -> str`

**干什么：** 把内存里的 `ExperimentConfig` **变成一段 yaml 字符串**（注意：默认**不**自动存盘，返回的是文本）。

步骤：对象 → 普通字典 → 去掉函数 → 转成 yaml 文本（键的顺序尽量保持、中文也能写）。

**常见用途：** 记录「这次实际跑的时候配置长什么样」、复现、调试对比。和 `load_experiment_config` 成对：**读进来是对象，倒出去是字**。

---

### `backend_spec_from_config(cfg)`

**干什么：** 从「一整份实验设置」里 **只拿出和量子后端有关的那几项**，整理成 `BackendSpec`，给 `qchem_stack.backends` 用。

例如：模拟器名字、每次测多少 shots、Qiskit 用哪种模式、IonStack 地址等；还会带上编译里和两比特门有关的一项（`native_twoq`）。

**为什么要单独函数：** 总配置很大，跑量子线路时后端只需要其中一小截；这里统一「裁剪」，避免后端代码到处写 `cfg.backend.xxx`。

---

### `compiler_pass_bundle_from_config(cfg)`

**干什么：** 从 `cfg.compiler` 里抽出 **线路编译相关** 的设置（优化级别、要做哪些编译步骤等），打成 `CompilerPassBundle`。

和上一个类似：**大配置 → 只给「编译线路」那一层用的小包**。

---

### `compiler_bundle_signature_from_config(cfg) -> str`

**干什么：** 根据编译相关设置算一个 **16 位的短编号**（对几项设置排序后做哈希，取前 16 个十六进制字符）。

**用途：** 写报告或复现时快速说「这次编译策略的指纹是 `a1b2c3…`」——两次运行指纹相同，可认为编译选项一致。不是加密，只是 **方便比对**。

---

## 和 `ExperimentConfig.from_yaml_dict` 的关系

`load_experiment_config` 读完 yaml 后，真正「展开几何文件、校验各段」主要在 `experiment.py` 的 `from_yaml_dict` 里，例如：

- 有 `geometry_file` → 先走 `geometry_files.py`  
- 有预计算数据路径 → 也会按 yaml 所在目录解析相对路径  
- 最后 `model_validate` 做各段字段检查  

所以：**`io.py` 管「文件 ↔ 字典」；`experiment.py` 管「字典 ↔ 合法的总配置对象」。**

---

## 日常怎么用（对照表）

| 你想做的事 | 用哪个 |
|------------|--------|
| 从 yaml 开始跑实验 / 写测试 | `load_experiment_config("configs/xxx.yaml")` |
| 把当前配置导出成 yaml 文字 | `dump_experiment_config(cfg)` |
| 一般不用管 | `_strip_callables` |
| 写 pipeline、接量子后端时（库内部） | `backend_spec_from_config`、`compiler_pass_bundle_from_config`、`compiler_bundle_signature_from_config` |

---

## 源码位置

| 内容 | 路径 |
|------|------|
| 本模块 | `src/qchem_stack/config/io.py` |
| 总配置模型 | `src/qchem_stack/config/experiment.py` |
| 对外常用入口 | `from qchem_stack.config import load_experiment_config`（见 `config/__init__.py`） |
