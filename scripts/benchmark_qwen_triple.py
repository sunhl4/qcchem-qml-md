#!/usr/bin/env python3
"""Run LLM benchmark for quantum algorithm engineer evaluation (Qwen + optional GPT)."""

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
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "benchmark_llm_scenarios.yaml"
DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"

# Fallback if config file is missing (keeps script usable in minimal checkouts).
_FALLBACK_SCENARIOS: dict[str, dict[str, str]] = {
    "S1_daily": {
        "title": "轻量日常：概念解释与沟通",
        "boundary_model": "qwen-flash",
        "system": (
            "你是量子计算算法工程师助手。回答要准确、简洁，面向已懂线性代数与量子力学基础的同事。"
        ),
        "user": (
            "请用中文向合作算法工程师解释 Jordan-Wigner 映射（180–220 字，3 条 bullet，不要代码）。"
        ),
    },
    "S2_coding": {
        "title": "日常编程：可运行 Python 实现",
        "boundary_model": "qwen3-coder-next",
        "system": "你是资深 Python 量子算法工程师。只输出一个完整 Python 代码块。",
        "user": "实现 `select_adapt_candidates(pool, gradient_scores, k, max_qubits)` 并附 3 个 assert。",
    },
    "S3_architecture": {
        "title": "复杂推理：架构与资源权衡",
        "boundary_model": "qwen3.7-max",
        "system": "你是量子-经典混合工作流架构师。输出结构化中文 memo。",
        "user": "H4 激发态流水线 memo（A–E），shots ≤ 5×10^5。",
    },
}

_FALLBACK_MODELS: dict[str, dict[str, Any]] = {
    "flash": {"provider": "dashscope", "model_id": "qwen-flash", "label": "qwen-flash"},
    "coder": {
        "provider": "dashscope",
        "model_id": "qwen3-coder-next",
        "label": "qwen3-coder-next",
    },
    "max": {"provider": "dashscope", "model_id": "qwen3.7-max", "label": "qwen3.7-max"},
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


def load_benchmark_config(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    if not path.is_file():
        return _FALLBACK_MODELS, _FALLBACK_SCENARIOS
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    models = data.get("models") or _FALLBACK_MODELS
    scenarios = data.get("scenarios") or _FALLBACK_SCENARIOS
    return models, scenarios


def provider_credentials(
    providers: dict[str, Any],
    provider_name: str,
    *,
    dashscope_api_key: str | None,
    openai_api_key: str | None,
    dashscope_base_url: str,
    openai_base_url: str,
) -> tuple[str, str]:
    spec = providers.get(provider_name) or {}
    env_name = spec.get("api_key_env") or ""
    if provider_name == "dashscope":
        api_key = dashscope_api_key or os.environ.get(env_name or "DASHSCOPE_API_KEY") or ""
        base_url = dashscope_base_url or spec.get("base_url") or DEFAULT_DASHSCOPE_BASE_URL
    else:
        api_key = openai_api_key or os.environ.get(env_name or "OPENAI_API_KEY") or ""
        base_url = openai_base_url or spec.get("base_url") or DEFAULT_OPENAI_BASE_URL
    return base_url, api_key


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


def select_models(
    all_models: dict[str, Any],
    *,
    with_gpt55: bool,
) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for key, spec in all_models.items():
        if spec.get("optional") and not with_gpt55:
            continue
        selected[key] = spec
    return selected


def run_benchmark(
    models: dict[str, Any],
    scenarios: dict[str, dict[str, str]],
    providers: dict[str, Any],
    *,
    dashscope_api_key: str | None,
    openai_api_key: str | None,
    dashscope_base_url: str,
    openai_base_url: str,
    gpt_model_id: str | None,
    timeout: int,
) -> list[RunResult]:
    results: list[RunResult] = []
    creds_cache: dict[str, tuple[str, str]] = {}

    for scenario_id, spec in scenarios.items():
        for model_key, model_spec in models.items():
            allowed = model_spec.get("scenarios")
            if allowed and scenario_id not in allowed:
                continue

            provider_name = model_spec.get("provider", "dashscope")
            if provider_name not in creds_cache:
                base_url, api_key = provider_credentials(
                    providers,
                    provider_name,
                    dashscope_api_key=dashscope_api_key,
                    openai_api_key=openai_api_key,
                    dashscope_base_url=dashscope_base_url,
                    openai_base_url=openai_base_url,
                )
                creds_cache[provider_name] = (base_url, api_key)
            else:
                base_url, api_key = creds_cache[provider_name]

            model_id = model_spec.get("model_id", model_key)
            if model_key == "gpt55" and gpt_model_id:
                model_id = gpt_model_id
            display_id = model_spec.get("label") or model_id

            if not api_key:
                env_hint = (providers.get(provider_name) or {}).get("api_key_env", "API_KEY")
                results.append(
                    RunResult(
                        scenario_id=scenario_id,
                        model_key=model_key,
                        model_id=display_id,
                        latency_s=0.0,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        content="",
                        error=f"Missing API key for {provider_name} (set {env_hint})",
                    )
                )
                continue

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
                        model_id=display_id,
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
                        model_id=display_id,
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
                        model_id=display_id,
                        latency_s=0.0,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        content="",
                        error=str(exc),
                    )
                )
    return results


def write_outputs(
    results: list[RunResult],
    out_dir: Path,
    *,
    scenarios: dict[str, dict[str, str]],
    prefix: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"{prefix}_{stamp}.json"
    md_path = out_dir / f"{prefix}_{stamp}.md"

    json_path.write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    title = "LLM 评测原始结果" if prefix != "qwen_benchmark" else "千问三模型评测原始结果"
    lines = [
        f"# {title}",
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

    for scenario_id in scenarios:
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
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="YAML with providers, models, and scenario prompts",
    )
    parser.add_argument("--api-key", default=os.environ.get("DASHSCOPE_API_KEY"))
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_DASHSCOPE_BASE_URL),
    )
    parser.add_argument("--openai-api-key", default=os.environ.get("OPENAI_API_KEY"))
    parser.add_argument(
        "--openai-base-url",
        default=os.environ.get("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL),
    )
    parser.add_argument(
        "--gpt-model",
        default=os.environ.get("BENCHMARK_GPT_MODEL"),
        help="API model id when using --with-gpt55 (default from config or gpt-5)",
    )
    parser.add_argument(
        "--with-gpt55",
        action="store_true",
        help="Also run optional GPT model on configured scenarios (default: S3 only)",
    )
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/qwen_benchmark"),
    )
    args = parser.parse_args()

    config_data: dict[str, Any] = {}
    if args.config.is_file():
        config_data = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}

    models, scenarios = load_benchmark_config(args.config)
    providers = config_data.get("providers") or {}
    active_models = select_models(models, with_gpt55=args.with_gpt55)

    needs_dashscope = any(
        m.get("provider", "dashscope") == "dashscope" for m in active_models.values()
    )
    if needs_dashscope and not args.api_key:
        print("Set DASHSCOPE_API_KEY or pass --api-key", flush=True)
        return 2

    gpt_model_id = args.gpt_model
    if args.with_gpt55 and not gpt_model_id:
        gpt_spec = models.get("gpt55") or {}
        gpt_model_id = gpt_spec.get("model_id", "gpt-5")

    results = run_benchmark(
        active_models,
        scenarios,
        providers,
        dashscope_api_key=args.api_key,
        openai_api_key=args.openai_api_key,
        dashscope_base_url=args.base_url,
        openai_base_url=args.openai_base_url,
        gpt_model_id=gpt_model_id,
        timeout=args.timeout,
    )
    prefix = "llm_benchmark" if args.with_gpt55 else "qwen_benchmark"
    write_outputs(results, args.out_dir, scenarios=scenarios, prefix=prefix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
