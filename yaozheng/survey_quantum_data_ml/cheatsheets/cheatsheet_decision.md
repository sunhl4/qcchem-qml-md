<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：路径决策总表

## 5 问决策
1. **经典可验证标签？** 是→1 / 否→2 / 部分→混合  
2. **量子成本 >> 经典 inference？** 是→Surrogate/Foundation/AL  
3. **原生量子测量？** 是→存 raw_outcomes/shadow  
4. **>20q + global fidelity kernel？** 是→改 local/shadow  
5. **sim→hw 漂移？** 是→UDA + calibration id  

## 路径对照
| | 路径 1 | 路径 2 | 混合 |
|--|--------|--------|------|
| 数据 | E, F, ⟨O⟩, 优化值 | bitstrings, shadows | 先 2 后 1 |
| ML | 监督/GNN/surrogate | GPT/SSL/contrastive | 预训练+微调 |
| 部署 | 纯经典 inference | 经典 decoder | 三阶段 |
| ROI | 降 quantum calls | 利用量子结构 | 最高但最贵 |

## 反模式（勿做）
小数据通用 QNN · 无 shot budget 宣传 · 50+q global kernel · 不存 measurement protocol

## Benchmark 必报项
经典强基线 · nested CV · shot budget · sim/hw 分离 · 噪声 ablation · 负结果

## 混合三阶段
**A** shadow 自监督 → **B** sparse label 微调 → **C** 经典部署

## Schema & 工具
- JSON: `schema/quantum_experiment_record.schema.json`  
- Python: `QuantumExperimentRecord` (Pydantic v2)  
- BibTeX: `quantum_data_ml_survey.bib` (83 entries)  
- LaTeX: `latex/main.tex` → `make`

## 领域 → 速查文件
多体→`many_body` · QEM→`qem_surrogate` · HEP→`hep` · 金融→`finance` · 化药→`life_chem_materials` · CV/传感/安全→`cv_sensing_security`

</div>
