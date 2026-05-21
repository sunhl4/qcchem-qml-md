# 本地 AI 一体机应用场景与落地方案调研

## 一、汇报结论

**定位**：公司内部研发与知识资产基础设施，服务量子计算软件研发、文献与算法复现、个人编码规范、实验数据沉淀四类工作。

**推荐技术路线**（均须本地部署，数据不上云、不出境）：


| 层次       | 组件                                       | 开源                         | 作用                      |
| ------------ | -------------------------------------------- | ------------------------------ | --------------------------- |
| 研发入口   | 已选 AI Coding 工具                        | 否，须私有化                 | 代码撰写、调试            |
| 知识库底座 | Dify + RAGFlow                             | 是                           | 文档解析、RAG、工作流入口 |
| 文献能力   | PaperQA                                    | 是                           | 论文问答、证据引用        |
| 实验数据   | 模板+库+对象存储+RAG；参考 Datalab/LaminDB | 参考项开源                   | 实验记录与检索            |
| 流程编排   | n8n；复杂流程用 LangGraph                  | n8n Fair-code；LangGraph MIT | 自动化与 Agent            |

**原则**：不做模型再训练，优先 RAG + 模板 + 工作流；商业 SaaS（Elicit、Benchling、LabArchives 等）仅作形态参考，不承载涉密数据。各场景共用 GPU/CPU/存储，按项目与权限隔离。

**落地节奏**：近期—知识库、文献问答、实验模板入库；中期—复现闭环、CI 联动、实验对比；长期—公司级实验库与 benchmark。

---

## 二、组件开源与本地部署属性


| 组件                             | 开源                              | 本地部署     | 作核心系统 |
| ---------------------------------- | ----------------------------------- | -------------- | ------------ |
| Dify                             | 社区版是（Apache 2.0）            | Docker/K8s   | 是         |
| RAGFlow                          | 是                                | Docker       | 是         |
| PaperQA                          | 是                                | Python 本地  | 是（文献） |
| n8n                              | 源码开放（Fair-code，商用查许可） | self-hosted  | 是（流程） |
| LangGraph                        | 是（MIT）                         | 自建服务     | 定制用     |
| Datalab / LaminDB / eLabFTW      | 是                                | 可自托管     | 参考/试点  |
| AI Coding                        | 否                                | 须企业私有化 | 须书面确认 |
| Elicit / Benchling / LabArchives | 否                                | 云为主       | 否，仅参考 |

---

## 三、四类应用场景（要点）

### 1. 云平台代码生成与智能调试

基于云平台代码库与示例，实现接口生成、CI/日志辅助排错、测试补全、代码解释。AI Coding 须私有化；一体机提供本地知识库、规范文档与日志索引。**难度**中偏高；**GPU** 建议 1×48GB 起（30B 级代码模型），多人并发建议 2×48GB/80GB。

### 2. 文献调研与算法复现

论文问答、带引用摘要、主题综述、复现计划与结果对比。**方案**：PaperQA + RAGFlow/Dify（均开源）。**难度**：问答中等，复现闭环偏高。**硬件**：与知识库共用 CPU/向量库/对象存储，GPU 走统一推理服务。

### 3. AI Coding 规范与个人助手

公式转代码、规范与接口适配检查、结合本地日志调试。配套建设规范库、公式库、接口示例库、常见 bug 库，对接 Git/CI。**硬件**：共享本地 GPU，禁止公有云推理。

### 4. 多模态实验数据库

模板化收集方法、参数、数据、图表、日志、代码与结论；结构化抽取与历史检索、报告生成。**方案**：短期「表单+对象存储+库+RAG」，参考 Datalab/LaminDB/eLabFTW（开源），不上重型 LIMS。**难度**：入库中等，全自动结构化偏高。**硬件**：以存储与数据库为主，AI 能力复用统一推理。

---

## 四、推荐组合、案例与资源

### 组合一：Dify + RAGFlow（开源，本地）

- **用途**：内部知识库、复杂 PDF/表格/扫描件、项目资料问答、报告与办公流程。
- **案例**：Kakaku.com（Dify 内部应用）；Wing（自托管 RAG，资料查找 10 分钟→1 分钟）；Hakuhodo DY ONE（流程自动化）。RAGFlow 侧重复杂文档 RAG 与研报类解析。
- **部署**：试点 Docker Compose，中等；生产需独立库、向量库、对象存储与监控。
- **硬件**：试点 4–8 核/16–32GB/200–500GB SSD；部门级 16 核+/64–128GB/1–2TB；本地大模型才需 GPU。
- **训练**：不需要。

### 组合二：PaperQA + RAGFlow/Dify（开源，本地）

- **用途**：文献问答、证据引用、综述草稿、复现计划、与内部结果对比。
- **案例**：FutureHouse PaperQA2（科学文献 RAG、带引用回答）；可迁移方法为全文检索与结论溯源，非直接套用其行业数据。
- **部署**：问答中等；复现需接代码库与 benchmark。
- **硬件**：PaperQA 轻量；PDF 与向量复用组合一；GPU 共享。
- **训练**：不需要。

### 组合三：实验库（轻量自建 + 开源参考）

- **用途**：实验沉淀、benchmark、报告与历史复用。
- **案例**：Gilead/Lyell（Benchling，商业仅参考）；NIH（LabArchives，商业仅参考）；落地参考 Datalab、LaminDB（开源）。
- **部署**：模板入库中等；标准化公司库偏高，难点在字段与流程而非模型。
- **硬件**：1TB+ SSD/对象存储起步，可扩至 5–20TB；AI 复用统一推理。
- **训练**：不需要。

### 组合四：n8n + LangGraph（本地）

- **用途**：论文抓取—总结—入库—推送；实验归档；CI/通知；接 Git、库、飞书/企微。
- **案例**：Vodafone、TMNZ、ITNT（n8n 自托管）；Trellix、AppFolio、Remote、C.H. Robinson（LangGraph 生产 Agent）。
- **部署**：n8n 低—中；LangGraph 中—高，需 Redis/PostgreSQL。
- **硬件**：n8n 以轻量 CPU 为主；GPU 共享。
- **训练**：不需要；n8n 商用须查 Fair-code 许可。

---

## 五、硬件共享与配置建议（AI建议待考证）

**可共享**：GPU 推理、embedding、向量库、文档解析、对象存储、PostgreSQL/MySQL/Redis、统一权限审计。

**须隔离**：生产/测试库、项目知识库、代码/实验/客户数据分级；GPU 设队列与并发上限。


| 档位     | 适用           | CPU       | 内存       | 存储                  | GPU                  |
| ---------- | ---------------- | ----------- | ------------ | ----------------------- | ---------------------- |
| 轻量试点 | 10–20 人      | ~16 核    | 64GB       | 2TB NVMe              | 可选 24GB（7B–14B） |
| 部门级   | 研发常态       | 32–64 核 | 128–256GB | 4–8TB + NAS/对象存储 | 1–2×48GB/80GB      |
| 公司级   | 多部门、高并发 | 64 核+    | 256GB+     | 10TB+ 可扩展          | 2–4×80GB，服务拆分 |

Dify/RAGFlow/n8n/数据库本身不强制 GPU；内网闭环下 GPU 用于本地 LLM、embedding、重排与图文解析。**禁止**将代码、论文、实验数据、日志发往外部 SaaS API。

---

## 六、落地路径（摘要）

1. **1–2 月**：部署 Dify+RAGFlow；接入文档与论文；PaperQA 试点；n8n 做文献流水线；实验模板+人工上传+AI 摘要。
2. **2–4 月**：接 Git/CI/规范库；论文复现接 benchmark；实验入库与对比报告。
3. **4–8 月**：统一实验目录与权限；跨文献/实验/代码检索；再评估是否小规模微调。

---

## 七、采购核查清单

- 核心组件开源或可自托管，许可满足商用（尤其 n8n、Dify 企业版）。
- 全链路本地：推理、解析、向量检索、日志均在内网；数据不上云、不出境。
- 支持多模型（通用/代码/embedding/rerank）、GPU 队列、私有 Git、对象存储、企微/飞书、CI。
- 权限隔离、审计、备份、脱敏；存储与 GPU 可扩展。

---

## 八、参考链接

- 开源仓库：Dify https://github.com/langgenius/dify | RAGFlow https://github.com/infiniflow/ragflow | PaperQA https://github.com/Future-House/paper-qa | n8n https://github.com/n8n-io/n8n | LangGraph https://github.com/langchain-ai/langgraph | Datalab https://github.com/datalab-org/datalab | LaminDB https://github.com/laminlabs/lamindb | eLabFTW https://github.com/elabftw/elabftw
- 案例：Dify/Kakaku https://dify.ai/blog/kakaku-accelerates-ai-adoption-with-dify-fast-secure-and-scalable | Dify/Wing https://weing.co.jp/dify-rag-case-study/ | n8n/Vodafone https://n8n.io/case-studies/vodafone | LangGraph/AppFolio https://www.langchain.com/blog/customers-appfolio | Benchling/Gilead https://www.benchling.com/customer-stories/gilead-partnering-with-benchling-to-improve-large-molecule-bioprocess | LabArchives/NIH https://www.labarchives.com/blog/national-institutes-for-health-selects-labarchives-as-its-one-approved-multi
