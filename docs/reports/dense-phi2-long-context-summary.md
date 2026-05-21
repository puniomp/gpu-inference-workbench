# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | microsoft/phi-2 |
| model_architecture | dense |
| profile | long_context_summary |
| concurrency | 2 |
| requests | 10 |
| successful_requests | 10 |
| failed_requests | 0 |
| elapsed_seconds | 22.757 |
| requests_per_second | 0.439 |
| total_input_tokens | 20480 |
| total_output_tokens | 2200 |
| avg_input_tokens_per_successful_request | 2048.0 |
| avg_output_tokens_per_successful_request | 220.0 |
| aggregate_output_tokens_per_second | 96.672 |
| latency_avg_ms | 4545.027 |
| latency_p50_ms | 4540.78 |
| latency_p95_ms | 4561.256 |
| latency_p99_ms | 4561.256 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Total token counts are summed across successful requests.
- Treat failed requests as first-class performance data, not noise.
