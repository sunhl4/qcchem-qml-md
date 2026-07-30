---
title: 开始使用
description: 安装 qchem-stack，并在数分钟内跑通第一条量子化学管线。
keywords:
  - qchem-stack
  - install
  - quickstart
---

# 开始使用

**qchem-stack** 用 YAML 编排量子化学工作流：化学定义 → 程序构建 → 后端执行 → 可复现导出。

English notes: [Getting started](/getting-started-en)。

---

## 安装

```bash
pip install "qchem-stack[chem,quantum]"
```

| Extra | 用途 |
|-------|------|
| *(core)* | 预计算管线与严格 repro |
| `chem` | PySCF |
| `quantum` | Qiskit / Aer |
| `api` | FastAPI 作业服务 |
| `gqe` | GPT-QE（JAX） |
| `uqc` | UQC 云客户端（实验面） |
| `dev` | 测试与 lint（默认不含 uqc） |

完整档位见 [安装档位](/reference/install-profiles)。无 PySCF 时可跑预计算烟测：

```bash
python3 scripts/smoke_pipeline.py --precomputed-only
```

### 从源码开发

```bash
git clone https://github.com/sunhl4/qcchem-qml-md.git
cd qcchem-qml-md
./scripts/bootstrap_dev.sh
```

---

## 第一条命令

```bash
qchem-run --scenario minimal_vqe
```

或在 Python 中：

```python
from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps

out = run_pipeline_from_config("configs/example_h2.yaml")
print(repro_json_dumps(out["repro"]))
```

---

## 下一步

| 目标 | 入口 |
|------|------|
| 端到端走通 | [15 分钟上手](/tutorial/quickstart) |
| 现成 YAML | [示例](/examples/) · [配置目录](/reference/configs-catalog) |
| 选型决策 | [手册](/guide/) |
| 包级深读 | [模块手册](/modules/) |
| API | [Python SDK](/reference/python-sdk) · [配置字段](/reference/config-fields/) |
| 排错 | [FAQ](/faq/) |
