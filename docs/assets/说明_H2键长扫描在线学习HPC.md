# H₂ 键长扫描 → 在线学习（HPC）

## 为什么要重做

先前 UQC 在线学习得到的 QML-FF **泛化不足**：长 MD（300 K / ps 级）中 H–H 键易解离。根因是初始训练集键长覆盖过稀、轮次偏少，且每轮主要靠短 MD 采点，**没有系统补扫 PES**。

正确流程（**非零样本**，不是 0-shot 在线学习）：

1. **Phase A**：量子计算化学对 H₂ 做稠密键长扫描，标注能量/力 → 初始训练集  
2. **Phase B**：只在该训练集上 **预训练力场**（`pretrain_epochs`，无 MD）  
3. **Phase C**：再跑 **在线学习 10–50 轮**（warm-start）；每轮可追加不同键长；短 MD 仅校验  
4. `stop_on_md_converged: false` 保证键长日程跑完

## 配置

| 文件 | 说明 |
|------|------|
| `configs/example_h2.yaml` | 实验：STO-3G + VQE（statevector） |
| `configs/example_h2_qmlff_bondscan_ol_20rounds.yaml` | 16 点种子扫描 + **20 轮** |
| `configs/example_h2_qmlff_bondscan_ol_50rounds.yaml` | 20 点种子扫描 + **50 轮** |

关键字段：`n_seed_geometries` + `seed_mode: bond_stretch`；`round_bonds_per_round: 1`；`stop_on_md_converged: false`。

## HPC 资源（1 核 ↔ 4G）

| CPUs | MEM |
|------|-----|
| **30** | **120G（默认）** |
| 8 | 32G |
| 4 | 16G |

## 提交

本机（需已配置 `sun_hl@192.168.110.220` SSH）：

```bash
cd /home/sunhl/projects/qchem_qml_md
./scripts/hpc/submit_h2_bondscan_online_learning.sh          # 20 轮, 30核120G
MAX_ROUNDS=50 ./scripts/hpc/submit_h2_bondscan_online_learning.sh
```

已在登录节点时：

```bash
cd ~/projects/qchem_qml_md && mkdir -p logs
sbatch scripts/hpc/h2_bondscan_online_learning.sbatch
MAX_ROUNDS=50 sbatch scripts/hpc/h2_bondscan_online_learning.sbatch
```

输出：`$HOME/results/h2_bondscan_ol_<profile>_r<rounds>_<jobid>/`  
含 `round_bond_schedule.json`、`md_validation_summary.json`、每轮 checkpoint。
