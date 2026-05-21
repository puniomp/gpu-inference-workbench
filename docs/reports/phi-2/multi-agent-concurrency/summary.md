# Phi-2 Multi-Agent Concurrency Sweep

This sweep keeps the model, backend, GPU, output cap, and workload fixed while changing request concurrency.

Setup:

- Model: `microsoft/phi-2`
- Architecture: dense
- Backend: PyTorch + Hugging Face Transformers
- GPU: RTX 4090
- Profile: `multi_agent_handoff`
- Requests/run: 40
- Max output tokens/request: 180

| Concurrency | Req/s | Output tok/s | p50 latency | p95 latency | p99 latency | Failures |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.659 | 118.685 | 1521.663 ms | 1525.447 ms | 1543.326 ms | 0 |
| 2 | 0.669 | 120.434 | 2985.18 ms | 3001.116 ms | 3018.792 ms | 0 |
| 4 | 0.627 | 112.84 | 6368.741 ms | 6478.917 ms | 6600.327 ms | 0 |
| 8 | 0.514 | 92.471 | 15524.506 ms | 15824.516 ms | 15976.4 ms | 0 |

Early read:

The baseline handles concurrency 1-2 without improving request throughput much, then degrades at higher concurrency. p95 latency rises from ~1.5s at concurrency 1 to ~15.8s at concurrency 8, while aggregate output throughput falls from ~118.7 to ~92.5 tokens/sec.

This suggests the current PyTorch/Transformers + FastAPI backend is useful as a transparent baseline, but not optimized for concurrent LLM serving. A future runtime comparison with vLLM, Triton, or TensorRT-LLM should use this same workload shape.
