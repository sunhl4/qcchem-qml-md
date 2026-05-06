# Windows + WSL + Cursor 开发环境配置指南

本文档汇总在本工程（`qchem-stack` / `qchem_qml_md`）上做 **开发与小体系测试**（小体系 PySCF、量子线路模拟器等）时，**硬件参考**、**WSL 使用要点**、**项目目录与同步**、以及 **Cursor 的 WSL 相关安装与配置**。

---

## 1. 硬件参考（开发与测试）

### 1.1 用途与硬件敏感点

| 方向 | 典型负载 | 硬件敏感点 |
|------|-----------|------------|
| 开发/测试 | IDE、`ruff`、`pytest`、依赖安装 | CPU 单核性能、SSD、内存 |
| 小体系 PySCF | 小分子 RHF/少量 post-HF、片段/DMET 玩具算例 | **内存**为主；电子数很少时 CPU 要求不高 |
| 模拟器 | statevector 随比特数指数吃内存 | **RAM** 最关键；多数场景 **GPU 非必需** |

### 1.2 配置档位参考

**最低可接受**

- CPU：4 核 / 8 线程级别  
- 内存：**16 GB**  
- 存储：**256 GB NVMe SSD**  
- GPU：非必需  

适合：很小分子、约 **≤16～18 qubit** 量级玩具线路、轻量 CI 类用例。

**推荐舒适**

- CPU：6～8 核 / 12～16 线程  
- 内存：**32 GB**  
- 存储：**512 GB NVMe SSD**  
- GPU：按需（固定使用 GPU 模拟器时再考虑中端卡与显存）  

更从容：并行 pytest、略大 PySCF、**约 20～24 qubit** statevector 需个案评估内存。

**若比特数或并行再放大**

- 内存 **32～64 GB**、CPU 8 核以上、存储 512 GB～1 TB。

### 1.3 本机配置对照（示例）

以下为一台已验证可舒适覆盖「开发 + 小体系 PySCF + 模拟器」的配置示例：

- **CPU**：13th Gen Intel Core i5-13600K（桌面级常见；若为笔记本请以任务管理器为准）  
- **内存**：32 GB  
- **系统**：64 位 Windows，x64  

结论：落在「推荐舒适档」偏上，一般 **无需** 为该档用途再升级 CPU/内存；有余力时可优先 **SSD 容量/备份** 或 **按需加 GPU**。

---

## 2. WSL 是否方便测试

**结论：方便**，且更接近 **Linux / CI** 环境；Python 科学栈在 Ubuntu 等发行版上文档与兼容性通常更好。

### 2.1 需要留意的点

1. **代码放哪（最重要）**  
   - 项目放在 **WSL 自己的 Linux 文件系统**（例如 `~/projects/...`，底层为 ext4）。  
   - **不要**长期在 **`/mnt/c/...`、`/mnt/d/...`** 上作为工作目录跑大量 I/O（测试会慢，文件监控易异常）。  

2. **与 Windows 的配合**  
   - **IDE**：Cursor / VS Code 使用 **Remote WSL** 打开 WSL 内的文件夹，编辑、终端、调试均在 Linux 一侧最省事。  
   - **浏览器访问本机 API**：在 WSL2 中启动的 `uvicorn` 等，Windows 浏览器一般仍访问 **`http://localhost:端口`**（端口转发默认打通）。  

3. **资源**  
   - WSL2 会占用一部分内存；**32 GB** 主机通常宽裕。若偶发 OOM，可在用户目录下的 **`.wslconfig`** 中调整内存上限等（见下文）。  

4. **GPU（可选）**  
   - 纯 CPU 的 PySCF 与模拟器无需 GPU。若使用 **NVIDIA + CUDA** 的 GPU 模拟路线，需本机驱动与 WSL CUDA 支持链。

---

## 3. 项目同步到 WSL（ext4）

推荐将本仓库的 Linux 工作副本放在：

```text
~/projects/qchem_qml_md
```

即 Windows 资源管理器中可表示为：

```text
\\wsl$\Ubuntu\home\<你的Linux用户名>\projects\qchem_qml_md
```

### 3.1 一次性同步示例（rsync）

在 **WSL Ubuntu** 终端中执行（将 Windows 的 `D:\Yaozheng\qchem_qml_md` 对应为 `/mnt/d/Yaozheng/qchem_qml_md`，按实际盘符修改）：

```bash
mkdir -p ~/projects
rsync -a --delete \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='node_modules' \
  --exclude='.tox' \
  --exclude='.ruff_cache' \
  /mnt/d/Yaozheng/qchem_qml_md/ ~/projects/qchem_qml_md/
```

之后在 WSL 内开发与跑测试，请使用该目录；Windows 侧 `D:\...` 可作为备份或与 Git 远程协作的另一份副本，**日常 heavy 测试以 WSL 内目录为准**。

### 3.2 `.wslconfig`（Windows 用户目录）

在 **`%USERPROFILE%\.wslconfig`**（例如 `C:\Users\<用户名>\.wslconfig`）中可为 WSL2 设置内存、处理器数、交换文件等。修改后需在 **PowerShell** 执行：

```powershell
wsl --shutdown
```

再重新打开 WSL 方生效。

**示例（32 GB 主机，为 Windows 与 IDE 预留余量）：**

```ini
[wsl2]
memory=24GB
processors=12
swap=8GB
localhostForwarding=true
```

可按实际负载调高/调低 `memory` 与 `processors`。

---

## 4. Cursor（Windows）WSL 相关安装与配置

### 4.1 扩展

Cursor 使用 **`anysphere.remote-wsl`**（Remote WSL），在扩展面板安装或命令行：

```powershell
cursor --install-extension anysphere.remote-wsl
```

（若已安装，可加 `--force` 尝试拉取更新。）

建议同时保留 **`ms-python.python`**、**`ms-python.debugpy`**（你通常已安装）。首次 **连接到 WSL 窗口** 时，编辑器可能在 WSL 侧再安装对应组件，按提示允许即可。

### 4.2 用户级 `settings.json`

路径：**`%APPDATA%\Cursor\User\settings.json`**。

建议增加（与现有 JSON 合并，注意逗号）：

```json
"remote.WSL.defaultDistribution": "Ubuntu",
"remote.autoForwardPorts": true,
"remote.restoreForwardedPorts": true,
"terminal.integrated.profiles.windows": {
    "Ubuntu (WSL)": {
        "path": "wsl.exe",
        "args": ["-d", "Ubuntu", "--cd", "~"],
        "icon": "terminal-linux"
    }
}
```

说明：

- **`remote.WSL.defaultDistribution`**：默认使用的 WSL 发行版名称（与 `wsl -l -v` 中一致）。  
- **`remote.autoForwardPorts` / `remote.restoreForwardedPorts`**：便于在 WSL 中跑 Web 服务并用 Windows 浏览器访问。  
- **`terminal.integrated.profiles.windows`**：在 **未** 打开 Remote 窗口时，仍可从集成终端下拉选择 **「Ubuntu (WSL)」** 快速进入 Ubuntu。

### 4.3 仓库内 `.vscode`（本工程已提供）

路径：**`qchem_qml_md/.vscode/`**

- **`settings.json`**（在 **WSL Remote** 打开仓库时生效）  
  - `python.defaultInterpreterPath`：`${workspaceFolder}/.venv/bin/python`  
  - `python.terminal.activateEnvironment`：`true`  
  - `terminal.integrated.defaultProfile.linux`：`bash`  
  - `files.eol`：`"\n"`  

- **`extensions.json`**  
  - 推荐使用：`anysphere.remote-wsl`、`ms-python.python`、`ms-python.debugpy`  

若你在 Windows 盘上修改了 `.vscode`，可再次用 **rsync** 将 `.vscode` 同步到 `~/projects/qchem_qml_md/`。

### 4.4 日常操作流程（推荐）

1. **用 WSL 打开工程**  
   - `Ctrl+Shift+P` → **`WSL: Open Folder in WSL...`**  
   - 选择 **`/home/<用户名>/projects/qchem_qml_md`**（或资源管理器 `\\wsl$\Ubuntu\...` 对应路径）。  

2. **在 WSL 中创建虚拟环境并安装可编辑包**（示例）  

```bash
cd ~/projects/qchem_qml_md
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

3. **选择解释器**  
   - `Ctrl+Shift+P` → **`Python: Select Interpreter`** → 选择 **`.venv` 中的 Python**。  

4. **运行测试**  

```bash
pytest
ruff check src tests
```

### 4.5 多 Windows 用户

若存在多个 Windows 登录账户，**`%APPDATA%\Cursor\User\settings.json`** 为 **按用户** 存储；每个常用账户需各自合并上述 **Remote WSL** 相关配置。

---

## 5. 检查清单（速查）

| 步骤 | 状态 |
|------|------|
| WSL2 Ubuntu 可用（`wsl -l -v`） | ☐ |
| 工程在 `~/projects/...`（非长期仅用 `/mnt/d/...`） | ☐ |
| 已按需配置 `%USERPROFILE%\.wslconfig` 并已 `wsl --shutdown` | ☐ |
| Cursor 已装 `anysphere.remote-wsl` | ☐ |
| 用户 `settings.json` 已合并 WSL/端口/终端配置 | ☐ |
| 使用「在 WSL 中打开文件夹」打开 `~/projects/qchem_qml_md` | ☐ |
| 已创建 `.venv` 并 `pip install -e ".[dev]"` | ☐ |
| 已选择 `.venv` 解释器 | ☐ |

---

## 6. 相关工程文档

- 软件分层与 CI 约定：`docs/ENGINEERING_ARCHITECTURE.md`  

---

*文档版本：与当前仓库实践一致；若你更改发行版名、盘符或用户名，请相应替换文中路径与 `defaultDistribution`。*
