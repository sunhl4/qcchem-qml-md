---
title: chem · 双线路经典输入
description: 在线 SCF 与 precomputed bundle、resolve_pre_quantum_path 与契约校验。
---

# chem · 双线路经典输入

本页说明两条互斥的经典入口如何汇合到统一的 `PreQuantumInput`（schema `pre_quantum_input_v1`）。

相关：[Solver](./solvers) · [哈密顿量](./hamiltonian) · [嵌入路径](./embedding)。

---

## 1. 文献与问题

| 角色 | 文档 |
|------|------|
| 契约 | 仓库 `docs/技术文档_双线路经典输入与统一PreQuantumInput契约.md` |
| 工程动机 | CI / 无 PySCF 环境复现；第三方只投递哈密顿量 |

不是所有部署都能现场跑 SCF。双线路设计：**在线**（PySCF/Psi4）与 **离线 bundle** 产出同一契约对象，下游量子算法无需感知入口差异。`resolve_pre_quantum_path` 保证路径选择确定性。

---

## 2. 理论思想

两条车道：

| 车道 | YAML | `PreQuantumPath` | `meta['source']` |
|------|------|------------------|------------------|
| Online SCF | `scf.driver: pyscf` / `psi4` | 再按 embedding 分支（默认 `canonical_active_space_integral_pack`） | 路径字面量 |
| Offline | `scf.driver: precomputed` | **恒为** `precomputed_bundle` | `precomputed_bundle` |

离线包 schema：`classical_reference_bundle_v1`。  
指纹 schema：`precomputed_config_fingerprint_v1`（几何、元素、电荷、多重度、基组、活性空间）。

统一下游消费：

$$
\text{PreQuantumInput} \;\supset\; \bigl(\text{classical reference},\; \hat{H}_{\mathrm{qubit}},\; \text{meta}\bigr)
$$

---

## 3. 本栈实现

### 3.1 路径解析

`config/_pre_quantum_path.py`：`resolve_pre_quantum_path(cfg)`  
**第一条规则**：`scf.driver == "precomputed"` → 短路为 `precomputed_bundle`（优先于一切 embedding live 路径）。

### 3.2 关键 API

| 符号 | 路径 |
|------|------|
| `precomputed_pre_quantum_input` | `chem/precomputed_pre_quantum.py` |
| `precomputed_config_fingerprint` | 同上 |
| `validate_precomputed_manifest_against_config` | 同上 |
| `load_bundle_dict` / `qubit_hamiltonian_from_bundle_payload` | `chem/precomputed_bundle.py` |
| `preprocess_precomputed_bundle_path` | `config/_experiment_validation_precomputed.py` |

### 3.3 Manifest 严格字段

校验至少对齐：`n_active_orbitals`、`n_active_electrons`、`fermion_qubit_mapping`、`n_qubits`、`molecule_symbols`、`config_fingerprint`。

### 3.4 约束

- Bundle 必须自带 `pre_quantum_input.qubit_hamiltonian`  
- `canonical_active_space_integral_pack` 在离线路径常为 `None`  
- `validate_precomputed_driver_excludes_live_hooks`：禁止 live AVAS / CASSCF / Schmidt / projection / post-HF  
- 相对路径相对 **YAML 文件目录** 解析  

构建 CLI：`scripts/build_precomputed_bundle.py`。

---

## 4. YAML 参数表

**正确嵌套**（不是扁平 `precomputed_bundle_path`）：

```yaml
scf:
  driver: precomputed
  method: RHF
  precomputed:
    bundle_path: configs/precomputed_classical_reference_h2.json
```

在线对照：

```yaml
scf:
  driver: pyscf
  method: RHF
# embedding / active_space 正常生效
```

| 字段 | 约束 |
|------|------|
| `scf.driver` | `precomputed` 时走离线 |
| `scf.precomputed.bundle_path` | 必需；相对 YAML 目录 |
| `active_space.*` | 须与 manifest 指纹一致 |
| live embedding / AVAS | **不可**与 precomputed 同开 |

示例：`configs/example_h2_precomputed_bundle.yaml`。

`PreQuantumInput.as_summary_dict` 稳定键：`schema`、`source`、`backend_tag`、`n_qubits`、`hamiltonian_fingerprint`、`integral_source`、`fermion_to_qubit_map` 等。

---

## 5. Python 调用

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.config._pre_quantum_path import resolve_pre_quantum_path
from qchem_stack.sdk import run_pipeline_from_config

cfg = load_experiment_config("configs/example_h2_precomputed_bundle.yaml")
assert cfg.scf.driver == "precomputed"
print(resolve_pre_quantum_path(cfg))  # precomputed_bundle

out = run_pipeline_from_config("configs/example_h2_precomputed_bundle.yaml")
print(out["pre_quantum_input"]["hamiltonian_fingerprint"][:24])
```

直接装载：

```python
from qchem_stack.chem.precomputed_pre_quantum import precomputed_pre_quantum_input
# pq = precomputed_pre_quantum_input(cfg, reference, cfg_path=...)
```

---

## 6. 验证命令

```bash
pytest tests/chem/test_precomputed_bundle.py \
  tests/orchestration/test_pipeline_precomputed_lane.py \
  tests/chem/test_precomputed_pipeline_no_pyscf.py \
  tests/integrations/test_smoke_pipeline_precomputed.py -q

python -c "from qchem_stack.config import load_experiment_config; c=load_experiment_config('configs/example_h2_precomputed_bundle.yaml'); assert c.scf.driver=='precomputed'; print('ok')"
```

期望打印 `ok`。

---

## 7. 调参 / 运维建议

| 场景 | 建议 |
|------|------|
| 生成 bundle | `scripts/build_precomputed_bundle.py` + 与在线同一 YAML 指纹字段 |
| Manifest 失败 | 对齐 CAS 尺寸、映射、元素表与 `config_fingerprint` |
| CI 无 PySCF | 只跑 precomputed 车道测试 |
| 误开 AVAS/嵌入 | 配置校验应拒绝；改回在线 driver |

---

## 8. 相关

- [Solver](./solvers) · [哈密顿量](./hamiltonian) · [嵌入](./embedding)  
- 选型：[双线路输入](/guide/dual-classical-ingress)  
- 仓库：`docs/技术文档_双线路经典输入与统一PreQuantumInput契约.md`
