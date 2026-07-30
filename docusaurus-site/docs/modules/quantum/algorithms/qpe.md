---
title: QPE（相位估计三件套）
description: Kitaev/确定性/信息论 QPE 完整手册：稠密演示语义、YAML、API 与侧车。
---

# QPE（相位估计三件套）

本页是 QPE **演示/估计器** 完整手册。本栈提供稠密本征谱上的相位—能量桥接，便于管线与 Methods 对照；**不是**完整容错硬件 QPE 电路。

实现：`qchem_stack.quantum.algorithms.qpe`。侧车：`orchestration.protocol_finalize_sidecars`。

---

## 1. 文献

| 角色 | 文献 |
|------|------|
| 相位估计框架 | A. Y. Kitaev, [arXiv:quant-ph/9511026](https://arxiv.org/abs/quant-ph/9511026) |
| 教科书 | Nielsen & Chuang，《量子计算与量子信息》QPE 章 |
| 化学应用 | Aspuru-Guzik et al., [Science **309**, 1704 (2005)](https://doi.org/10.1126/science.1113479) |

---

## 2. 要解决什么问题

若 $U|\psi\rangle=e^{2\pi i\phi}|\psi\rangle$，标准 QPE 用受控-$U^{2^k}$ + 逆 QFT 读 $\phi$。化学中常取 $U=e^{-iHt}$，使

$$
\phi \sim -\frac{E t}{2\pi}\pmod{1}
$$

容错 QPE 电路深；本栈在小体系上用 **稠密对角化锚点** 报告「若做 QPE 会看到的相位统计」，验证配置/parity，而非替代 VQE 主路径。

---

## 3. 理论思想

| 变体 | 思想 |
|------|------|
| 确定性 / 标准风格 | 多轮精度 $\sim 2^{-n_{\mathrm{rounds}}}$ |
| Kitaev 迭代 | 单辅助比特逐位读相位，精度 $\sim 2^{-n_{\mathrm{bits}}}$ |
| 信息论采样 | 相位附近高斯/采样统计（`info_samples`） |

三者均先 `eigvalsh(H)` 取基态 $e_0$，再构造 $\phi=(-e_0\cdot t)/(2\pi)\bmod 1$。**`energy_estimate` 锚定稠密 $e_0$**，不是从相位 unwrap 反推。

---

## 4. 数学实现（本栈）

| 类 | 算法 ID | 关键旋钮 |
|----|---------|----------|
| `AlgorithmDeterministicQPE` | `qpe_deterministic` | `time`, `n_rounds` |
| `AlgorithmKitaevQPE` | `qpe_kitaev` | `time`, `n_bits` |
| `AlgorithmInfoTheoryQPE` | `qpe_info_theory` | `time`, `n_samples`, `resolution` |

结果：`QPEResult`（相位、sigma、能量估计、meta）。  
管线入口：`variational_plugins.builtins.run_qpe_{kitaev,deterministic,info_theory}`。

主算法路径返回零 HEA 角度；能量来自 QPE 报告。

---

## 5. 参数详表

### 5.1 作为主算法

```yaml
quantum:
  algorithm: qpe_kitaev   # qpe_deterministic | qpe_info_theory
  demos:
    qpe:
      three_pack:
        time: 1.0
        deterministic_rounds: 4
        kitaev_bits: 6
        info_samples: 32
```

主算法参数从 `quantum.demos.qpe.three_pack` 读取（与侧车共用字段）。

| 配置 | 用途 |
|------|------|
| `configs/example_h2_qpe_main.yaml` | `qpe_kitaev` |
| `configs/example_h2_qpe_deterministic.yaml` | 确定性 |
| `configs/example_h2_qpe_info_theory.yaml` | 信息论 |
| `configs/example_h2_qpe_zne_pauli.yaml` | + 缓解 |

### 5.2 变分后侧车（不改主算法）

```yaml
quantum:
  algorithm: vqe
  demos:
    qpe:
      track_after_variational: true    # 或 pipeline_integration
      demo_track_n_bits: 4
      three_pack:
        after_variational: true
        time: 1.0
        deterministic_rounds: 4
        kitaev_bits: 6
        info_samples: 32
```

代表：`configs/example_h2_qpe_track.yaml`。  
脚本：`scripts/run_qpe_track_demo.py`。

### 5.3 类默认

| 类 | 默认 |
|----|------|
| Deterministic | `time=1.0`, `n_rounds=4` |
| Kitaev | `time=1.0`, `n_bits=6` |
| InfoTheory | `time=1.0`, `resolution=2**10`, `n_samples=64` |

---

## 6. 函数调用与验证

```python
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
from qchem_stack.sdk import run_pipeline_from_config

s = set(list_registered_algorithm_ids())
assert {"qpe_deterministic", "qpe_kitaev", "qpe_info_theory"} <= s
out = run_pipeline_from_config("configs/example_h2_qpe_deterministic.yaml")
print([k for k in sorted(out) if "qpe" in k.lower() or "energy" in k.lower()][:15])
```

### 验证命令

```bash
python3 -c "
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
s=set(list_registered_algorithm_ids())
assert {'qpe_deterministic','qpe_kitaev','qpe_info_theory'}<=s
print('ok')
"
```

### 期望输出

- `ok`  
- 管线含算法报告 / 能量相关键  

---

## 7. 调参与边界

| 现象 | 说明 |
|------|------|
| 大体系 OOM | 稠密 $2^n$；仅小分子烟雾 |
| 相位→能量歧义 | 模 1；报告同时给谱 $e_0$ |
| 与 VQE 能量差 | 正常：主路径语义不同 |
| 要硬件电路 | 当前未实现；用演示轨道做契约 |

---

## 8. 相关

- [VQE/HEA](./vqe-hea) · [缓解](/modules/mitigation) · [算法索引](./)
