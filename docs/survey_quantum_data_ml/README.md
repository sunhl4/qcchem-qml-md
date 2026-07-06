# 量子数据 → 经典 ML：调研交付包

本目录包含行业调研与文献综述的**可交付资产**（LaTeX 报告、速查表、数据 Schema）。

## 目录结构

```
survey_quantum_data_ml/
├── README.md                          ← 本文件
├── latex/                             ← LaTeX 报告（\input 分章）
│   ├── main.tex
│   ├── preamble.tex
│   ├── Makefile
│   └── chapters/01–08.tex
├── cheatsheets/                       ← 分领域一页纸速查
│   ├── 00_index.md
│   └── cheatsheet_*.md
├── schema/                            ← JSON Schema + Pydantic + 入库
│   ├── quantum_experiment_record.schema.json
│   ├── quantum_experiment_record.py
│   ├── quantum_data_store.py          ← SQLite / Parquet
│   ├── ingest_cli.py
│   ├── validate_record.py
│   ├── test_quantum_data_store.py
│   └── examples/*.json
├── data/                              ← 默认 SQLite + 导出 Parquet
│   ├── quantum_experiment_records.sqlite
│   └── records.parquet
└── (上级) ../quantum_data_ml_survey.bib  ← 83 条 BibTeX
    ../调研_量子数据用于经典机器学习_文献库与决策框架.md
```

## 1. LaTeX 报告

**依赖**：TeX Live（`xelatex` + `ctex`）、`bibtex`

```bash
cd docs/survey_quantum_data_ml/latex
make              # 本地 xelatex
./build_report.sh # 优先本地，否则 Docker texlive/texlive
make clean
```

- 主文件：`main.tex`，分 8 章 `\input{chapters/...}`
- 参考文献：自动引用 `docs/quantum_data_ml_survey.bib`

## 2. 一页纸速查表

| 文件 | 领域 |
|------|------|
| `cheatsheet_many_body.md` | 量子多体 / 相分类 |
| `cheatsheet_qem_surrogate.md` | QEM / 代理 / VQE |
| `cheatsheet_hep.md` | 高能物理 |
| `cheatsheet_finance.md` | 金融 |
| `cheatsheet_life_chem_materials.md` | 药物 / 化学 / 材料 |
| `cheatsheet_cv_sensing_security.md` | 视觉 / 传感 / 安全 |
| `cheatsheet_decision.md` | 路径决策总表 |

**批量合并 PDF**：

```bash
cd docs/survey_quantum_data_ml/cheatsheets
./build_cheatsheets_pdf.sh   # 需 pandoc + xelatex
```

## 3. 数据 Schema（入库）

**JSON Schema**：`schema/quantum_experiment_record.schema.json`（draft 2020-12）

**Pydantic v2 模型**：`schema/quantum_experiment_record.py`

```python
import sys
sys.path.insert(0, "docs/survey_quantum_data_ml/schema")
from quantum_experiment_record import QuantumExperimentRecord

record = QuantumExperimentRecord.model_validate(payload)
```

**命令行校验**：

```bash
# 使用项目虚拟环境（含 pydantic）
.venv/bin/python docs/survey_quantum_data_ml/schema/validate_record.py \
  docs/survey_quantum_data_ml/schema/examples/hybrid_many_body.json

.venv/bin/python docs/survey_quantum_data_ml/schema/validate_record.py \
  docs/survey_quantum_data_ml/schema/examples/native_shadow_only.json
```

### path_type 约束

| path_type | 必填 |
|-----------|------|
| `labeled` | `labels`（至少一个标签字段） |
| `native` | `measurement.raw_outcomes` 或 `shadow_vectors` |
| `hybrid` | `labels` + 原生测量字段 |

## 4. SQLite / Parquet 入库

**依赖**：项目 `.venv`（`pydantic`；Parquet 需 `pyarrow`）

```bash
# 入库（单文件或目录）
.venv/bin/python docs/survey_quantum_data_ml/schema/ingest_cli.py ingest \
  docs/survey_quantum_data_ml/schema/examples

# 列出 / 查看
.venv/bin/python docs/survey_quantum_data_ml/schema/ingest_cli.py list
.venv/bin/python docs/survey_quantum_data_ml/schema/ingest_cli.py show <uuid>

# Parquet 往返
.venv/bin/python docs/survey_quantum_data_ml/schema/ingest_cli.py export-parquet \
  -o docs/survey_quantum_data_ml/data/records.parquet
.venv/bin/python docs/survey_quantum_data_ml/schema/ingest_cli.py import-parquet \
  docs/survey_quantum_data_ml/data/records.parquet --db /tmp/other.sqlite
```

默认数据库：`data/quantum_experiment_records.sqlite`

**测试**：

```bash
.venv/bin/pytest docs/survey_quantum_data_ml/schema/test_quantum_data_store.py -q
```

## 5. 与主调研文档关系

- 完整决策树 + BibTeX 分组：`docs/调研_量子数据用于经典机器学习_文献库与决策框架.md`
- 独立 `.bib`：`docs/quantum_data_ml_survey.bib`

## 版本

- Schema version: **1**
- 文档 pack version: **1.0**（2026-07-02）
