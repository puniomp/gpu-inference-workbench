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
| elapsed_seconds | 19.547 |
| requests_per_second | 0.512 |
| total_input_tokens | 5120 |
| total_output_tokens | 2200 |
| avg_input_tokens_per_successful_request | 512.0 |
| avg_output_tokens_per_successful_request | 220.0 |
| aggregate_output_tokens_per_second | 112.552 |
| latency_avg_ms | 3905.586 |
| latency_p50_ms | 3837.608 |
| latency_p95_ms | 4180.78 |
| latency_p99_ms | 4180.78 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Total token counts are summed across successful requests.
- Treat failed requests as first-class performance data, not noise.
