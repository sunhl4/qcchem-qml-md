<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：计算机视觉 / 量子传感 / 网络安全

**路径**：混合或 2 · **TRL**：2–4

## 视觉 & 遥感
| 项 | 内容 |
|----|------|
| 栈 | H-QCNN / NQK / VQC + classical head |
| 规模 | Utility-scale: H-2 72q, MedMNIST 127q IBM |
| 数据 | angle/amplitude encoding；必须存 shots + mitigation |
| 文献 | UtilityScaleImage2025, MedMNIST2025, SatelliteNQK2025 |
| 坑 | 模拟 vs 真机差距大；MNIST 级 ≠ 实用 advantage |

## 量子传感 & 计量
| 项 | 内容 |
|----|------|
| 栈 | VQC + NN readout；Quantum Digital Twin |
| 数据 | 连续测量轨迹 I(t)；多基 expectations |
| 文献 | VQS2024, QDigitalTwin2025, VQ-CNNI2026 |
| 坑 | 需 joint 优化 quantum encoding + classical decoder |

## 网络安全 & 工控
| 项 | 内容 |
|----|------|
| 栈 | QSVM / QAE；经典预处理 + quantum kernel |
| 数据 | 网络/ CPS 特征 → quantum feature map |
| 文献 | QOC-SVM2024, QAE-BETH2025, Cyber taxonomy 2025 |
| 坑 | 少样本 QAE 有增益但需与 CAE 公平 shot/compute 对照 |

## 通用验收
Accuracy/F1 · shots · sim/hw · 经典 QSVM/CAE baseline · 是否 path-2 native data

**BibTeX 键**：`UtilityScaleImage2025`, `VQS2024`, `QOC-SVM2024`, `QAECyberBETH2025`

</div>
