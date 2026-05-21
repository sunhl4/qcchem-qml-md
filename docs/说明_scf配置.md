# 实验 YAML 中的 `scf:` 配置说明

本文说明 `src/qchem_stack/config/scf.py` 里 `SCFSpec` 各字段的含义与写法。加载流程见 [说明_实验配置加载_io.md](说明_实验配置加载_io.md)；分子与电荷/多重度见 [说明_molecule配置与自旋多重度.md](说明_molecule配置与自旋多重度.md)。

---

## 这段配置管什么

`scf:` 决定 **经典平均场怎么算**（最常见是 Hartree–Fock）：用哪家程序（`driver`）、闭壳还是开壳 HF（`method`），以及可选的收敛/加速选项。算出的轨道等会供后面的活性空间、量子哈密顿量使用。

**不负责：** 原子坐标、基组名（在 `molecule:`）、VQE 算法（在 `quantum:`）。

---

## Canonical 嵌套形态（P15+）

顶层 `scf:` 仅保留 **判别键** 与 **各 driver 子块**；收敛/加速类控制项落在对应 driver 子块内：

```yaml
scf:
  driver: pyscf          # pyscf | psi4 | precomputed | 插件 id
  method: RHF            # RHF | ROHF | UHF（全 driver 共享）
  pyscf:                 # driver=pyscf 时读取
    max_cycle: 100
    density_fit: false
  psi4:                  # driver=psi4 时读取（字段名与 pyscf 对齐）
    max_cycle: 80
  precomputed:           # driver=precomputed 时读取
    bundle_path: configs/precomputed_classical_reference_h2.json
```

**嵌套：** driver 专属控制项写在 `scf.pyscf.*` / `scf.psi4.*` / `scf.precomputed.bundle_path`；顶层 flat 键在加载时会被拒绝。

**代码读取：** 优先 `scf_helpers.resolve_*`（按 `driver` 分派），或直接访问 `cfg.scf.pyscf.max_cycle` / `cfg.scf.psi4.max_cycle`。

---

## 为什么很多示例只写两行

多数 `configs/example_h2_*.yaml` 只有：

```yaml
scf:
  driver: pyscf
  method: RHF
```

其余字段在模型里 **有默认值**，省略即使用默认。简单 H₂ 用默认即可；只有换后端、读离线数据、密度拟合或难收敛时才多写。

---

## 参数详解

实现：`SCFSpec`（`scf.py`）。下列「默认」指 YAML 不写该键时的行为。

### `driver`

| 项目 | 说明 |
|------|------|
| **含义** | 用哪套 **经典计算程序**（solver 注册表 id） |
| **默认** | `"pyscf"`（加载后统一成小写） |
| **常见取值** | 见下表 |

| 取值 | 何时使用 |
|------|----------|
| `pyscf` | 本机现场用 PySCF 算平均场（仓库主路径） |
| `psi4` | 用 Psi4（需安装；部分高级功能仅 PySCF） |
| `precomputed` | 不算 SCF，改读 JSON 经典结果包（须配 `precomputed.bundle_path`） |
| 其它插件 id | 扩展注册的第三方 solver |

**注意：** 与 `molecule` 独立——换 `driver` 不改变基组/几何，只改变「谁来做 SCF」。

**多后端说明：** 本仓库 **已实现 PySCF 与 Psi4 两种内置 driver**（外加 `precomputed`），并通过 `SolverCapabilities` 在加载实验配置时检查「当前 driver 是否支持所选功能」，**架构上不绑定单一程序**。各 driver 能力差异（AVAS、PBC、embedding 等）见 [说明_经典化学后端驱动_registry与能力位.md](说明_经典化学后端驱动_registry与能力位.md)。

**示例：**

- `configs/example_h2_geometry_file_xyz.yaml` — `pyscf`
- `configs/example_h2_psi4_rhf_sto3g.yaml` — `psi4`
- `configs/example_h2_precomputed_bundle.yaml` — `precomputed`

---

### `method`

| 项目 | 说明 |
|------|------|
| **含义** | Hartree–Fock 的 **自旋处理方式**（不是 `quantum.algorithm`） |
| **默认** | `"RHF"` |
| **允许值** | `RHF`、`ROHF`、`UHF`（大小写按 yaml 写，模型会校验） |

| 取值 | 适用场景 |
|------|----------|
| `RHF` | 闭壳，`multiplicity: 1`，α/β 共用同一套轨道（H₂ 基态典型） |
| `UHF` | 开壳，α、β 轨道可不同（自由基等） |
| `ROHF` | 开壳的限制性开壳 HF |

须与 `molecule.multiplicity` 一致：单重态却用 `UHF`、或开壳却只写 `RHF`，可能不收敛或物理不对。

**示例：** 多数 H₂ 为 `RHF`；`configs/tutorial_chain_h2.yaml` 使用 `ROHF`。

---

### `pyscf` / `psi4` 子块（收敛与加速控制）

| 子块 | 何时生效 | 常见字段 |
|------|----------|----------|
| `pyscf` | `driver: pyscf` | `max_cycle`, `chkfile`, `init_guess`, `level_shift`, `use_newton`, `diis_space_dimension`, `density_fit`, `density_fit_auxbasis` |
| `psi4` | `driver: psi4` | 同上（Psi4 适配器映射到对应选项） |

下列各节仍按 **字段语义** 说明；YAML 中请写在对应 driver 子块下（`scf.pyscf.*` / `scf.psi4.*` / `scf.precomputed.*`）。

### `max_cycle`（`pyscf.max_cycle` / `psi4.max_cycle`）

| 项目 | 说明 |
|------|------|
| **含义** | SCF **最多迭代轮数**（PySCF：`mf.max_cycle`） |
| **默认** | `None`（不覆盖，用程序内置默认） |
| **范围** | 若填写：整数 `1`–`512` |

难收敛体系（过渡金属、部分开壳）可显式加大。

**示例：** `configs/example_fe_sto3g_helike_rhf_cas22.yaml` — `max_cycle: 120`  
**常见示例：** 不写。

---

### `chkfile`

| 项目 | 说明 |
|------|------|
| **含义** | PySCF **检查点文件路径**（`mf.chkfile`），用于存盘/续算 |
| **默认** | `None` |

常与 `init_guess: chkfile` 配合，从上次结果接着猜。教学与小分子 parity 配置一般不需要。

**常见示例：** 不写。

---

### `init_guess`

| 项目 | 说明 |
|------|------|
| **含义** | 第一轮 SCF 的 **初始轨道猜测**（PySCF 令牌） |
| **默认** | `None`（PySCF 默认策略） |

常见令牌（由 PySCF 定义，非本仓库枚举）：`minao`、`atom`、`huckel`、`chkfile` 等。收敛困难时可尝试更换。

**常见示例：** 不写。

---

### `level_shift`

| 项目 | 说明 |
|------|------|
| **含义** | **能级移动**，抬高虚轨道能量以帮助 SCF 收敛 |
| **默认** | `None`（关闭） |
| **类型** | 浮点数（交给 PySCF mean-field 对象） |

过渡金属、开壳体系偶尔使用。

**常见示例：** 不写。

---

### `use_newton`

| 项目 | 说明 |
|------|------|
| **含义** | 是否在 RHF/ROHF 上使用 **Newton–Raphson** 求解（`scf.RHF(...).newton()`） |
| **默认** | `false` |

部分体系比纯 DIIS 更稳；默认关闭即可。

**常见示例：** 不写。

---

### `diis_space_dimension`

| 项目 | 说明 |
|------|------|
| **含义** | DIIS 历史中保留的步数（`mf.diis_space`） |
| **默认** | `None` |
| **范围** | 若填写：整数 ≥ `2` |

高级调参项，一般用户可忽略。

**常见示例：** 不写。

---

### `density_fit`

| 项目 | 说明 |
|------|------|
| **含义** | 是否启用 **密度拟合 / RI** 加速 SCF（需后端支持） |
| **默认** | `false` |

大分子或重元素配合 ECP 时，可设 `true` 降低积分成本。与 `density_fit_auxbasis` 配合使用。

**示例：**

- `configs/example_h2_sto3g_density_fit.yaml` — `density_fit: true`
- `configs/example_mg_lanl2dz_ecp_density_fit.yaml`、`example_hbr_zmatrix_lanl2dz_ecp_density_fit.yaml`

**你的 geometry_file H₂ 示例：** 不写（默认 `false`）。

---

### `density_fit_auxbasis`

| 项目 | 说明 |
|------|------|
| **含义** | 密度拟合用的 **辅助基组名**（如 `weigend`） |
| **默认** | `None` |

**强制规则（`scf.py` 校验）：** 仅当 `density_fit: true` 时可写；否则加载配置报错。

**示例：** `configs/example_h2_zmatrix_sto3g_density_fit.yaml`：

```yaml
density_fit: true
density_fit_auxbasis: "weigend"
```

只开 `density_fit: true` 而不写 auxbasis 时，由 PySCF 侧选择默认辅助基。

---

### `precomputed.bundle_path`

| 项目 | 说明 |
|------|------|
| **含义** | `driver: precomputed` 时，指向 **预计算经典结果** JSON（`classical_reference_bundle_v1` 格式） |
| **YAML 路径** | `scf.precomputed.bundle_path` |
| **默认** | `None` |

**强制规则：**

| 条件 | 要求 |
|------|------|
| `driver: precomputed` | 路径 **必填**且非空 |
| `driver` 为其它值 | **不能** 出现此字段 |

路径可为绝对路径，或相对路径（与 [说明_实验配置加载_io.md](说明_实验配置加载_io.md) 中 yaml 目录解析规则一致；预计算 bundle 在 `ExperimentConfig.from_yaml_dict` 里也会按 yaml 所在目录解析）。

**示例：** `configs/example_h2_precomputed_bundle.yaml`：

```yaml
scf:
  driver: precomputed
  method: RHF
  precomputed:
    bundle_path: precomputed_classical_reference_h2.json
```

---

## 加载时的自动检查（`scf.py` 第 66–96 行）

各字段类型检查通过后，`SCFSpec` 还会跑三个 **`@model_validator(mode="after")`**：不跑 SCF，只保证 **字段之间不矛盾**，并 **规范化** `driver`、路径字符串。失败时加载配置直接 `ValueError`，避免跑到 pipeline 才发现写错。

```
YAML scf: { ... }
    → 单字段校验（类型、max_cycle 范围等）
    → ① 密度拟合与辅助基是否配套
    → ② driver 转小写、去空格
    → ③ precomputed 与 bundle 路径成对
    → 合法的 SCFSpec
```

### `_density_fit_auxbasis_consistency`

**要点：** 写了 `density_fit_auxbasis` 就必须 `density_fit: true`。

| 写法 | 结果 |
|------|------|
| `density_fit: true` + `density_fit_auxbasis: weigend` | ✅ |
| 只有 `density_fit_auxbasis`，未开 `density_fit` | ❌ |

### `_normalize_driver_id`

**要点：** `driver` 统一成 **小写、无首尾空格** 再存进对象；禁止空串或 id 中间带空格。

| YAML 里写的 | 对象里变成 |
|-------------|------------|
| `PySCF` | `pyscf` |
| `"  psi4  "` | `psi4` |
| 空 / 含空格 | ❌ |

这样与后面 `driver == "precomputed"` 的判断一致，避免大小写当成两种后端。

### `_precomputed_bundle_requirements`

**要点：** 离线经典模式与 bundle 路径 **必须成对**；路径会 `strip()`，全空当没写。

| `driver` | `scf.precomputed.bundle_path` | 结果 |
|----------|---------------------------|------|
| `precomputed` | 非空路径 | ✅ |
| `precomputed` | 省略或 `""` | ❌ 必须提供 |
| `pyscf` / `psi4` 等 | 省略 | ✅ |
| `pyscf` 等 | 写了路径 | ❌ 仅 `precomputed` 可用 |

此处 **不检查文件是否存在**；只检查配置是否自洽。文件缺失在后续读 bundle 时再报错。

实现位置：`src/qchem_stack/config/scf.py`。更一般的 config 分层约定见 [config_校验分层约定.md](config_校验分层约定.md)。

---

## 参数与示例 yaml 对照

| 参数 | `example_h2_geometry_file_xyz.yaml` | 仓库中另有示例 |
|------|-------------------------------------|----------------|
| `driver` | ✅ `pyscf` | `psi4`、`precomputed` 等 |
| `method` | ✅ `RHF` | `ROHF`（tutorial） |
| `density_fit` | 默认 false | `example_h2_sto3g_density_fit.yaml` |
| `density_fit_auxbasis` | — | `example_h2_zmatrix_sto3g_density_fit.yaml` |
| `precomputed.bundle_path` | — | `example_h2_precomputed_bundle.yaml` |
| `max_cycle` | — | `example_fe_sto3g_helike_rhf_cas22.yaml` |
| `chkfile`、`init_guess`、`level_shift`、`use_newton`、`diis_space_dimension` | — | 高级用法，parity 样例中极少出现 |

---

## 按场景的最小写法

**现场 PySCF + 闭壳（与当前 H₂ geometry 示例同类）：**

```yaml
scf:
  driver: pyscf
  method: RHF
```

**离线经典 → 只跑量子段：**

```yaml
scf:
  driver: precomputed
  method: RHF
  precomputed:
    bundle_path: "precomputed_classical_reference_h2.json"
```

**密度拟合加速：**

```yaml
scf:
  driver: pyscf
  method: RHF
  density_fit: true
  # density_fit_auxbasis: weigend   # 可选
```

**难收敛时按需追加（示例）：**

```yaml
  max_cycle: 120
  level_shift: 0.2
  init_guess: atom
```

---

## 与 `molecule` 的分工

| 配置块 | 内容 |
|--------|------|
| `molecule` | 结构、电荷、多重度、基组、ECP |
| `scf` | 经典平均场程序与 HF 类型、SCF 技巧 |

二者需一致：例如开壳 `multiplicity: 2` 时不应仍用 `method: RHF` 指望得到正确开壳态。

---

## 源码

| 内容 | 路径 |
|------|------|
| `SCFSpec` 与校验 | `src/qchem_stack/config/scf.py` |
| 总配置中的位置 | `src/qchem_stack/config/experiment.py` → `scf: SCFSpec` |
