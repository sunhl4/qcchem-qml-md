---
title: 研究级 ansatz 索引
description: qite / vsqs / uccgd 等研究插件导航与能力位；iQCC 见算法入口。
---

# 研究级 ansatz 索引

下列 ID 在 `ansatz_registry` 中常标 `research_plugin` 或「开放/切片」语义：可跑通契约与小分子，**不**宣称与闭源产品比特级一致。完整手册见子页。

**iQCC** 已升为外环算法（`quantum.algorithm: iqcc`），手册见 [iQCC / iQCC+PT](./iqcc)；下方仅保留遗留 `ansatz: iqcc` 别名说明。

---

## 深读入口

| ID | 手册 | 一句话 |
|----|------|--------|
| `uccgd` | [UCCGD](./uccgd) | 广义 doubles 稠密 UCC |
| `iqcc`（遗留 ansatz） | [iQCC](./iqcc) | 请改用 `algorithm: iqcc`；别名仍转入同一 runner |
| `qite` | [QITE](./qite) | 最速下降虚时步进 |
| `vsqs` | [VSQS](./vsqs-ansatz) | $H(\tau)$ 调度 Trotter |
| `qcc` / `upccgsd` / `puccd` | [QCC 族](./qcc-paired) | 结构化化学 ansatz |

侧车（非 ansatz）：

| 主题 | 手册 |
|------|------|
| VQS 轨迹 | [VQS](./vqs) |
| QPE 演示 | [QPE](./qpe) |
| GQE | [GQE](./gqe) |
| 自定义工厂 | [自定义插件](./custom-plugin) |

---

## 查询能力位

```python
from qchem_stack.quantum.ansatz_registry import ansatz_registry_export, list_registered_ansatz_ids

for aid in sorted(list_registered_ansatz_ids()):
    cap = ansatz_registry_export().get(aid, {}).get("capabilities") or {}
    if cap.get("research_plugin"):
        print(aid, cap)
```

---

## 选型建议

1. 生产主路径：`hea` / `uccsd` + [ADAPT](./adapt-vqe)  
2. 激发态：[VQD](./vqd) / [QSE](./qse)  
3. 研究对照：本页插件 + 固定 `random_seed` + `repro`  

---

## 相关

- [算法菜单](/guide/algorithm-and-ansatz-menu) · [算法索引](./)
- [能力 SLA](/product/capability-sla)（研究插件多为 partial / stub_only）
- 验证：各子页「验证」块；`pytest -k "iqcc or qite or vsqs"`
