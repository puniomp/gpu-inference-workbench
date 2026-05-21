from __future__ import annotations

import argparse
import asyncio
import csv
import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx


PROFILES = {
    "short_chat": [
        "Explain LLM inference latency in two concise paragraphs.",
        "What are common GPU bottlenecks during text generation?",
        "Summarize the tradeoff between throughput and latency for LLM serving.",
    ],
    "support_agent": [
        """
You are answering a support ticket for an enterprise AI assistant.

Retrieved context:
- The customer uses a retrieval-augmented generation workflow over product manuals.
- p95 latency increased after the team added longer retrieved passages.
- The application now sends 12 chunks of context instead of 4.
- The model output quality improved slightly, but user satisfaction dropped.

Write a concise response with:
1. likely root cause
2. two experiments to run
3. one recommendation
""".strip(),
        """
You are helping a product team debug an AI support assistant.

Retrieved context:
- The assistant sometimes answers without citations.
- The retriever returns relevant documents, but the generation prompt is near the context limit.
- The team wants to keep latency below 2 seconds at p95.

Write a practical engineering recommendation.
""".strip(),
    ],
    "infra_debug": [
        """
You are reviewing logs from an LLM inference service.

Symptoms:
- p50 latency is stable.
- p99 latency spikes during traffic bursts.
- GPU memory is close to full.
- Some requests wait in the application queue before generation starts.

Identify the likely bottleneck and the next three debugging steps.
""".strip(),
        """
You are advising a team deploying an internal coding assistant.

Current setup:
- One GPU instance.
- FastAPI application server.
- Hugging Face model loaded in-process.
- No request batching.
- Traffic comes in bursts after team meetings.

Explain which bottleneck you would investigate first and why.
""".strip(),
    ],
    "multi_agent_handoff": [
        """
You are the coordinator in a multi-agent applied AI workflow.

Planner notes:
- User wants to understand why a retrieval-augmented assistant became slower after adding more
  context.
- The task should be split into retrieval quality, prompt length, model runtime, and serving
  concurrency checks.

Retriever notes:
- The retriever now returns 12 chunks instead of 4.
- Average prompt length is close to the configured input limit.
- Top documents are relevant, but several chunks repeat the same troubleshooting section.

Executor notes:
- p95 latency increased after the prompt change.
- GPU memory usage is stable, but request queue time increased during traffic bursts.
- No request failures were observed in the latest run.

Reviewer notes:
- The answer should avoid over-optimizing retrieval if the main bottleneck is generation time.
- The final recommendation should include one measurement step before changing architecture.

Write the coordinator response:
1. what each agent found
2. the likely bottleneck
3. the next experiment
4. one concise recommendation
""".strip(),
        """
You are synthesizing a handoff from an AI coding assistant workflow.

Planner notes:
- The user asked for help debugging slow inference.
- The plan is to check prompt size, output length, runtime backend, and concurrency.

Tool agent notes:
- The benchmark uses a PyTorch Transformers backend.
- The service is running on one GPU.
- The current profile uses a fixed output token cap.

Critic notes:
- The benchmark must distinguish total tokens across the run from tokens per request.
- The writeup should not imply a single request used the total token count.

Write a final handoff that a technical lead could use to decide the next benchmark.
""".strip(),
    ],
    "long_context_summary": [
        "Summarize this incident review for an engineering director. Focus on root cause, "
        "customer impact, and prevention. "
        + (
            "The service experienced elevated latency after a model rollout. "
            "The new prompt template included more retrieved context, increasing input tokens. "
            "Concurrency also increased because several teams began testing the assistant. "
            "GPU memory pressure rose, queueing became visible, and p99 latency regressed. "
            "The team mitigated by reducing retrieved chunks, adding request limits, and planning "
            "a serving-runtime evaluation. "
        )
        * 60
    ],
}


@dataclass(frozen=True)
class RequestMetric:
    request_id: int
    model_id: str
    model_architecture: str
    profile: str
    concurrency: int
    ok: bool
    latency_ms: float
    input_tokens: int
    output_tokens: int
    tokens_per_second: float
    status_code: int | None
    error: str | None


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((pct / 100) * (len(ordered) - 1)))
    return ordered[index]


async def send_request(
    client: httpx.AsyncClient,
    args: argparse.Namespace,
    request_id: int,
    prompt: str,
) -> RequestMetric:
    started = time.perf_counter()
    try:
        response = await client.post(
            args.url,
            json={"prompt": prompt, "max_new_tokens": args.max_new_tokens},
            timeout=None,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        if response.is_error:
            return RequestMetric(
                request_id,
                args.model_id,
                args.model_architecture,
                args.profile,
                args.concurrency,
                False,
                latency_ms,
                0,
                0,
                0.0,
                response.status_code,
                response.text,
            )

        payload = response.json()
        return RequestMetric(
            request_id=request_id,
            model_id=args.model_id,
            model_architecture=args.model_architecture,
            profile=args.profile,
            concurrency=args.concurrency,
            ok=True,
            latency_ms=latency_ms,
            input_tokens=int(payload["input_tokens"]),
            output_tokens=int(payload["output_tokens"]),
            tokens_per_second=float(payload["tokens_per_second"]),
            status_code=response.status_code,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001 - benchmark scripts should preserve failures as data.
        latency_ms = (time.perf_counter() - started) * 1000
        return RequestMetric(
            request_id,
            args.model_id,
            args.model_architecture,
            args.profile,
            args.concurrency,
            False,
            latency_ms,
            0,
            0,
            0.0,
            None,
            str(exc),
        )


async def run_benchmark(args: argparse.Namespace) -> list[RequestMetric]:
    prompts = PROFILES[args.profile]
    limits = httpx.Limits(max_connections=args.concurrency)
    semaphore = asyncio.Semaphore(args.concurrency)

    async with httpx.AsyncClient(limits=limits) as client:
        async def bounded_send(request_id: int) -> RequestMetric:
            async with semaphore:
                prompt = prompts[request_id % len(prompts)]
                return await send_request(client, args, request_id, prompt)

        return await asyncio.gather(*(bounded_send(i) for i in range(args.requests)))


def summarize(metrics: list[RequestMetric], elapsed_seconds: float) -> dict[str, float | int | str]:
    successful = [metric for metric in metrics if metric.ok]
    latencies = [metric.latency_ms for metric in successful]
    output_tokens = sum(metric.output_tokens for metric in successful)
    input_tokens = sum(metric.input_tokens for metric in successful)
    successful_count = len(successful)
    first = successful[0] if successful else None
    return {
        "model_id": first.model_id if first else "unknown",
        "model_architecture": first.model_architecture if first else "unknown",
        "profile": first.profile if first else "unknown",
        "concurrency": first.concurrency if first else 0,
        "requests": len(metrics),
        "successful_requests": len(successful),
        "failed_requests": len(metrics) - len(successful),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "requests_per_second": round(len(successful) / elapsed_seconds, 3) if elapsed_seconds else 0,
        "total_input_tokens": input_tokens,
        "total_output_tokens": output_tokens,
        "avg_input_tokens_per_successful_request": round(input_tokens / successful_count, 3)
        if successful_count
        else 0,
        "avg_output_tokens_per_successful_request": round(output_tokens / successful_count, 3)
        if successful_count
        else 0,
        "aggregate_output_tokens_per_second": round(output_tokens / elapsed_seconds, 3)
        if elapsed_seconds
        else 0,
        "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0,
        "latency_p50_ms": round(percentile(latencies, 50), 3),
        "latency_p95_ms": round(percentile(latencies, 95), 3),
        "latency_p99_ms": round(percentile(latencies, 99), 3),
    }


def write_outputs(
    out_prefix: Path,
    metrics: list[RequestMetric],
    summary: dict[str, float | int | str],
) -> None:
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    json_path = out_prefix.with_suffix(".json")
    csv_path = out_prefix.with_suffix(".csv")
    md_path = out_prefix.with_suffix(".md")

    json_path.write_text(
        json.dumps({"summary": summary, "requests": [asdict(metric) for metric in metrics]}, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(asdict(metrics[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(metric) for metric in metrics)

    lines = [
        "# Benchmark Report",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        *[f"| {key} | {value} |" for key, value in summary.items()],
        "",
        "## Interpretation Notes",
        "",
        "- Compare p95/p99 latency against the target user experience.",
        "- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.",
        "- Total token counts are summed across successful requests.",
        "- Treat failed requests as first-class performance data, not noise.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark the LLM inference HTTP endpoint.")
    parser.add_argument("--url", default="http://localhost:8000/generate")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="short_chat")
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--model-id", default="unknown")
    parser.add_argument("--model-architecture", choices=["dense", "moe", "unknown"], default="unknown")
    parser.add_argument("--out", type=Path, default=Path("docs/reports/local-benchmark"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    metrics = asyncio.run(run_benchmark(args))
    elapsed_seconds = time.perf_counter() - started
    summary = summarize(metrics, elapsed_seconds)
    write_outputs(args.out, metrics, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
