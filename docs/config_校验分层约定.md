# Config 校验分层约定

本文约定 `qchem_stack.config` 的校验分层，目标是让新增字段/策略时保持一致的工程风格与可维护性。

## 1) 分层原则

- `*.py`（如 `quantum.py` / `embedding.py` / `experiment.py`）负责：
  - Pydantic 字段声明（类型、默认值、`Field` 约束）
  - 轻量 `@field_validator` / `@model_validator` 入口（仅转调）
- `_xxx_validation.py` 负责：
  - 复杂跨字段规则
  - 多分支策略校验
  - 规则复用与可测试函数
- `_validation.py` 负责：
  - 跨模块的通用规整函数（如字符串 strip、可选值归一）

## 2) 目录内当前实现

- 通用规整：`config/_validation.py`
- ActiveSpace 规则：`config/_active_space_validation.py`
- ChemistryExtended 规则：`config/_chemistry_extended_validation.py`
- Quantum 规则：`config/_quantum_validation.py`
- Embedding 规则：`config/_embedding_validation.py`
- Experiment 顶层跨模块规则：`config/_experiment_validation.py`

## 3) 新增配置字段时的推荐步骤

1. 先在对应模型文件增加字段与基础 `Field` 约束。
2. 若规则只依赖单字段，优先写 `@field_validator`。
3. 若规则跨字段/跨子模块，写入对应 `_xxx_validation.py`，模型中只保留入口。
4. 在 `tests/test_config_validation_helpers.py` 或现有 config 测试里补函数级与模型级回归用例。
5. 保持错误信息稳定（尽量不破坏已有测试的 `match` 文本）。

## 4) 何时需要新建 `_xxx_validation.py`

满足任一条件即可新建：

- 单模型内跨字段规则超过 2-3 个分支；
- 同一规则在多个模型/路径需要复用；
- 现有模型文件因为 validator 逻辑显著变长（可读性下降）。

## 5) 兼容性要求

- 不变更已公开 YAML 字段名；
- 不在重构中改变业务语义（除非任务明确要求）；
- 保持 `ValidationError` 错误语义与核心提示稳定。
