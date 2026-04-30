# Vol.04 Extensions — 可选能力包与安装叙事

**读者**：发布工程、依赖管理、合作伙伴技术评审。  
**证据**：已抓取 [`extensions-overview.html`](https://docs.quantinuum.com/inquanto/extensions/extensions-overview.html)。

---

## 1. Extensions 的产品含义

InQuanto **核心 wheel** 与 **扩展包** 分离：扩展提供 **外部程序接口**（PySCF、Nexus、NGLView、Phayes）或 **专用硬件加速**（cuTensorNet）。文档层将扩展描述为 **「增强综合能力」** 的可选模块，而非核心必装。

---

## 2. 当前扩展清单（已证实）

| 扩展 | 文档职责 |
|------|-----------|
| InQuanto-Nexus | 云编译、远程设备、项目引用 |
| InQuanto-PySCF | 高级量子化学与驱动 |
| InQuanto-NGLView | Jupyter 内分子可视化 |
| InQuanto-Phayes | 贝叶斯 QPE 变体 |
| InQuanto-cuTensorNet | GPU 张量网络后端；链向 API `CuTensorNetProtocol` 与 examples |

---

## 3. 文档结构模式

- **extensions-overview**：总表 + 一段话定位。
- **各扩展独立 HTML**：安装命令、版本约束、与 **core API** 的交互点。
- **API 子域**：`api/extensions/inquanto-*_api.html` 承载 **类级参考**（与 Vol.05 衔接）。

---

## 4. 与 Python 打包生态的映射（推断）

**推断**：扩展以 **独立 PyPI 包** 或 **可选 extra** 形式分发（具体以发布说明为准）；文档站通过 **安装章节** 降低「import error」支持成本。

---

## 5. 本仓库 parity 策略（工程事实）

manifest 对 `inquanto_nexus`、`inquanto_nglview` 等标注 **`not-applicable` 或 `placeholder`**，并在 `reason_*` 中写明边界 — 文档站 **镜像节点仍存在**，避免读者以为「漏做页面」。

---

## 6. 自建「模拟器云平台」扩展叙事

建议新增 **一等扩展文档**（非 mirror）：

| 自建扩展 | 文档内容 |
|-----------|-----------|
| `qchem-simulator-cloud` | 租户、配额、队列、日志保留 |
| `qchem-repro-exporter` | `repro` JSON schema 版本、签名校验 |
| `qchem-backend-registry` | 支持的 `BackendSpec` 与能力矩阵 |

在 IA 上可与 InQuanto **extensions-overview** 平行，但 **不要** 伪装成 Quantinuum 官方扩展。

---

## 7. 本卷结论

Extensions 文档 = **可选依赖的商业与技术边界说明**。自建站优势：**开源扩展可直接链接到 GitHub README 与 CI badge**，透明度高于闭源扩展列表。

**下一卷**：[`vol-05-api-reference-patterns.md`](./vol-05-api-reference-patterns.md)。
