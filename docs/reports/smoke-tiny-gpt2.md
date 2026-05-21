# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | sshleifer/tiny-gpt2 |
| model_architecture | dense |
| profile | short_chat |
| concurrency | 1 |
| requests | 5 |
| successful_requests | 5 |
| failed_requests | 0 |
| elapsed_seconds | 0.472 |
| requests_per_second | 10.6 |
| input_tokens | 61 |
| output_tokens | 160 |
| aggregate_output_tokens_per_second | 339.188 |
| latency_avg_ms | 88.542 |
| latency_p50_ms | 25.262 |
| latency_p95_ms | 341.381 |
| latency_p99_ms | 341.381 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Treat failed requests as first-class performance data, not noise.