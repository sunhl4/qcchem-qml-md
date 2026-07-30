---
title: 安装档位 / Install profiles
description: pip extras 矩阵（中英对照）：minimal、chem、quantum、api、full 与 Postgres 可选。
keywords:
  - install
  - extras
  - pip
  - profiles
---

# 安装档位 / Install profiles

支持的 `pip install` 组合矩阵。仓库原文：[install_profiles.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/install_profiles.md)。

| Profile / 档位 | Extras | Python | OS | Use case / 用途 |
|----------------|--------|--------|-----|-----------------|
| **minimal** | *(core)* | 3.10–3.12 | linux / mac / win | Precomputed pipeline, strict repro export / 预计算管线、严格 repro |
| **chem** | `chem` | 3.10–3.12 | linux (PySCF wheels) | Live PySCF SCF + Hamiltonian / 在线 PySCF SCF 与哈密顿量 |
| **quantum** | `chem,quantum` | 3.10–3.12 | linux | VQE/ADAPT + Qiskit Aer |
| **api** | `chem,quantum,api` | 3.12 | linux | HTTP API + SQLite worker |
| **full** | `dev`（可选 `pytket,nexus`） | 3.12 | linux | Maintainer / `release_precheck.sh`（ruff、pyright、pip-audit、pytest-cov） |
| **md-classical** | `chem` only | 3.12 | linux | Classical H₂ FF + QMEF（无 QML-FF）。**档位名，不是 pip extra。** |
| **all** | `all` = chem,quantum,pytket,nexus | 3.12 | linux | 完整开源面（不含 UQC） |
| **all-cloud** | `all-cloud` = all + uqc | 3.12 | linux | 实验性 UQC 云客户端 |
| **jobs-postgres** | `api,jobs-postgres` | 3.12 | linux | HA worker with Postgres job ledger |
| **observability** | `observability` | 3.12 | linux | OTLP export for pipeline events |
| **gqe**（常用附加） | `gqe` | 3.10–3.12 | linux | GPT-QE / JAX（见 [FAQ](/faq/)） |

### Extras 说明

- **`dev`**：`chem,quantum,api` + 测试/ lint 工具，**不含** `uqc` / `all`
- **`dev-uqc`**：`dev` + 实验性 `uqc`（CVE allowlist 仅用于该安装面，见仓库 `SECURITY.md`）
- **`md-classical`**：文档档位名 → `pip install -e ".[chem]"`，无对应空 extra

---

## PyPI 示例 / PyPI examples

```bash
pip install "qchem-stack[chem,quantum]"
pip install "qchem-stack[chem,quantum,api]"
pip install "qchem-stack[gqe]"
pip install "qchem-stack[all]"
pip install "qchem-stack[all-cloud]"
```

## 可编辑安装 / Editable examples

```bash
pip install -e ".[chem,dev]"
pip install -e ".[chem,quantum,api,jobs-postgres]"
pip install -e ".[dev,observability]"
pip install -e ".[dev-uqc]"
```

QML-FF 仍为旁路可编辑安装；见仓库 [README](https://github.com/sunhl4/qcchem-qml-md/blob/main/README.md)。

---

## 本地 Postgres 合规（可选）/ Local Postgres conformance

无需 CI 即可对 Postgres 跑 job-store 协议测试：

```bash
docker compose up -d postgres   # see docker-compose.yml
export QCHEM_JOB_DATABASE_URL=postgresql://qchem:qchem@127.0.0.1:5432/qchem_jobs  # pragma: allowlist secret
pytest tests/jobs/test_job_store_protocol_conformance.py -q
```

详见仓库 [job_store_extension.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/job_store_extension.md)。

---

## 相关

- [开始使用](/getting-started) · [English bridge](/getting-started-en)
- [HTTP + SQLite jobs](/reference/http-api-sqlite-jobs)
