# 新对话任务：QML-FF 长时间 MD（立方盒子 / 保留质心）

请在仓库 `/home/sunhl/projects/qchem_qml_md` 执行下面任务，**不要**再做「每帧去质心钉在格子上」的可视化（那会看不到布朗运动）。

## 背景
- 力场 checkpoint：`results/uqc_cloud_sim_md_ml_optimized/qmlff_checkpoints/round_05/final.npz`
- 现成脚本：`docs/assets/run_qmlff_md_long_ovito.py`（已写好，保留 COM drift，**立方盒子**）
- 本机吞吐约 **17 steps/s / 单分子 H2**（CPU）

## 运行结构与超参数（推荐）

| 项 | 值 |
|----|-----|
| 力场 | QML-FF `atomic_amplitude`，round_05 checkpoint |
| 系综 | NVT-Langevin |
| T | 300 K |
| dt | 0.25 fs |
| n_mol | 10 |
| n_steps / mol | 10_000（~2 h CPU 合计） |
| save_frames | 50 → stride=200 |
| 模拟时长 | ~2.5 ps / mol |
| **盒子** | **立方**：`(22.5, 22.5, 22.5)` Bohr ≈ `11.91 Å`（3×3×3 格子，spacing=7.5 Bohr） |
| 输出 | `results/qmlff_md_long_ovito/h2_qmlff_md_long.extxyz` + `run_meta.json` |

## 2 小时预算怎么选
| 模式 | 命令 | 模拟时长 | 帧数 |
|------|------|----------|------|
| **推荐：10×H2 立方盒子** | `python docs/assets/run_qmlff_md_long_ovito.py --n-mol 10 --n-steps 10000 --save-frames 50` | 每分子 ~2.5 ps | 50 |
| 单分子尽量长 | `python docs/assets/run_qmlff_md_long_ovito.py --n-mol 1 --n-steps 100000 --save-frames 50` | ~25 ps | 50 |

`save_stride = n_steps / 50`（脚本自动算）。

## 要做的事
1. 用 `.venv/bin/python` 跑上表**推荐**命令（可先 `--n-steps 2000` smoke，再正式 2h）
2. 确认 Lattice 三边相等（立方盒子）
3. 输出 OVITO 可读 extxyz（Å + Lattice）到 `results/qmlff_md_long_ovito/h2_qmlff_md_long.extxyz`
4. 写 `run_meta.json`（步数、stride、墙钟、平均温度、box）
5. 把文件同步到 `D:\Yaozheng\述职_合订本\figures\uqc\`（PowerShell Copy-Item）
6. 简要汇报：总步数、50 帧 stride、模拟时长、墙钟、盒子边长、质心是否在动

## 约束
- NVT-Langevin，T=300 K，dt=0.25 fs
- **盒子必须立方**（Lx=Ly=Lz），不要用旧的扁平 5×2 板状盒
- 必须保留质心运动；装箱时只加格子平移，不要每帧 `local-com` 钉死
- 不要改无关文件
