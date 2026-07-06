# 幺正量子 HPC 登录与环境配置教程

**适用集群**：幺正量子 HPC（Slurm `uq_hpc`，OpenSCOW 门户）  
**登录节点**：`192.168.110.220`（`login01`）  
**门户**：http://192.168.110.37/  
**账号**：与 SSH 相同（示例：`sun_hl`）  
**家目录 `$HOME`**：`/data/home/<用户名>` — **所有代码、conda 环境、依赖、结果均在此**  
**临时目录 `/data/scratch/<用户名>`**：**禁止存放任何数据或依赖**（集群会不定期清理）

**关联工程**：`qchem_qml_md` + sibling `QML-FF`  
**目标**：在 HPC 上创建 conda 环境，打通 **UQC 内网云**，跑通 **力场在线学习 smoke**（mock + 云）。

---

## 0. 工作目录：只用 `$HOME`，禁止用 scratch

| 路径 | 说明 |
|------|------|
| **`$HOME`** = `/data/home/sun_hl` | **唯一工作根目录**：代码、Miniforge、conda 环境、pip 依赖、实验结果、日志 |
| **`/data/scratch/<用户名>`** | **临时目录，集群会不定期清理** — **禁止**放代码、conda、环境、结果或任何需保留的数据 |

> **重要**：`/data/scratch/` 仅适合 Slurm 作业运行时产生的**可丢弃**中间文件（若确有需要）。本项目的持久化内容**一律放在 `$HOME`**。

SSH 登录后 `$HOME` 自动指向 `/data/home/sun_hl`：

```bash
cd ~/projects/qchem_qml_md
```

### 0.1 若 scratch 中有历史残留

家目录恢复前曾临时用过 scratch，应清理：

```bash
# 确认 $HOME 下环境可用后再执行
source ~/env.sh
python -c "import qchem_stack; print('OK')"

# 删除 scratch 中的旧数据（不可恢复）
rm -rf /data/scratch/$(whoami)/*
```

**禁止**在脚本、Slurm 作业、文档示例中使用 `/data/scratch/` 作为安装或输出路径。

### 0.2 权限自检

```bash
ls -ld $HOME
test -w $HOME && echo HOME_WRITE_OK
touch $HOME/_perm_test && rm $HOME/_perm_test && echo HOME_TOUCH_OK
```

期望：`drwx------ sun_hl g1`，读写正常。

---

## 1. 集群资源速览

| 项目 | 值 |
|------|-----|
| 调度器 | Slurm 23.11.4 |
| 分区 | `hpc`（默认，最长 7 天） |
| 计算节点 | `compute01`、`compute02`（各 192 CPU，~755 GiB 内存） |
| GPU | **无**（纯 CPU；JAX 请设 `JAX_PLATFORMS=cpu`） |
| 家目录 | **`/data/home/<用户名>`** — 持久存储 |
| 临时 scratch | **`/data/scratch/<用户名>`** — 不定期清理，**禁止**放依赖/结果 |
| UQC 内网 | `192.168.110.148:8003`（HPC 登录节点 **TCP 可达**） |

---

## 2. 完整操作流程（从零到 smoke 通过）

### 阶段 A：本机同步代码到 HPC

```bash
LOCAL_QCHEM=/home/sunhl/projects/qchem_qml_md
LOCAL_QMLFF=/home/sunhl/projects/QML-FF
REMOTE=sun_hl@192.168.110.220

rsync -avz --progress \
  --exclude '.git' --exclude '.venv' --exclude '.micromamba' \
  --exclude 'htmlcov' --exclude 'docusaurus-site' --exclude 'results' \
  --exclude '__pycache__' --exclude '.pytest_cache' \
  "$LOCAL_QCHEM/" "$REMOTE:~/projects/qchem_qml_md/"

rsync -avz --progress \
  --exclude '.git' --exclude '__pycache__' \
  "$LOCAL_QMLFF/" "$REMOTE:~/projects/QML-FF/"
```

同步 UQC token（**勿提交 Git**）：

```bash
scp "$LOCAL_QCHEM/.env" "$REMOTE:~/projects/qchem_qml_md/.env"
# HPC 上: chmod 600 ~/projects/qchem_qml_md/.env
```

### 阶段 B：SSH 登录

```bash
ssh sun_hl@192.168.110.220
mkdir -p ~/projects ~/envs ~/logs ~/results
cd ~/projects/qchem_qml_md
```

### 阶段 C：一键安装 conda 环境

```bash
cd ~/projects/qchem_qml_md
proxy_on    # 下载 Miniforge / pip 包时需要
bash scripts/hpc/setup_qchem_stack_env.sh
```

脚本会：

1. 安装 Miniforge3 → `~/miniforge3`
2. 创建 conda 环境 → `~/envs/qchem-stack`
3. pip 安装本工程 + QML-FF + UQC 插件
4. 写入 `.env` 模板（若不存在）
5. 写入 `~/env.sh`（登录快捷激活）
6. 跑 `smoke_pipeline` + **mock 力场在线学习 smoke**

### 阶段 D：每次登录激活环境

```bash
source ~/env.sh
# 等价于：
# source ~/miniforge3/etc/profile.d/conda.sh
# conda activate ~/envs/qchem-stack
# export JAX_PLATFORMS=cpu
# cd ~/projects/qchem_qml_md
```

### 阶段 E：UQC 连通性检查

```bash
source ~/env.sh
proxy_off
python scripts/check_uqc_connectivity.py
```

期望：

```text
TCP 192.168.110.148:8003 ... OK
Socket.IO + get_chips ... OK ['qiskit-sim', 'iontrap-sim']
```

### 阶段 F：跑力场在线学习 smoke

#### F1. mock（无 token，~2 分钟）

```bash
source ~/env.sh
python scripts/run_uqc_md_ml.py \
  --backend-profile uqc_mock \
  --experiment configs/example_h2_uqc_mock_md_ml.yaml \
  --loop configs/example_h2_uqc_mock_qmlff_loop_smoke.yaml \
  --output ~/results/hpc_smoke_uqc_mock
```

#### F2. UQC 内网云 iontrap-sim（需有效 token，~1–2 分钟）

```bash
source ~/env.sh
proxy_off
python scripts/run_uqc_md_ml.py \
  --backend-profile uqc_cloud \
  --experiment configs/example_h2_uqc_cloud_sim_md_ml.yaml \
  --loop configs/example_h2_uqc_cloud_sim_qmlff_loop_smoke.yaml \
  --output ~/results/hpc_smoke_uqc_cloud
```

通过标志：`~/results/.../md_validation_summary.json` 存在，且 `converged=true`。

### 阶段 G：Slurm 批处理（可选）

```bash
cd ~/projects/qchem_qml_md
mkdir -p ~/logs logs

PROFILE=uqc_mock sbatch scripts/hpc/smoke_uqc_md_ml.sbatch
PROFILE=uqc_cloud sbatch scripts/hpc/smoke_uqc_md_ml.sbatch

squeue -u $USER
tail -f logs/uqc_mdml_smoke_<jobid>.out
```

---

## 3. SSH 与 Slurm

```bash
ssh sun_hl@192.168.110.220
sinfo -s
squeue
sbatch job.sh
scancel <jobid>
```

---

## 4. 代理开关

登录节点 `~/.bashrc` 已内置：

```bash
proxy_on() {
  export http_proxy="http://192.168.110.143:7897"
  export https_proxy="http://192.168.110.143:7897"
  export HTTP_PROXY="$http_proxy"
  export HTTPS_PROXY="$https_proxy"
  export no_proxy="localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,.local"
  export NO_PROXY="$no_proxy"
}

proxy_off() {
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
  unset all_proxy ALL_PROXY no_proxy NO_PROXY
}
```

| 场景 | 命令 |
|------|------|
| pip / git / Miniforge 下载 | `proxy_on` |
| UQC 内网 `192.168.110.148` | `proxy_off` |

---

## 5. OpenSCOW 门户

1. http://192.168.110.37/ — 同 SSH 账号登录
2. UQC token：用户中心复制 → 更新 `~/projects/qchem_qml_md/.env`

---

## 6. 目录布局（家目录标准结构）

```text
/data/home/sun_hl/          (= $HOME)
├── env.sh                  # 登录激活脚本
├── miniforge3/
├── envs/qchem-stack/
├── projects/
│   ├── qchem_qml_md/       # 主工程 + .env
│   └── QML-FF/
├── results/
│   ├── hpc_smoke_uqc_mock/
│   └── hpc_smoke_uqc_cloud/
└── logs/
```

---

## 7. UQC 配置

`~/projects/qchem_qml_md/.env`：

```bash
SERVER_HOST=192.168.110.148
SERVER_PORT=8003
UQC_API_TOKEN=<门户用户中心，约 30 分钟有效>
JAX_PLATFORMS=cpu
```

---

## 8. Smoke 配置

| 模式 | profile | 实验 YAML | 环 YAML | token |
|------|---------|-----------|---------|-------|
| mock | `uqc_mock` | `configs/example_h2_uqc_mock_md_ml.yaml` | `configs/example_h2_uqc_mock_qmlff_loop_smoke.yaml` | 否 |
| 云 | `uqc_cloud` | `configs/example_h2_uqc_cloud_sim_md_ml.yaml` | `configs/example_h2_uqc_cloud_sim_qmlff_loop_smoke.yaml` | 是 |

---

## 9. 验证清单

| # | 步骤 | 命令 | 通过标准 |
|---|------|------|----------|
| 1 | SSH | `ssh sun_hl@192.168.110.220` | 进入 login01，无 chdir 报错 |
| 2 | 家目录 | `touch ~/._t && rm ~/._t` | 无报错 |
| 3 | 环境 | `source ~/env.sh && python -c "import pyscf,qmlff,jax_md,uqc_client"` | 无 ImportError |
| 4 | 流水线 | `python scripts/smoke_pipeline.py` | 退出码 0 |
| 5 | UQC | `proxy_off && python scripts/check_uqc_connectivity.py` | TCP + get_chips OK |
| 6 | mock | §2 F1 | `md_validation_summary.json` + converged |
| 7 | 云 | §2 F2 | 同上 + backend=uqc_cloud |

---

## 10. 常见问题

| 现象 | 处理 |
|------|------|
| `pip` / `git clone` 超时 | `proxy_on` |
| UQC TCP 失败 | `proxy_off`；`SERVER_HOST=192.168.110.148` |
| token 过期 | 门户重新复制 → 更新 `.env` |
| 误把 conda/代码装到 scratch | 改到 `$HOME`；清理 scratch：`rm -rf /data/scratch/$(whoami)/*` |
| scratch 被集群清理导致环境丢失 | 说明依赖不应在 scratch；在 `$HOME` 重装 `setup_qchem_stack_env.sh` |

---

## 11. 相关脚本

| 文件 | 说明 |
|------|------|
| [`environment-hpc.yml`](../environment-hpc.yml) | conda 基础依赖 |
| [`scripts/hpc/setup_qchem_stack_env.sh`](../scripts/hpc/setup_qchem_stack_env.sh) | 一键安装 |
| [`scripts/hpc/smoke_uqc_md_ml.sbatch`](../scripts/hpc/smoke_uqc_md_ml.sbatch) | Slurm smoke |

---

## 附录 A：Cursor Skill 草稿

### 触发条件

- 幺正 HPC、`192.168.110.220`、`sun_hl`、UQC 内网、力场在线学习 smoke

### 标准步骤

1. rsync 本机 `qchem_qml_md` + `QML-FF` → `~/projects/`
2. scp 本机 `.env` → `~/projects/qchem_qml_md/.env`
3. `proxy_on && bash scripts/hpc/setup_qchem_stack_env.sh`
4. `source ~/env.sh`
5. `proxy_off && python scripts/check_uqc_connectivity.py`
6. mock smoke → `~/results/hpc_smoke_uqc_mock`
7. UQC 云 smoke → `~/results/hpc_smoke_uqc_cloud`

### 成功判据

- `md_validation_summary.json` 存在，`converged == true`
- UQC 云：`backend_profile == "uqc_cloud"`

### 禁止事项

- **禁止**在 `/data/scratch/` 存放代码、conda、pip 环境、实验结果或任何需保留的数据（集群不定期清理）
- 勿将 `.env` / token 提交 Git
- UQC 任务不要开 `http_proxy`

---

**安全提醒**：勿将 `UQC_API_TOKEN` 提交 Git。
