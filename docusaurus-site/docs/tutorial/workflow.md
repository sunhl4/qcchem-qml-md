# 工作流与 YAML 概览

这页说明一条任务在 YAML 中的组织方式，目的是让你知道“改哪个块会影响什么”。

## 一条管线的逻辑顺序

1. 分子与经典化学（驱动、基组、电荷）  
2. 量子子问题（活性空间、映射、算法）  
3. 协议与阶段（变分、Pauli、激发）  
4. 后端与采样（statevector/qiskit/shots）  
5. 作业与可复现（HTTP、队列、repro）  

## YAML 中最常改的块

| 块 | 作用 | 常见改动 |
|----|------|---------|
| 分子与经典设置 | 定义体系与计算基础 | 分子坐标、基组、SCF 参数 |
| 量子与活性空间 | 指定映射和算法输入 | 活性轨道/电子数、算法选择 |
| 后端与采样 | 执行方式、shots、提供方 | 从 statevector 切到 qiskit shots |
| 作业/API | 与队列和服务接口联动 | 同步改异步、切换数据库路径 |

## 一个实用改法（推荐）

1. 复制 `configs/example_h2.yaml` 作为你的实验配置  
2. 每次只改一个块，并记录改动目的  
3. 每次改动后跑一次最小回归（至少看 `run_summary`）  
4. 跑通后再叠加下一块改动

## 进阶建议

- 先跑通 `configs/example_h2.yaml`
- 再按 P1-P4 逐柱扩展配置
- 通过小样例做回归，避免一次性改动过大

## 对应文档

- 化学与嵌入字段： [P1](../guide/chemistry-and-embedding)
- 算法与协议字段： [P2](../guide/program-construction)
- 执行与后端字段： [P3](../guide/execution-and-analysis)
- 作业与可复现字段： [P4](../guide/jobs-and-reproducibility)

## 验证命令

```bash
python scripts/smoke_pipeline.py --config configs/example_h2.yaml
```

## 期望输出

- 退出码 `0`
- YAML 块 `molecule` / `quantum` / `backend` 可被加载
