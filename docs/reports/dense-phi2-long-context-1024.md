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
| elapsed_seconds | 20.79 |
| requests_per_second | 0.481 |
| total_input_tokens | 10240 |
| total_output_tokens | 2200 |
| avg_input_tokens_per_successful_request | 1024.0 |
| avg_output_tokens_per_successful_request | 220.0 |
| aggregate_output_tokens_per_second | 105.821 |
| latency_avg_ms | 4154.323 |
| latency_p50_ms | 4085.639 |
| latency_p95_ms | 4428.645 |
| latency_p99_ms | 4428.645 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Total token counts are summed across successful requests.
- Treat failed requests as first-class performance data, not noise.
