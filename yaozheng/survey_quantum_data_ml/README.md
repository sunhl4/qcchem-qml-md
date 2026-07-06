# 量子数据 → 经典 ML：调研交付包（独立版）

本目录位于 **yaozheng** 根文件夹内，不依赖任何外部 Python 包或 qchem 工程。

## 目录结构

```
survey_quantum_data_ml/
├── latex/          main.tex + chapters/01–08.tex
├── cheatsheets/    分领域一页纸速查
├── schema/         JSON Schema、Pydantic、SQLite 入库
└── data/           默认 quantum_experiment_records.sqlite
```

上级目录还有：
- `../调研_量子数据用于经典机器学习_文献库与决策框架.md`
- `../quantum_data_ml_survey.bib`

## 1. LaTeX 报告

**Windows**：在 yaozheng 根目录运行 `scripts\build_report.bat`

**Linux / WSL**：

```bash
cd survey_quantum_data_ml/latex
make
# 或 ./build_report.sh
```

参考文献：`../../quantum_data_ml_survey.bib`

## 2. 速查表

Markdown 在 `cheatsheets/`。合并 PDF：

- Windows: `scripts\build_cheatsheets.bat`
- Linux: `./cheatsheets/build_cheatsheets_pdf.sh`

## 3. Schema 校验

在 **yaozheng 根目录**、已激活 `.venv` 后：

```bash
python survey_quantum_data_ml/schema/validate_record.py \
  survey_quantum_data_ml/schema/examples/hybrid_many_body.json
```

## 4. SQLite / Parquet 入库

```bash
python survey_quantum_data_ml/schema/ingest_cli.py ingest \
  survey_quantum_data_ml/schema/examples
python survey_quantum_data_ml/schema/ingest_cli.py list
```

默认 DB：`data/quantum_experiment_records.sqlite`

### path_type 约束

| path_type | 必填 |
|-----------|------|
| `labeled` | `labels` |
| `native` | `measurement.raw_outcomes` 或 `shadow_vectors` |
| `hybrid` | `labels` + 原生测量字段 |

## 5. 测试

```bash
pytest survey_quantum_data_ml/schema/test_quantum_data_store.py -q
```

或 Windows: `scripts\run_tests.bat`
