# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | microsoft/phi-2 |
| model_architecture | dense |
| profile | support_agent |
| concurrency | 3 |
| requests | 30 |
| successful_requests | 30 |
| failed_requests | 0 |
| elapsed_seconds | 40.227 |
| requests_per_second | 0.746 |
| input_tokens | 2580 |
| output_tokens | 4800 |
| aggregate_output_tokens_per_second | 119.322 |
| latency_avg_ms | 4016.478 |
| latency_p50_ms | 3981.063 |
| latency_p95_ms | 4353.32 |
| latency_p99_ms | 4356.126 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Treat failed requests as first-class performance data, not noise.