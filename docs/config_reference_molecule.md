# `molecule` — 分子怎么定义

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**源码：** `molecule.py`  
**详细说明：** [说明_molecule配置与自旋多重度.md](说明_molecule配置与自旋多重度.md)

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `symbols` | `list[str]` | — | 元素符号 |
| `coordinates` | `list[list[float]] \| None` | `None` | Cartesian 坐标；单位看 `coordinate_unit` |
| `zmatrix` | `str \| None` | `None` | Z-matrix 文本；和 `coordinates` 二选一 |
| `coordinate_unit` | `"angstrom" \| "bohr"` | `"angstrom"` | 坐标单位 |
| `charge` | `int` | `0` | 总电荷 |
| `multiplicity` | `int` | `1` | 自旋多重度 2S+1 |
| `basis` | `str` | `"sto-3g"` | 基组 |
| `ecp` | `str \| dict \| None` | `None` | 有效核芯势 |

**常用代码：**

```python
coords_bohr = cfg.molecule.coordinates_in_bohr()  # np.ndarray, shape (n_atom, 3)
```

**也可以引用外置文件（加载时自动展开）：**

```yaml
molecule:
  geometry_file: "structures/h2.xyz"
  geometry_file_format: xyz   # 可选，默认按后缀猜
  coordinate_unit: angstrom
```

**谁在用：** 所有需要原子坐标的阶段；embedding 原子索引校验等。
