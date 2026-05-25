#!/usr/bin/env python3
"""Run 3-scenario × 3-model Qwen benchmark for quantum algorithm engineer evaluation."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODELS = {
    "flash": "qwen-flash",
    "coder": "qwen3-coder-next",
    "max": "qwen3.7-max",
}

SCENARIOS = {
    "S1_daily": {
        "title": "轻量日常：概念解释与沟通",
        "boundary_model": "qwen-flash",
        "system": (
            "你是量子计算算法工程师助手。回答要准确、简洁，面向已懂线性代数与量子力学基础的同事。"
        ),
        "user": """请用中文向合作算法工程师解释下面概念，总字数 180–220 字，分 3 条 bullet，不要代码：

主题：Jordan-Wigner 映射如何把费米子算符映射到 qubit 算符。

必须覆盖：
1) 为什么需要映射（量子硬件只原生支持 Pauli 门）
2) 映射后哈密顿量项的形式变化（字符串/局域性）
3) 一个实际代价（如链式 JW 的非局域性或 qubit 数）

禁止编造不存在的定理名称。""",
    },
    "S2_coding": {
        "title": "日常编程：可运行 Python 实现",
        "boundary_model": "qwen3-coder-next",
        "system": (
            "你是资深 Python 量子算法工程师。只输出一个完整 Python 代码块，"
            "使用 typing，函数带 docstring，不要依赖外部库（numpy 可用）。"
        ),
        "user": """实现函数 `select_adapt_candidates(pool, gradient_scores, k, max_qubits)`：

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

附带 3 个 assert 自测（写在 if __name__ == "__main__" 块），不要其他解释文字。""",
    },
    "S3_architecture": {
        "title": "复杂推理：架构与资源权衡",
        "boundary_model": "qwen3.7-max",
        "system": (
            "你是量子-经典混合工作流架构师。输出结构化中文 memo，"
            "结论必须可执行，区分「推荐 / 条件推荐 / 不推荐」。"
        ),
        "user": """背景：你在维护 `qchem_stack` 流水线，分子 H4（4 电子/active 4 qubit 量级），目标：
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

不要泛泛而谈 NISQ；必须绑定上述模块名与 shots 约束。""",
    },
}


@dataclass
class RunResult:
    scenario_id: str
    model_key: str
    model_id: str
    latency_s: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    content: str
    error: str | None = None


def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    timeout: int,
) -> tuple[str, dict, float]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    elapsed = time.perf_counter() - t0
    content = body["choices"][0]["message"]["content"]
    usage = body.get("usage") or {}
    return content, usage, elapsed


def run_benchmark(api_key: str, base_url: str, timeout: int) -> list[RunResult]:
    results: list[RunResult] = []
    for scenario_id, spec in SCENARIOS.items():
        for model_key, model_id in MODELS.items():
            try:
                content, usage, elapsed = chat_completion(
                    base_url,
                    api_key,
                    model_id,
                    spec["system"],
                    spec["user"],
                    timeout,
                )
                results.append(
                    RunResult(
                        scenario_id=scenario_id,
                        model_key=model_key,
                        model_id=model_id,
                        latency_s=round(elapsed, 2),
                        prompt_tokens=int(usage.get("prompt_tokens") or 0),
                        completion_tokens=int(usage.get("completion_tokens") or 0),
                        total_tokens=int(usage.get("total_tokens") or 0),
                        content=content,
                    )
                )
            except urllib.error.HTTPError as exc:
                err_body = exc.read().decode("utf-8", errors="replace")
                results.append(
                    RunResult(
                        scenario_id=scenario_id,
                        model_key=model_key,
                        model_id=model_id,
                        latency_s=0.0,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        content="",
                        error=f"HTTP {exc.code}: {err_body[:500]}",
                    )
                )
            except OSError as exc:
                results.append(
                    RunResult(
                        scenario_id=scenario_id,
                        model_key=model_key,
                        model_id=model_id,
                        latency_s=0.0,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        content="",
                        error=str(exc),
                    )
                )
    return results


def write_outputs(results: list[RunResult], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"qwen_benchmark_{stamp}.json"
    md_path = out_dir / f"qwen_benchmark_{stamp}.md"

    json_path.write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# 千问三模型评测原始结果",
        "",
        f"生成时间（UTC）：{stamp}",
        "",
        "## 汇总",
        "",
        "| 场景 | 模型 | 延迟(s) | 输入 tokens | 输出 tokens | 状态 |",
        "|------|------|---------|-------------|-------------|------|",
    ]
    for r in results:
        status = "OK" if not r.error else f"ERR: {r.error[:40]}"
        lines.append(
            f"| {r.scenario_id} | {r.model_id} | {r.latency_s} | "
            f"{r.prompt_tokens} | {r.completion_tokens} | {status} |"
        )

    for scenario_id in SCENARIOS:
        lines.extend(["", f"## {scenario_id}", ""])
        for r in results:
            if r.scenario_id != scenario_id:
                continue
            lines.extend([f"### {r.model_id}", ""])
            if r.error:
                lines.append(f"**Error:** {r.error}")
            else:
                lines.append(r.content)
            lines.extend(["", "---", ""])

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-key", default=os.environ.get("DASHSCOPE_API_KEY"))
    parser.add_argument(
        "--base-url", default=os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL)
    )
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/qwen_benchmark"),
    )
    args = parser.parse_args()
    if not args.api_key:
        print("Set DASHSCOPE_API_KEY or pass --api-key", flush=True)
        return 2

    results = run_benchmark(args.api_key, args.base_url, args.timeout)
    write_outputs(results, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
