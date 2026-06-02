# `scf` — 经典自洽场怎么算

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**源码：** `scf.py`, `scf_specs.py`, `scf_enums.py`  
**详细说明：** [说明_scf配置.md](说明_scf配置.md)

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `driver` | `str` | `"pyscf"` | `pyscf` / `psi4` / `precomputed` / 插件 |
| `method` | `"RHF" \| "ROHF" \| "UHF"` | `"RHF"` | 自旋处理方式 |
| `pyscf` | `ScfPyscfSpec` | 默认工厂 | driver=pyscf 时用 |
| `psi4` | `ScfPsi4Spec` | 默认工厂 | driver=psi4 时用 |
| `precomputed` | `ScfPrecomputedSpec` | 默认工厂 | driver=precomputed 时用 |

## pyscf / psi4 子块常见字段

| 字段 | 说明 |
|------|------|
| `max_cycle` | SCF 最多迭代几轮 |
| `chkfile` | 检查点文件路径 |
| `init_guess` | 初猜方式 |
| `level_shift` | level shift |
| `use_newton` | 是否用 Newton SCF |
| `diis_space_dimension` | DIIS 空间维数 |
| `density_fit` | 是否 density fitting |
| `density_fit_auxbasis` | 辅助基组 |

## precomputed 子块

| 字段 | 说明 |
|------|------|
| `bundle_path` | 预先算好的经典参考 bundle（JSON）路径 |

**谁在用：** `orchestration/scf_stage.py`、`chem/solvers/registry.py` 等。
