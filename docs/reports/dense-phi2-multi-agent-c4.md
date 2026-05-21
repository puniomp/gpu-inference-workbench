# Benchmark Report

| Metric | Value |
| --- | ---: |
| model_id | microsoft/phi-2 |
| model_architecture | dense |
| profile | multi_agent_handoff |
| concurrency | 4 |
| requests | 40 |
| successful_requests | 40 |
| failed_requests | 0 |
| elapsed_seconds | 63.807 |
| requests_per_second | 0.627 |
| total_input_tokens | 7640 |
| total_output_tokens | 7200 |
| avg_input_tokens_per_successful_request | 191.0 |
| avg_output_tokens_per_successful_request | 180.0 |
| aggregate_output_tokens_per_second | 112.84 |
| latency_avg_ms | 6367.171 |
| latency_p50_ms | 6368.741 |
| latency_p95_ms | 6478.917 |
| latency_p99_ms | 6600.327 |

## Interpretation Notes

- Compare p95/p99 latency against the target user experience.
- Compare aggregate tokens/sec across model, runtime, hardware, and batching changes.
- Total token counts are summed across successful requests.
- Treat failed requests as first-class performance data, not noise.
