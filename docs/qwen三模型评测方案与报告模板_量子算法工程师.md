# 千问三模型能力边界评测方案（量子计算算法工程师）

面向角色：**量子计算算法工程师**（分子电子结构、变分量子算法、`qchem_stack` 类流水线）

对标模型：

| 档位 | API 名称 | 设计边界 |
|------|----------|----------|
| 轻量日常 | `qwen-flash` | 概念解释、沟通、轻量文档 |
| 日常编程 | `qwen3-coder-next` | 可运行代码、调试、Agent 编码 |
| 千问最强 | `qwen3.7-max` | 架构决策、多约束权衡、长链推理 |

**评测原则：** 每个场景有一条「主场 Prompt」，但 **三个模型都跑同一 Prompt**，观察是否「越界仍能完成」或「主场模型显著更优」。

---

## 一、三个工作场景与 Prompt

### 场景 S1 — 轻量日常（能力边界：Flash）

**工作情境：** 向合作者快速解释概念，写进 Slack / 会议纪要，不需要代码。

**主场模型：** `qwen-flash`

**统一 Prompt（三模型共用）：**

```text
[System]
你是量子计算算法工程师助手。回答要准确、简洁，面向已懂线性代数与量子力学基础的同事。

[User]
请用中文向合作算法工程师解释下面概念，总字数 180–220 字，分 3 条 bullet，不要代码：

主题：Jordan-Wigner 映射如何把费米子算符映射到 qubit 算符。

必须覆盖：
1) 为什么需要映射（量子硬件只原生支持 Pauli 门）
2) 映射后哈密顿量项的形式变化（字符串/局域性）
3) 一个实际代价（如链式 JW 的非局域性或 qubit 数）

禁止编造不存在的定理名称。
```

**预期能力边界：**

| 模型 | 预期表现 |
|------|----------|
| flash | 字数受控、三点齐全、无废话 → **应达标** |
| coder-next | 可能附带代码倾向或超长 → **可能越界** |
| 3.7-max | 内容过详、超字数 → **过度交付** |

**评分维度（1–5）：** 物理准确性、简洁性、结构合规（条数/字数）、幻觉（反向分）

---

### 场景 S2 — 日常编程（能力边界：Coder-Next）

**工作情境：** 在 ADAPT-VQE / operator pool 相关模块里加一个确定性选择函数。

**主场模型：** `qwen3-coder-next`

**统一 Prompt（三模型共用）：**

```text
[System]
你是资深 Python 量子算法工程师。只输出一个完整 Python 代码块，使用 typing，函数带 docstring，不要依赖外部库（numpy 可用）。

[User]
实现函数 `select_adapt_candidates(pool, gradient_scores, k, max_qubits)`：

- `pool`: list[tuple[str, tuple[int, ...]]]`，元素为 (算符名字, 涉及 qubit 索引)
- `gradient_scores`: dict[str, float]`，算符名 → |梯度|
- `k`: 本轮最多选几个算符
- `max_qubits`: 电路宽度上限

规则（按顺序）：
1) 只保留 gradient_scores 中存在且 score > 1e-8 的 pool 项
2) 按 score 降序
3) 若多个算符涉及 qubit 的并集超过 max_qubits，跳过该算符继续向下选
4) 选满 k 个或 pool 耗尽即停止
5) 返回 list[str]（算符名）

附带 3 个 assert 自测（写在 if __name__ == "__main__" 块），不要其他解释文字。
```

**参考正确答案要点（人工判分用）：**

- 排序键为 gradient 降序
- qubit 并集约束在「选入前」检查
- 跳过不满足宽度约束的候选，而非整体失败
- 3 个 assert 覆盖：正常选取、宽度过滤、阈值过滤

**评分维度（1–5）：** 逻辑正确性、可运行性、边界 case、代码风格、是否多余 prose

---

### 场景 S3 — 复杂架构（能力边界：3.7-Max）

**工作情境：** 为 H4 激发态流水线做方案选型 memo，绑定 shots 预算与现有模块名。

**主场模型：** `qwen3.7-max`

**统一 Prompt（三模型共用）：**

```text
[System]
你是量子-经典混合工作流架构师。输出结构化中文 memo，结论必须可执行，区分「推荐 / 条件推荐 / 不推荐」。

[User]
背景：你在维护 `qchem_stack` 流水线，分子 H4（4 电子/active 4 qubit 量级），目标：
(1) 基态能量 (2) 前 2 个激发态能量 (3) 在 NISQ 上可落地的 shot budget 上界。

现有模块：UCCSD-VQE、FermionicAdaptVQE、VQD、QSE（fermionic singles basis）、SCEOM sidecar。
约束：单实验总 shots 上界 5×10^5；允许 statevector 做开发对照，生产路径必须 shot-based。

请输出 memo（中文，800–1200 字），必须包含：
A. 推荐 pipeline 拓扑（文字流程图即可）
B. 三档方案对比表：{方案名, 预期精度, shots 量级, 实现复杂度, 主要风险}
   至少包含：UCCSD-VQE only / Adapt-VQE + VQD / Adapt-VQE + QSE(gaussian_h)
C. 若 Adapt 与 UCCSD 二选一，给出决策树（≥3 个分支条件）
D. 明确「不推荐」的组合及原因（≥2 条）
E. 给算法工程师的 5 条验证实验（可测指标 + 通过阈值）

不要泛泛而谈 NISQ；必须绑定上述模块名与 shots 约束。
```

**评分维度（1–5）：** 约束满足、模块绑定、方案可比性、决策树可用性、验证实验可测性

---

## 二、执行方式

```bash
# 1. 设置 API Key（华北2 按量计费示例）
export DASHSCOPE_API_KEY="sk-xxx"

# 2. 跑 3 场景 × 3 模型 = 9 次调用（Prompt 见 configs/benchmark_llm_scenarios.yaml）
python scripts/benchmark_qwen_triple.py

# 3. 结果输出到 artifacts/qwen_benchmark/
#    - qwen_benchmark_<timestamp>.json  （机器可读）
#    - qwen_benchmark_<timestamp>.md    （原始回答汇总）

# 可选：S3 第四对照 GPT（OpenAI 兼容 API）
export OPENAI_API_KEY="sk-xxx"
python scripts/benchmark_qwen_triple.py --with-gpt55

# GPT 5.5 Cursor 归档（无需 API）：
#    artifacts/qwen_benchmark/gpt55_s3_architecture.md
```

**API 参数建议：** `temperature=0.3`（已在脚本中），每个场景记录 latency 与 token 用量。

---

## 三、人工评分表（填完即得报告核心）

### 3.1 综合得分矩阵（1–5 分，5 最好）

| 场景 | 维度 | qwen-flash | qwen3-coder-next | qwen3.7-max |
|------|------|:----------:|:----------------:|:-----------:|
| S1 日常 | 物理准确性 | | | |
| S1 日常 | 简洁性 | | | |
| S1 日常 | 格式合规 | | | |
| S2 编程 | 逻辑正确 | | | |
| S2 编程 | 可运行性 | | | |
| S2 编程 | 边界 case | | | |
| S3 架构 | 约束满足 | | | |
| S3 架构 | 模块绑定 | | | |
| S3 架构 | 决策可执行 | | | |

### 3.2 效率矩阵（脚本自动填 token / 延迟）

| 场景 | 模型 | 延迟 (s) | 输入 tokens | 输出 tokens | 估算成本* |
|------|------|----------|-------------|-------------|-----------|
| S1 | flash | | | | |
| S1 | coder-next | | | | |
| S1 | max | | | | |
| S2 | flash | | | | |
| S2 | coder-next | | | | |
| S2 | max | | | | |
| S3 | flash | | | | |
| S3 | coder-next | | | | |
| S3 | max | | | | |

\* 成本按 [百炼定价](https://help.aliyun.com/zh/model-studio/model-pricing) 填入。

### 3.3 「主场命中率」判定规则

| 场景 | 主场模型 | 判定「主场胜出」条件 |
|------|----------|----------------------|
| S1 | flash | S1 总分（三维度均值）≥ 其他两模型 + 0.5 分，且 token 最少 |
| S2 | coder-next | S2 逻辑正确 = 5 且可运行性 ≥ 4，且其他模型 ≤ 3 |
| S3 | max | S3 三维度均 ≥ 4，且决策树 + 验证实验齐全 |

---

## 四、分析报告模板（跑完测试后填写）

### 4.1 执行摘要（200 字）

- 测试目的：
- 三模型是否落在设计边界：
- 对公司选型的单一建议：

### 4.2 分场景结论

**S1 — 轻量日常**

- 最佳模型：
- flash 是否足够：
- 用 max/coder 的浪费点（token、延迟、过度解释）：

**S2 — 日常编程**

- 最佳模型：
- flash 失败模式（若存在）：
- max 是否值得为 coding 付溢价：

**S3 — 复杂架构**

- 最佳模型：
- flash/coder 的结构化缺失（若存在）：
- max 相对优势是否 justify 成本：

### 4.3 交叉对比（关键发现）

用一段话回答：

1. **是否存在「一个模型通吃」？** （通常不应）
2. **量子算法工程师日常工作流如何分配三模型？** 建议比例例如 60% / 30% / 10%
3. **与 Claude/GPT 相比的缺口**（若并行测了其他模型）

### 4.4 推荐工作流（Cursor 内）

| 任务类型 | 推荐模型 | 示例 |
|----------|----------|------|
| 解释 JW / 写 meeting notes | qwen-flash | S1 类 prompt |
| 写 ADAPT 选择器 / 修 pytest | qwen3-coder-next | S2 类 prompt |
| H4 激发态 pipeline 方案评审 | qwen3.7-max | S3 类 prompt |

### 4.5 风险与局限

- 单次评测随机性（建议每场景重复 3 次取中位数）
- 商业版参数量未公开，结论基于任务表现而非参数规模
- Prompt 对 qchem_stack 有绑定，换其他量子栈需改 S3

---

## 五、基于模型定位的预期报告（运行前参考）

以下为 **未实际调用 API 时的假设性结论**，正式报告必须以 `artifacts/qwen_benchmark/` 中的真实输出替换。

| 场景 | 预期冠军 | 理由 |
|------|----------|------|
| S1 | flash | 字数与格式约束下成本最低 |
| S2 | coder-next | 编程规则 + 自测 assert 的命中率最高 |
| S3 | qwen3.7-max | 多模块 + shots 约束 + 决策树的同时满足 |

**预期反例（需在真实输出中验证）：**

- flash 在 S2 可能生成不完整代码或漏掉 qubit 并集逻辑
- coder-next 在 S3 可能缺少「不推荐」条目或 shots 量化
- max 在 S1 可能严重超字数，性价比最差

---

## 六、下一步

1. 提供 `DASHSCOPE_API_KEY`，运行 `scripts/benchmark_qwen_triple.py`
2. 按第三节评分表人工打分（建议你和一位同事双盲各评一次）
3. 将第四节模板填完整，即为可提交公司的 **《千问三模型量子算法工作流评测报告》**

如需，可在同脚本上增加 **第 4 组对照**（例如 `qwen-plus` 作为「中等通用」基线）。
