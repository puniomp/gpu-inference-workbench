# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | microsoft/phi-2 |
| model_architecture | dense |
| profile | long_summary |
| concurrency | 2 |
| requests | 10 |
| successful_requests | 10 |
| failed_requests | 0 |
| elapsed_seconds | 22.775 |
| requests_per_second | 0.439 |
| input_tokens | 20480 |
| output_tokens | 2200 |
| aggregate_output_tokens_per_second | 96.598 |
| latency_avg_ms | 4548.848 |
| latency_p50_ms | 4542.894 |
| latency_p95_ms | 4573.425 |
| latency_p99_ms | 4573.425 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Treat failed requests as first-class performance data, not noise.