# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | microsoft/phi-2 |
| model_architecture | dense |
| profile | infra_debug |
| concurrency | 3 |
| requests | 30 |
| successful_requests | 30 |
| failed_requests | 0 |
| elapsed_seconds | 39.863 |
| requests_per_second | 0.753 |
| input_tokens | 2100 |
| output_tokens | 4800 |
| aggregate_output_tokens_per_second | 120.413 |
| latency_avg_ms | 3981.568 |
| latency_p50_ms | 3969.33 |
| latency_p95_ms | 4051.597 |
| latency_p99_ms | 4051.731 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Treat failed requests as first-class performance data, not noise.