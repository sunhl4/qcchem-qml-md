<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：高能物理 (HEP) & 异常检测

**路径**：2 + 经典 AE 降维 · **TRL**：3–4

## 何时选此路线
- 碰撞事件 / jet 数据，目标发现 BSM 异常
- 经典 AE 先降维 → 量子核/聚类在 latent space
- 需要 entanglement 资源时量子核可超经典（LHC 2024）

## 推荐 ML 栈
| 阶段 | 方法 |
|------|------|
| 降维 | Classical autoencoder（适配 qubit 限制） |
| 异常检测 | Quantum kernel SVM / quantum clustering |
| 编码 | 1P1Q（每粒子一 qubit，无经典压缩） |
| 监督 | VQC jet 分类（vs ParT 等经典 SOTA） |

## 必读文献
- Quantum anomaly detection LHC 2024（Communications Physics）
- 1 Particle–1 Qubit 2025 · Belis Rev. Phys. 2024
- Frontiers HEP big dataset QML（负结果：需降采样）

## 数据形态
- Latent vectors from AE · 或 1P1Q 编码后的 quantum features
- CMS 真数据验证（1P1Q QAE）

## 常见坑
- 全量 LHC 数据无法直接上量子 → 必须降维/采样
- 无 entanglement 时 quantum advantage 不保证
- Benchmark 需与 classical AE+SVM 公平对照

## 验收指标
Anomaly significance · signal efficiency @ fixed background · qubit/entanglement ablation

**BibTeX 键**：`LHCQuantumAnomaly2024`, `OneP1Q2025`

</div>
