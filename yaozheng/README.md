# 量子数据 → 经典 ML：独立交付包

本文件夹 **与 qchem_qml_md 工程完全脱钩**，可直接复制到 Windows（例如 `D:\yaozheng\`）独立使用。

## 目录一览

```
yaozheng/
├── README.md                          ← 本文件（Windows 操作说明）
├── requirements.txt                   ← 仅 pydantic / pandas / pyarrow / pytest
├── setup.bat / setup.ps1              ← 创建本地 .venv
├── scripts/                           ← Windows 一键脚本
├── 调研_量子数据用于经典机器学习_文献库与决策框架.md
├── quantum_data_ml_survey.bib         ← 83 条文献
└── survey_quantum_data_ml/
    ├── README.md
    ├── latex/                         ← LaTeX 报告（8 章）
    ├── cheatsheets/                   ← 7 张领域速查 + 决策表
    ├── schema/                        ← JSON Schema + Pydantic + SQLite 入库
    └── data/                          ← 示例 SQLite / Parquet（可选）
```

## 复制到 Windows

1. 将整个 `yaozheng` 文件夹复制到目标路径，例如 `D:\yaozheng\`
2. 打开 **命令提示符** 或 **PowerShell**，进入该目录：
   ```cmd
   cd /d D:\yaozheng
   ```
3. 双击或在终端运行：
   ```cmd
   setup.bat
   ```
   或 PowerShell：
   ```powershell
   .\setup.ps1
   ```

> 本包自带虚拟环境，**不要**依赖原 Linux 项目里的 `.venv`。

## Python 常用操作
（先 `setup.bat`，再 `call .venv\Scripts\activate.bat`）

```cmd
scripts\validate_examples.bat
scripts\ingest_examples.bat
scripts\run_tests.bat

.venv\Scripts\python.exe survey_quantum_data_ml\schema\ingest_cli.py list
.venv\Scripts\python.exe survey_quantum_data_ml\schema\ingest_cli.py show <uuid>
.venv\Scripts\python.exe survey_quantum_data_ml\schema\ingest_cli.py export-parquet -o survey_quantum_data_ml\data\records.parquet
```

## 生成 PDF（Windows）

**LaTeX 报告**（需 [MiKTeX](https://miktex.org/download) 或 TeX Live，含 `xelatex` + 中文 `ctex`）：

```cmd
scripts\build_report.bat
```

输出：`survey_quantum_data_ml\latex\main.pdf`

**速查表合并 PDF**（需 [Pandoc](https://pandoc.org/installing.html) + xelatex）：

```cmd
scripts\build_cheatsheets.bat
```

## 内容说明

| 资产 | 说明 |
|------|------|
| 主调研 Markdown | 决策树、路径 1/2 矩阵、BibTeX 分组、benchmark 清单 |
| **`路径1_真数据标签_文献综述.md`** | **路径 1 专题深度综述（本对话新增）** |
| `quantum_data_ml_survey.bib` | 独立文献库，LaTeX 通过 `../../quantum_data_ml_survey` 引用 |
| LaTeX `main.tex` | 8 章报告，与 Markdown 内容对应 |
| Schema v1 | `path_type`: labeled / native / hybrid，带 Pydantic 校验 |
| 入库 CLI | SQLite 索引 + Parquet 导出/导入 |

## 版本

- Pack version: **1.0-standalone**
- Schema version: **1**
- 打包日期: 2026-07-02

## 与本仓库关系

此目录为 **只读快照**，用于 Windows 侧继续编辑/编译。若在 `qchem_qml_md` 中更新了调研内容，请重新生成或手动同步 `yaozheng` 文件夹。
